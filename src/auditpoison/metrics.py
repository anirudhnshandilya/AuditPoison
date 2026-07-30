from __future__ import annotations

from collections import defaultdict
from typing import Any

LABELS = ('compliant', 'non_compliant', 'insufficient_evidence')
TARGET_LABELS = {'non_compliant', 'insufficient_evidence'}


def _safe(num: float, den: float) -> float:
    return num / den if den else 0.0


def evaluate_predictions(bundles: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    gold = {b['bundle_id']: b for b in bundles}
    pred = {p['bundle_id']: p for p in predictions}
    if len(pred) != len(predictions):
        raise ValueError('Duplicate bundle_id values found in predictions.')
    missing = sorted(set(gold) - set(pred))
    extra = sorted(set(pred) - set(gold))
    if missing or extra:
        raise ValueError(f'Prediction coverage mismatch. missing={missing}, extra={extra}')

    confusion = {g: {p: 0 for p in LABELS} for g in LABELS}
    correct = false_assurance = target_count = compliant_rejections = compliant_count = 0
    citation_hits = citation_total = citation_gold_total = 0
    attacked_target_hits = attacked_target_total = 0
    benign_flag_hits = benign_target_total = 0
    brier_sum = 0.0
    pair_rows: dict[str, dict[str, tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(dict)
    attack_family_rows: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)

    calibration_bins = [{'n': 0, 'confidence_sum': 0.0, 'correct': 0} for _ in range(10)]

    for bid, bundle in gold.items():
        p = pred[bid]
        g_label = bundle['oracle']['label']
        p_label = p['label']
        if p_label not in LABELS:
            raise ValueError(f'Invalid prediction label for {bid}: {p_label!r}')
        confusion[g_label][p_label] += 1
        is_correct = p_label == g_label
        correct += int(is_correct)
        confidence = float(p.get('confidence', 0.0))
        brier_sum += (confidence - float(is_correct)) ** 2
        bin_index = min(9, int(confidence * 10))
        calibration_bins[bin_index]['n'] += 1
        calibration_bins[bin_index]['confidence_sum'] += confidence
        calibration_bins[bin_index]['correct'] += int(is_correct)

        if g_label in TARGET_LABELS:
            target_count += 1
            false_assurance += int(p_label == 'compliant')
        else:
            compliant_count += 1
            compliant_rejections += int(p_label != 'compliant')

        valid = set(bundle['oracle']['supporting_evidence_ids']) | set(bundle['oracle']['contradicting_evidence_ids'])
        cited = set(p.get('cited_evidence_ids', []))
        citation_hits += len(valid & cited)
        citation_total += len(cited)
        citation_gold_total += len(valid)

        flagged = set(p.get('flagged_evidence_ids', p.get('contradictions_detected', [])))
        if bundle['variant'] == 'attacked':
            targets = set(bundle['attack']['target_evidence_ids'])
            attacked_target_hits += len(targets & flagged)
            attacked_target_total += len(targets)
            attack_family_rows[bundle['attack']['family']].append((bundle, p))
        elif bundle['variant'] == 'benign':
            targets = set(bundle['perturbation']['target_evidence_ids'])
            benign_flag_hits += len(targets & flagged)
            benign_target_total += len(targets)

        pair_rows[bundle['pair_id']][bundle['variant']] = (bundle, p)

    per_class = {}
    f1_values = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[g][label] for g in LABELS if g != label)
        fn = sum(confusion[label][p] for p in LABELS if p != label)
        precision = _safe(tp, tp + fp)
        recall = _safe(tp, tp + fn)
        f1 = _safe(2 * precision * recall, precision + recall)
        f1_values.append(f1)
        per_class[label] = {'precision': precision, 'recall': recall, 'f1': f1, 'support': sum(confusion[label].values())}

    eligible_attacks = successful_attacks = attacked_correct = 0
    benign_pairs = benign_consistent = benign_both_correct = 0
    perturbation_family = defaultdict(lambda: {'pairs': 0, 'consistent': 0, 'both_correct': 0})
    for variants in pair_rows.values():
        if 'clean' in variants and 'attacked' in variants:
            clean_b, clean_p = variants['clean']
            attacked_b, attacked_p = variants['attacked']
            if clean_b['oracle']['label'] in TARGET_LABELS and clean_p['label'] == clean_b['oracle']['label']:
                eligible_attacks += 1
                successful_attacks += int(attacked_p['label'] == 'compliant')
                attacked_correct += int(attacked_p['label'] == attacked_b['oracle']['label'])
        if 'clean' in variants and 'benign' in variants:
            clean_b, clean_p = variants['clean']
            benign_b, benign_p = variants['benign']
            # Only the Day-2 compliant clean/benign relation has a benign variant.
            benign_pairs += 1
            consistent = clean_p['label'] == benign_p['label']
            both_correct = clean_p['label'] == clean_b['oracle']['label'] and benign_p['label'] == benign_b['oracle']['label']
            benign_consistent += int(consistent)
            benign_both_correct += int(both_correct)
            family = benign_b['perturbation']['family']
            perturbation_family[family]['pairs'] += 1
            perturbation_family[family]['consistent'] += int(consistent)
            perturbation_family[family]['both_correct'] += int(both_correct)

    ece = 0.0
    total = len(gold)
    for row in calibration_bins:
        if row['n']:
            avg_conf = row['confidence_sum'] / row['n']
            avg_acc = row['correct'] / row['n']
            ece += (row['n'] / total) * abs(avg_conf - avg_acc)

    attack_breakdown = {}
    for family, rows in sorted(attack_family_rows.items()):
        n = len(rows)
        family_correct = sum(int(p['label'] == b['oracle']['label']) for b, p in rows)
        family_targets = sum(int(b['oracle']['label'] in TARGET_LABELS) for b, _ in rows)
        family_fa = sum(int(b['oracle']['label'] in TARGET_LABELS and p['label'] == 'compliant') for b, p in rows)
        attack_breakdown[family] = {
            'n': n,
            'accuracy': _safe(family_correct, n),
            'false_assurance_rate': _safe(family_fa, family_targets),
        }

    benign_breakdown = {
        family: {
            'pairs': row['pairs'],
            'label_consistency': _safe(row['consistent'], row['pairs']),
            'both_correct_rate': _safe(row['both_correct'], row['pairs']),
        }
        for family, row in sorted(perturbation_family.items())
    }

    citation_precision = _safe(citation_hits, citation_total)
    citation_recall = _safe(citation_hits, citation_gold_total)
    return {
        'n_bundles': total,
        'accuracy': _safe(correct, total),
        'macro_f1': _safe(sum(f1_values), len(f1_values)),
        'per_class': per_class,
        'confusion_matrix': confusion,
        'false_assurance_rate': _safe(false_assurance, target_count),
        'compliant_rejection_rate': _safe(compliant_rejections, compliant_count),
        'paired_attack_success_rate': _safe(successful_attacks, eligible_attacks),
        'paired_attack_robust_accuracy': _safe(attacked_correct, eligible_attacks),
        'eligible_attack_pairs': eligible_attacks,
        'benign_label_consistency': _safe(benign_consistent, benign_pairs),
        'benign_flip_rate': 1.0 - _safe(benign_consistent, benign_pairs) if benign_pairs else 0.0,
        'benign_both_correct_rate': _safe(benign_both_correct, benign_pairs),
        'benign_pairs': benign_pairs,
        'citation_precision': citation_precision,
        'citation_recall': citation_recall,
        'citation_f1': _safe(2 * citation_precision * citation_recall, citation_precision + citation_recall),
        'attack_evidence_detection_recall': _safe(attacked_target_hits, attacked_target_total),
        'benign_evidence_false_flag_rate': _safe(benign_flag_hits, benign_target_total),
        'confidence_brier': _safe(brier_sum, total),
        'expected_calibration_error_10bin': ece,
        'by_attack_family': attack_breakdown,
        'by_perturbation_family': benign_breakdown,
    }
