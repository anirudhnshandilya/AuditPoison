from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open('r', encoding='utf-8') as handle:
        return json.load(handle)


def load_bundles(root: str | Path) -> list[dict[str, Any]]:
    root = Path(root)
    paths = sorted((root / 'data' / 'pilot').rglob('*.json'))
    return [load_json(path) for path in paths]


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open('r', encoding='utf-8') as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSONL at line {line_number}: {exc}') from exc
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', encoding='utf-8', newline='\n') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')


def append_jsonl(path: str | Path, row: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('a', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + '\n')
