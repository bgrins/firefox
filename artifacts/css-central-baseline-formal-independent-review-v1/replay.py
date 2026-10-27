import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEAD = '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
TOOL_SHA = 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
CASES = [('css-central-baseline-arithmetic-v1', 'CentralSynthesis.lean', 17),
         ('css-central-baseline-range-v1', 'Range.lean', 4),
         ('css-central-baseline-domain-v1', 'Domain.lean', 5)]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def authenticate(base, pins):
    for name, value in pins.items():
        p = base / name
        assert p.is_file() and not p.is_symlink() and digest(p) == value, name

assert digest(LEAN) == TOOL_SHA
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
env.pop('LEAN_PATH', None)
source_pins = {}
bindings = read(ROOT / 'artifacts/css-central-baseline-arithmetic-v1/BINDINGS.json')
authenticate(ROOT, bindings['references'])
retained = ROOT / bindings['head_source']['retained_path']
assert digest(retained) == bindings['head_source']['sha256']
for directory, _, _ in CASES[1:]:
    pins = read(ROOT / 'artifacts' / directory / 'SOURCE-PINS.json')
    assert pins['head'] == HEAD
    for name, value in pins['sources'].items():
        assert name not in source_pins or source_pins[name] == value
        source_pins[name] = value
for name, value in source_pins.items():
    raw = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', HEAD + ':' + name], cwd=ROOT, env=env)
    assert hashlib.sha256(raw).hexdigest() == value, name
rows = []
inputs = {'toolchain_sha256': TOOL_SHA, 'head': HEAD, 'source_pins': source_pins, 'capsules': {}}
for directory, filename, expected in CASES:
    p = ROOT / 'artifacts' / directory
    manifest = read(p / 'FILES.json')
    authenticate(p, manifest)
    source = (p / filename).read_bytes()
    text = source.decode()
    assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', text)
    assert text.count('#print axioms ') == expected
    assert re.findall(r'^import (.*)$', text, flags=re.M) == ['Std']
    output = HERE / filename
    output.write_bytes(source)
    log = HERE / (filename + '.log')
    command = [str(LEAN), str(output)]
    with log.open('w') as stream:
        process = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=60)
    content = log.read_text()
    assert process.returncode == 0, filename
    audit_lines = [line for line in content.splitlines() if 'depends on axioms:' in line or 'does not depend on any axioms' in line]
    assert len(audit_lines) == expected, content
    for line in audit_lines:
        if 'depends on axioms:' in line:
            ax = line.split('depends on axioms:', 1)[1].strip().strip('[]')
            assert set(ax.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}, line
    assert not any(t in content for t in ['sorryAx', 'error:', 'warning:'])
    inputs['capsules'][directory] = {'manifest_sha256': digest(p / 'FILES.json'), 'payloads': manifest}
    rows.append({'module': filename, 'command': command, 'exit': process.returncode,
                 'source_sha256': digest(output), 'log_sha256': digest(log), 'audited_declarations': expected})
    authenticate(p, manifest)
assert not list(HERE.glob('*.olean')) and not list(HERE.glob('*.ilean'))
(HERE / 'INPUTS.json').write_text(json.dumps(inputs, indent=2) + '\n')
result = {'status': 'PASS', 'rows': rows, 'audited_declarations': sum(row['audited_declarations'] for row in rows),
          'native_execution': False, 'compiler_products_created': False, 'sealed_inputs_unchanged': True}
(HERE / 'REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
