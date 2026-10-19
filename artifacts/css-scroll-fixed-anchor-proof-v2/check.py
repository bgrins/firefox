import argparse
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
import lean_mutations
import extension_check

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(argv, out, name, stdin=None, env=None, timeout=180):
    try:
        p = subprocess.run(list(map(str, argv)), input=stdin, capture_output=True, text=True,
                           env=env, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        def decode(s):
            return s.decode() if isinstance(s, bytes) else s or ''
        p = subprocess.CompletedProcess(argv, 124, decode(error.stdout), decode(error.stderr))
        timed_out = True
    else:
        timed_out = False
    (out / (name + '.stdout')).write_text(p.stdout)
    (out / (name + '.stderr')).write_text(p.stderr)
    (out / (name + '.json')).write_text(json.dumps(dict(argv=list(map(str, argv)),
        exit_code=p.returncode, timed_out=timed_out, timeout_seconds=timeout,
        stdout_sha256=sha(out / (name + '.stdout')), stderr_sha256=sha(out / (name + '.stderr')),
        stdin_sha256=hashlib.sha256(stdin.encode()).hexdigest() if stdin is not None else None), indent=2)+'\n')
    return p


def differences(output, cases, repaired):
    rows = output.splitlines()
    assert len(rows) == len(cases), ('row count', len(rows), len(cases))
    bad = []
    for c, line in zip(cases, rows):
        values, events = line.split('|')
        actual = dict(values=list(map(int, values.split())),
                      events=events.rstrip(';').split(';') if events else [])
        assert actual['values'][0] == c['id']
        expected = fixtures.oracle(c, repaired)
        if actual != expected:
            bad.append(dict(id=c['id'], name=c['name'], value_difference=actual['values'] != expected['values'],
                            actual=actual, expected=expected))
    return bad


def safe_model(source):
    assert not re.search(r'\b(sorry|admit|axiom|unsafe)\b', source), 'prohibited proof construct'


def main(out, skip_mutations=False):
    out.mkdir(parents=True, exist_ok=False)
    pins = json.loads((ROOT / 'REPLAY-INPUTS-v1.json').read_text())
    def verify_pins():
        assert json.loads((ROOT / 'REPLAY-INPUTS-v1.json').read_text()) == pins
        for path, digest in pins.items():
            assert sha(ROOT / path) == digest, path
    verify_pins()
    tool = json.loads((ROOT / 'TOOLCHAIN-v1.json').read_text())
    for key in ['compiler', 'lean']:
        assert sha(Path(tool[key])) == tool[key + '_sha256']
    assert str(Path(tool['compiler']).resolve()) == tool['compiler_realpath']
    assert sha(Path(tool['sdk']) / 'SDKSettings.json') == tool['sdk_settings_sha256']
    for name in ['compiler', 'lean']:
        p = execute([tool[name], '--version'], out, name + '-version')
        assert p.returncode == 0 and p.stdout == tool[name + '_version']
    compiler = [tool['compiler'], '-isysroot', tool['sdk'], '-std=c++20', '-O1', '-g',
                '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
                '-fsanitize=undefined,implicit-integer-truncation', '-fno-sanitize-recover=all']
    cases = fixtures.corpus()
    wire = '\n'.join(fixtures.wire(c) for c in cases) + '\n'
    (out / 'cases.json').write_text(json.dumps(cases, indent=2)+'\n')
    (out / 'inputs.txt').write_text(wire)
    (out / 'EXTRACTION-v1.json').write_text(json.dumps(bridge.extraction_map(), indent=2)+'\n')
    for repaired in [False, True]:
        name = 'candidate' if repaired else 'original'
        source = out / (name + '.cpp'); source.write_text(bridge.generate(repaired))
        p = execute(compiler + [source, '-o', out / name], out, name + '-compile')
        assert p.returncode == 0, p.stderr[:3000]
        p = execute([out / name], out, name + '-run', wire)
        assert p.returncode == 0, p.stderr[:3000]
        bad = differences(p.stdout, cases, repaired)
        (out / (name + '-differences.json')).write_text(json.dumps(bad, indent=2)+'\n')
        assert not bad, bad[:2]
    before = differences((out / 'original-run.stdout').read_text(), cases, True)
    (out / 'original-vs-candidate.json').write_text(json.dumps(before, indent=2)+'\n')
    assert any(x['value_difference'] for x in before)
    source = (ROOT / 'Anchor.lean').read_text(); safe_model(source)
    model = out / 'Anchor.lean'; model.write_text(source)
    env = os.environ.copy(); env['LEAN_PATH'] = str(out)
    p = execute([tool['lean'], '-o', out / 'Anchor.olean', model], out, 'lean-model', env=env)
    assert p.returncode == 0, p.stdout[:5000]
    names = re.findall(r'^theorem (\w+)', source, re.M)
    audit = out / 'Audit.lean'; audit.write_text('import Anchor\n' + '\n'.join('#print axioms Anchor.'+n for n in names)+'\n')
    p = execute([tool['lean'], audit], out, 'lean-axioms', env=env)
    assert p.returncode == 0 and len(re.findall("'Anchor\\.", p.stdout)) == len(names)
    assert 'sorryAx' not in p.stdout and 'Lean.ofReduceBool' not in p.stdout
    for axioms in re.findall(r'depends on axioms: \[(.*?)\]', p.stdout):
        assert set(axioms.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}
    export = out / 'Cases.lean'; export.write_text(lean_cases.generate(cases))
    p = execute([tool['lean'], export], out, 'lean-cases', env=env)
    assert p.returncode == 0, p.stdout[:5000]
    lines = p.stdout.splitlines(); assert len(lines) == len(cases)
    for c, row in zip(cases, lines):
        fields = row.split(' '); assert len(fields) == 5
        expected = [str(c['id'])]
        old, new = fixtures.oracle(c, False), fixtures.oracle(c, True)
        expected += [str(old['values'][1]), str(new['values'][1])]
        expected += [','.join(e[1:] for e in o['events'] if e.startswith('E')) for o in [old, new]]
        assert fields == expected, (c['id'], fields, expected)
    semantic = []; lean_mutants = []; diagnostics = []
    if not skip_mutations:
        native = bridge.generate(True)
        fixed_block = '''if (disp->mPosition == StylePositionProperty::Fixed ||
      aFrame->IsStickyPositioned()) {
    ANCHOR_LOG("\\t\\tExcluding fixed or sticky positioning.\\n");
    return ExamineResult::Exclude;
  }'''
        changes = [
            ('remove-fixed', 'disp->mPosition == StylePositionProperty::Fixed ||', 'false ||'),
            ('exclude-absolute', 'disp->mPosition == StylePositionProperty::Fixed ||',
             'disp->mPosition == StylePositionProperty::Absolute || disp->mPosition == StylePositionProperty::Fixed ||'),
            ('remove-sticky', 'aFrame->IsStickyPositioned()', 'false'),
            ('fixed-pass-through', fixed_block, fixed_block.replace('ExamineResult::Exclude', 'ExamineResult::PassThrough')),
            ('reject-local-placeholder', 'if (!nsLayoutUtils::IsProperAncestorFrame(Frame(), realFrame))',
             'if (true || !nsLayoutUtils::IsProperAncestorFrame(Frame(), realFrame))'),
            ('examine-placeholder', 'child = realFrame;', '(void)realFrame;'),
            ('omit-absolute-pass', 'if (nsIFrame* anchor = FindAnchorInList(absPosList))', 'if (nsIFrame* anchor = nullptr)'),
            ('traverse-before-child', 'case ExamineResult::Traverse: {', 'case ExamineResult::Traverse: { return child;'),
            ('pass-returns-self', 'case ExamineResult::PassThrough: {', 'case ExamineResult::PassThrough: { return child;'),
            ('continue-after-accept', 'case ExamineResult::Accept: {\n        return child;', 'case ExamineResult::Accept: {\n        continue;'),
            ('bypass-maintenance', 'if (CanMaintainAnchor()) {', 'if (true) {'),
            ('flags-not-cleared', 'SetAnchorFlags(Frame()->mScrolledFrame, oldAnchor, false);',
             'SetAnchorFlags(Frame()->mScrolledFrame, oldAnchor, true);'),
        ]
        for name, old, new in changes:
            assert native.count(old) == 1, (name, native.count(old))
            file = out / (name + '.cpp'); file.write_text(native.replace(old, new))
            p = execute(compiler + ['-Wno-unused-variable', file, '-o', out / name], out, name + '-compile')
            assert p.returncode == 0, (name, p.stderr[:3000])
            p = execute([out / name], out, name + '-run', wire)
            assert p.returncode == 0, (name, p.stderr[:2000])
            bad = differences(p.stdout, cases, True)
            values = [e for e in bad if e['value_difference']]
            assert values, (name, 'no semantic/state mismatch')
            (out / (name + '-differences.json')).write_text(json.dumps(bad, indent=2)+'\n')
            semantic.append(dict(name=name, input_count=len(cases), differences=len(bad),
                                 value_differences=len(values), first_witness=values[0]['id'],
                                 witness_name=values[0]['name'], compile_exit=0, run_exit=0))
        for name, old, new in lean_mutations.CHANGES:
            assert old in source
            changed = source.replace(old, new, 1)
            file = out / ('mutation-' + name + '.lean'); file.write_text(changed)
            p = execute([tool['lean'], file], out, 'mutation-' + name, env=env)
            assert p.returncode == 1 and ('unsolved goals' in p.stdout or 'failed' in p.stdout or 'mismatch' in p.stdout), (name, p.stdout[:1000])
            witness, expected, mutated_expected, explanation = lean_mutations.WITNESSES[name]
            receipts = []
            for variant, body, wanted in [('reference', source, expected), ('changed', changed, mutated_expected)]:
                executable = out / ('witness-' + name + '-' + variant + '.lean')
                executable.write_text(lean_mutations.executable(body, name))
                run = execute([tool['lean'], executable], out, 'witness-' + name + '-' + variant, env=env)
                assert run.returncode == 0 and run.stdout == wanted, (name, variant, run.stdout, run.stderr)
                receipts.append(dict(variant=variant, exit_code=run.returncode, stdout=run.stdout))
            assert expected != mutated_expected
            lean_mutants.append(dict(name=name, witness=witness, explanation=explanation,
                                     proof_failure_exit=p.returncode, executions=receipts))
        broken = out / 'diagnostic-api.cpp'; broken.write_text(native.replace('bool IsStickyPositioned() const', 'bool MissingStickyAPI() const'))
        p = execute(compiler + [broken, '-o', out / 'diagnostic-api'], out, 'diagnostic-api')
        assert p.returncode != 0 and 'IsStickyPositioned' in p.stderr
        diagnostics.append('missing provider API compile rejection; not semantic evidence')
        invalid = out / 'diagnostic-external-anchor.cpp'
        invalid.write_text(native.replace('if (!nsLayoutUtils::IsProperAncestorFrame(Frame(), realFrame))',
                                         'if (false && !nsLayoutUtils::IsProperAncestorFrame(Frame(), realFrame))'))
        p = execute(compiler + [invalid, '-o', out / 'diagnostic-external-anchor'], out, 'diagnostic-external-anchor-compile')
        assert p.returncode == 0, p.stderr[:2000]
        p = execute([out / 'diagnostic-external-anchor'], out, 'diagnostic-external-anchor-run', wire)
        assert p.returncode != 0 and 'Assertion failed: (frame)' in p.stderr and 'function SetAnchorFlags' in p.stderr
        diagnostics.append('removed ancestor guard violates SetAnchorFlags invariant; assertion diagnostic, incomplete corpus not semantic evidence')
        for token in ['sorry', 'axiom', 'admit', 'unsafe']:
            try:
                safe_model(source + '\n' + token)
            except AssertionError:
                diagnostics.append('prohibited ' + token)
            else:
                raise AssertionError(token)
        malformed = fixtures.base(); malformed['frames'][1]['lists'] = [(0, [1])]
        try:
            fixtures.validate(malformed)
        except AssertionError as e:
            assert 'cycle' in str(e)
            diagnostics.append('cyclic provider graph rejected before native execution')
        else:
            raise AssertionError('cycle validation')
        shadow = out / 'diagnostic-source-drift'; shadow.mkdir()
        shutil.copyfile(ROOT / 'SOURCE-v1.json', shadow / 'SOURCE-v1.json')
        shutil.copytree(ROOT / 'source', shadow / 'source')
        changed = shadow / 'source/candidate.cpp'; changed.write_text(changed.read_text() + '\n')
        saved = bridge.ROOT
        bridge.ROOT = shadow
        try:
            bridge.extract()
        except AssertionError as e:
            assert 'candidate.cpp' in str(e)
            diagnostics.append('source identity drift rejected before extraction')
        else:
            raise AssertionError('source drift accepted')
        finally:
            bridge.ROOT = saved
    extension_result = None
    if not skip_mutations:
        extension_result = extension_check.run(out / 'extension-v1', tool, compiler, execute, safe_model, semantic)
    verify_pins()
    result = dict(status='PASS' if not skip_mutations else 'PREFLIGHT_NO_MUTATIONS',
        native_cases_per_variant=len(cases), direct_classifier_cases=sum(c['mode'] == 1 for c in cases),
        public_selection_cases=sum(c['mode'] == 0 for c in cases),
        original_vs_candidate_differences=len(before),
        original_vs_candidate_value_differences=sum(e['value_difference'] for e in before),
        extracted_items_per_variant=8, lean_theorems=len(names), lean_evaluations=len(cases),
        native_semantic_mutations=semantic, lean_semantic_mutations=lean_mutants,
        required_interpreter_extension=extension_result,
        diagnostics=diagnostics, sanitizers='UBSan and implicit integer truncation; no ASan execution claimed',
        replay_inputs=len(pins), replay_input_manifest_sha256=sha(ROOT / 'REPLAY-INPUTS-v1.json'))
    (out / 'SUMMARY.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); p.add_argument('--skip-mutations', action='store_true')
    args = p.parse_args(); main(Path(args.out).resolve(), args.skip_mutations)
