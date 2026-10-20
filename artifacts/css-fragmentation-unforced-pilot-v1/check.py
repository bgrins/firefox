import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess

ROOT = Path(__file__).resolve().parent
LEAN_SHA = 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
SOURCE_SHA = '57df3c079bf09547c05c1c0745b1ea1067344e88adaa844ec2e1ed1cde5faa82'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            assert key not in result, 'duplicate JSON key'
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def authenticate():
    manifest = load(ROOT / 'MANIFEST.json')
    freeze = load(ROOT / 'FREEZE.json')
    assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
    expected_files = set(manifest['files']) | {'MANIFEST.json', 'FREEZE.json'}
    expected_dirs = set()
    for relative in expected_files:
        name = PurePosixPath(relative)
        assert not name.is_absolute() and str(name) == relative and '\\' not in relative
        assert all(part not in {'.', '..', ''} for part in name.parts)
        expected_dirs.update(str(parent) for parent in name.parents if str(parent) != '.')
    actual_files, actual_dirs = set(), set()
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            actual_files.add(relative)
        elif stat.S_ISDIR(mode):
            actual_dirs.add(relative)
        else:
            raise AssertionError('nonregular input: ' + relative)
    assert actual_files == expected_files, 'file roster'
    assert actual_dirs == expected_dirs, 'directory roster'
    for relative, expected in manifest['files'].items():
        assert sha(ROOT / relative) == expected, relative
    return manifest


def definitions(text):
    return re.sub(r'^theorem\s+.*?(?=^(?:def |theorem |inductive |structure |end ))', '', text, flags=re.M | re.S)


def check(lean, output):
    manifest = authenticate()
    assert not output.is_relative_to(ROOT), 'output must be outside capsule'
    assert sha(lean) == LEAN_SHA, 'Lean executable identity'
    raw = (ROOT / 'source/fragmentation.html').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    bindings = load(ROOT / 'BINDINGS.json')
    for binding in bindings:
        part = raw[binding['start']:binding['end']]
        assert part == (ROOT / binding['path']).read_bytes()
        assert hashlib.sha256(part).hexdigest() == binding['sha256']
    assert raw[99200:104879] == (ROOT / 'source/unforced-breaks.html').read_bytes()
    inventory = load(ROOT / 'AUDITS.json')
    names = []
    for module, expected in inventory.items():
        text = (ROOT / 'lean' / (module + '.lean')).read_text()
        assert re.findall(r'^theorem\s+(\w+)', text, re.M) == expected
        assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b', text)
        names.extend('Fragmentation.' + n for n in expected)
    assert len(names) == len(set(names))
    audit = (ROOT / 'lean/Audit.lean').read_text()
    assert re.findall(r'#print axioms (\S+)', audit) == names
    assert not output.exists()
    output.mkdir(parents=True)
    env = {k:v for k,v in os.environ.items() if not k.startswith('LEAN_')}
    logs = []

    def run(folder, arguments, label, reject=False):
        env['LEAN_PATH'] = str(folder)
        result = subprocess.run([str(lean), *arguments], cwd=folder, env=env,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log = output / (label + '.log')
        log.write_text(result.stdout)
        logs.append({'label':label,'exit_code':result.returncode,'sha256':sha(log)})
        if reject:
            assert result.returncode != 0
            assert 'Tactic `decide` proved that the proposition' in result.stdout and 'is false' in result.stdout, label
            assert 'unknownIdentifier' not in result.stdout and 'unexpected token' not in result.stdout, label
        else:
            assert result.returncode == 0, label + ': ' + result.stdout
        return result.stdout

    baseline = output / 'baseline'
    baseline.mkdir()
    for module in inventory:
        shutil.copyfile(ROOT / 'lean' / (module + '.lean'), baseline / (module + '.lean'))
        run(baseline, ['-o',module + '.olean',module + '.lean'], module)
    shutil.copyfile(ROOT / 'lean/Audit.lean', baseline / 'Audit.lean')
    audit_log = run(baseline, ['Audit.lean'], 'audit')
    observed = re.findall(r"'([^']+)' (?:depends on axioms:|does not depend on any axioms)", audit_log)
    assert observed == names
    for group in re.findall(r'depends on axioms: \[([^]]*)\]', audit_log):
        assert set(x.strip() for x in group.split(',') if x.strip()) <= {'propext','Classical.choice','Quot.sound'}
    mutants = load(ROOT / 'MUTATIONS.json')
    for mutation in mutants:
        name = mutation['name']
        gate = (ROOT / mutation['gate']).read_text()
        (baseline / 'Gate.lean').write_text(gate)
        run(baseline, ['Gate.lean'], name + '-baseline-gate')
        folder = output / name
        folder.mkdir()
        for module in inventory:
            text = definitions((ROOT / 'lean' / (module + '.lean')).read_text())
            assert not re.search(r'^theorem\s', text, re.M)
            if module == mutation['module']:
                assert text.count(mutation['old']) == 1, name
                text = text.replace(mutation['old'], mutation['new'])
            (folder / (module + '.lean')).write_text(text)
            run(folder, ['-o',module + '.olean',module + '.lean'], name + '-' + module)
        (folder / 'Gate.lean').write_text(gate)
        run(folder, ['Gate.lean'], name + '-semantic-rejection', reject=True)
    assert authenticate() == manifest, 'inputs changed during replay'
    result = {'status':'PASS','inputs':len(manifest['files']),'modules':len(inventory),
              'exact_audits':names,'source_bindings':len(bindings),'mutants':len(mutants),
              'commands':logs,'lean_sha256':sha(lean),'spec_sha256':SOURCE_SHA,
              'scope':'Conditional abstract rule/grid component; CSS sufficiency, region and layout admission open.'}
    (output / 'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'commands','exact_audits'}}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check(args.lean.resolve(), args.output.resolve())
