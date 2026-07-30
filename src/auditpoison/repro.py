from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_paths(paths: Iterable[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda p: p.as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative + b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def dataset_sha256(root: str | Path) -> str:
    root = Path(root)
    paths = list((root / "data" / "pilot").rglob("*.json"))
    paths.extend([root / "data" / "controls.json", root / "data" / "manifest.json", root / "schema" / "evidence_bundle.schema.json"])
    return sha256_paths(paths, root)


def git_commit(root: str | Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(root),
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else None


def build_run_manifest(
    root: str | Path,
    predictions_path: str | Path,
    adapter: str,
    model: str,
    provider: str,
    config: dict[str, Any],
    bundle_ids: list[str],
    prompt_file: str = "prompts/auditor_system_v0.2.txt",
) -> dict[str, Any]:
    root = Path(root)
    predictions_path = Path(predictions_path)
    prompt_path = root / prompt_file
    now = datetime.now(timezone.utc)
    return {
        "schema_version": "1.0.0",
        "run_id": now.strftime("%Y%m%dT%H%M%SZ") + "-" + hashlib.sha256((adapter + model + str(now.timestamp())).encode()).hexdigest()[:8],
        "created_at_utc": now.isoformat(),
        "adapter": adapter,
        "provider": provider,
        "model": model,
        "configuration": config,
        "bundle_count": len(bundle_ids),
        "bundle_ids": bundle_ids,
        "dataset_sha256": dataset_sha256(root),
        "prompt_file": prompt_path.relative_to(root).as_posix(),
        "prompt_sha256": sha256_file(prompt_path),
        "predictions_file": predictions_path.name,
        "predictions_sha256": sha256_file(predictions_path),
        "git_commit": git_commit(root),
        "environment": {
            "python": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "secrets_recorded": False,
    }


def write_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def verify_manifest(root: str | Path, manifest_path: str | Path) -> list[str]:
    root = Path(root)
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    if dataset_sha256(root) != manifest["dataset_sha256"]:
        failures.append("dataset hash mismatch")
    prompt_path = root / manifest["prompt_file"]
    if not prompt_path.exists() or sha256_file(prompt_path) != manifest["prompt_sha256"]:
        failures.append("prompt hash mismatch")
    predictions_path = manifest_path.parent / manifest["predictions_file"]
    if not predictions_path.exists() or sha256_file(predictions_path) != manifest["predictions_sha256"]:
        failures.append("predictions hash mismatch")
    return failures
