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


def bindings():
    result = []
    for variant in ['original', 'candidate', 'combined']:
        s = (ROOT / 'source' / (variant + '.rs')).read_text()
        impls = list(re.finditer(r'^impl[^\n]*\{', s, re.M))
        for m in re.finditer(r'^    (?:pub )?fn (\w+)\(', s, re.M):
            impl = [i for i in impls if i.start() < m.start()][-1].group(0)
            end = s.index('\n    }', m.end()) + 6
            body = s[m.start():end]
            result.append({'variant': variant, 'impl': impl, 'name': m.group(1),
                           'start_byte': len(s[:m.start()].encode()), 'end_byte': len(s[:end].encode()),
                           'body': body, 'sha256': hashlib.sha256(body.encode()).hexdigest(),
                           'scope': 'proof bridge' if (('Iterator for' in impl and m.group(1) == 'next') or
                               (impl == 'impl Inner {' and m.group(1) in ['iter', 'get']) or
                               (impl == 'impl CustomPropertiesMap {' and m.group(1) == 'get_index'))
                           else 'retained context, not count/COW proof'})
    assert result == read('SOURCE-BINDINGS.json')
    assert len(result) == 54
    original = (ROOT / 'source/original.rs').read_text()
    candidate = (ROOT / 'source/candidate.rs').read_text()
    old_loop = '        loop {\n            let (name, value)'
    old_continue = 'if descendant.own_properties.contains_key(name) {\n                    continue;'
    assert original.count(old_loop) == original.count(old_continue) == 1
    assert original.replace(old_loop, "        'properties: loop {\n            let (name, value)").replace(
        old_continue, "if descendant.own_properties.contains_key(name) {\n                    continue 'properties;") == candidate
    rows = {(r['variant'], r['impl'], r['name']): r['body'] for r in result}
    for (variant, impl, name), body in rows.items():
        if variant == 'candidate' and name not in ['insert', 'get_index']:
            assert rows[('combined', impl, name)] == body
    getter = rows[('combined', 'impl CustomPropertiesMap {', 'get_index')]
    formatted = 'self.0\n            .iter()\n            .filter(|(_, value)| value.is_some())\n            .nth(index)'
    old_combined = (ROOT / 'history/combined-unformatted.rs').read_text()
    assert old_combined.replace('self.0.iter().filter(|(_, value)| value.is_some()).nth(index)', formatted) == (ROOT / 'source/combined.rs').read_text()
    for name, pin in read('SOURCE-PINS.json')['files'].items():
        assert sha(ROOT / name) == pin
    assert formatted in getter
    assert rows[('candidate', 'impl CustomPropertiesMap {', 'get_index')].replace(
        'self.0.iter().nth(index)', formatted) == getter
    return result


def definitions(module, names):
    s = (ROOT / 'lean' / (module + '.lean')).read_text()
    chunks = []
    for name in names:
        start = re.search(r'^(?:abbrev|def|structure|inductive) ' + name + r'\b', s, re.M)
        assert start, name
        stop = re.search(r'^\s*(?:theorem|def|structure|inductive|abbrev|end|variable)\b', s[start.end():], re.M)
        assert stop, name
        chunks.append(s[start.start():start.end() + stop.start()].rstrip())
    return '\n\n'.join(chunks)


def model_text():
    return 'import Std\nnamespace MapIterator\n' + definitions('Iterator', ['Entry', 'Node', 'Chain']) + \
        '\nvariable {K V : Type} [DecidableEq K]\n' + definitions('Iterator',
        ['owns', 'shadow', 'visible', 'reference', 'Cursor', 'start', 'rank', 'Action', 'step', 'walk', 'drain']) + \
        '\n' + definitions('Contracts', ['live', 'getIndex']) + '\nend MapIterator\n'


