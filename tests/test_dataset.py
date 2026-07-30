from collections import Counter
from pathlib import Path

from auditpoison.io import load_bundles
from auditpoison.metrics import evaluate_predictions
from auditpoison.parsing import parse_model_response
from auditpoison.prompting import render_user_prompt
from auditpoison.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_repository_validates():
    assert validate_repository(ROOT) == []


def test_day2_composition():
    bundles = load_bundles(ROOT)
    assert len(bundles) == 40
    assert Counter(b['variant'] for b in bundles) == {'clean': 20, 'attacked': 10, 'benign': 10}
    assert Counter(b['oracle']['label'] for b in bundles) == {
        'compliant': 20, 'non_compliant': 15, 'insufficient_evidence': 5
    }


def test_attack_and_perturbation_coverage():
    bundles = load_bundles(ROOT)
    attacks = {b['attack']['family'] for b in bundles if b['variant'] == 'attacked'}
    perturbations = {b['perturbation']['family'] for b in bundles if b['variant'] == 'benign'}
    assert attacks == {
        'instruction_injection', 'authority_spoofing', 'contradiction_flooding',
        'temporal_rollback', 'scope_substitution', 'evidence_omission'
    }
    assert perturbations == {
        'formatting_noise', 'evidence_reordering', 'irrelevant_context',
        'duplicate_support', 'semantic_paraphrase', 'metadata_noise'
    }


def test_prompt_does_not_leak_gold_or_transformation_metadata():
    attacked = next(b for b in load_bundles(ROOT) if b['variant'] == 'attacked')
    prompt = render_user_prompt(attacked)
    assert '"oracle"' not in prompt
    assert '"attack"' not in prompt
    assert 'attacker_capability' not in prompt
    assert 'expected_secure_behavior' not in prompt
    assert attacked['oracle']['rationale'] not in prompt
    assert attacked['bundle_id'] not in prompt
    assert '-attacked' not in prompt


def test_parser_accepts_fenced_json_and_validates_evidence_ids():
    bundle = next(b for b in load_bundles(ROOT) if b['bundle_id'] == 'AP-AC2-001-attacked')
    parsed = parse_model_response(bundle, '```json\n{"label":"non_compliant","confidence":0.9,"cited_evidence_ids":["E2"],"flagged_evidence_ids":["E4"],"rationale":"x"}\n```')
    assert parsed['label'] == 'non_compliant'
    assert parsed['flagged_evidence_ids'] == ['E4']


def test_perfect_predictions_have_perfect_core_metrics():
    bundles = load_bundles(ROOT)
    predictions = []
    for b in bundles:
        predictions.append({
            'bundle_id': b['bundle_id'],
            'label': b['oracle']['label'],
            'confidence': 1.0,
            'cited_evidence_ids': b['oracle']['supporting_evidence_ids'] + b['oracle']['contradicting_evidence_ids'],
            'flagged_evidence_ids': b['attack']['target_evidence_ids'] if b['variant'] == 'attacked' else [],
        })
    result = evaluate_predictions(bundles, predictions)
    assert result['accuracy'] == 1.0
    assert result['macro_f1'] == 1.0
    assert result['false_assurance_rate'] == 0.0
    assert result['paired_attack_success_rate'] == 0.0
    assert result['benign_label_consistency'] == 1.0
    assert result['benign_both_correct_rate'] == 1.0
    assert result['attack_evidence_detection_recall'] == 1.0
    assert result['benign_evidence_false_flag_rate'] == 0.0
