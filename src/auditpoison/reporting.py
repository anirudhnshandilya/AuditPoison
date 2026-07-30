from __future__ import annotations

import json
from pathlib import Path
from typing import Any


COLUMNS = [
    ("accuracy", "Accuracy", "Acc."),
    ("macro_f1", "Macro F1", "Macro F1"),
    ("false_assurance_rate", "False assurance", "FAR $\\downarrow$"),
    ("paired_attack_success_rate", "Attack success", "ASR $\\downarrow$"),
    ("compliant_rejection_rate", "Compliant rejection", "CRR $\\downarrow$"),
    ("benign_label_consistency", "Benign consistency", "Benign $\\uparrow$"),
    ("citation_f1", "Citation F1", "Citation F1"),
    ("attack_evidence_detection_recall", "Attack detection", "Attack det. $\\uparrow$"),
]


def _pct(value: Any) -> str:
    try:
        return f"{100 * float(value):.1f}"
    except (TypeError, ValueError):
        return "--"


def _latex_escape(value: str) -> str:
    return value.replace("_", "\\_").replace("%", "\\%").replace("&", "\\&")


def load_metric_files(paths: list[str | Path]) -> list[dict[str, Any]]:
    rows = []
    for path in paths:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
        obj["_path"] = str(path)
        rows.append(obj)
    return rows


def markdown_table(rows: list[dict[str, Any]]) -> str:
    headers = ["Model"] + [label for _, label, _ in COLUMNS]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] + ["---:"] * len(COLUMNS)) + "|"]
    for row in rows:
        values = [str(row.get("model", Path(row["_path"]).stem))] + [_pct(row.get(key)) for key, _, _ in COLUMNS]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def latex_table(rows: list[dict[str, Any]]) -> str:
    headers = ["Model"] + [label for _, _, label in COLUMNS]
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\small",
        "\\caption{AuditPoison pilot results. All metrics are percentages. Lower is better for FAR, ASR, and CRR; higher is better otherwise.}",
        "\\label{tab:auditpoison-main}",
        "\\begin{tabular}{l" + "r" * len(COLUMNS) + "}",
        "\\toprule",
        " & ".join(headers) + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        model = _latex_escape(str(row.get("model", Path(row["_path"]).stem)))
        values = [model] + [_pct(row.get(key)) for key, _, _ in COLUMNS]
        lines.append(" & ".join(values) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])
    return "\n".join(lines)
