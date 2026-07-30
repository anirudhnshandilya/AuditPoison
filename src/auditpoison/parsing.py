from __future__ import annotations

import json
import re
from typing import Any

VALID_LABELS = {'compliant', 'non_compliant', 'insufficient_evidence'}


def _extract_json_text(text: str) -> str:
    text = text.strip()
    fence = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, flags=re.I | re.S)
    if fence:
        return fence.group(1)
    if text.startswith('{') and text.endswith('}'):
        return text
    start = text.find('{')
    if start < 0:
        raise ValueError('Model response contains no JSON object.')
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise ValueError('Model response contains an unterminated JSON object.')


def parse_model_response(bundle: dict[str, Any], response: str | dict[str, Any]) -> dict[str, Any]:
    obj = response if isinstance(response, dict) else json.loads(_extract_json_text(response))
    if not isinstance(obj, dict):
        raise ValueError('Model response must be a JSON object.')
    label = obj.get('label')
    if label not in VALID_LABELS:
        raise ValueError(f'Invalid label: {label!r}')
    try:
        confidence = float(obj.get('confidence'))
    except (TypeError, ValueError) as exc:
        raise ValueError('confidence must be numeric.') from exc
    if not 0.0 <= confidence <= 1.0:
        raise ValueError('confidence must be between 0 and 1.')

    evidence_ids = {e['evidence_id'] for e in bundle['evidence']}
    cited = list(obj.get('cited_evidence_ids', []))
    flagged = list(obj.get('flagged_evidence_ids', obj.get('contradictions_detected', [])))
    if not all(isinstance(x, str) for x in cited + flagged):
        raise ValueError('Evidence identifier fields must contain strings only.')
    unknown = sorted((set(cited) | set(flagged)) - evidence_ids)
    if unknown:
        raise ValueError(f'Response references unknown evidence identifiers: {unknown}')

    return {
        'bundle_id': bundle['bundle_id'],
        'label': label,
        'confidence': confidence,
        'cited_evidence_ids': cited,
        'flagged_evidence_ids': flagged,
        'rationale': str(obj.get('rationale', '')).strip(),
    }
