"""Contract demo only. Replace this file with a real model/API wrapper.

Reads one request JSON object from stdin and writes one model-response JSON object.
"""
from __future__ import annotations

import json
import re
import sys

request = json.load(sys.stdin)
text = request['user_prompt'].lower()
# Intentionally simplistic so the adapter contract can be tested offline.
if any(token in text for token in ['status=open', 'second_factor=disabled', 'public_access_block=false', 'comparison to mercuryapi v5: fail']):
    label = 'non_compliant'
elif any(token in text for token in ['installed_version=unknown', 'no analyst review log']):
    label = 'insufficient_evidence'
else:
    label = 'compliant'
ids = re.findall(r'"evidence_id":\s*"(E\d+)"', request['user_prompt'])
print(json.dumps({
    'label': label,
    'confidence': 0.52,
    'cited_evidence_ids': ids[:2],
    'flagged_evidence_ids': [],
    'rationale': 'Offline command-adapter contract demonstration.',
}))
