import argparse
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--replay', action='store_true')
p.add_argument('--lean', type=Path)
p.add_argument('--output', type=Path)
a = p.parse_args()
def load(f): return json.loads(f.read_text())
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
freeze = load(P / 'FREEZE.json')
assert sha(P / 'INPUTS.json') == freeze['inputs_sha256']
inputs = load(P / 'INPUTS.json')
assert len(inputs) == freeze['entries']
for name, expected in inputs.items(): assert sha(P / name) == expected, name
for name, pin in [('capsule','e36a649e14d3c4f1e066cc65cdc40873d9326656ab5a7909a13b5a3f0650e82c'), ('capsule-v2','c014113cbe91c76e52cf27a07f4407432a660cf73a83e436871f4a242491a137')]:
    q = P / name
    assert sha(q / 'MANIFEST.json') == pin
    for rel, expected in load(q / 'MANIFEST.json').items(): assert sha(q / rel) == expected
    r = subprocess.run(['python3', str(P / 'audit_tables.py'), str(q)], capture_output=True, text=True, check=True)
    assert json.loads(r.stdout) == load(P / ('TABLE-AUDIT-v2.json' if name.endswith('v2') else 'TABLE-AUDIT.json'))
delta = load(P / 'V2-DELTA.json')
assert delta['unchanged_source'] and delta['unchanged_lean']
assert (P / 'capsule/generated/CurrentInvocations.lean').read_bytes() == (P / 'capsule-v2/generated/CurrentInvocations.lean').read_bytes()
for prefix in ['fresh', 'relocated', 'fresh-v2', 'relocated-v2']:
    result = load(P / prefix / 'RESULT.json')
    assert result['current_source_invocations'] == 22 and result['source_byte_decisions'] == 5632
    commands = load(P / prefix / 'commands.json')
    overwrite = next(x for x in commands if x['cmd'][-1] == 'overwrite-existing.lean')
    endpoint = next(x for x in commands if x['cmd'][-1] == 'exclusive-endpoint.lean')
    for c in [overwrite, endpoint]:
        log = c['stdout'] + c['stderr']
        assert c['exit'] != 0 and 'unsolved goals' in log and 'is false' in log
        assert 'unexpected token' not in log
    if prefix.endswith('v2'):
        assert result['second_named_binding_rejected'] and result['UTF8_source_offsets_checked']
for file in ['TAMPER.json','TAMPER-v2.json']:
    result = load(P / file)
    assert result['exit'] != 0 and result['output_created'] is False
assert load(P / 'reader-probes/two-bindings/RESULT.json')['exit'] == 0
assert load(P / 'reader-probes/guard/RESULT.json')['exit'] != 0
if a.replay:
    assert a.lean and a.output
    subprocess.run(['python3', str(P / 'capsule-v2/check.py'), '--lean', str(a.lean.resolve()), '--output', str(a.output.resolve())], check=True)
print(json.dumps({'status':'PASS','authenticated_inputs':len(inputs),'v2_verdict':'ACCEPT_SCOPED_CONDITIONAL_DISPATCH_COMPONENT','current_invocations':22,'byte_decisions':5632,'whole_tokenizer':'OPEN','native_compiler_refinement':'EXTERNAL'},indent=2))
