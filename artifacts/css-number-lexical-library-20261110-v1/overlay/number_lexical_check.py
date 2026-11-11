import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
RESEARCH = ROOT / 'research/derivation/number-lexical'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def restore_imports(data, inverse):
    return re.sub(r'(?m)^import (\S+)$', lambda m: 'import ' + inverse.get(m[1], m[1]), data.decode()).encode()


def facade_sources(root):
    registry = json.loads((root / 'research/derivation/number-lexical/FACADE.json').read_text())
    seen, active, ordered = set(), set(), []
    def visit(module):
        if module in active:
            raise ValueError('Cyclic lexical facade: ' + module)
        if module in seen:
            return
        name = module.replace('.', '/') + '.lean'
        path = root / name
        if not path.is_file():
            raise ValueError('Missing lexical facade dependency: ' + name)
        data = path.read_bytes()
        if registry.get(name) != digest(data):
            raise ValueError('Changed lexical facade dependency: ' + name)
        if '/Tools/' in name or '/Tests/' in name:
            raise ValueError('Runtime or test dependency in facade: ' + name)
        active.add(module)
        for raw in data.decode().splitlines():
            line = raw.strip()
            if line.startswith('--'):
                continue
            if re.search(r'\bimport\b', line):
                match = re.fullmatch(r'import ([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)', line)
                if not match:
                    raise ValueError('Unsupported import: ' + line)
                dep = match[1]
                if dep.split('.')[0] in {'CssDerivation', 'CssSemantics'}:
                    visit(dep)
                elif dep.split('.')[0] not in {'Lean', 'Std', 'Init'}:
                    raise ValueError('External dependency: ' + dep)
        active.remove(module); seen.add(module); ordered.append(name)
    visit('CssDerivation.NumberLexical')
    if set(ordered) != set(registry):
        raise ValueError('Lexical facade registry is not exact')
    return ordered


