from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .io import load_bundles, load_json

VALID_LABELS = {'compliant', 'non_compliant', 'insufficient_evidence'}


def validate_repository(root: str | Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    schema = load_json(root / 'schema' / 'evidence_bundle.schema.json')
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    bundles = load_bundles(root)
    if not bundles:
        return ['No bundles found.']

    by_id: dict[str, dict[str, Any]] = {}
    for bundle in bundles:
        bid = bundle.get('bundle_id', '<missing>')
        if bid in by_id:
            errors.append(f'Duplicate bundle_id: {bid}')
        by_id[bid] = bundle
        for err in sorted(validator.iter_errors(bundle), key=lambda e: list(e.path)):
            loc = '.'.join(str(x) for x in err.path)
            errors.append(f'{bid}: schema {loc}: {err.message}')
        errors.extend(_semantic_errors(bundle))

    manifest = load_json(root / 'data' / 'manifest.json')
    manifest_ids: set[str] = set()
    for pair in manifest.get('pairs', []):
        base = by_id.get(pair['base_bundle_id'])
        transformed = by_id.get(pair['transformed_bundle_id'])
        manifest_ids.update([pair['base_bundle_id'], pair['transformed_bundle_id']])
        if base is None:
            errors.append(f"Manifest missing base bundle: {pair['base_bundle_id']}")
        if transformed is None:
            errors.append(f"Manifest missing transformed bundle: {pair['transformed_bundle_id']}")
        if base and transformed:
            if base['pair_id'] != transformed['pair_id'] or base['pair_id'] != pair['pair_id']:
                errors.append(f"Pair mismatch in {pair['pair_id']}")
            if base['control']['control_id'] != transformed['control']['control_id']:
                errors.append(f"Control mismatch in pair {pair['pair_id']}")
            if base['variant'] != pair['base_variant'] or transformed['variant'] != pair['transformed_variant']:
                errors.append(f"Variant mismatch in pair {pair['pair_id']}")
            if base['oracle']['label'] != pair['base_label'] or transformed['oracle']['label'] != pair['transformed_label']:
                errors.append(f"Label mismatch in manifest pair {pair['pair_id']}")
            if pair['relation_type'] == 'adversarial' and transformed['variant'] != 'attacked':
                errors.append(f"Adversarial pair {pair['pair_id']} must end in attacked variant")
            if pair['relation_type'] == 'benign_stability' and transformed['variant'] != 'benign':
                errors.append(f"Benign pair {pair['pair_id']} must end in benign variant")

    if manifest_ids != set(by_id):
        errors.append(f'Manifest coverage mismatch: unlisted={sorted(set(by_id)-manifest_ids)}, missing={sorted(manifest_ids-set(by_id))}')

    counts = Counter(b['variant'] for b in bundles)
    expected = {'clean': 20, 'attacked': 10, 'benign': 10}
    if dict(counts) != expected:
        errors.append(f'Unexpected variant composition: {dict(counts)} != {expected}')
    labels = Counter(b['oracle']['label'] for b in bundles)
    expected_labels = {'compliant': 20, 'non_compliant': 15, 'insufficient_evidence': 5}
    if dict(labels) != expected_labels:
        errors.append(f'Unexpected label composition: {dict(labels)} != {expected_labels}')
    return errors


def _semantic_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    bid = bundle.get('bundle_id', '<missing>')
    evidence_ids = [e.get('evidence_id') for e in bundle.get('evidence', [])]
    existing = set(evidence_ids)
    if len(existing) != len(evidence_ids):
        errors.append(f'{bid}: duplicate evidence_id')

    oracle = bundle.get('oracle', {})
    refs: list[str] = []
    refs += oracle.get('supporting_evidence_ids', [])
    refs += oracle.get('contradicting_evidence_ids', [])
    for predicate in oracle.get('predicates', []):
        refs += predicate.get('evidence_ids', [])
    missing_refs = sorted(set(refs) - existing)
    if missing_refs:
        errors.append(f'{bid}: oracle references missing evidence {missing_refs}')

    label = oracle.get('label')
    statuses = [p.get('status') for p in oracle.get('predicates', [])]
    derived = 'compliant'
    if 'failed' in statuses:
        derived = 'non_compliant'
    elif 'unknown' in statuses:
        derived = 'insufficient_evidence'
    if label in VALID_LABELS and label != derived:
        errors.append(f'{bid}: label {label} conflicts with predicate-derived label {derived}')

    attack = bundle.get('attack', {})
    perturbation = bundle.get('perturbation', {})
    variant = bundle.get('variant')
    if variant == 'attacked':
        if not attack.get('present') or perturbation.get('present'):
            errors.append(f'{bid}: attacked variant requires attack only')
    elif variant == 'benign':
        if attack.get('present') or not perturbation.get('present'):
            errors.append(f'{bid}: benign variant requires perturbation only')
    elif variant == 'clean':
        if attack.get('present') or perturbation.get('present'):
            errors.append(f'{bid}: clean variant cannot contain a transformation')

    if attack.get('present'):
        if not attack.get('family'):
            errors.append(f'{bid}: attacked bundle missing family')
        bad_targets = sorted(set(attack.get('target_evidence_ids', [])) - existing)
        if bad_targets:
            errors.append(f'{bid}: attack targets missing evidence {bad_targets}')
        if attack.get('family') == 'evidence_omission' and not attack.get('removed_evidence_ids'):
            errors.append(f'{bid}: omission attack requires removed_evidence_ids')
    if perturbation.get('present'):
        if not perturbation.get('family'):
            errors.append(f'{bid}: benign bundle missing perturbation family')
        bad_targets = sorted(set(perturbation.get('target_evidence_ids', [])) - existing)
        if bad_targets:
            errors.append(f'{bid}: perturbation targets missing evidence {bad_targets}')
    return errors
