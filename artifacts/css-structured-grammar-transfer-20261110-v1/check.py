import argparse
import copy
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
MODULES = ['Grammar', 'Laws', 'Program', 'ProgramLaws', 'JsonInput', 'Runner', 'Fixture', 'Reference']


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
    lean, output = args.lean.resolve(), args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    assert sha(lean) == json.loads((ROOT / 'preserved/TOOLCHAIN.json').read_text())['sha256']
    if (ROOT / 'SOURCE-ONLY.json').exists():
        for name, digest in json.loads((ROOT / 'SOURCE-ONLY.json').read_text()).items():
            assert sha(ROOT / name) == digest, name
    benchmark = runpy.run_path(str(ROOT / 'benchmark.py'))
    result, generated = benchmark['run']()
    assert result['original_successes'] == 0 and result['selected_context_successes'] == 4
    assert list(generated) == ['text-align', 'resize', 'visibility', 'box-sizing']
    assert benchmark['ORIGINAL']['quote_program'](generated['resize']['program']) == (ROOT / 'Fixture.lean').read_text()
    protocol = json.loads((ROOT / 'PROTOCOL.json').read_text())
    assert [op[1] for op in generated['resize']['program'] if op[0] == 'keyword'] == protocol['anticipated_oracle']
    for value in generated.values():
        for mapping in value['source_map']:
            for field in ['expression', 'operator']:
                record = mapping[field]
                data = (ROOT / record['file']).read_bytes()
                assert data[slice(*record['bytes'])].decode() == record['text']
    save(output / 'RESULTS.json', result)
    contexts = json.loads((ROOT / 'CONTEXTS.json').read_text())
    resize = next(r for r in contexts['properties'] if r['property'] == 'resize')
    rejected = []
    for name in ['anchor', 'start-offset', 'trailing-span']:
        altered = copy.deepcopy(resize)
        if name == 'anchor':
            altered['anchor'] = 'missing-reviewed-anchor'
        elif name == 'start-offset':
            altered['value']['bytes'][0] += 1
        else:
            altered['value']['bytes'][1] += 1
        try:
            benchmark['adapted'](altered, contexts['productions'])
        except benchmark['ORIGINAL']['Refusal']:
            rejected.append(name)
        else:
            raise AssertionError('changed context accepted: ' + name)
    for text in ['none || both', 'none && both', 'none |', '[ none', 'none ]', 'none*', 'none{1,2}', '<<length [0,∞]>>']:
        try:
            benchmark['ORIGINAL']['Parser'](text, 0).parse()
        except benchmark['ORIGINAL']['Refusal']:
            rejected.append('grammar: ' + text)
        else:
            raise AssertionError('unsupported notation accepted')
    commands, audits = [], []
    with tempfile.TemporaryDirectory(prefix='css-grammar-transfer-') as directory:
        work = Path(directory)
        for module in MODULES:
            path = ROOT / (module + '.lean')
            if not path.exists():
                path = ROOT / 'preserved' / (module + '.lean')
            shutil.copyfile(path, work / (module + '.lean'))
            text = path.read_text()
            assert not re.search(r'\b(sorry|admit|axiom|unsafe|partial|native_decide)\b', text)
            audits += ['CssGrammar.' + n for n in re.findall(r'^theorem\s+([A-Za-z0-9_]+)', text, re.M)]

        def run(label, command, cwd=work, fail=False):
            out, err = output / (label + '.stdout'), output / (label + '.stderr')
            with out.open('wb') as stdout, err.open('wb') as stderr:
                completed = subprocess.run([str(x) for x in command], cwd=cwd,
                    env=dict(os.environ, LEAN_PATH=str(cwd)), stdout=stdout, stderr=stderr)
            commands.append(dict(label=label, command=[str(x) for x in command], exit=completed.returncode,
                stdout_sha256=sha(out), stderr_sha256=sha(err)))
            save(output / 'COMMANDS.json', commands)
            assert (completed.returncode != 0) if fail else (completed.returncode == 0), label
            return out.read_text(), err.read_text()

        for module in MODULES:
            out, err = run('compile-' + module, [lean, '-o', module + '.olean', module + '.lean'])
            assert not out and not err
        (work / 'Audit.lean').write_text('import Reference\n' + '\n'.join('#print axioms ' + name for name in audits) + '\n')
        out, err = run('audit', [lean, 'Audit.lean'])
        matched = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", out)
        assert not err and [name for name, _ in matched] == audits
        assert all({x.strip() for x in names.split(',') if x.strip()} <= {'propext', 'Quot.sound', 'Classical.choice'} for _, names in matched)
        save(output / 'AXIOMS.json', {name: names for name, names in matched})
        save(work / 'resize.json', generated['resize']['program'])
        shutil.copyfile(ROOT / 'cases.json', work / 'cases.json')
        out, _ = run('actual-file', [lean, '--run', 'Runner.lean', 'resize.json', 'cases.json'])
        assert [json.loads(line) for line in out.splitlines()] == json.loads((ROOT / 'expected.json').read_text())
        for name, kind, expected in [('invented-keyword', 'keyword', ['flex']), ('sequence-for-alternative', 'alt', ['none', 'both'])]:
            variant = work / name; variant.mkdir()
            for module in MODULES[:-2]:
                shutil.copyfile(work / (module + '.olean'), variant / (module + '.olean'))
            mutated = copy.deepcopy(generated['resize']['program'])
            if kind == 'keyword':
                index = mutated.index(['keyword', 'inline'])
                mutated[index] = ['keyword', 'flex']
            else:
                index = mutated.index(['alt'])
                mutated[index] = ['seq']
            (variant / 'Fixture.lean').write_text(benchmark['ORIGINAL']['quote_program'](mutated))
            shutil.copyfile(ROOT / 'Reference.lean', variant / 'Reference.lean')
            out, err = run(name + '-compile', [lean, '-o', 'Fixture.olean', 'Fixture.lean'], cwd=variant)
            assert not out and not err
            out, err = run(name + '-reference-rejects', [lean, 'Reference.lean'], cwd=variant, fail=True)
            assert 'error:' in out and not err
            witness = 'import Fixture\nopen CssGrammar\nexample : accepts ((decode extractedProgram).getD (.keyword "INVALID")) ' + json.dumps(expected) + ' = true := by decide\n'
            (variant / 'Witness.lean').write_text(witness)
            out, err = run(name + '-witness', [lean, 'Witness.lean'], cwd=variant)
            assert not out and not err
        for label, filename in [('wrong-source', 'inputs/css-ui-4.bs'), ('changed-original-parser', 'preserved/original-extract.py')]:
            variant = work / label; variant.mkdir()
            for name in ['benchmark.py', 'PROTOCOL.json', 'PROTOCOL.sha256', 'PRESERVED.json', 'SOURCES.json', 'CONTEXTS.json', 'ORIGINAL-RESULTS.json']:
                shutil.copyfile(ROOT / name, variant / name)
            for directory_name in ['inputs', 'preserved']:
                shutil.copytree(ROOT / directory_name, variant / directory_name)
            path = variant / filename; path.write_bytes(path.read_bytes() + b'\n')
            out, err = run(label, [sys.executable, '-I', 'benchmark.py', '--out', 'generated'], cwd=variant, fail=True)
            assert 'source or preserved input changed' in err and not (variant / 'generated').exists()
            rejected.append(label)
    save(output / 'CHECK.json', dict(status='PASS', modules=len(MODULES), axiom_audits=len(audits),
        benchmark_properties=8, css_modules=4, original_successes=0, selector_adapted_successes=4,
        grammar_parser_changed=False, resize_oracle_unchanged=True, resize_sequences=6,
        actual_file_rows=15, refusal_controls=rejected, compiling_data_mutants=2,
        temporary_compiled_output_removed=True, whole_property_conformance=False))


if __name__ == '__main__':
    main()
