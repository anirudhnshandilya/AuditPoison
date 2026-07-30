from pathlib import Path

from auditpoison.io import load_bundles
from auditpoison.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_repository_validates():
    assert validate_repository(ROOT) == []


def test_pilot_has_ten_pairs_and_six_attack_families():
    bundles = load_bundles(ROOT)
    assert len(bundles) == 20
    assert len({b['pair_id'] for b in bundles}) == 10
    families = {b['attack']['family'] for b in bundles if b['variant'] == 'attacked'}
    assert families == {
        'instruction_injection', 'authority_spoofing', 'contradiction_flooding',
        'temporal_rollback', 'scope_substitution', 'evidence_omission'
    }


def test_no_compliant_oracles_in_red_team_pilot():
    assert all(b['oracle']['label'] != 'compliant' for b in load_bundles(ROOT))
