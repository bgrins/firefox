import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
import bridge
import fixtures
import lean_cases

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(command, directory, name, stdin=None, env=None, timeout=180):
    timed_out = False
    try:
        result = subprocess.run([str(x) for x in command], input=stdin, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as error:
        timed_out = True
        decode = lambda value: value.decode() if isinstance(value, bytes) else value or ''
        result = subprocess.CompletedProcess(command, 124, decode(error.stdout), decode(error.stderr))
    (directory / (name + '.stdout')).write_text(result.stdout)
    (directory / (name + '.stderr')).write_text(result.stderr)
    (directory / (name + '.json')).write_text(json.dumps(dict(command=list(map(str, command)),
        exit_code=result.returncode, timed_out=timed_out, timeout_seconds=timeout,
        stdout_sha256=sha(directory / (name + '.stdout')),
        stderr_sha256=sha(directory / (name + '.stderr'))), indent=2)+'\n')
    return result


def mismatches(output, cases, repaired):
    rows = [json.loads(line) for line in output.splitlines()]
    if len(rows) != len(cases):
        return [{'kind': 'row-count', 'actual': len(rows), 'expected': len(cases)}]
    errors = []
    for case, row in zip(cases, rows):
        assert case['id'] == row['id']
        difference = fixtures.discrepancies(case, row, repaired)
        if difference:
            errors.append(dict(id=case['id'], errors=difference))
    return errors


def main(out, mutations):
    out.mkdir(parents=True, exist_ok=False)
    inputs_file = ROOT / 'REPLAY-INPUTS-v1.json'
    input_hashes = None
    if inputs_file.exists():
        input_hashes = json.loads(inputs_file.read_text())
        for path, digest in input_hashes.items():
            assert sha(ROOT / path) == digest, path
    tool = json.loads((ROOT / 'TOOLCHAIN-v1.json').read_text())
    for name in ['lean', 'compiler']:
        assert sha(Path(tool[name])) == tool[name + '_sha256']
    assert sha(Path(tool['sdk']) / 'SDKSettings.json') == tool['sdk_settings_sha256']
    compiler = [tool['compiler'], '-isysroot', tool['sdk'], '-std=c++20', '-O1', '-g',
                '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter']
    undefined = ['-fsanitize=undefined', '-fno-sanitize-recover=all']
    address = ['-fsanitize=address,undefined', '-fsanitize-address-use-after-scope',
               '-fno-omit-frame-pointer', '-fno-sanitize-recover=all']
    cases = fixtures.corpus()
    wire = '\n'.join(fixtures.wire(case) for case in cases) + '\n'
    (out / 'inputs.txt').write_text(wire)
    native = {}
    for candidate in [False, True]:
        name = 'candidate' if candidate else 'original'
        source = out / (name + '.cpp'); source.write_text(bridge.generate(candidate))
        binary = out / name
        result = execute(compiler + undefined + [source, '-o', binary], out, name + '-compile')
        assert result.returncode == 0, result.stderr[:3000]
        result = execute([binary], out, name + '-run', wire)
        assert result.returncode == 0, result.stderr[:3000]
        errors = mismatches(result.stdout, cases, candidate)
        (out / (name + '-differences.json')).write_text(json.dumps(errors, indent=2)+'\n')
        assert not errors, errors[:3]
        native[name] = dict(exit_code=0, cases=len(cases), discrepancies=0)
    original_vs_spec = mismatches((out / 'original-run.stdout').read_text(), cases, True)
    (out / 'original-vs-spec.json').write_text(json.dumps(original_vs_spec, indent=2)+'\n')
    assert original_vs_spec

    lean_env = os.environ.copy(); lean_env['LEAN_PATH'] = str(out)
    theorem_count = 0
    for name in ['Mask', 'Image']:
        model = (ROOT / (name + '.lean')).read_text()
        assert not re.search(r'\b(sorry|axiom|admit|unsafe)\b', model)
        source = out / (name + '.lean'); source.write_text(model)
        result = execute([tool['lean'], '-o', out / (name + '.olean'), source], out,
                         name + '-lean', env=lean_env)
        assert result.returncode == 0, result.stdout[:3000]
        names = re.findall(r'^theorem (\w+)', model, re.M)
        theorem_count += len(names)
        audit = out / (name + '-Audit.lean')
        audit.write_text('import ' + name + '\n' + '\n'.join('#print axioms '+name+'.'+n for n in names)+'\n')
        result = execute([tool['lean'], audit], out, name + '-audit', env=lean_env)
        assert result.returncode == 0
        assert len(re.findall("'"+name+r'\.', result.stdout)) == len(names)
        assert 'sorryAx' not in result.stdout and 'Lean.ofReduceBool' not in result.stdout
        for axioms in re.findall(r'depends on axioms: \[(.*?)\]', result.stdout):
            assert set(axioms.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}
    lean_source = out / 'Cases.lean'; lean_source.write_text(lean_cases.generate(cases))
    result = execute([tool['lean'], lean_source], out, 'lean-cases', env=lean_env)
    assert result.returncode == 0, result.stdout[:3000]
    lines = result.stdout.splitlines(); assert len(lines) == len(cases)
    for case, line in zip(cases, lines):
        index, value = line.split(' ', 1)
        assert int(index) == case['id']
        assert Fraction(value) == fixtures.oracle(case)['alpha'], (index, value)

    diagnostic = out / 'asan-startup.cpp'; diagnostic.write_text('int main(){return 0;}\n')
    result = execute(compiler + address + [diagnostic, '-o', out / 'asan-startup'], out, 'asan-startup-compile')
    assert result.returncode == 0
    result = execute([out / 'asan-startup'], out, 'asan-startup-run', timeout=8)
    asan_available = result.returncode == 0
    assert asan_available or result.returncode == 124, result.stderr[:2000]
    sanitizer = {'startup': 'available' if asan_available else 'empty program timed out without output'}
    for name in ['original', 'candidate']:
        binary = out / (name + '-asan')
        result = execute(compiler + address + [out / (name + '.cpp'), '-o', binary], out, name + '-asan-compile')
        assert result.returncode == 0, result.stderr[:3000]
        if asan_available:
            result = execute([binary], out, name + '-asan-run', wire, timeout=20)
            assert result.returncode == 0, 'ASan execution failed: ' + result.stderr[:2000]
            assert not mismatches(result.stdout, cases, name == 'candidate')
            sanitizer[name] = dict(exit_code=0, cases=len(cases))
        else:
            sanitizer[name] = dict(compile_exit=0, execution='not claimed; ASan startup unavailable')
    lifetime = ROOT / 'lifetime-control.cpp'
    result = execute(compiler + undefined + [lifetime, '-o', out / 'lifetime-good'], out, 'lifetime-good-compile')
    assert result.returncode == 0
    result = execute([out / 'lifetime-good'], out, 'lifetime-good-run')
    assert result.returncode == 0 and result.stdout == '17\n'
    result = execute(compiler + ['-DDANGLING', lifetime, '-o', out / 'lifetime-diagnostic'], out, 'lifetime-diagnostic')
    assert result.returncode != 0 and 'dangling' in result.stderr
    result = execute(compiler + address + ['-DDANGLING', '-Wno-error=dangling', lifetime, '-o', out / 'lifetime-bad'], out, 'lifetime-bad-compile')
    assert result.returncode == 0
    if asan_available:
        result = execute([out / 'lifetime-bad'], out, 'lifetime-bad-run', timeout=20)
        assert result.returncode != 0 and 'stack-use-after-scope' in result.stderr

    mutation_results = []
    diagnostic_results = []
    if mutations:
        source = bridge.generate(True)
        changes = [
            ('omit-ready', 'paintMask && state.mImageRenderer.IsReady()', 'paintMask'),
            ('omit-mask', 'paintMask && state.mImageRenderer.IsReady()', 'state.mImageRenderer.IsReady()'),
            ('clear-all-ops', 'co == CompositionOp::OP_IN || co == CompositionOp::OP_OUT', 'true'),
            ('skip-in', 'co == CompositionOp::OP_IN || co == CompositionOp::OP_OUT', 'co == CompositionOp::OP_OUT'),
            ('skip-out', 'co == CompositionOp::OP_IN || co == CompositionOp::OP_OUT', 'co == CompositionOp::OP_IN'),
            ('dirty-is-fill', 'currentLayerClipState.mDirtyRectInDevPx.IsEmpty()', 'state.mFillArea.IsEmpty()'),
            ('bottom-override', 'aLayerIndex == (aLayers.mImageCount - 1)', 'false'),
            ('origin-loss', 'dt->ClearRect(Rect(dt->GetRect()));', 'dt->ClearRect(Rect(0, 0, dt->GetRect().width, dt->GetRect().height));'),
            ('restore-loss', 'dt->SetTransform(transform);', '(void)transform;'),
            ('identity-loss', 'dt->SetTransform(Matrix());', '(void)0;'),
            ('stop-upper', 'dt->SetTransform(transform);', 'dt->SetTransform(transform); break;'),
            ('aggregation-loss', 'result &= state.mImageRenderer.PrepareResult();', 'result = ImgDrawResult::SUCCESS;'),
        ]
        for name, old, new in changes:
            assert source.count(old) == 1, name
            mutation = out / ('mutation-' + name + '.cpp'); mutation.write_text(source.replace(old, new))
            binary = out / ('mutation-' + name)
            result = execute(compiler + undefined + ['-Wno-unused-variable', mutation, '-o', binary], out, 'mutation-' + name + '-compile')
            assert result.returncode == 0, (name, result.stderr[:3000])
            result = execute([binary], out, 'mutation-' + name + '-run', wire)
            if result.returncode:
                expected_assertion = {'origin-loss': 'value.IsEqualEdges(rect)',
                                      'identity-loss': 'transform==Matrix()'}
                assert name in expected_assertion and expected_assertion[name] in result.stderr, (name, result.stderr[:1000])
                kind, errors = 'native-state-assertion', []
            else:
                assert len(result.stdout.splitlines()) == len(cases), (name, 'invalid/incomplete mutant execution')
                errors = mismatches(result.stdout, cases, True)
                assert errors, name
                kind = 'oracle-mismatch'
            (out / ('mutation-' + name + '-differences.json')).write_text(json.dumps(errors, indent=2)+'\n')
            mutation_results.append(dict(name=name, compile_exit=0, execution_exit=result.returncode,
                                         rejection=kind, discrepancies=len(errors)))
        bad_model = (ROOT / 'Image.lean').read_text().replace('if clear i then 0 else oldStep i d', 'oldStep i d')
        path = out / 'Mutation-Image.lean'; path.write_text(bad_model)
        result = execute([tool['lean'], path], out, 'lean-semantic-mutation', env=lean_env)
        assert result.returncode != 0 and 'unsolved goals' in result.stdout
        diagnostic_results.append(dict(name='Lean changed dispatch', rejection='theorem failure'))
        missing = out / 'diagnostic-missing-api.cpp'
        missing.write_text(source.replace('void SetTransform(Matrix value)', 'void MissingSetTransform(Matrix value)'))
        result = execute(compiler + [missing, '-o', out / 'diagnostic-missing-api'], out, 'diagnostic-missing-api')
        assert result.returncode != 0 and 'SetTransform' in result.stderr
        diagnostic_results.append(dict(name='missing adapter API', rejection='compile failure; not semantic mutation'))
        drift = out / 'diagnostic-source-drift'; drift.mkdir()
        entries = json.loads((ROOT / 'SOURCE-v1.json').read_text())
        (drift / 'SOURCE-v1.json').write_text(json.dumps(entries))
        first = drift / entries[0]['copy']; first.parent.mkdir(parents=True)
        first.write_bytes((ROOT / entries[0]['copy']).read_bytes() + b'\n')
        saved = bridge.ROOT
        bridge.ROOT = drift
        rejected = False
        try:
            bridge.generate()
        except AssertionError:
            rejected = True
        finally:
            bridge.ROOT = saved
        assert rejected
        diagnostic_results.append(dict(name='source drift', rejection='hash authentication'))
        for token in ['sorry', 'axiom', 'admit', 'unsafe']:
            assert re.search(r'\b(sorry|axiom|admit|unsafe)\b', 'theorem bad : True := ' + token)
            diagnostic_results.append(dict(name=token, rejection='prohibited model token'))
    if input_hashes is not None:
        assert json.loads(inputs_file.read_text()) == input_hashes
        for path, digest in input_hashes.items():
            assert sha(ROOT / path) == digest, ('input changed during replay', path)
    summary = dict(status='PASS' if asan_available else 'PASS_WITH_ASAN_STARTUP_LIMITATION',
        native=native, original_vs_spec=len(original_vs_spec),
        lean_theorems=theorem_count, lean_cases=len(cases), sanitizer=sanitizer,
        lifetime_negative_control=('stack-use-after-scope detected' if asan_available else
            'Clang lifetimebound dangling diagnostic; runtime ASan control not executed'),
        mutations=mutation_results, diagnostics=diagnostic_results)
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--skip-mutations', action='store_true')
    args = parser.parse_args()
    main(Path(args.out).resolve(), not args.skip_mutations)
