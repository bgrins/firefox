from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGIN = '3d55e8e0d364b92dde0110553202aacbb0983dfb'
OLD = 'artifacts/css-keyframe-group-order-runtime-20261110-v1'
BASIS = '33b02650a474a0a4c2d9f6421283ba89f9a18b1c'
AUTHOR = ROOT / 'artifacts/css-named-range-group-order-candidate-20261110-v1'
NATIVE = 'servo/ports/geckolib/glue.rs'
MERGE = 'testing/web-platform/tests/scroll-animations/css/merge-timeline-offset-keyframes.html'
NEW = 'testing/web-platform/tests/scroll-animations/css/named-range-group-earliest-order.html'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git_file(revision, name, optional=False):
    r = subprocess.run(['git', '-c', 'core.fsmonitor=false', 'show', revision + ':' + name], cwd=ROOT, capture_output=True)
    if r.returncode:
        assert optional, (revision, name, r.stderr)
        return None
    return r.stdout


def put(name, data):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def save(name, value):
    put(name, (json.dumps(value, indent=2)+'\n').encode())


def main():
    assert not (HERE / 'RUN-INPUTS.json').exists(), 'Do not rewrite frozen runtime inputs'
    preserved = {}
    for name in ['bundle.py', 'process.py', 'analyze.py', 'parser-controls.py', 'run.py']:
        data = git_file(ORIGIN, OLD + '/' + name)
        put(name, data)
        preserved[name] = digest(data)
    old_run = (HERE / 'run.py').read_text()
    old_lint = "[PYTHON, './mach', 'lint', '--linter', 'wpt', 'testing/web-platform/tests/css/css-animations/KeyframeEffect-getKeyframes.tentative.html']"
    new_lint = "[PYTHON, './mach', 'lint', '--linter', 'wpt', *plan['lint_paths']]"
    assert old_run.count(old_lint) == 1
    run = old_run.replace(old_lint, new_lint)
    old_block = """        if mode == 'candidate':
            results['lint'] = process.run([PYTHON, './mach', 'lint', '--linter', 'wpt', *plan['lint_paths']], output / 'lint.log', env, 600)
            save(output / 'LINT.json', results['lint'])
            assert results['lint']['exit_code'] == 0, 'WPT lint failed'
"""
    new_block = """        results['lint'] = process.run([PYTHON, './mach', 'lint', '--linter', 'wpt', *plan['lint_paths']], output / 'lint.log', env, 600)
        save(output / 'LINT.json', results['lint'])
        assert results['lint']['exit_code'] == 0, 'WPT lint failed'
        if mode == 'candidate':
"""
    assert run.count(old_block) == 1
    run = run.replace(old_block, new_block)
    run = run.replace("    assert git('rev-parse', 'HEAD').decode().strip() == plan['head'], 'HEAD changed; review/re-pin'", "    assert isinstance(plan['head'], str) and len(plan['head']) == 40, 'Execution HEAD is not frozen'\n    assert git('rev-parse', 'HEAD').decode().strip() == plan['head'], 'HEAD changed; review/re-pin'")
    put('run.py', run.encode())
    put('WRAPPER-DIFF.patch', ''.join(difflib.unified_diff(old_run.splitlines(True), run.splitlines(True), fromfile='signed/run.py', tofile='range/run.py')).encode())
    controls = (HERE / 'parser-controls.py').read_text()
    old_controls = controls
    controls = controls.replace("    events = [{'action': 'suite_start'}]", "    expected_baseline = json.loads((HERE / 'EXPECTED-BASELINE.json').read_text())\n    baseline_statuses = {(r['test'], r['subtest']): r['status'] for r in expected_baseline['subtests']}\n    events = [{'action': 'suite_start'}]")
    controls = controls.replace("'status': 'FAIL' if (test, name) in improving else 'PASS'", "'status': baseline_statuses[(test, name)]")
    controls = controls.replace("if row['action'] == 'test_status':\n                row['status'] = 'PASS'", "if row['action'] == 'test_status' and (row['test'], row['subtest']) in improving:\n                row['status'] = 'PASS'")
    controls = controls.replace("        baseline = parse(events)\n", "        baseline = parse(events)\n        assert a.rows(baseline) == a.rows(expected_baseline)\n        wrong_baseline = copy.deepcopy(baseline)\n        next(r for r in wrong_baseline['subtests'] if r['status'] == 'FAIL' and (r['test'], r['subtest']) not in improving)['status'] = 'PASS'\n        assert a.rows(wrong_baseline) != a.rows(expected_baseline)\n        rejected.append('changed-known-baseline-failure')\n")
    put('parser-controls.py', controls.encode())
    put('PARSER-DIFF.patch', ''.join(difflib.unified_diff(old_controls.splitlines(True), controls.splitlines(True), fromfile='signed/parser-controls.py', tofile='range/parser-controls.py')).encode())
    patch = (AUTHOR / 'range-order.patch').read_bytes()
    assert digest(patch) == 'c0884212b8fb2d574395950c8e08abb754614809abe36983bd606accd61725cd'
    put('range-order.patch', patch)
    roles = {}
    for p in [NATIVE, MERGE]:
        before = git_file(BASIS, p)
        assert before == (AUTHOR / 'source' / p).read_bytes()
        after = (AUTHOR / 'candidate' / p).read_bytes()
        put('source/' + p, before)
        put('candidate/' + p, after)
        roles[p] = {'base':digest(before), 'candidate':digest(after), 'install_both': p == MERGE}
    save('SOURCE-ROLES.json', roles)
    fixture = (AUTHOR / 'candidate' / NEW).read_bytes()
    put('runtime-inputs/named-range-group-earliest-order.html', fixture)
    retained_origin = 'artifacts/css-keyframe-group-order-current-build-20261110-v1/build-result.json'
    retained = git_file(BASIS, retained_origin)
    put('runtime-inputs/retained-build.json', retained)
    old_plan = json.loads(git_file(ORIGIN, OLD + '/RUN-PLAN.json'))
    plan = dict(old_plan, head=None, native_basis='883d620fdbd6b66d4df871d660ee9612d1c20985',
                debug_gate='Optimized bounded named-range group-order comparison; debug unrun, separate missing-pseudo CSSOM debug gate remains open.',
                fixtures={NEW:'named-range-group-earliest-order.html'},
                suites=old_plan['suites']+[NEW], lint_paths=[MERGE, NEW])
    save('RUN-PLAN.json', plan)
    old_pins = json.loads(git_file(ORIGIN, OLD+'/runtime-inputs/test-source-pins.json'))
    pins = {}
    for p in list(old_pins) + [NEW, NEW.replace('/tests/', '/meta/', 1)+'.ini']:
        data = git_file(BASIS, p, optional=True)
        assert data is not None or p in [NEW, NEW.replace('/tests/', '/meta/', 1)+'.ini'] or old_pins[p] is None
        pins[p] = digest(data) if data is not None else None
    save('runtime-inputs/test-source-pins.json', pins)
    baseline_origin = OLD+'/candidate1/TEST-RESULTS.json'
    observed = json.loads(git_file(ORIGIN, baseline_origin))
    baseline = {field: [{k:r[k] for k in ['test','subtest','status'] if k in r} for r in observed[field]] for field in ['subtests','harness']}
    merge_url = '/'+MERGE.removeprefix('testing/web-platform/tests/')
    new_url = '/'+NEW.removeprefix('testing/web-platform/tests/')
    merge_name = 'Keyframes with same easing and timeline offset are merged.'
    row = next(r for r in baseline['subtests'] if r['test']==merge_url and r['subtest']==merge_name)
    assert row['status']=='PASS'
    row['status']='FAIL'
    changes = [{'kind':'assertion', 'test':merge_url, 'subtest':merge_name, 'baseline':'FAIL','candidate':'PASS'}]
    for key in ['unique-groups','repeated-group','repeated-groups']:
        name=key+': equal-offset named-range group order and declaration precedence'
        status='PASS' if key=='unique-groups' else 'FAIL'
        baseline['subtests'].append({'test':new_url,'subtest':name,'status':status})
        if status=='FAIL': changes.append({'kind':'assertion','test':new_url,'subtest':name,'baseline':'FAIL','candidate':'PASS'})
    baseline['harness'].append({'test':new_url,'status':'OK'})
    baseline['subtest_count']=len(baseline['subtests'])
    baseline['test_count']=len(baseline['harness'])
    assert baseline['subtest_count']==89 and baseline['test_count']==10
    assert Counter(r['status'] for r in baseline['subtests']) == {'PASS':77,'FAIL':12}
    callbacks=sorted([[r['test'],r['subtest']] for r in baseline['subtests']], key=repr)
    changes.sort(key=lambda r:repr((r['kind'],r['test'],r['subtest'])))
    save('EXPECTED-BASELINE.json',baseline)
    save('EXPECTED-CALLBACKS.json',callbacks)
    save('EXPECTED-CHANGES.json',changes)
    save('ORIGINS.json',{'signed_origin':ORIGIN,'origin_directory':OLD,'origin_hashes':preserved,
                         'source_test_pin_revision':BASIS,'candidate_patch_sha256':digest(patch),
                         'fixture_sha256':digest(fixture),'retained_build_origin':retained_origin,
                         'retained_build_sha256':digest(retained),'baseline_result_origin':baseline_origin,
                         'baseline_result_sha256':digest(git_file(ORIGIN,baseline_origin)),
                         'expected_status_derivation':'prior accepted candidate status vector, corrected merge first callback predicted FAIL, new unique PASS and repeated/repeated-pair FAIL; actual baseline must match exactly'})
    print('Prepared, execution HEAD and RUN-INPUTS deliberately unfrozen.')


if __name__ == '__main__':
    main()
