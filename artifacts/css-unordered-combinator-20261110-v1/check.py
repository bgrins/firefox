import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
MODULES = ['Grammar', 'Laws', 'Program', 'ProgramLaws', 'JsonInput', 'Selections',
           'SelectionLaws', 'Unordered', 'UnorderedLaws', 'ProgramV2', 'JsonV2',
           'Fixture', 'TextLaws', 'Cases', 'RunnerV2']
BASE = {'Grammar', 'Laws', 'Program', 'ProgramLaws', 'JsonInput'}
ALLOWED_AXIOMS = {'propext', 'Quot.sound', 'Classical.choice'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit_text(text, names):
    found = re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])", text)
    assert [name for name, _ in found] == names, (names, found)
    for _, axes in found:
        assert {x.strip() for x in axes.split(',') if x.strip()} <= ALLOWED_AXIOMS


def source_checks():
    for manifest in ('PROPOSAL-FILES.json', 'SOURCE-ONLY.json'):
        for relative, expected in json.loads((ROOT / manifest).read_text()).items():
            assert sha(ROOT / relative) == expected, relative
    for manifest in ('PRESERVED.json', 'COMPATIBILITY-SOURCES.json'):
        for row in json.loads((ROOT / manifest).read_text()):
            assert sha(ROOT / row['copy']) == row['sha256']
    extractor = load('extract_v2')
    generated = load('generate')
    result, fixture = generated.generate()
    assert fixture == (ROOT / 'Fixture.lean').read_text()
    assert result == json.loads((ROOT / 'extraction.json').read_text())
    assert result['program'] == json.loads((ROOT / 'program.json').read_text())
    oracle = json.loads((ROOT / 'text-transform-oracle.json').read_text())
    assert len(oracle) == len({tuple(x) for x in oracle}) == 38
    alphabet = ['none', 'capitalize', 'uppercase', 'lowercase', 'full-width', 'full-size-kana']
    cases = [list(x) for n in range(5) for x in itertools.product(alphabet, repeat=n)]
    cases += [['bogus'], ['UPPERCASE'], ['inherit'], ['full-width', 'tail']]
    assert cases == json.loads((ROOT / 'cases.json').read_text())
    assert [[x, x in oracle] for x in cases] == json.loads((ROOT / 'expected.json').read_text())
    failures = []

    def refusal(label, action, expected):
        try:
            action()
        except extractor.Refusal as error:
            assert expected in str(error), (label, error)
            failures.append(dict(label=label, diagnostic=str(error)))
        else:
            raise AssertionError('accepted ' + label)

    grammar = next(x for x in json.loads((ROOT / 'inputs/transfer-contexts.json').read_text())['properties'] if x['property'] == 'text-transform')['value']['text']
    refusal('historical-parser-unchanged', lambda: extractor.baseline.Parser(grammar, 0).parse(), 'Unsupported double-bar')
    assert extractor.Parser(grammar).parse()['op'] == 'alt'
    for text in ('a && b', 'a ||| b', 'a ||', '|| a', 'a*', 'a#', 'a{1,2}', '[a || b', 'a ]', 'a??', '[]', 'a / b', '<<unknown>>'):
        refusal('text:' + text, lambda text=text: extractor.Parser(text).parse(), '')
    display = (ROOT / 'inputs/css-display-3.bs').read_text()
    match = re.search(r'<dfn>&lt;display-listitem></dfn> = ([^\n]+)', display)
    assert match and '&&' in match[1]
    refusal('display-listitem-remains-unsupported', lambda: extractor.Parser(match[1]).parse(), 'Unsupported grammar text')
    source = (ROOT / 'inputs/css-text-3.bs').read_bytes()
    refusal('changed-source', lambda: extractor.pinned_text_transform(source + b' '), 'Pinned source changed')
    contexts = json.loads((ROOT / 'inputs/transfer-contexts.json').read_text())
    target = next(x for x in contexts['properties'] if x['property'] == 'text-transform')
    target['anchor'] = 'wrong-anchor'
    refusal('changed-anchor', lambda: extractor.pinned_text_transform(contexts=contexts), 'reviewed anchor')
    contexts = json.loads((ROOT / 'inputs/transfer-contexts.json').read_text())
    target = next(x for x in contexts['properties'] if x['property'] == 'text-transform')
    target['value']['bytes'][1] -= 1
    refusal('truncated-source-span', lambda: extractor.pinned_text_transform(contexts=contexts), 'source span')
    for text in ('a', 'a | b', '[a | b] c?', 'a? b', 'a b | c d', '[[a b] | c]?', 'a | b c?'):
        assert extractor.Parser(text).parse() == extractor.baseline.Parser(text, 0).parse()
    flat = extractor.Parser('a || b || c').parse()
    nested = extractor.Parser('a || [b || c]').parse()
    assert flat['op'] == 'unordered' and len(flat['args']) == 3
    assert len(nested['args']) == 2 and nested['args'][1]['op'] == 'unordered'
    precedence = extractor.Parser('a b || c | d').parse()
    assert precedence['op'] == 'alt' and precedence['args'][0]['args'][0]['op'] == 'seq'
    for text in ('a || b || c', 'a || [b || c]', 'a? b || c', grammar):
        data = extractor.emit(extractor.Parser(text).parse(), text)
        for row in data['source_map']:
            for span in [row['source'], *row['operators']]:
                assert text.encode()[slice(*span['bytes'])].decode() == span['text']
        assert data['source_map'][-1]['source']['text'] == text
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    options = parser.parse_args()
    lean = options.lean.resolve()
    assert sha(lean) == json.loads((ROOT / 'TOOLCHAIN.json').read_text())['sha256']
    out = options.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    failures = source_checks()
    (out / 'SOURCE-CONTROLS.json').write_text(json.dumps(failures, indent=2) + '\n')
    commands = []
    with tempfile.TemporaryDirectory(prefix='css-unordered-') as temp:
        scratch = Path(temp)
        env = dict(os.environ, LEAN_PATH=str(scratch))
        for module in MODULES:
            path = ROOT / ('baseline' if module in BASE else '') / (module + '.lean')
            text = path.read_text()
            assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', text), module
            shutil.copyfile(path, scratch / path.name)

        def command(label, args, okay=True):
            run = subprocess.run([str(lean), *args], cwd=scratch, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            logfile = out / (label + '.log')
            logfile.write_text(run.stdout)
            commands.append(dict(label=label, argv=[str(lean), *args], cwd=str(scratch), returncode=run.returncode, log=logfile.name, sha256=sha(logfile)))
            (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
            if okay:
                assert run.returncode == 0 and 'warning:' not in run.stdout and 'error:' not in run.stdout, (label, run.stdout)
            else:
                assert run.returncode != 0 and ('error:' in run.stdout or 'uncaught exception:' in run.stdout), (label, run.stdout)
                assert not any(x in run.stdout for x in ('unknown module', 'object file', 'unknown identifier', 'failed to synthesize')), run.stdout
            return run.stdout

        def compile_module(module, label=None, okay=True):
            return command(label or ('compile-' + module), ['-o', module + '.olean', module + '.lean'], okay)

        for module in MODULES:
            compile_module(module)
        names = []
        for module in MODULES:
            text = (scratch / (module + '.lean')).read_text()
            namespace = 'CssGrammar' if module in BASE else 'CssUnordered'
            names += [namespace + '.' + name for name in re.findall(r'^theorem\s+(\w+)', text, re.M)]
        assert names == json.loads((ROOT / 'THEOREMS.json').read_text())
        (scratch / 'Audit.lean').write_text('\n'.join('import ' + x for x in MODULES) + '\n' + '\n'.join('#print axioms ' + x for x in names) + '\n')
        audit_text(command('axioms', ['Audit.lean']), names)

        def runtime(label, program, cases, expected):
            pp, cp = scratch / (label + '-program.json'), scratch / (label + '-cases.json')
            if label == 'text-transform':
                pp.write_bytes((ROOT / 'program.json').read_bytes())
            else:
                pp.write_text(json.dumps(program))
            cp.write_text(json.dumps(cases))
            result = command(label, ['--run', 'RunnerV2.lean', str(pp), str(cp)])
            rows = [json.loads(x) for x in result.splitlines()]
            assert rows == expected, label
            return len(rows)

        program = json.loads((ROOT / 'program.json').read_text())
        main_rows = runtime('text-transform', program, json.loads((ROOT / 'cases.json').read_text()), json.loads((ROOT / 'expected.json').read_text()))
        old = json.loads((ROOT / 'compatibility/old-program.json').read_text())
        current = json.loads((ROOT / 'compatibility/current-program.json').read_text())
        old_rows = 0
        for name, prog in [('old', old), ('resize', json.loads((ROOT / 'compatibility/resize-program.json').read_text()))]:
            cases = json.loads((ROOT / ('compatibility/' + name + '-cases.json')).read_text())
            expected = json.loads((ROOT / ('compatibility/' + name + '-expected.json')).read_text())
            old_rows += runtime('compat-' + name, prog, cases, expected)
        drift = [[word] for word in ('flow-start', 'flow-end')] + [[prefix, word] for prefix in ('safe', 'unsafe') for word in ('flow-start', 'flow-end')]
        old_rows += runtime('compat-historical-drift', old, drift, [[x, False] for x in drift])
        old_rows += runtime('compat-current-drift', current, drift, [[x, True] for x in drift])
        changed = copy.deepcopy(old)
        for op in changed:
            if op == ['keyword', 'normal']:
                op[1] = 'ordinary'
        changed_cases = [['normal'], ['ordinary'], ['safe', 'left'], ['safe', 'stretch']]
        old_rows += runtime('compat-changed-program', changed, changed_cases, [[x, b] for x, b in zip(changed_cases, [False, True, True, False])])
        changed = copy.deepcopy(program)
        changed[0] = ['keyword', 'ordinary']
        actual_changed = runtime('changed-text-program', changed, [['none'], ['ordinary'], ['uppercase', 'full-width']], [[['none'], False], [['ordinary'], True], [['uppercase', 'full-width'], True]])
        extractor = load('extract_v2')
        shape_rows = 0
        shapes = [
            ('a || a', [['a'], ['a', 'a'], ['a', 'a', 'a'], []], [True, True, False, False]),
            ('a || b || c', [['b', 'a', 'c'], ['a', 'b', 'c']], [True, True]),
            ('a || [b || c]', [['b', 'a', 'c'], ['b', 'c', 'a']], [False, True]),
            ('a? b || c', [['b'], ['c', 'b'], ['c', 'a', 'b'], []], [True, True, True, False]),
            ('a b || c | d', [['a', 'b'], ['c', 'a', 'b'], ['d'], ['a'], ['c', 'd']], [True, True, True, False, False]),
        ]
        for index, (text, cases, expected) in enumerate(shapes):
            prog = extractor.emit(extractor.Parser(text).parse(), text)['program']
            shape_rows += runtime('shape-' + str(index), prog, cases, [[x, b] for x, b in zip(cases, expected)])
        bad = [
            ('unknown-op', [['permutation', 2]], 'unknown opcode'),
            ('arity-field-missing', [['unordered']], 'unknown opcode'),
            ('arity-field-extra', [['unordered', 2, 3]], 'unknown opcode'),
            ('arity-string', [['unordered', '2']], 'Nat'),
            ('arity-bool', [['unordered', True]], 'Nat'),
            ('arity-zero', [['unordered', 0]], 'invalid stack'),
            ('arity-one', [['keyword', 'a'], ['unordered', 1]], 'invalid stack'),
            ('arity-underflow', [['keyword', 'a'], ['unordered', 2]], 'invalid stack'),
            ('residual-stack', [['keyword', 'a'], ['keyword', 'b']], 'invalid stack'),
        ]
        for label, text in [('nullable', 'a? || b'), ('all-nullable', 'a? || b?'), ('nested-nullable', '[a? || b] c || d')]:
            bad.append((label, extractor.emit(extractor.Parser(text).parse(), text)['program'], 'invalid stack'))
        for label, prog, expected in bad:
            pp = scratch / ('bad-' + label + '.json')
            pp.write_text(json.dumps(prog))
            result = command('bad-' + label, ['--run', 'RunnerV2.lean', str(pp), str(ROOT / 'cases.json')], False)
            assert expected.lower() in result.lower(), (label, result)

        mutations = [
            ('missing-combinations', 'Selections', 'SelectionLaws', 'smaller ++ smaller.flatMap (insertions head)', 'smaller ++ [[head]]', '([0, 1] : List Nat) ∉ orders [0, 1]'),
            ('reused-occurrence', 'Selections', 'SelectionLaws', '| [] => [[item]]', '| [] => [[item, item]]', '([0, 0] : List Nat) ∈ orders [0]'),
            ('nullable-admitted', 'Unordered', 'UnorderedLaws', 'if valid children then', 'if decide (2 ≤ children.length) then', 'lower [.optional (.keyword "a"), .keyword "b"] ≠ none'),
        ]
        for label, impl, laws, before, after, witness in mutations:
            path = scratch / (impl + '.lean')
            original = path.read_text()
            assert original.count(before) == 1
            witness_path = scratch / 'Witness.lean'
            witness_path.write_text('import ' + impl + '\nnamespace CssUnordered\ntheorem mutant_witness : ' + witness + ' := by decide\nend CssUnordered\n#print axioms CssUnordered.mutant_witness\n')
            baseline = command(label + '-baseline-witness', ['Witness.lean'], False)
            assert 'false' in baseline
            path.write_text(original.replace(before, after))
            compile_module(impl, label + '-implementation')
            command(label + '-unchanged-laws', [laws + '.lean'], False)
            audit_text(command(label + '-semantic-witness', ['Witness.lean']), ['CssUnordered.mutant_witness'])
            path.write_text(original)
            compile_module(impl, label + '-restore')
        report = dict(status='PASS', modules=len(MODULES), audits=len(names), new_audits=len([n for n in names if n.startswith('CssUnordered.')]),
            text_rows=main_rows, old_rows=old_rows, changed_rows=actual_changed, shape_rows=shape_rows,
            source_refusals=len(failures), json_refusals=len(bad), semantic_mutants=len(mutations), commands=len(commands), compiled_scratch_removed=True)
    assert not scratch.exists()
    (out / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(ROOT))
    main()
