import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PRODUCER = HERE.parent / 'css-sticky-negative-inset-overflow-proof-v2'
MANIFEST = '5681c063bbd21555a538e439ed5400ac77a2a0bdcc1ae73bff9e44b5617b230a'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.exists()
    capsule = PRODUCER / 'capsule'
    assert SHA(capsule / 'FILES.json') == MANIFEST
    for entry in json.loads((capsule / 'FILES.json').read_text())['files']:
        assert SHA(capsule / entry['path']) == entry['sha256']
    tool = json.loads((capsule / 'TOOLCHAIN.json').read_text())
    lean = Path(tool['lean'])
    assert SHA(lean) == tool['lean_sha256']
    modules = []
    def visit(name):
        if name in modules:
            return
        source = (capsule / 'lean' / (name + '.lean')).read_text()
        for dep in re.findall(r'^import (\w+)$', source, re.M):
            if dep != 'Std':
                visit(dep)
        modules.append(name)
    visit('WideWitnesses')
    out.mkdir(parents=True)
    inventory = [{'path':str(capsule / 'lean' / (name + '.lean')),
                  'sha256':SHA(capsule / 'lean' / (name + '.lean'))} for name in modules]
    inventory.append({'path':str(HERE / 'Challenges.lean'),'sha256':SHA(HERE / 'Challenges.lean')})
    (out / 'INPUTS.json').write_text(json.dumps(inventory, indent=2) + '\n')
    records = []
    with tempfile.TemporaryDirectory(prefix='sticky-negative-review-') as temporary:
        work = Path(temporary)
        env = {k:v for k,v in os.environ.items() if not k.startswith('LEAN_')}
        env['LEAN_PATH'] = str(work)
        for name in modules + ['Challenges']:
            source = HERE / 'Challenges.lean' if name == 'Challenges' else capsule / 'lean' / (name + '.lean')
            (work / (name + '.lean')).write_bytes(source.read_bytes())
            argv = [str(lean), '-o', str(work / (name + '.olean')), str(work / (name + '.lean'))]
            result = subprocess.run(argv, cwd=work, env=env, text=True, capture_output=True)
            (out / (name + '.log')).write_text(result.stdout + result.stderr)
            records.append({'module':name,'exit':result.returncode,'command':argv})
            (out / 'COMMANDS.json').write_text(json.dumps(records, indent=2) + '\n')
            assert result.returncode == 0, name
        names = ['IndependentNegative.' + n for n in re.findall(r'^theorem (\w+)', (HERE / 'Challenges.lean').read_text(), re.M)]
        (work / 'Audit.lean').write_text('import Challenges\n' + '\n'.join('#print axioms ' + name for name in names) + '\n')
        result = subprocess.run([str(lean), str(work / 'Audit.lean')], cwd=work, env=env, text=True, capture_output=True)
        (out / 'Audit.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 0
        pattern = re.compile(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|(does not depend on any axioms))\n")
        pos = 0
        audits = {}
        while pos < len(result.stdout):
            match = pattern.match(result.stdout, pos)
            assert match is not None
            name, content, empty = match.groups()
            values = [] if empty or not content else [v.strip() for v in content.split(',')]
            assert name not in audits and set(values) <= {'propext','Classical.choice','Quot.sound'}
            audits[name] = values
            pos = match.end()
        assert list(audits) == names
        (out / 'AUDITS.json').write_text(json.dumps(audits, indent=2) + '\n')
    for entry in inventory:
        assert SHA(Path(entry['path'])) == entry['sha256']
    (out / 'RESULT.json').write_text(json.dumps({'status':'PASS','dependencies':len(modules),'independent_results':len(names),
        'fresh_kernel_compilation':True,'temporary_products_removed':True,'capsule_manifest_sha256':MANIFEST},indent=2)+'\n')

if __name__ == '__main__':
    main()
