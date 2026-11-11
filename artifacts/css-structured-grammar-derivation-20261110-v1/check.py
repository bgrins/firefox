import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MODULES = ['Grammar', 'Laws', 'Program', 'ProgramLaws', 'JsonInput', 'Runner', 'Fixture', 'Reference', 'CurrentFixture', 'CurrentReference', 'Cases']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    lean = args.lean.resolve()
    assert sha(lean) == json.loads((ROOT / 'TOOLCHAIN.json').read_text())['sha256']
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if (ROOT / 'SOURCE-ONLY.json').exists():
        for name, expected in json.loads((ROOT / 'SOURCE-ONLY.json').read_text()).items():
            assert sha(ROOT / name) == expected, name
    for name in ['extract.py', 'check.py']:
        ast.parse((ROOT / name).read_text())
    pins = json.loads((ROOT / 'SOURCE.json').read_text())
    for record in pins['files']:
        assert sha(ROOT / record['file']) == record['sha256']
    extractor = runpy.run_path(str(ROOT / 'extract.py'))
    source = (ROOT / 'inputs/css-align-3.bs').read_text()
    drift_pin = json.loads((ROOT / 'DRIFT-SOURCE.json').read_text())
    assert sha(ROOT / drift_pin['file']) == drift_pin['sha256']
    assert sha(ROOT / 'drift/current-commit.json') == drift_pin['commit_metadata_sha256']
    current = extractor['extract']((ROOT / drift_pin['file']).read_text())
    extraction = extractor['extract'](source)
    assert extractor['quote_program'](extraction['program']) == (ROOT / 'Fixture.lean').read_text()
    assert extractor['quote_program'](current['program']).replace('extracted', 'current') == (ROOT / 'CurrentFixture.lean').read_text()
    raw = source.encode()
    for record in extraction['source_map']:
        for field in ['source', 'operator_source']:
            a, b = record[field]['bytes']
            assert raw[a:b].decode() == record[field]['text']
    assert [r['source']['text'] for r in extraction['source_map'] if r['op'] == 'seq'] == [
        '<<overflow-position>>? [ <<content-position>> | left | right ]']
    for record in json.loads((ROOT / 'SEMANTIC-SOURCES.json').read_text())['excerpts']:
        data = (ROOT / record['file']).read_bytes()
        a, b = record['bytes']
        assert data[a:b].decode() == record['text']
    refusals = {}

    def reject(label, function, message=None):
        try:
            function()
        except extractor['Refusal'] as error:
            if message:
                assert message in str(error), (label, str(error))
            refusals[label] = str(error)
        else:
            raise AssertionError('Unsupported text accepted: ' + label)

    grammar = extraction['value']['text']
    for label, value in [('double-bar', 'left || right'), ('double-ampersand', 'left && right'),
                         ('star', 'left*'), ('plus', 'left+'), ('bounds', 'left{1,2}'),
                         ('hash', 'left#'), ('empty-alternative', 'left |'),
                         ('unclosed-group', '[ left | right'), ('extra-close', 'left ]'),
                         ('double-question', 'left??'), ('markup', '<script>left</script>'),
                         ('prose', 'If this value is safe, return left.')]:
        reject(label, lambda value=value: extractor['extract'](source.replace(grammar, value, 1)))
    reject('missing-production', lambda: extractor['extract'](source.replace('<<content-position>> | left', '<<unknown-position>> | left', 1)), 'Unresolved')
    production = '<dfn>&lt;content-position></dfn> = center | start | end | flex-start | flex-end'
    reject('cycle', lambda: extractor['extract'](source.replace(production,
        '<dfn>&lt;content-position></dfn> = <<content-position>>', 1)), 'Cyclic')
    reject('duplicate-production', lambda: extractor['extract'](source + "\n<pre class='prod'>" + production + '</pre>'), 'Duplicate production')
    reject('duplicate-property', lambda: extractor['extract'](source + extraction['property_block']['text']), 'Duplicate property')
    reject('anchor-drift', lambda: extractor['extract'](source.replace("id='align-justify-content'", "id='changed-anchor'", 1)), 'anchor')
    reject('missing-property', lambda: extractor['extract'](source.replace('Name: justify-content', 'Name: different-property', 1)), 'Missing property')
    reject('actual-justify-items', lambda: extractor['extract'](source, 'justify-items'))
    save(output / 'TEXT-REFUSALS.json', refusals)
    save(output / 'extraction.json', extraction)
    declarations = []
    for module in MODULES:
        text = (ROOT / (module + '.lean')).read_text()
        assert not re.search(r'\b(sorry|admit|axiom|unsafe|partial|native_decide)\b', text.replace('"unsafe"', '"UNSAFE"'))
        declarations += ['CssGrammar.' + name for name in re.findall(r'^theorem\s+([A-Za-z0-9_]+)', text, re.M)]
    commands = []
    with tempfile.TemporaryDirectory(prefix='css-grammar-derivation-') as directory:
        temporary = Path(directory)
        workspace = temporary / 'baseline'
        workspace.mkdir()
        for module in MODULES:
            shutil.copyfile(ROOT / (module + '.lean'), workspace / (module + '.lean'))
        save(workspace / 'program.json', extraction['program'])
        shutil.copyfile(ROOT / 'cases.json', workspace / 'cases.json')

        def run(label, argv, cwd=workspace, failed=False):
            stdout, stderr = output / (label + '.stdout'), output / (label + '.stderr')
            with stdout.open('wb') as out, stderr.open('wb') as err:
                result = subprocess.run([str(x) for x in argv], cwd=cwd,
                    env=dict(os.environ, LEAN_PATH=str(cwd)), stdout=out, stderr=err)
            commands.append(dict(label=label, argv=[str(x) for x in argv], exit=result.returncode,
                stdout_sha256=sha(stdout), stderr_sha256=sha(stderr)))
            save(output / 'COMMANDS.json', commands)
            assert (result.returncode != 0) if failed else (result.returncode == 0), label
            return stdout.read_text(), stderr.read_text()

        for module in MODULES:
            a, b = run('compile-' + module, [lean, '-o', module + '.olean', module + '.lean'])
            assert not (a or b), (module, a, b)
        audit = 'import Cases\n' + '\n'.join('#print axioms ' + name for name in declarations) + '\n'
        (workspace / 'Audit.lean').write_text(audit)
        result, error = run('audit', [lean, 'Audit.lean'])
        assert not error
        matched = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", result)
        assert [name for name, _ in matched] == declarations, result
        for name, names in matched:
            axioms = {x.strip() for x in names.split(',') if x.strip()}
            assert axioms <= {'propext', 'Quot.sound', 'Classical.choice'}, (name, axioms)
        save(output / 'AXIOMS.json', {name: [x.strip() for x in names.split(',') if x.strip()] for name, names in matched})
        actual, _ = run('runtime', [lean, '--run', 'Runner.lean', 'program.json', 'cases.json'])
        rows = [json.loads(line) for line in actual.splitlines()]
        assert rows == json.loads((ROOT / 'expected.json').read_text())
        changed = extractor['extract'](source.replace(grammar, grammar.replace('normal', 'ordinary', 1), 1))
        save(workspace / 'changed.json', changed['program'])
        save(workspace / 'changed-cases.json', [['normal'], ['ordinary'], ['safe', 'left'], ['safe', 'stretch']])
        actual, _ = run('changed-program', [lean, '--run', 'Runner.lean', 'changed.json', 'changed-cases.json'])
        assert [json.loads(line) for line in actual.splitlines()] == [[['normal'], False], [['ordinary'], True], [['safe', 'left'], True], [['safe', 'stretch'], False]]
        drift_cases = [[word] for word in ['flow-start', 'flow-end']] + [
            [flag, word] for flag in ['safe', 'unsafe'] for word in ['flow-start', 'flow-end']]
        save(workspace / 'drift-program.json', current['program'])
        save(workspace / 'drift-cases.json', drift_cases)
        for label, path, accepted in [('historical', 'program.json', False), ('current', 'drift-program.json', True)]:
            actual, _ = run('drift-' + label, [lean, '--run', 'Runner.lean', path, 'drift-cases.json'])
            assert [json.loads(line) for line in actual.splitlines()] == [[words, accepted] for words in drift_cases]
        save(output / 'DRIFT.json', dict(historical_revision=pins['files'][0]['revision'],
            current_revision=drift_pin['revision'], current_instructions=len(current['program']),
            added_sequences=drift_cases, universal_current_language_theorem=True))
        bad_json = {'unknown-op': [['run', 'code']], 'wrong-arity': [['seq', 'ignored']],
            'wrong-type': [['keyword', True]], 'underflow': [['seq']],
            'leftover': [['keyword', 'a'], ['keyword', 'b']], 'empty': [],
            'object-program': {'program': extraction['program']}}
        for label, value in bad_json.items():
            save(workspace / 'bad.json', value)
            run('json-' + label, [lean, '--run', 'Runner.lean', 'bad.json', 'cases.json'], failed=True)
        mutants = [
            ('optional-required', 'Grammar', '| .optional body, input => input :: run body input',
             '| .optional body, input => run body input', 'Laws',
             'example : run (.optional (.keyword "x")) [] = [] := by decide'),
            ('sequence-reversed', 'Grammar', '(run left input).flatMap (run right)',
             '(run right input).flatMap (run left)', 'Laws',
             'example : run (.seq (.keyword "safe") (.keyword "left")) ["left", "safe"] = [[]] := by decide'),
            ('postfix-order-lost', 'Program', 'execute code (.seq left right :: stack)',
             'execute code (.seq right left :: stack)', 'ProgramLaws',
             'example : decode (encode (.seq (.keyword "safe") (.keyword "left"))) = some (.seq (.keyword "left") (.keyword "safe")) := by decide')]
        for label, module, before, after, law, witness in mutants:
            owned = temporary / label
            owned.mkdir()
            for name in ['Grammar', 'Laws', 'Program', 'ProgramLaws']:
                shutil.copyfile(ROOT / (name + '.lean'), owned / (name + '.lean'))
            path = owned / (module + '.lean')
            text = path.read_text(); assert text.count(before) == 1
            path.write_text(text.replace(before, after, 1))
            for name in (['Grammar'] if module == 'Grammar' else ['Grammar', 'Program']):
                a, b = run(label + '-compile-' + name, [lean, '-o', name + '.olean', name + '.lean'], cwd=owned)
                assert not (a or b)
            a, b = run(label + '-unchanged-law', [lean, law + '.lean'], cwd=owned, failed=True)
            assert 'error:' in a and not b
            (owned / 'Witness.lean').write_text('import ' + module + '\nopen CssGrammar\n' + witness + '\n')
            a, b = run(label + '-witness', [lean, 'Witness.lean'], cwd=owned)
            assert not (a or b)
        pin_copy = temporary / 'source-drift'
        pin_copy.mkdir()
        (pin_copy / 'inputs').mkdir()
        for name in ['extract.py', 'SOURCE.json']:
            shutil.copyfile(ROOT / name, pin_copy / name)
        for record in pins['files']:
            shutil.copyfile(ROOT / record['file'], pin_copy / record['file'])
        path = pin_copy / 'inputs/css-align-3.bs'; path.write_bytes(path.read_bytes() + b'\n')
        a, b = run('wrong-source', [sys.executable, '-I', 'extract.py', '--out', 'generated'], cwd=pin_copy, failed=True)
        assert 'Pinned source changed' in b
    save(output / 'REPORT.json', dict(status='PASS', lean_sha256=sha(lean), compiled_modules=len(MODULES),
        axiom_audits=len(declarations), reference_language_sequences=26, current_language_sequences=32, actual_file_rows=len(rows),
        changed_file_rows=4, drift_file_rows=12, source_text_refusals=len(refusals), malformed_json_refusals=len(bad_json),
        compiling_semantic_mutants=len(mutants), pinned_source_refusals=1,
        generated_instructions=len(extraction['program']), production_dependencies=len(extraction['dependencies']),
        temporary_builds_removed=True, prose_correspondence_proved=False, json_text_parser_proved=False))


if __name__ == '__main__':
    main()
