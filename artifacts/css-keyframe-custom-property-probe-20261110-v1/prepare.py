import difflib
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ORIGIN='3f8f7324c20de730eddcf07b224dd93e9be6694d'
OLD='artifacts/css-pseudo-animation-owned-generation-runtime-20261110-v1'
FIXTURE='testing/web-platform/tests/css/css-animations/custom-keyframe-value-observations.html'
PROPOSAL='artifacts/css-keyframe-custom-property-contract-20261110-v1/proposal/custom-keyframe-value-observations.html'


def git_file(rev,path,optional=False):
    r=subprocess.run(['git','-c','core.fsmonitor=false','show',rev+':'+path],cwd=ROOT,capture_output=True)
    if r.returncode:
        assert optional,(path,r.stderr)
        return None
    return r.stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2)+'\n')


def main():
    assert not (HERE/'RUN-INPUTS.json').exists()
    origin_hashes={}
    for name in ['run.py','bundle.py','process.py','analyze.py','freeze.py']:
        data=git_file(ORIGIN,OLD+'/'+name)
        (HERE/name).write_bytes(data);origin_hashes[name]=sha(data)
    old=(HERE/'run.py').read_text();run=old
    run=run.replace("bundle, process, analyze = module('bundle'), module('process'), module('analyze')", "bundle, process, analyze, observe = module('bundle'), module('process'), module('analyze'), module('observe')")
    run=run.replace("assert mode in ['baseline', 'candidate'] and len(prior) == (mode == 'candidate')", "assert mode == 'baseline' and not prior, 'This diagnostic is baseline-only'")
    start=run.index('    for path, role in roles.items():')
    end=run.index('    retained = ',start)
    run=run[:start]+'    assert roles == {}, \'No native or tracked-test roles permitted\'\n'+run[end:]
    start=run.index('    if prior:')
    end=run.index('    output = HERE / name',start)
    run=run[:start]+run[end:]
    start=run.index('        for path, role in roles.items():')
    end=run.index('        for path, fixture in fixtures.items():',start)
    run=run[:start]+run[end:]
    start=run.index("        if mode == 'candidate':")
    end=run.index('        binaries = ',start)
    run=run[:start]+"        results['build'] = {'skipped': True, 'reason': 'Baseline-only retained binary; no build path', 'retained_build_receipt': retained}\n        save(output / 'BUILD.json', results['build'])\n"+run[end:]
    run=run.replace("assert results['wpt']['exit_code'] in (0, 1)","assert results['wpt']['exit_code'] == 0")
    run=run.replace("assert analyze.compare(expected_baseline, parsed)['accepted_changes_only'], 'baseline vector or diagnostics/classification changed'", "assert analyze.rows(expected_baseline) == analyze.rows(parsed), 'baseline status vector changed'")
    start=run.index('        if baseline is not None:')
    end=run.index('    except BaseException:',start)
    run=run[:start]+"        observations = observe.parse(output / 'wpt-raw.jsonl')\n        save(output / 'OBSERVATIONS.json', observations)\n"+run[end:]
    run=run.replace('    binaries = comparison = None','    binaries = comparison = observations = None')
    run=run.replace("'native_fix_acceptance': False,", "'native_fix_acceptance': False, 'observation_count': len(observations) if observations is not None else None,")
    run=run.replace('    index = hashlib.sha256', "    assert mode == 'baseline' and roles == {} and baseline is None\n    index = hashlib.sha256",1)
    assert "'build', 'binaries'" not in run and "mode == 'candidate'" not in run
    (HERE/'run.py').write_text(run)
    (HERE/'RUN-DIFF.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),run.splitlines(True),fromfile='signed/run.py',tofile='probe/run.py')))
    (HERE/'runtime-inputs').mkdir(exist_ok=True)
    fixture=(ROOT/PROPOSAL).read_bytes()
    assert sha(fixture)=='a5f93e8ad01f9a8188d8123d19064f59e20b44a56fc3941c9856e21d471632e6'
    original_fixture=fixture
    text=fixture.decode()
    text=text.replace('to { --kc-length: 2em; --kc-tokens: 2em; }', 'to { --kc-length: 2em; --kc-tokens: 2em; margin-left: 2em; }')
    text=text.replace('["color", "transform", "font-size", ...names]', '["color", "transform", "font-size", "margin-left", ...names]')
    text=text.replace('      target.style.setProperty("--kc-length", "2em");', '      target.style.marginLeft = "2em";\n      assert_equals(getComputedStyle(target).marginLeft, "32px",\n                    "Ordinary static control computes relative units");\n      target.style.marginLeft = "10px";\n      target.style.setProperty("--kc-length", "2em");')
    text=text.replace('{"--kc-length": "2em", "--kc-tokens": "2em"}', '{"--kc-length": "2em", "--kc-tokens": "2em", marginLeft: "2em"}')
    fixture=text.encode()
    (HERE/'runtime-inputs/custom-keyframe-value-observations.html').write_bytes(fixture)
    (HERE/'FIXTURE-DELTA.patch').write_text(''.join(difflib.unified_diff(original_fixture.decode().splitlines(True),text.splitlines(True),fromfile='frozen-proposal/v1.html',tofile='runtime-proposal/v2.html')))
    receipt='artifacts/css-keyframe-order-combined-current-build-20261110-v1/build-result.json'
    retained=git_file(ORIGIN,receipt)
    (HERE/'runtime-inputs/retained-build.json').write_bytes(retained)
    retained_json=json.loads(retained)
    save('RUN-PLAN.json',{'head':None,'native_basis':retained_json['head'],'mozconfig_sha256':retained_json['mozconfig_sha256'],
                        'debug_gate':'Baseline-only getter observation; no native repair or final CSSOM/debug acceptance.',
                        'fixtures':{FIXTURE:'custom-keyframe-value-observations.html'},'suites':[FIXTURE],'lint_paths':[FIXTURE]})
    save('SOURCE-ROLES.json',{})
    save('EXPECTED-CHANGES.json',[])
    cases=['original-variable','original-custom-only','unregistered-reference','registered-relative','registered-add','waapi-specified-control']
    names=['Register the typed length diagnostic property']+[case+': capture complete keyframes and value context' for case in cases]
    url='/'+FIXTURE.removeprefix('testing/web-platform/tests/')
    save('EXPECTED-CALLBACKS.json',[[url,name] for name in names])
    save('EXPECTED-BASELINE.json',{'subtests':[{'test':url,'subtest':name,'status':'PASS'} for name in names],
                                 'harness':[{'test':url,'status':'OK'}],'subtest_count':7,'test_count':1})
    save('OBSERVATION-SCHEMA.json',{'marker':'KCUSTOM-V1 ','ids':cases,'phases':['created','quarter','three-quarters'],
                                 'style_properties':['color','transform','font-size','margin-left','--end-color','--not-used','--source','--stored','--kc-length','--kc-tokens'],
                                 'records':18})
    pin_names=[FIXTURE,FIXTURE.replace('/tests/','/meta/',1)+'.ini',
               'testing/web-platform/meta/css/css-animations/__dir__.ini','testing/web-platform/meta/css/__dir__.ini','testing/web-platform/meta/__dir__.ini',
               'testing/web-platform/tests/resources/testharness.js','testing/web-platform/tests/resources/testharnessreport.js']
    pins={}
    for name in pin_names:
        data=git_file(ORIGIN,name,optional=True)
        pins[name]=None if data is None else sha(data)
    assert pins[FIXTURE] is None and pins[FIXTURE.replace('/tests/','/meta/',1)+'.ini'] is None
    save('runtime-inputs/test-source-pins.json',pins)
    save('ORIGINS.json',{'signed_origin':ORIGIN,'origin_directory':OLD,'origin_hashes':origin_hashes,'source_test_pin_revision':ORIGIN,
                        'proposal_origin':PROPOSAL,'proposal_sha256':sha(original_fixture),'runtime_fixture_sha256':sha(fixture),'retained_build_origin':receipt,'retained_build_sha256':sha(retained)})
    print('Prepared baseline-only capsule; execution HEAD/ready manifest remain unset.')


if __name__=='__main__':main()
