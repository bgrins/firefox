import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LEAN_HOME = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def absent(pgid):
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    return False


def authenticate():
    for name, expected in json.loads((HERE / 'ORIGINS.json').read_text()).items():
        assert sha(ROOT / name) == expected, name
    for name, expected in json.loads((HERE / 'TARGET-INPUTS.json').read_text()).items():
        assert sha(HERE / name) == expected, name
    for name, origin in json.loads((HERE / 'TRANSPORT.json').read_text()).items():
        assert sha(HERE / name) == origin['sha256'] == sha(ROOT / origin['path']), name
    if (HERE / 'SOURCE-ONLY.json').exists():
        for name, expected in json.loads((HERE / 'SOURCE-ONLY.json').read_text()).items():
            assert sha(HERE / name) == expected, name



def audit(text, names):
    found = []
    for line in text.splitlines():
        m = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[(.*)\]|does not depend on any axioms)", line)
        assert m, line
        found.append(m[1])
        assert set(filter(None, (m[2] or '').split(', '))) <= {'propext', 'Classical.choice', 'Quot.sound'}, line
    assert found == names and len(set(found)) == len(names)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--modules', nargs='+')
    args = parser.parse_args()
    lean = LEAN_HOME / 'bin/lean'
    assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
    tool = json.loads((HERE / 'TOOLS.json').read_text())
    manifest = ROOT / tool['stdlib_manifest']
    assert sha(manifest) == tool['stdlib_manifest_sha256']
    for name, value in json.loads(manifest.read_text()).items():
        assert sha(LEAN_HOME / name) == value
    authenticate()
    sources = {str(p.relative_to(HERE / 'proof')): sha(p) for p in (HERE / 'proof').rglob('*.lean')}
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(HERE / 'proof', out / 'source')
    work = out / 'scratch'
    shutil.copytree(out / 'source', work)
    (out / 'SOURCES.json').write_text(json.dumps(sources, indent=2) + '\n')
    env = {k: v for k, v in os.environ.items() if not k.startswith('LEAN_')}
    env.update(LEAN_PATH=str(work), LEAN_NUM_THREADS='1')
    records = []
    safe = True
    status = 'FAIL'
    try:
        modules = args.modules or json.loads((HERE / 'ORDER.json').read_text())
        refusals = {} if args.modules else json.loads((HERE / 'REFUSALS.json').read_text())
        for name, refusal in refusals.items():
            (work / ('refusal-' + name + '.lean')).write_text(
                'import FlexMBP.Controls\nexample : ' + refusal['proposition'] +
                ' := by rw [' + refusal['rewrite'] + ']; decide\n')
        for module in modules + ['refusal-' + n for n in refusals]:
            log_path = out / (module.replace('/', '-') + '.log')
            argv = [str(lean), '-j1', '-M4096', '-DwarningAsError=true', '-o', module + '.olean', module + '.lean']
            record = {'module': module, 'argv': argv}
            started = time.monotonic()
            previous_safe = safe
            safe = False
            with log_path.open('xb') as log:
                proc = subprocess.Popen(argv, cwd=work, env=env, stdout=log,
                                        stderr=subprocess.STDOUT, start_new_session=True)
                record['pgid'] = proc.pid
                try:
                    record['exit'] = proc.wait(timeout=180)
                finally:
                    if not absent(proc.pid):
                        os.killpg(proc.pid, signal.SIGTERM)
                        try:
                            proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            os.killpg(proc.pid, signal.SIGKILL)
                            proc.wait(timeout=5)
                    record['group_absent'] = absent(proc.pid)
                    safe = previous_safe and record['group_absent']
                    record['seconds'] = time.monotonic() - started
                    record['log_sha256'] = sha(log_path)
                    records.append(record)
                    (out / 'COMMANDS.json').write_text(json.dumps(records, indent=2) + '\n')
            assert safe
            if module.startswith('refusal-'):
                text = log_path.read_text()
                assert record['exit'] == 1 and text.count('error:') == 1, record
                assert 'proved that the proposition' in text and 'is false' in text, text
            else:
                assert record['exit'] == 0, record
        if not args.modules:
            audit((out / 'ProofAudit.log').read_text(), json.loads((HERE / 'AUDIT-NAMES.json').read_text()))
        assert sources == {str(p.relative_to(HERE / 'proof')): sha(p) for p in (HERE / 'proof').rglob('*.lean')}
        authenticate()
        assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
        assert sha(manifest) == tool['stdlib_manifest_sha256']
        for name, value in json.loads(manifest.read_text()).items():
            assert sha(LEAN_HOME / name) == value
        status = 'PASS'
    finally:
        if safe:
            shutil.rmtree(work)
        (out / 'RESULT.json').write_text(json.dumps({'status': status, 'commands': len(records),
            'scope': 'development' if args.modules else 'full',
            'audit_roots': 0 if args.modules else len(json.loads((HERE / 'AUDIT-NAMES.json').read_text())),
            'expected_refusals': 0 if args.modules else len(json.loads((HERE / 'REFUSALS.json').read_text())),
            'scratch_removed': not work.exists(), 'groups_absent': safe}, indent=2) + '\n')


if __name__ == '__main__':
    main()
