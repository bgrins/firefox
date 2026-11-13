import collections
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
out = HERE / 'baseline'
commands = json.loads((out / 'COMMANDS.json').read_text())
assert len(commands) == 1
command = commands[0]
assert command['exit'] == 1 and command['label'] == 'baseline'
assert 'timeout' not in command
try:
    os.killpg(command['pgid'], 0)
except ProcessLookupError:
    pass
else:
    raise RuntimeError('Owned WPT group is still present')
inputs = json.loads((HERE / 'INPUTS.json').read_text())
for name, pins in inputs.items():
    expected = pins.get('original', pins['candidate'])
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
before = json.loads((out / 'before-BINARIES.json').read_text())
assert before == json.loads((out / 'after-BINARIES.json').read_text())
for name, pin in before.items():
    assert Path(name).stat().st_size == pin['bytes']
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == pin['sha256']
results = json.loads((out / 'wptreport.json').read_text())['results']
assert len(results) == 1 and results[0]['status'] == 'OK'
assert results[0]['test'] == '/css/cssom/resolved-margins-overconstrained-block.html'
subtests = results[0]['subtests']
assert len({t['name'] for t in subtests}) == 96
assert collections.Counter(t['status'] for t in subtests) == {'PASS': 30, 'FAIL': 66}
result = dict(status='checked after independent lifecycle recovery', pass_count=30,
              fail=66, files=1, subtests=96, groups_absent_now=True,
              source_and_binaries_unchanged=True, original_failure_preserved=True)
assert not (out / 'RESULT.json').exists()
(out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
