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
    for pair in manifest.get('pairs', []):
        clean = by_id.get(pair['clean_bundle_id'])
        attacked = by_id.get(pair['attacked_bundle_id'])
        if clean is None:
            errors.append(f"Manifest missing clean bundle: {pair['clean_bundle_id']}")
        if attacked is None:
            errors.append(f"Manifest missing attacked bundle: {pair['attacked_bundle_id']}")
        if clean and attacked:
            if clean['pair_id'] != attacked['pair_id']:
                errors.append(f"Pair mismatch: {clean['bundle_id']} vs {attacked['bundle_id']}")
            if clean['control']['control_id'] != attacked['control']['control_id']:
                errors.append(f"Control mismatch in pair {clean['pair_id']}")
            if clean['variant'] != 'clean' or attacked['variant'] != 'attacked':
                errors.append(f"Variant mismatch in pair {clean['pair_id']}")

    counts = Counter(b['variant'] for b in bundles)
    if counts['clean'] != counts['attacked']:
        errors.append(f"Unbalanced pair count: {dict(counts)}")
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
    if bundle.get('variant') == 'clean' and attack.get('present'):
        errors.append(f'{bid}: clean variant cannot have attack.present=true')
    if bundle.get('variant') == 'attacked' and not attack.get('present'):
        errors.append(f'{bid}: attacked variant must have attack.present=true')
    if attack.get('present'):
        if not attack.get('family'):
            errors.append(f'{bid}: attacked bundle missing family')
        bad_targets = sorted(set(attack.get('target_evidence_ids', [])) - existing)
        if bad_targets:
            errors.append(f'{bid}: attack targets missing evidence {bad_targets}')
        if attack.get('family') == 'evidence_omission' and not attack.get('removed_evidence_ids'):
            errors.append(f'{bid}: omission attack requires removed_evidence_ids')
    return errors
