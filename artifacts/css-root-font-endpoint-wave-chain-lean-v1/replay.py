import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(LEAN) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
assert len(sys.argv) == 2 and Path(sys.argv[1]).name == sys.argv[1]
out = HERE / sys.argv[1]
out.mkdir()
names = re.findall(r'^theorem (\w+)', (HERE / 'Waves.lean').read_text(), re.M)
assert not re.search(r'\b(sorry|axiom|native_decide)\b', (HERE / 'Waves.lean').read_text())
controls = {
    'LocalReadyMeansGlobalCoherence': 'EndpointApplication.ready (waves 3 1 double 2 zeroNodes 2) → (waves 3 1 double 2 zeroNodes 2).installed.value = expected 1 double 2',
    'FixedTwoPasses': '(waves 4 1 double 2 zeroNodes 3).installed.value = expected 1 double 3',
    'ReadsSameWaveParent': '(waves 2 1 double 1 zeroNodes 1).installed.value = 4',
    'ChangedRootOneWaveEnough': '(waves 3 2 double 1 (waves 3 1 double 3 zeroNodes) 2).installed.value = 16',
    'NoApplicationNeeded': '(waves 1 1 double 0 zeroNodes 0).installed.value = 2',
    'OutsideFiniteChainChanges': '(wave 1 1 double zeroNodes 1).installed.value = 2',
}


records = []
with tempfile.TemporaryDirectory(prefix='endpoint-wave-lean-', dir='/private/tmp') as tmp:
    scratch = Path(tmp)
    env = dict(os.environ, LEAN_PATH=tmp, LEAN_NUM_THREADS='2')
    pins = json.loads((HERE / 'IMPORTS.json').read_bytes())
    for name, pin in pins.items():
        assert sha(ROOT / pin['path']) == pin['sha256']
        shutil.copyfile(ROOT / pin['path'], scratch / (name + '.lean'))
    shutil.copyfile(HERE / 'Waves.lean', scratch / 'Waves.lean')
    (scratch / 'Audit.lean').write_text('import Waves\n' + ''.join('#print axioms EndpointWaves.' + n + '\n' for n in names))
    for name, claim in controls.items():
        (scratch / (name + '.lean')).write_text('import Waves\nopen EndpointWaves\nexample : ' + claim + ' := by decide +kernel\n')
    for file in scratch.iterdir():
        shutil.copyfile(file, out / file.name)
    for name, success in [(n, True) for n in [*pins, 'Waves', 'Audit']] + [(n, False) for n in controls]:
        result = subprocess.run([str(LEAN), '-o', name + '.olean', name + '.lean'], cwd=scratch, env=env, capture_output=True, timeout=60)
        log = result.stdout + result.stderr
        (out / (name + '.log')).write_bytes(log)
        records.append({'module': name, 'exit': result.returncode, 'expected_success': success, 'log_sha256': sha(out / (name + '.log'))})
        (out / 'COMMANDS.json').write_text(json.dumps(records, indent=2) + '\n')
        assert (result.returncode == 0) == success, log.decode()
        if not success:
            assert b'is false' in log and b'decide' in log, log
        else:
            assert b'warning:' not in log and b'sorryAx' not in log, log
    audit = (out / 'Audit.log').read_text()
    assert audit.count('depends on axioms:') + audit.count('does not depend on any axioms') == len(names)
    axioms = {x.strip() for group in re.findall(r'axioms: \[(.*?)\]', audit) for x in group.split(',') if x.strip()}
    assert axioms <= {'propext', 'Quot.sound', 'Classical.choice'}
assert not scratch.exists()
result = {'success': True, 'audits': names, 'false_controls': list(controls), 'records': records,
          'tested_source': sha(HERE / 'Waves.lean'), 'tested_replay': sha(HERE / 'replay.py'),
          'imports_sha256': sha(HERE / 'IMPORTS.json'), 'compiler_sha256': sha(LEAN),
          'scratch_path': str(scratch), 'scratch_removed': True, 'native_refinement': False,
          'native_queue_mapping': False, 'browser_or_native_build': False}
(out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