DRIVER = '''import Model
open MapIterator
def main : IO Unit := do
  let shadow : Chain Nat Nat := [[(0,some 20)],[(0,some 10),(1,some 30)]]
  let deep : Chain Nat Nat := [[(0,some 40)],[],[(0,some 10),(1,some 30)]]
  let tomb : Chain Nat Nat := [[(0,none)],[(0,some 10),(1,some 30)]]
  let checks := [decide (drain (start shadow) = [(0,some 20),(1,some 30)]),
    decide (drain (start deep) = [(0,some 40),(1,some 30)]),
    decide (drain (start tomb) = [(0,none),(1,some 30)]),
    decide (getIndex tomb 1 0 = some (1,some 30)),
    decide (drain (start ([[],[],[]] : Chain Nat Nat)) = [])]
  IO.println (String.intercalate "|" (checks.map toString))
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    pins = authenticate()
    source = bindings()
    inventory = read('LEAN-INVENTORY.json')
    names = []
    for module in inventory['modules']:
        s = (ROOT / 'lean' / (module + '.lean')).read_text()
        assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b', s)
        names.extend('MapIterator.' + n for n in re.findall(r'^theorem (\w+)', s, re.M))
    assert names == read('AUDIT-NAMES.json') and len(names) == inventory['theorems']
    assert (ROOT / 'lean/Audit.lean').read_text() == 'import Witnesses\n' + '\n'.join('#print axioms ' + n for n in names) + '\n'
    tool = read('TOOLCHAIN.json')
    lean = Path(tool['lean'])
    assert sha(lean) == tool['lean_sha256'], 'Lean binary identity'
    for relative, pin in read('TOOLCHAIN-LIBRARY.json').items():
        assert sha(lean.parent.parent / relative) == pin, 'Lean library identity: ' + relative
    out = args.output.absolute()
    assert not out.exists() and not out.is_relative_to(ROOT) and not ROOT.is_relative_to(out), 'fresh external output required'
    assert not any(p.is_symlink() for p in [out.parent, *out.parent.parents]), 'output parent symlink'
    out.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'LEAN_'))}

    def run(arguments, directory, label):
        actual_env = dict(env, LEAN_PATH=str(directory))
        p = subprocess.run([str(lean), *arguments], cwd=directory, env=actual_env, text=True, capture_output=True)
        (directory / (label + '.log')).write_text(p.stdout + p.stderr)
        assert p.returncode == 0, label + ': ' + p.stdout + p.stderr
        return p.stdout

    for module in [*inventory['modules'], 'Audit']:
        (out / (module + '.lean')).write_bytes((ROOT / 'lean' / (module + '.lean')).read_bytes())
    for module in inventory['modules']:
        run(['-o', str(out / (module + '.olean')), str(out / (module + '.lean'))], out, module)
    audit = run([str(out / 'Audit.lean')], out, 'axioms')
    reports = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit)
    assert [name for name, _ in reports] == names, 'exact theorem audit roster'
    for name, axioms in reports:
        assert set(a.strip() for a in axioms.split(',') if a.strip()) <= {'propext', 'Quot.sound', 'Classical.choice'}, name
    source_model = model_text()
    mutations = read('MUTATIONS.json')
    results = []
    for item in [None, *mutations]:
        label = 'baseline' if item is None else item['id']
        directory = out / label
        directory.mkdir()
        model = source_model
        if item:
            assert model.count(item['old']) == 1, label
            model = model.replace(item['old'], item['new'])
        (directory / 'Model.lean').write_text(model)
        (directory / 'Driver.lean').write_text(DRIVER)
        run(['-o', str(directory / 'Model.olean'), str(directory / 'Model.lean')], directory, 'definitions')
        observed = run(['--run', str(directory / 'Driver.lean')], directory, 'observations').strip()
        assert re.fullmatch(r'(true|false)(\|(true|false)){4}', observed), 'observation grammar'
        expected = 'true|true|true|true|true'
        assert (observed == expected) == (item is None), 'semantic mutant not distinguished: ' + label
        results.append({'id': label, 'observed': observed, 'expected': expected})
    result = {'authenticated_files': len(pins), 'source_methods': len(source), 'modules': inventory['modules'],
              'theorem_axiom_reports': len(reports), 'mutations': results,
              'native_Rust_or_browser_executed': False, 'count_constructor_preservation': 'external open obligation'}
    (out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
