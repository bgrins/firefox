import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-document-schema-20261110-v1'
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    origins = json.loads((SOURCE / 'ORIGINS.json').read_text())
    for name, expected in origins['canonical_git_objects'].items():
        data = subprocess.check_output(['git', '-C', str(ROOT / 'artifacts/css-spec-lean'),
            '-c', 'core.fsmonitor=false', 'show', origins['canonical_commit'] + ':' + name])
        assert sha(data) == expected == sha((SOURCE / name).read_bytes())
    for name, expected in origins['prototype_git_objects'].items():
        data = subprocess.check_output(['git', '-C', str(ROOT), '-c', 'core.fsmonitor=false',
            'show', origins['prototype_commit'] + ':artifacts/css-document-schema-design-20261110-v1/' + name])
        assert sha(data) == expected == sha((SOURCE / name).read_bytes())
    modules = json.loads((SOURCE / 'PRESERVED.json').read_text())['canonical_modules'] + [
        'Model.lean', 'Prototype.lean', 'DocumentModel.lean', 'KeyLaws.lean',
        'DefinitionLaws.lean', 'DocumentLaws.lean', 'AliasBridge.lean', 'Examples.lean']
    inputs = {name: sha((SOURCE / name).read_bytes()) for name in modules}
    inputs['Boundary.lean'] = sha((HERE / 'Boundary.lean').read_bytes())
    available = {name[:-5].replace('/', '.'): name for name in modules + ['Boundary.lean']}
    needed = set()
    def visit(module):
        if module not in available or module in needed:
            return
        needed.add(module)
        name = available[module]
        text = ((HERE if name == 'Boundary.lean' else SOURCE) / name).read_text()
        for imported in re.findall(r'^import ([A-Za-z0-9_.]+)$', text, re.M):
            visit(imported)
    visit('Boundary')
    compile_modules = [name for name in modules + ['Boundary.lean']
                       if name[:-5].replace('/', '.') in needed]
    commands = {}
    with tempfile.TemporaryDirectory(prefix='source-only-', dir=out) as directory:
        work = Path(directory)
        for name in modules + ['Boundary.lean']:
            source = HERE / name if name == 'Boundary.lean' else SOURCE / name
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        def run(label, argv):
            result = subprocess.run([str(x) for x in argv], cwd=work,
                env=dict(os.environ, LEAN_PATH=str(work), PYTHONDONTWRITEBYTECODE='1'),
                capture_output=True, text=True)
            output = result.stdout + result.stderr
            (out / (label + '.log')).write_text(output)
            commands[label] = {'exit': result.returncode, 'sha256': sha(output.encode())}
            assert result.returncode == 0, (label, output)
            assert not re.search(r'(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()', output), (label, output)
            return output
        run('version', [LEAN, '--version'])
        for name in compile_modules:
            run('build-' + name.replace('/', '-'), [LEAN, '-o', name[:-5] + '.olean', name])
        names = ['accepted_definition_count_is_signature_count',
                 'constant_alias_without_input_is_refused',
                 'normalized_document_relation_still_holds',
                 'document_relation_does_not_imply_acceptance']
        (work / 'Audit.lean').write_text('import Boundary\n' + ''.join(
            '#print axioms CssDerivation.DocumentReview.' + name + '\n' for name in names))
        output = run('audits', [LEAN, 'Audit.lean'])
        audits = {}
        for line in re.sub(r',\n\s*', ', ', output).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            assert match, line
            axioms = set(match[3].split(', ')) if match[3] else set()
            assert axioms <= {'propext', 'Classical.choice', 'Quot.sound'} and match[1] not in audits
            audits[match[1]] = sorted(axioms)
        assert len(audits) == 4
    for name, expected in inputs.items():
        assert sha(((HERE if name == 'Boundary.lean' else SOURCE) / name).read_bytes()) == expected
    (out / 'CHECK.json').write_text(json.dumps({'status': 'pass', 'source_sha256': inputs,
        'origins': origins, 'lean_sha256': sha(LEAN.read_bytes()), 'commands': commands,
        'independent_audits': audits, 'fresh_module_count': len(compile_modules),
        'temporary_compiled_files_removed': True}, indent=2) + '\n')
    print(f'PASS: 23 Git-authenticated dependencies; {len(compile_modules)} fresh modules; four independent boundary audits')


if __name__ == '__main__':
    main()
