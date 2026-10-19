import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, 'invoke Python with -I -S without optimization'
ROOT = Path(__file__).absolute().parent


def unique(pairs):
    out = {}
    for key, value in pairs:
        assert key not in out, 'duplicate JSON key'
        out[key] = value
    return out


def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    assert not any(p.is_symlink() for p in [ROOT, *ROOT.parents]), 'source path symlink'
    for p in ROOT.rglob('*'):
        assert not p.is_symlink() and (p.is_dir() or p.is_file()), 'nonregular input'
    freeze = read('FREEZE.json')
    assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256'], 'manifest hash'
    assert sha(ROOT / 'check.py') == freeze['checker_sha256'], 'checker hash'
    pins = read('MANIFEST.json')
    expected = set(pins) | {'MANIFEST.json', 'FREEZE.json'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == expected, 'closed file roster'
    expected_dirs = {str(p) for name in expected for p in Path(name).parents if str(p) != '.'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_dir()} == expected_dirs, 'closed directory roster'
    for name, pin in pins.items():
        p = Path(name)
        assert not p.is_absolute() and '..' not in p.parts and str(p) == name, 'unsafe input name'
        assert sha(ROOT / p) == pin, 'input hash: ' + name
    return pins


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    pins = authenticate()
    deps = read('DEPENDENCIES.json')
    for label, info in deps.items():
        for name, digest in info['pins'].items():
            assert sha(ROOT / 'imports' / label / name) == digest, 'dependency seal'
        manifest = read('imports/' + label + '/MANIFEST.json')
        entries = manifest['files'] if label == 'count' else manifest
        assert len(entries) == info['inputs']
        for name, digest in entries.items():
            assert sha(ROOT / 'imports' / label / name) == digest, 'dependency input'
    join = read('SOURCE-JOIN.json')
    assert [row['variant'] for row in join] == ['original', 'combined']
    for row in join:
        assert row['iterator'] == 'imports/iterator/source/' + row['variant'] + '.rs'
        assert row['count'] == 'imports/count/source/' + row['variant'] + '.rs'
        assert sha(ROOT / row['iterator']) == sha(ROOT / row['count']) == row['sha256']
    assert join[1]['sha256'] == '9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d'
    inventory = read('AUDITS.json')
    names = []
    for module in inventory['modules']:
        source = (ROOT / 'lean' / (module + '.lean')).read_text()
        assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b', source)
        names.extend('MapComposition.' + n for n in re.findall(r'^theorem (\w+)', source, re.M))
    assert names == inventory['names'] and len(names) == 32
    assert (ROOT / 'lean/CompositionAudit.lean').read_text() == 'import CompositionWitnesses\n' + '\n'.join('#print axioms ' + n for n in names) + '\n'
    tool = read('imports/iterator/TOOLCHAIN.json')
    lean = Path(tool['lean'])
    assert sha(lean) == tool['lean_sha256']
    for relative, digest in read('imports/iterator/TOOLCHAIN-LIBRARY.json').items():
        assert sha(lean.parent.parent / relative) == digest, 'Lean standard library'
    out = args.output.absolute()
    assert not out.exists() and not out.is_relative_to(ROOT) and not ROOT.is_relative_to(out)
    assert not any(p.is_symlink() for p in [out.parent, *out.parent.parents])
    out.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'LEAN_'))}
    commands = []

    def run(command, cwd, label, lean_path=None):
        actual_env = dict(env)
        if lean_path is not None:
            actual_env['LEAN_PATH'] = str(lean_path)
        p = subprocess.run(command, cwd=cwd, env=actual_env, text=True, capture_output=True)
        (out / (label + '.log')).write_text(p.stdout + p.stderr)
        commands.append({'label': label, 'command': command, 'returncode': p.returncode})
        assert p.returncode == 0, label + ': ' + p.stdout + p.stderr
        return p.stdout

    for label in ['iterator', 'count']:
        command = [sys.executable, '-I', '-S', str(ROOT / 'imports' / label / 'check.py'), '--output', str(out / label)]
        if label == 'count':
            command += ['--lean', str(lean)]
        run(command, out, label + '-replay')
    inherited_iterator = json.loads((out / 'iterator/CHECK.json').read_text(), object_pairs_hook=unique)
    inherited_count = json.loads((out / 'count/RESULT.json').read_text(), object_pairs_hook=unique)
    assert inherited_iterator['theorem_axiom_reports'] == 50 and inherited_count['audited_theorems'] == 55
    build = out / 'composition'
    build.mkdir()
    imported = {'iterator': ['Iterator', 'Contracts', 'CursorHistory'], 'count': ['Count', 'Domain', 'Cow', 'Index']}
    for label, modules in imported.items():
        for module in modules:
            for suffix in ['.olean', '.lean']:
                (build / (module + suffix)).write_bytes((out / label / (module + suffix)).read_bytes())
    for module in [*inventory['modules'], 'CompositionAudit']:
        (build / (module + '.lean')).write_bytes((ROOT / 'lean' / (module + '.lean')).read_bytes())
    for module in inventory['modules']:
        run([str(lean), '-o', module + '.olean', module + '.lean'], build, module, build)
    audit = run([str(lean), 'CompositionAudit.lean'], build, 'composition-axioms', build)
    observed = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit)
    assert [name for name, _ in observed] == names, 'exact composition audit roster'
    for name, axioms in observed:
        assert set(a.strip() for a in axioms.split(',') if a.strip()) <= {'propext', 'Quot.sound', 'Classical.choice'}, name
    base = (ROOT / 'mutants/Model.lean').read_text()
    driver = (ROOT / 'mutants/Driver.lean').read_text()
    mutations = []
    for record in [None, *read('MUTATIONS.json')]:
        label = 'baseline' if record is None else record['id']
        folder = out / label
        folder.mkdir()
        model = base
        if record:
            assert model.count(record['old']) == 1
            model = model.replace(record['old'], record['new'])
        (folder / 'Model.lean').write_text(model)
        (folder / 'Driver.lean').write_text(driver)
        path = str(folder) + os.pathsep + str(build)
        run([str(lean), '-o', 'Model.olean', 'Model.lean'], folder, label + '-definitions', path)
        observed = run([str(lean), '--run', 'Driver.lean'], folder, label + '-gate', path).strip()
        assert re.fullmatch(r'(true|false)(\|(true|false)){4}', observed)
        assert (observed == 'true|true|true|true|true') == (record is None), 'undiscriminated wiring mutant'
        mutations.append({'label': label, 'observed': observed, 'compiled_definitions': True})
    result = {'inputs': len(pins), 'new_modules': len(inventory['modules']), 'new_axiom_reports': len(names),
              'inherited_axiom_reports': 105, 'total_axiom_reports': 105 + len(names),
              'raw_enumeration': 'DERIVED', 'finite_history_live_count': 'DERIVED',
              'mutations': mutations, 'commands': commands, 'native_or_browser_execution': False}
    (out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
