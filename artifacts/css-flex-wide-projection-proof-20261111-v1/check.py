import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = ROOT / 'artifacts/css-flex-main-positioning-target-20261111-v2'
TARGET = ROOT / 'artifacts/css-flex-total-violation-caller-target-20261111-v1'
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64'
NAMES = ['clamp_commutes', 'corrected_violation', 'minimum_flag', 'maximum_flag',
         'exclusive_flags', 'correction_bound', 'aggregate_identity',
         'correction_budget', 'adjustment_budget', 'combined_prefix_fits64',
         'saturation_changes_sign', 'step_budget', 'distribution_budget',
         'native_sized_budget', 'distribution_prefix_fits64', 'rounding_overshoot_is_admitted']
EXPECTED = ''.join(
    "'FlexWideProjection." + name + "' " +
    ('does not depend on any axioms' if name in ['saturation_changes_sign', 'rounding_overshoot_is_admitted'] else
     'depends on axioms: [propext, Classical.choice, Quot.sound]' if name in
     ['minimum_flag', 'maximum_flag', 'exclusive_flags', 'combined_prefix_fits64',
      'distribution_budget', 'native_sized_budget', 'distribution_prefix_fits64'] else
     'depends on axioms: [propext, Quot.sound]') + '\n'
    for name in NAMES)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    assert sha(TARGET / 'FILES.json') == 'e954d8318eb1dcbdbe892db732b46c87fc0db07813203b77f2e430fa3ada229b'
    pins = json.loads((TARGET / 'FILES.json').read_text())
    assert sha(TARGET / 'TOOLS.json') == pins['TOOLS.json']
    tools = json.loads((TARGET / 'TOOLS.json').read_text())
    manifest = ROOT / tools['stdlib_manifest']
    assert sha(manifest) == tools['stdlib_manifest_sha256']
    for name, expected in json.loads(manifest.read_text()).items():
        assert sha(LEAN / name) == expected, name
    assert sha(LEAN / 'bin/lean') == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
    assert sha(ENGINE / 'FILES.json') == 'eb2bbc722e548fb13d6f9bd306998990344628fced432eb0dcde431e8a24e7f2'
    assert sha(ENGINE / 'process.py') == json.loads((ENGINE / 'FILES.json').read_text())['process.py']


authenticate()
out = HERE / sys.argv[1]
out.mkdir(exist_ok=False)
source = out / 'source'
source.mkdir()
for name in ['Projection.lean', 'Distribution.lean', 'Audit.lean']:
    shutil.copyfile(HERE / name, source / name)
pins = {p.name: sha(p) for p in source.iterdir()}
(out / 'SOURCE.json').write_text(json.dumps(pins, indent=2) + '\n')
work = out / 'scratch'
shutil.copytree(source, work)
helper = runpy.run_path(str(ENGINE / 'process.py'))
runner = helper['Runner'](out)
result = {'status': 'INCOMPLETE', 'native_refinement': False, 'native_budget_proved': False}
try:
    env = {k: v for k, v in os.environ.items() if not k.startswith('LEAN_')}
    env.update(LEAN_PATH=str(work), LEAN_NUM_THREADS='1')
    for module in ['Projection', 'Distribution', 'Audit']:
        record, log = runner.run([str(LEAN / 'bin/lean'), '-j1', '-M1024',
                                  '-DwarningAsError=true', '-o', module + '.olean', module + '.lean'],
                                 work, env, module, timeout=180)
        if record['exit'] != 0 or log != (EXPECTED if module == 'Audit' else ''):
            print(log)
            raise RuntimeError('Compile or exact audit mismatch')
    authenticate()
    assert all(sha(source / name) == expected for name, expected in pins.items())
    result.update(status='PASS', modules=3, exact_audits=len(NAMES))
finally:
    safe = runner.safe_cleanup and all(helper['absent'](g) for g in runner.groups)
    (out / 'REMOVED-SCRATCH.json').write_text(json.dumps(
        {str(p.relative_to(work)): sha(p) for p in work.rglob('*') if p.is_file()}, indent=2) + '\n')
    if safe:
        shutil.rmtree(work)
    result.update(groups_absent=safe, scratch_removed=not work.exists())
    (out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
assert result['groups_absent'] and result['scratch_removed']
print(json.dumps(result))
