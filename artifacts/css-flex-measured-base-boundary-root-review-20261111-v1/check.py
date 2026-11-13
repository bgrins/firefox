import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = ROOT / 'artifacts/css-flex-total-violation-caller-target-20261111-v1'
AUTHOR = ROOT / 'artifacts/css-flex-total-violation-caller-proof-20261111-v1'
ENGINE = ROOT / 'artifacts/css-flex-main-positioning-target-20261111-v2'
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64'
MODULES = ['FlexViolation/Model', 'FlexViolation/Target', 'FlexViolationCaller/Model',
           'FlexViolationCaller/Target', 'ProviderBoundary', 'BoundaryAudit']
EXPECTED = """'FlexViolationCaller.measured_base_counterexample' does not depend on any axioms
'FlexViolationCaller.representable_target_reporting' depends on axioms: [propext, Classical.choice, Quot.sound]
'FlexViolationCaller.outside32_aggregate_sign' does not depend on any axioms
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    assert sha(TARGET / 'FILES.json') == 'e954d8318eb1dcbdbe892db732b46c87fc0db07813203b77f2e430fa3ada229b'
    for name, expected in json.loads((TARGET / 'FILES.json').read_text()).items():
        assert sha(TARGET / name) == expected, name
    engine_files = json.loads((ENGINE / 'FILES.json').read_text())
    assert sha(ENGINE / 'process.py') == engine_files['process.py']
    tools = json.loads((TARGET / 'TOOLS.json').read_text())
    manifest = ROOT / tools['stdlib_manifest']
    assert sha(manifest) == tools['stdlib_manifest_sha256']
    for name, expected in json.loads(manifest.read_text()).items():
        assert sha(LEAN / name) == expected, name
    assert sha(LEAN / 'bin/lean') == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'


authenticate()
source = HERE / 'source'
source.mkdir(exist_ok=False)
origins = {}
for module in MODULES:
    owner = TARGET if module in MODULES[:4] else AUTHOR
    origin = owner / 'proof' / (module + '.lean')
    target = source / (module + '.lean')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(origin.read_bytes())
    origins[module] = {'path': str(origin.relative_to(ROOT)), 'sha256': sha(target)}
(HERE / 'ORIGINS.json').write_text(json.dumps(origins, indent=2) + '\n')
work = HERE / 'scratch'
shutil.copytree(source, work)
helper = runpy.run_path(str(ENGINE / 'process.py'))
runner = helper['Runner'](HERE)
result = {'status': 'INCOMPLETE', 'native_refinement': False, 'universal_caller_target': False}
try:
    env = {k: v for k, v in os.environ.items() if not k.startswith('LEAN_')}
    env.update(LEAN_PATH=str(work), LEAN_NUM_THREADS='1')
    for module in MODULES:
        record, log = runner.run([str(LEAN / 'bin/lean'), '-j1', '-M1024',
                                  '-DwarningAsError=true', '-o', module + '.olean', module + '.lean'],
                                 work, env, module.replace('/', '-'), timeout=180)
        assert record['exit'] == 0
        assert log == (EXPECTED if module == 'BoundaryAudit' else '')
    authenticate()
    for module, origin in origins.items():
        assert sha(source / (module + '.lean')) == origin['sha256']
    result.update(status='PASS', modules=6, exact_audits=3)
finally:
    safe = runner.safe_cleanup and all(helper['absent'](g) for g in runner.groups)
    (HERE / 'REMOVED-SCRATCH.json').write_text(json.dumps(
        {str(p.relative_to(work)): sha(p) for p in work.rglob('*') if p.is_file()}, indent=2) + '\n')
    if safe:
        shutil.rmtree(work)
    result.update(groups_absent=safe, scratch_removed=not work.exists())
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
assert result['groups_absent'] and result['scratch_removed']
print(json.dumps(result))
