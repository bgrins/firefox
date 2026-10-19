import itertools
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'development-build/full'
reference = runpy.run_path(str(ROOT / 'transform-reference.py'))['reference']
cases = []
for size in range(5):
    for units in itertools.product([65, 32, 9, 10, 13, 173], repeat=size):
        for mode, incoming, width in itertools.product(range(4), range(4), [8, 16]):
            cases.append((list(units), mode, incoming, width, 'en', reference(units, mode, incoming)))
for language in ['en', 'ja', 'JA-jp', 'zh', 'zho', '-', 'jaX']:
    for a, b, skip in [(0x4e00, 0x4e01, True), (0xac00, 0xac01, False), (0x20a9, 0x4e00, False), (0x200b, 65, True), (65, 0xff01, language in ['ja', 'JA-jp', 'zh'])]:
        cases.append(([a, 10, b], 2, 0, 16, language, ([a, b] if skip else [a, 32, b], [True, not skip, True], 0, 0)))
lines = [' '.join(map(str, [i, width, mode, incoming, language, len(units), *units])) for i, (units, mode, incoming, width, language, _) in enumerate(cases)]
(OUT / 'transform-inputs.txt').write_text('\n'.join(lines) + '\n')
run = subprocess.run([OUT / 'transform'], input='\n'.join(lines)+'\n', text=True, capture_output=True, timeout=60)
(OUT / 'transform-native.log').write_text(run.stdout)
(OUT / 'transform-stderr.log').write_text(run.stderr)
assert run.returncode == 0, run.stderr
results = run.stdout.splitlines()
assert len(results) == len(cases)
failures = []
for case, line in zip(cases, results):
    tokens = line.split()
    positions = {key: tokens.index(key) for key in ['OUT', 'SKIP', 'CONTEXT', 'FLAGS', 'COUNT', 'KEPT']}
    out = list(map(int, tokens[positions['OUT']+1:positions['SKIP']]))
    skip = ''.join(tokens[positions['SKIP']+1:positions['CONTEXT']])
    context = int(tokens[positions['CONTEXT']+1])
    flags = int(tokens[positions['FLAGS']+1])
    units, mode, incoming, width, language, expected = case
    actual = (out, [c == '0' for c in skip], context, flags)
    assert int(tokens[positions['COUNT']+1]) == len(units)
    assert int(tokens[positions['KEPT']+1]) == len(out)
    if actual != expected:
        failures.append({'case':case,'actual':actual})
(OUT / 'transform-results.json').write_text(json.dumps({'cases':len(cases),'failures':len(failures),'examples':failures[:20]}, indent=2)+'\n')
print(len(cases), 'cases', len(failures), 'failures')
assert not failures
