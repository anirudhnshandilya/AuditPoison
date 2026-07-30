import json
from pathlib import Path

from auditpoison.reporting import latex_table, markdown_table
from auditpoison.repro import build_run_manifest, dataset_sha256, verify_manifest, write_manifest
from auditpoison.providers import OpenAICompatibleAdapter, OUTPUT_JSON_SCHEMA
from auditpoison.io import append_jsonl, read_jsonl


def test_openai_compatible_endpoint():
    adapter = OpenAICompatibleAdapter("model", "prompt", "secret", "https://example.test/v1")
    assert adapter._endpoint() == "https://example.test/v1/chat/completions"
    adapter = OpenAICompatibleAdapter("model", "prompt", "secret", "https://example.test/v1/chat/completions")
    assert adapter._endpoint() == "https://example.test/v1/chat/completions"


def test_output_schema_has_canonical_fields():
    assert set(OUTPUT_JSON_SCHEMA["required"]) == {
        "label", "confidence", "cited_evidence_ids", "flagged_evidence_ids", "rationale"
    }


def test_reporting_outputs_tables(tmp_path):
    row = {
        "_path": "metrics.json",
        "model": "demo_model",
        "accuracy": 0.9,
        "macro_f1": 0.8,
        "false_assurance_rate": 0.1,
        "paired_attack_success_rate": 0.2,
        "benign_label_consistency": 1.0,
        "citation_f1": 0.5,
        "attack_evidence_detection_recall": 0.4,
    }
    assert "demo_model" in markdown_table([row])
    assert "demo\\_model" in latex_table([row])


def test_manifest_round_trip(project_root, tmp_path):
    predictions = tmp_path / "predictions.jsonl"
    predictions.write_text('{"bundle_id":"x"}\n', encoding="utf-8")
    manifest = build_run_manifest(
        project_root,
        predictions,
        adapter="test",
        model="test-model",
        provider="test-provider",
        config={"temperature": 0},
        bundle_ids=["x"],
    )
    manifest_path = tmp_path / "predictions.manifest.json"
    write_manifest(manifest_path, manifest)
    assert verify_manifest(project_root, manifest_path) == []
    predictions.write_text('{"bundle_id":"changed"}\n', encoding="utf-8")
    assert "predictions hash mismatch" in verify_manifest(project_root, manifest_path)


def test_dataset_hash_is_stable(project_root):
    assert dataset_sha256(project_root) == dataset_sha256(project_root)


def test_append_jsonl_checkpoints_rows(tmp_path):
    path = tmp_path / "rows.jsonl"
    append_jsonl(path, {"bundle_id": "a"})
    append_jsonl(path, {"bundle_id": "b"})
    assert read_jsonl(path) == [{"bundle_id": "a"}, {"bundle_id": "b"}]
