import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError("isolated nonoptimized Python required")
ROOT = Path(__file__).absolute().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def unique(pairs):
    d = {}
    for k, v in pairs:
        assert k not in d, 'duplicate JSON key'
        d[k] = v
    return d

def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)

def authenticate():
    assert not any(p.is_symlink() for p in [ROOT, *ROOT.parents]), 'source path symlink'
    for p in ROOT.rglob('*'):
        assert not p.is_symlink() and (p.is_file() or p.is_dir()), 'nonregular input'
    seal = read('FREEZE.json')
    assert sha(ROOT / 'MANIFEST.json') == seal['manifest_sha256'], 'manifest hash'
    assert sha(ROOT / 'check.py') == seal['checker_sha256'], 'checker hash'
    m = read('MANIFEST.json')
    expected = set(m) | {'FREEZE.json', 'MANIFEST.json'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == expected, 'closed file roster'
    dirs = {str(p) for n in expected for p in Path(n).parents if str(p) != '.'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_dir()} == dirs, 'closed directory roster'
    for n, h in m.items():
        assert not Path(n).is_absolute() and '..' not in Path(n).parts and str(Path(n)) == n, 'unsafe input name'
        assert sha(ROOT / n) == h, 'input hash: ' + n
    return m

def source_bindings():
    pins = read('SOURCE-PINS.json')
    for n, h in pins.items():
        assert sha(ROOT / n) == h
    rows = read('SOURCE-BINDINGS.json')
    for row in rows:
        raw = (ROOT / row['file']).read_bytes()
        body = raw[row['start_byte']:row['end_byte']]
        assert body.decode() == row['body'] and hashlib.sha256(body).hexdigest() == row['sha256']
        text = raw.decode()
        start = text.index(row['signature'], text.index(row['scope']) if row['scope'] else 0)
        assert len(text[:start].encode()) == row['start_byte']
        assert row['body'].rstrip().endswith('}')
    map_path = 'servo/components/style/custom_properties_map.rs'
    cascade_path = 'servo/components/style/properties/cascade.rs'
    original = (ROOT / 'source/original' / map_path).read_text()
    candidate = (ROOT / 'source/candidate' / map_path).read_text()
    before = 'if self.get(name) == value.as_ref() {'
    after = 'if can_deduplicate_values(self.get(name), value.as_ref()) {'
    assert original.count(before) == 1 and original.replace(before, after) == candidate
    original = (ROOT / 'source/original' / cascade_path).read_text()
    candidate = (ROOT / 'source/candidate' / cascade_path).read_text()
    before = 'if let Some(existing_value) = existing_value.as_universal() {\n                    return existing_value != value;'
    after = 'if let Some(existing_unparsed) = existing_value.as_universal() {\n                    return existing_value.attr_tainted != value.is_attr_tainted()\n                        || existing_unparsed != value;'
    assert original.count(before) == 1 and original.replace(before, after) == candidate
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    m = authenticate()
    bindings = source_bindings()
    audit = read('AUDITS.json')
    names = []
    for module in audit['modules']:
        s = (ROOT / 'lean' / (module + '.lean')).read_text()
        assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b', s)
        names.extend('TaintShortcut.' + n for n in re.findall(r'^theorem (\w+)', s, re.M))
    assert names == audit['names']
    assert (ROOT / 'lean/Audit.lean').read_text() == 'import Witnesses\n' + '\n'.join('#print axioms ' + n for n in names) + '\n'
    tool = read('TOOLCHAIN.json')
    lean = Path(tool['lean'])
    assert sha(lean) == tool['lean_sha256']
    for n, h in read('TOOLCHAIN-LIBRARY.json').items():
        assert sha(lean.parent.parent / n) == h, 'Lean library identity'
    out = args.output.resolve()
    source = ROOT.resolve()
    assert not out.exists() and not out.is_relative_to(source) and not source.is_relative_to(out), 'fresh external output required'
    out.mkdir(parents=True)
    env = {k:v for k,v in os.environ.items() if not k.startswith(('LEAN_', 'PYTHON'))}
    commands = []
    def run(args, cwd, label):
        p = subprocess.run([str(lean), *args], cwd=cwd, env=dict(env, LEAN_PATH=str(cwd)), capture_output=True, text=True)
        (cwd / (label + '.log')).write_text(p.stdout + p.stderr)
        commands.append({'label':label, 'command':[str(lean), *args], 'cwd':str(cwd), 'exit':p.returncode})
        assert p.returncode == 0, label + ': ' + p.stdout + p.stderr
        return p.stdout
    for module in [*audit['modules'], 'Audit']:
        (out / (module + '.lean')).write_bytes((ROOT / 'lean' / (module + '.lean')).read_bytes())
    for module in audit['modules']:
        run(['-o',module+'.olean',module+'.lean'],out,module)
    log = run(['Audit.lean'],out,'axioms')
    reports = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", log)
    assert [n for n,_ in reports] == names
    for name, axioms in reports:
        assert {a.strip() for a in axioms.split(',') if a.strip()} <= {'propext','Quot.sound','Classical.choice'}, name
    results = []
    baseline = (ROOT / 'lean/Model.lean').read_text()
    expected = '|'.join(['true'] * 7)
    for mutation in [None, *read('MUTATIONS.json')]:
        name = 'baseline' if mutation is None else mutation['id']
        d = out / name
        d.mkdir()
        model = baseline
        if mutation:
            assert model.count(mutation['old']) == 1
            model = model.replace(mutation['old'], mutation['new'])
        (d / 'Model.lean').write_text(model)
        (d / 'Driver.lean').write_bytes((ROOT / 'mutants/Driver.lean').read_bytes())
        run(['-o','Model.olean','Model.lean'],d,'definitions')
        observed = run(['--run','Driver.lean'],d,'observations').strip()
        assert re.fullmatch(r'(true|false)(\|(true|false)){6}', observed)
        assert (observed == expected) == (mutation is None), 'semantic mutant not distinguished'
        results.append({'id':name,'observed':observed,'compiled_definitions':True})
    result = {'inputs':len(m),'modules':audit['modules'],'axiom_reports':len(reports),'source_bindings':len(bindings),
              'mutations':results,'commands':commands,'native_execution':False,
              'full_native_eligibility_provider_admission':'OPEN','global_PartialEq_changed':False}
    (out / 'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__ == '__main__':
    main()
