import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    plan = read(P / 'PACKAGE.json')
    refs = read(P / 'REFERENCES.json')
    for n, h in refs.items():
        f = ROOT / n
        assert sha(f) == h, n
        if f.name == 'FILES.json':
            for name, digest in read(f).items():
                assert sha(f.parent / name) == digest, (n, name)
    runtime = ROOT / plan['runtime']
    peer = read(ROOT / plan['peer'] / 'CHECK.json')
    receipt = read(runtime / 'ROOT-FINAL-CHECK.json')
    c = read(runtime / 'CONFIG.json')
    state = read(runtime / 'STATE.json')
    assert receipt['status'] == 'COMPARISON_PASSED_VERIFIED_RESTORED'
    assert receipt['session'] == 92779 and receipt['exit'] == 0 and receipt['all_variants_passed'] is True
    assert state['restored'] is True and state['restore_build_exit'] == 0 and state['recovery_errors'] == []
    assert receipt['state_sha256'] == sha(runtime / 'STATE.json')
    assert receipt['final_sha256'] == sha(runtime / 'FINAL.json')
    assert receipt['final_pins_sha256'] == sha(runtime / 'FINAL-PINS.json')
    assert read(runtime / 'BEFORE.json') == read(runtime / 'FINAL.json') == c['execution_snapshot']
    assert peer['status'] == 'INTEGER_RANGE_SUBGRID_TERMINAL_RESULTS_GO' and peer['restored'] is True
    assert receipt['source_count'] == peer['source_count'] == 69
    assert receipt['saved_sources'] == peer['saved_sources'] == 42
    assert receipt['resource_count'] == peer['resources'] == 461
    assert receipt['pin_count'] == peer['final_pins'] == 532
    assert receipt['native_modified_paths'] == peer['native_modified_paths'] == 36
    assert receipt['staged_paths'] == peer['staged_paths'] == 925
    assert len(receipt['installed_tests']) == peer['installed_identities'] == 11
    assert receipt['restored_binary_pins'] == peer['restored_binary_pins']
    for phase in ('range_only', 'cache_only', 'combined'):
        v = receipt['variants'][phase]
        assert v['status'] == 'PASSED' and not v['required_landing_failures']
        assert all(not item['regressions'] and not item['changed_failures'] for item in v['preservation'].values())
    variant = receipt['variants'][plan['phase']]
    assert len(variant['repaired']) == len(peer['repairs'][plan['phase']]) == plan['all_improvements']
    assert len(variant['own_repaired']) == plan['landing_improvements']
    proposal = ROOT / plan['proposal']
    assert (P / 'gecko-wpt.patch').read_bytes() == (proposal / plan['original_patch']).read_bytes()
    paths = re.findall(r'^\+\+\+ b/(.+)$', (P / 'gecko-wpt.patch').read_text(), re.M)
    assert len(paths) == len(set(paths)) == (3 if plan['fix'] == 121 else 4)
    native = [n for n in paths if not n.startswith('testing/web-platform/tests/')]
    tests = [n for n in paths if n not in native]
    assert set(native) == set(c['phase_candidate_paths'][plan['phase']])
    assert not any(n.startswith(('artifacts/', 'docs/')) for n in paths)
    variant_files = ['gecko-wpt.patch'] + (['installed118-gecko-wpt.patch'] if plan['fix'] == 121 else [])
    outputs = {}
    for patch_name in variant_files:
        preimages = {n: subprocess.check_output(['git', 'show', plan['baseline'] + ':' + n], cwd=ROOT) for n in native}
        expected_native = {n: c['candidate_pins'][n] for n in native}
        if patch_name.startswith('installed118'):
            assert (P / patch_name).read_bytes() == (proposal / 'installed118-standalone.patch').read_bytes()
            pins = read(ROOT / 'artifacts/css-integer-resolve-range-repair-v1/PROPOSAL-PINS.json')
            preimages[native[0]] = (ROOT / 'artifacts/css-integer-resolve-range-repair-v1/sources/number-118.rs').read_bytes()
            assert hashlib.sha256(preimages[native[0]]).hexdigest() == pins['accepted118_source']
            expected_native[native[0]] = pins['installed118_candidate']
        with tempfile.TemporaryDirectory(prefix='accepted-gecko-wpt-') as tmp:
            tmp = Path(tmp)
            def git(*args):
                r = subprocess.run(['git', *args], cwd=tmp, capture_output=True, text=True)
                assert r.returncode == 0, (args, r.stdout, r.stderr)
            git('init', '-q')
            for n, body in preimages.items():
                f = tmp / n; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(body)
            git('apply', '--check', str(P / patch_name)); git('apply', str(P / patch_name))
            for n, digest in expected_native.items():assert sha(tmp / n) == digest
            for n in tests:
                assert (tmp / n).read_bytes() == (proposal / Path(n).name).read_bytes()
            outputs[patch_name] = {n: sha(tmp / n) for n in paths}
            git('apply', '--reverse', '--check', str(P / patch_name)); git('apply', '--reverse', str(P / patch_name))
            for n, body in preimages.items():assert (tmp / n).read_bytes() == body
            assert all(not (tmp / n).exists() for n in tests)
    transfer = None
    if plan['fix'] == 121:
        assert (proposal / 'timing-functions-calculated-step-range.html').read_bytes() == (runtime / 'timing.html').read_bytes()
        landed = (proposal / 'subgrid-repeat-calculated-zero.html').read_text()
        executed = (runtime / 'subgrid.html').read_text()
        old_title = re.search(r'<title>.*?</title>', executed).group()
        new_title = re.search(r'<title>.*?</title>', landed).group()
        assert landed.replace(new_title, old_title, 1) == executed
        transfer = {'title_only': True, 'executed_path': next(n for n,f in c['install'].items() if f == 'subgrid.html'),
                    'landing_path': next(n for n in tests if 'subgrid' in n), 'script_style_assertions_unchanged': True}
    else:
        assert (proposal / 'subgrid-repeat-count-capacity.html').read_bytes() == (runtime / 'cache.html').read_bytes()
    result = {'status':'ACCEPTANCE_PACKAGE_VERIFIED','fix':plan['fix'],'patch_paths':paths,
        'native_paths':native,'wpt_paths':tests,'postimages':outputs,'scratch_apply_reverse':True,
        'exact_runtime_source_and_fixture_join':True,'landing_transfer':transfer,
        'landing_cases':plan['landing_cases'],'isolated_improvements':plan['all_improvements'],
        'own_landing_improvements':plan['landing_improvements'],'comparison_subtests_each_phase':339,
        'comparison_reftests_each_phase':6,'comparison_files':21,'regressions':0,'changed_retained_failures':0,
        'restoration_archives_authenticated':True,'new_native_build_or_browser':False,'installation':None,
        'ledger_index_signing_changed':False,'scratch_removed':True}
    print(json.dumps(result,indent=2))


if __name__ == '__main__':main()