def parse_audits(output, names):
    audits = {}
    for line in re.sub(r',\n\s*', ', ', output).splitlines():
        match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
        if not match:
            raise ValueError('Unexpected axiom output: ' + line)
        values = set(match[3].split(', ')) if match[3] else set()
        if not values <= {'propext', 'Classical.choice', 'Quot.sound'} or match[1] in audits:
            raise ValueError('Unapproved axiom record: ' + line)
        audits[match[1]] = sorted(values)
    if set(audits) != set(names):
        raise ValueError('Incomplete axiom inventory')
    return audits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    transport = json.loads((RESEARCH / 'TRANSPORT.json').read_text())
    accepted = json.loads((RESEARCH / 'origin/SOURCE-ONLY.json').read_text())
    if digest((RESEARCH / 'origin/SOURCE-ONLY.json').read_bytes()) != transport['source_manifest_sha256']:
        raise ValueError('Accepted manifest differs')
    records, mapping = transport['records'], transport['module_map']
    inverse = {new: old for old, new in mapping.items()}
    if len(inverse) != len(mapping) or len(records) != len(accepted):
        raise ValueError('Noninjective transport')
    if {r['source']: r['source_sha256'] for r in records} != accepted:
        raise ValueError('Transport does not cover accepted source roster')
    restored, inputs = {}, {}
    for record in records:
        source = record['source']
        expected_path = (mapping.get(source[:-5].replace('/', '.'), source[:-5].replace('/', '.')).replace('.', '/') + '.lean'
            if source.endswith('.lean') else 'research/derivation/number-lexical/origin/' + source)
        if record['installed'] != expected_path:
            raise ValueError('Unexpected transport destination: ' + source)
        path = ROOT / record['installed']
        data = path.read_bytes()
        if digest(data) != record['installed_sha256']:
            raise ValueError('Installed source changed: ' + record['installed'])
        raw = restore_imports(data, inverse) if path.suffix == '.lean' else data
        if digest(raw) != record['source_sha256']:
            raise ValueError('Non-import change: ' + record['source'])
        restored[record['source']] = raw
        inputs[record['installed']] = digest(data)
    compatibility = json.loads((RESEARCH / 'COMPATIBILITY.json').read_text())
    for name, expected in compatibility.items():
        if digest((ROOT / name).read_bytes()) != expected:
            raise ValueError('Existing library changed: ' + name)
        inputs[name] = expected
    facade = facade_sources(ROOT)
    for name in facade + ['number_lexical_check.py']:
        inputs[name] = digest((ROOT / name).read_bytes())
    for path in RESEARCH.rglob('*'):
        if path.is_file():
            inputs[path.relative_to(ROOT).as_posix()] = digest(path.read_bytes())
    commands = {}
    def run(label, argv, work, known=None):
        result = subprocess.run([str(x) for x in argv], cwd=work,
            env=dict(os.environ, LEAN_PATH=str(work), PYTHONDONTWRITEBYTECODE='1'),
            capture_output=True, text=True)
        output = result.stdout + result.stderr
        (out / (label + '.log')).write_text(output)
        commands[label] = {'argv': [str(x) for x in argv], 'exit': result.returncode,
                           'output_sha256': digest(output.encode())}
        normalized = output
        if known is not None:
            for new, old in inverse.items():
                normalized = normalized.replace(new.replace('.', '/') + '.lean:', old + '.lean:')
            if digest(normalized.encode()) != known:
                raise ValueError('Legacy diagnostic drift: ' + label + '\n' + output)
        elif re.search(r'(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()', output):
            raise ValueError('Unexpected diagnostic: ' + label + '\n' + output)
        if result.returncode:
            raise ValueError('Command failed: ' + label + '\n' + output)
        return output
    with tempfile.TemporaryDirectory(prefix='number-lexical-library-', dir=out) as directory:
        temp = Path(directory)
        origin, work = temp / 'accepted', temp / 'relocated'
        origin.mkdir(); work.mkdir()
        for name, data in restored.items():
            target = origin / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        shutil.copyfile(RESEARCH / 'origin/SOURCE-ONLY.json', origin / 'SOURCE-ONLY.json')
        run('accepted-replay', [sys.executable, '-B', origin / 'check.py', '--lean', lean, '--out', out / 'accepted'], origin)
        reference = json.loads((out / 'accepted/report.json').read_text())
        spec = importlib.util.spec_from_file_location('accepted_lexical', origin / 'check.py')
        helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
        modules = json.loads(restored['PRESERVED.json'])['modules'] + [n + '.lean' for n in helper.OWN]
        names = [name for module in modules for name in helper.declarations(origin / module)]
        if len(names) != 457 or len(reference['new_declarations']) != 59 or len(reference['kernel_cases']) != 22:
            raise ValueError('Accepted theorem count changed')
        installed = {r['source']: r['installed'] for r in records}
        for name in set(installed.values()) | set(facade):
            if not name.endswith('.lean'): continue
            target = work / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        known = json.loads(restored['LEGACY-DIAGNOSTICS.json'])
        for module in modules:
            name = installed[module]
            run('build-' + name.replace('/', '-'), [lean, '-o', name[:-5] + '.olean', name], work,
                known.get('build-' + module.replace('/', '-')))
        run('public-facade', [lean, '-o', 'CssDerivation/NumberLexical.olean', 'CssDerivation/NumberLexical.lean'], work)
        (work / 'Audit.lean').write_text('import CssDerivation.Tests.NumberLexicalCases\n' + ''.join('#print axioms ' + n + '\n' for n in names))
        audits = parse_audits(run('audits', [lean, 'Audit.lean'], work), names)
        if audits != reference['audits']:
            raise ValueError('Relocated axiom audit differs')
        runtime = {}
        for label, argv, expected in [
            ('actual-file', [installed['Runner.lean'], RESEARCH/'origin/number.json', RESEARCH/'origin/corpus.json'], 'expected.json'),
            ('reference', [installed['ReferenceRunner.lean'], RESEARCH/'origin/corpus.json'], 'expected.json'),
            ('changed-valid', [installed['Runner.lean'], RESEARCH/'origin/changed-number.json', RESEARCH/'origin/changed-corpus.json'], 'changed-expected.json')]:
            rows = [json.loads(line) for line in run(label, [lean, '--run', *argv], work).splitlines()]
            if rows != json.loads(restored[expected]) or rows != reference['runtime'][label]:
                raise ValueError('Relocated runtime differs: ' + label)
            runtime[label] = rows
        controls = {}
        (work / 'research/derivation/number-lexical').mkdir(parents=True)
        shutil.copyfile(RESEARCH/'FACADE.json', work/'research/derivation/number-lexical/FACADE.json')
        for mutation in ['missing', 'changed']:
            name = 'CssDerivation/NumberLexical/DocumentBridge.lean'
            path = work/name; data = path.read_bytes()
            if mutation == 'missing': path.unlink()
            else: path.write_bytes(data + b'\n')
            try: facade_sources(work)
            except ValueError as error:
                expected = ('Missing' if mutation == 'missing' else 'Changed') + ' lexical facade dependency: ' + name
                if str(error) != expected: raise
                controls[mutation] = str(error)
            else: raise ValueError('Facade drift accepted')
            path.write_bytes(data)
        run('coverage', [sys.executable, '-B', ROOT/'check.py', '--coverage-only'], ROOT)
    for name, expected in inputs.items():
        if digest((ROOT/name).read_bytes()) != expected:
            raise ValueError('Input changed during verification: ' + name)
    report = {'status': 'pass', 'audits': audits, 'new_declarations': reference['new_declarations'],
        'kernel_cases': reference['kernel_cases'], 'runtime': runtime,
        'accepted_semantic_controls': reference['controls'], 'accepted_malformed_documents': reference['malformed_documents'],
        'facade_controls': controls, 'facade': facade, 'commands': commands, 'inputs': inputs,
        'temporary_builds_removed': True, 'native_refinement': False, 'native_execution_rerun': False,
        'float_correctness': False, 'mechanical_prose_derivation': False}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS: {len(audits)} audits (398 preserved + 59 new), 22 cases, 126 relocated runtime rows; cold builds removed')


if __name__ == '__main__':
    main()
