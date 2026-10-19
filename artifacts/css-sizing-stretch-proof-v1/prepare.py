import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
REQUESTS = [
    ('layout/generic/nsContainerFrame.cpp', 'nsContainerFrame::ComputeSizeWithIntrinsicDimensions(', 'native-candidate.cpp'),
    ('layout/generic/nsHTMLCanvasFrame.cpp', 'nsHTMLCanvasFrame::ComputeSize(', 'canvas-caller.cpp'),
    ('layout/generic/nsGridContainerFrame.cpp', 'nsGridContainerFrame::ReflowInFlowChild(', 'grid-caller.cpp'),
    ('layout/generic/ReflowInput.cpp', 'ReflowInput::InitConstraints(', 'reflow-caller.cpp'),
]


def extract(text, marker):
    if text.count(marker) != 1:
        raise RuntimeError('Ambiguous source marker')
    start = text.index(marker)
    return text[start:text.index('\n}', start) + 2] + '\n'


def main():
    records = []
    for path, marker, snapshot in REQUESTS:
        raw = (ROOT / path).read_bytes()
        text = extract(raw.decode(), marker)
        (BASE / snapshot).write_text(text)
        records.append({'source': path, 'source_sha256': hashlib.sha256(raw).hexdigest(),
                        'marker': marker, 'snapshot': snapshot,
                        'sha256': hashlib.sha256(text.encode()).hexdigest()})
    before = json.loads((BASE / 'BEFORE-v1.json').read_text())
    records.append({'source': before['path'], 'source_sha256': before['sha256'],
                    'marker': REQUESTS[0][1], 'snapshot': 'native-before.cpp',
                    'sha256': before['fragment_sha256']})
    (BASE / 'SOURCE-v1.json').write_text(json.dumps(records, indent=2) + '\n')

if __name__ == '__main__':
    main()
