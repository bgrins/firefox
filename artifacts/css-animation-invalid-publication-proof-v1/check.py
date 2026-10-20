import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, 'use python3 -I -S'
ROOT = Path(__file__).absolute().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for k, v in pairs:
        assert k not in result, 'duplicate key'
        result[k] = v
    return result

def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)

def authenticate():
    assert not any(p.is_symlink() for p in [ROOT, *ROOT.parents]), 'symlink source'
    assert all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in ROOT.rglob('*')), 'nonregular input'
    seal = read('FREEZE.json')
    assert sha(ROOT/'MANIFEST.json') == seal['manifest_sha256'], 'manifest hash'
    assert sha(ROOT/'check.py') == seal['checker_sha256'], 'checker hash'
    manifest = read('MANIFEST.json')
    expected = set(manifest) | {'FREEZE.json', 'MANIFEST.json'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == expected, 'closed file roster'
    dirs = {str(p) for n in expected for p in Path(n).parents if str(p) != '.'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_dir()} == dirs, 'closed directory roster'
    for n, h in manifest.items():
        assert not Path(n).is_absolute() and '..' not in Path(n).parts and str(Path(n)) == n, 'unsafe input'
        assert sha(ROOT/n) == h, 'input hash: '+n
    return manifest

def source_check():
    import difflib
    assert sha(ROOT/'discovery/FILES.json') == 'a771dedbb574da459c448cbde3748bc29830b33c78d6f7c8cad51ba19be70eae'
    discovery = read('discovery/FILES.json')
    for n, h in read('SOURCE-PINS.json').items():
        assert sha(ROOT/n) == h, n
        for prefix in ['source/original/', 'source/providers/']:
            if n.startswith(prefix):
                assert h == discovery['sources/'+n[len(prefix):]], n
    patch = ''
    for n, h in read('LANDING-PINS.json').items():
        assert sha(ROOT/'source/landing'/n) == h, n
        a = (ROOT/'source/original'/n).read_text().splitlines(keepends=True)
        b = (ROOT/'source/landing'/n).read_text().splitlines(keepends=True)
        patch += ''.join(difflib.unified_diff(a, b, fromfile='a/'+n, tofile='b/'+n))
    assert patch == (ROOT/'native-only.patch').read_text(), 'exact native delta'
    result = subprocess.run([sys.executable, '-I', '-S', str(ROOT/'source_bindings.py')], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == read('SOURCE-BINDINGS.json'), 'source extraction changed'
    assert sha(ROOT/'import-origin/MANIFEST.json') == read('import-origin/FREEZE.json')['manifest_sha256']
    old = read('import-origin/MANIFEST.json')['files']
    assert sha(ROOT/'import-origin/map-combined.rs') == old['source/combined.rs']
    transfer = read('SOURCE-TRANSFER.json')
    before = (ROOT/'import-origin/map-combined.rs').read_text()
    after = (ROOT/'source/providers/servo/components/style/custom_properties_map.rs').read_text()
    assert before.count(transfer['old']) == 1 and before.replace(transfer['old'], transfer['new']) == after
    for row in read('IMPORTS.json'):
        assert sha(ROOT/row['retained']) == row['sha256'] == old[row['source']]
    return read('SOURCE-BINDINGS.json')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    manifest = authenticate()
    bindings = source_check()
    audit = read('AUDITS.json')
    names = []
    for module in audit['modules']:
        content = (ROOT/'lean'/(module+'.lean')).read_text()
        assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b', content), 'proof bypass'
        namespace = 'LiveCount' if module in ['Count', 'Domain', 'Cow'] else 'InvalidPublication'
        names += [namespace+'.'+n for n in re.findall(r'^theorem (\w+)', content, re.M)]
    assert names == audit['names'] and len(set(names)) == len(names)
    assert (ROOT/'lean/Audit.lean').read_text() == 'import PublicationWitnesses\n'+'\n'.join('#print axioms '+n for n in names)+'\n'
    tool = read('TOOLCHAIN.json')
    lean = Path(tool['lean'])
    assert sha(lean) == tool['lean_sha256']
    for n, h in read('TOOLCHAIN-LIBRARY.json').items():
        assert sha(lean.parent.parent/n) == h, n
    rust = read('RUST-TOOLCHAIN.json')
    assert sha(Path(rust['rustc'])) == rust['sha256']
    out = args.output.resolve()
    assert not out.exists() and not out.is_relative_to(ROOT.resolve()) and not ROOT.resolve().is_relative_to(out), 'fresh external output required'
    out.mkdir(parents=True)
    env = {k:v for k,v in os.environ.items() if not k.startswith(('LEAN_', 'PYTHON', 'RUST'))}
    commands = []
    def run(cmd, cwd, label, succeeds=True):
        proc = subprocess.run(cmd, cwd=cwd, env=dict(env, LEAN_PATH=str(cwd)), capture_output=True, text=True)
        (cwd/(label+'.log')).write_text(proc.stdout+proc.stderr)
        commands.append(dict(command=[str(c) for c in cmd], cwd=str(cwd), label=label, exit=proc.returncode))
        if succeeds:
            assert proc.returncode == 0, label+': '+proc.stdout+proc.stderr
        else:
            assert proc.returncode != 0 and 'assertion `left == right` failed' in proc.stderr, label+': wrong rejection cause'
        return proc.stdout
    for module in [*audit['modules'], 'Audit']:
        (out/(module+'.lean')).write_bytes((ROOT/'lean'/(module+'.lean')).read_bytes())
    for module in audit['modules']:
        run([str(lean), '-o', module+'.olean', module+'.lean'], out, module)
    log = run([str(lean), 'Audit.lean'], out, 'axioms')
    reports = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", log)
    assert [n for n,_ in reports] == names
    for n, ax in reports:
        assert [a.strip() for a in ax.split(',') if a.strip()] == audit['axioms'][n], n
    mutations = []
    for mutant in [None, *read('MUTATIONS.json')]:
        name = 'baseline' if mutant is None else mutant['id']
        d = out/('lean-'+name)
        d.mkdir()
        for filename in ['PublicationModel.lean', 'Driver.lean']:
            source = ROOT/'lean'/filename if filename != 'Driver.lean' else ROOT/filename
            code = source.read_text()
            if mutant and mutant['file'] == filename:
                assert code.count(mutant['old']) == 1
                code = code.replace(mutant['old'], mutant['new'])
            (d/filename).write_text(code)
        for module in ['PublicationModel', 'Driver']:
            run([str(lean), '-o', module+'.olean', module+'.lean'], d, module)
        observed = run([str(lean), '--run', 'Driver.lean'], d, 'observations').strip()
        expected = '|'.join(['true']*16) if mutant is None else mutant['expected']
        assert observed == expected, (name, observed, expected)
        if mutant:
            assert observed != '|'.join(['true']*16)
        mutations.append(dict(id=name, observed=observed, compiled=True))
    native = []
    template = (ROOT/'native_driver.rs').read_text()
    comparator = next(b['body'] for b in bindings if b['signature'] == 'fn can_deduplicate_values(')
    for version in ['original', 'landing', 'mutant-initial', 'mutant-empty', 'mutant-name']:
        source_version = 'original' if version == 'original' else 'landing'
        relevant = [b for b in bindings if b['file'].startswith('source/'+source_version+'/')]
        body = next(b['body'] for b in relevant if b['signature'] == 'pub(crate) fn to_declaration(')
        if version == 'mutant-initial':
            body = body.replace('None => CustomDeclarationValue::GuaranteedInvalid', 'None => CustomDeclarationValue::CSSWideKeyword(CSSWideKeyword::Initial)')
        if version == 'mutant-empty':
            body = body.replace('None => CustomDeclarationValue::GuaranteedInvalid', 'None => CustomDeclarationValue::Parsed(ComputedValue { tokens: vec![], attr_tainted: false })')
        if version == 'mutant-name':
            body = body.replace('name: self.name.clone()', 'name: String::new()')
        code = template.replace('// EXACT_FROM_COMPUTED', next(b['body'] for b in relevant if b['signature'] == 'pub fn from_computed('))
        code = code.replace('// EXACT_TO_DECLARATION', body).replace('// EXACT_REMOVAL_COMPARATOR', comparator)
        d = out/('rust-'+version)
        d.mkdir()
        (d/'main.rs').write_text(code)
        for mode, flags in [('debug', []), ('release', ['-O'])]:
            cfg = ['--cfg', 'original'] if version == 'original' else []
            run([rust['rustc'], '--edition=2021', *flags, *cfg, 'main.rs', '-o', mode], d, 'compile-'+mode)
            observed = run([str(d/mode)], d, 'run-'+mode, succeeds=not version.startswith('mutant'))
            if not version.startswith('mutant'):
                assert observed.strip() == 'conversion_rows=24;removal_rows=3'
            native.append(dict(version=version, mode=mode, intended_assertion_rejected=version.startswith('mutant'), rows=27 if not version.startswith('mutant') else None))
    result = dict(inputs=len(manifest), modules=audit['modules'], reports=len(reports), imported=audit['imported'], new=audit['new'],
                  bindings=len(bindings), lean_mutations=mutations, native=native, commands=commands,
                  native_translation_proof=False, browser_execution=False, provider_scheduler_admission='OPEN')
    (out/'CHECK.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'commands'}))

if __name__ == '__main__':
    main()
