import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
assert sys.flags.isolated and not sys.flags.optimize
OUT = HERE / sys.argv[1]
assert OUT.parent == HERE and not OUT.exists()
TOOL = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


assert sha(TOOL / 'bin/lean') == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
pins = json.loads((ROOT / 'artifacts/css-historical-extracted-counterexample-20261111-v1/DEPENDENCY-PINS.json').read_text())
prefix = str(TOOL.relative_to(ROOT)) + '/'
pins = {name: digest for name, digest in pins.items() if name.startswith(prefix)}
assert len(pins) == 7482
for name, digest in pins.items():
    assert sha(ROOT / name) == digest, name
OUT.mkdir()
work = OUT / 'work'
shutil.copytree(HERE / 'proof', work)
sources = {str(p.relative_to(work)): sha(p) for p in work.rglob('*.lean')}
save(OUT / 'SOURCES.json', sources)
save(OUT / 'DEPENDENCIES.json', pins)
names = ['PrefixTarget', 'DifferenceTarget', 'FoldTarget', 'SelectionTarget',
         'ProgressTarget', 'CompatibilityTarget', 'WitnessTarget', 'UniversalTarget']
(work / 'Audit.lean').write_text('import FlexViolation.Target\n' + ''.join(
    '#print axioms FlexViolation.' + name + '\n' for name in names))
env = dict(os.environ)
for key in ['LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_CC', 'LEAN_CXX']:
    env.pop(key, None)
env['LEAN_PATH'] = str(work)
records = []
for module in ['FlexViolation/Model', 'FlexViolation/Target', 'Audit']:
    argv = [str(TOOL / 'bin/lean'), '-j1', '-M1024', '-DwarningAsError=true',
            '-o', module + '.olean', module + '.lean']
    label = module.replace('/', '-')
    with (OUT / (label + '.stdout')).open('xb') as stdout, (OUT / (label + '.stderr')).open('xb') as stderr:
        proc = subprocess.Popen(argv, cwd=work, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        timed_out = False
        try:
            code = proc.wait(timeout=60)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGKILL)
            code = proc.wait(timeout=10)
    try:
        os.killpg(proc.pid, 0)
        absent = False
    except ProcessLookupError:
        absent = True
    records.append(dict(argv=argv, cwd=str(work), exit=code, timeout=timed_out,
                        pgid=proc.pid, group_absent=absent,
                        stdout_sha256=sha(OUT / (label + '.stdout')),
                        stderr_sha256=sha(OUT / (label + '.stderr'))))
    save(OUT / 'COMMANDS.json', records)
    assert code == 0 and not timed_out and absent, label
    assert (OUT / (label + '.stderr')).read_bytes() == b'', label
expected = ''.join("'FlexViolation." + name + "' does not depend on any axioms\n" for name in names)
assert (OUT / 'Audit.stdout').read_text() == expected
for name, digest in sources.items():
    assert sha(HERE / 'proof' / name) == digest == sha(work / name), name
for name, digest in pins.items():
    assert sha(ROOT / name) == digest, name
save(OUT / 'SCRATCH.json', {str(p.relative_to(work)): dict(sha256=sha(p), bytes=p.stat().st_size)
                           for p in work.rglob('*') if p.is_file()})
shutil.rmtree(work)
save(OUT / 'RESULT.json', dict(status='PASS definitions only', modules=3,
                              audited_definitions=names, correctness_proofs=0,
                              dependencies=len(pins), scratch_removed=not work.exists()))
print('PASS definitions only; zero correctness proofs')
