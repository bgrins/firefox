import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def raw_rows(p):return [r for r in map(json.loads,p.read_text().splitlines()) if r.get('action')=='test_status']
def key(r):return (r['test'],r['subtest'])
def status(r):return (r['status'],r.get('message'))

def run(repo,out):
    review=repo/'artifacts/css-animation-invalid-publication-review-v1'
    source=repo/'artifacts/css-animation-publication-reachability-v1'
    fix=repo/'artifacts/css-animation-invalid-publication-fix-v1'
    for name in ['SOURCE-PINS.json','UPSTREAM-PINS.json']:
        for p in read(source/name):assert sha(source/p['snapshot'])==p['sha256']
    for p in read(source/'SPEC-PINS.json'):assert sha(source/p['path'])==p['sha256']
    original=read(fix/'ORIGINAL-PINS.json');landing=read(fix/'LANDING-PINS.json');runtime=read(fix/'RUN.json')
    for name,pin in original.items():
        suffix=Path(name).relative_to('servo/components/style');assert sha(fix/'source/original'/suffix)==pin
        assert sha(fix/'source/candidate'/suffix)==runtime['native_candidate'][name]
        assert sha(fix/'source/landing'/suffix)==landing[name]
    transfer=read(fix/'FORMAT-TRANSFER.json');suffix=Path(transfer['path']).relative_to('servo/components/style')
    compiled=(fix/'source/candidate'/suffix).read_text();restored=(fix/'source/landing'/suffix).read_text()
    assert compiled.count(transfer['exact_removed_text'])==1
    assert compiled.replace(transfer['exact_removed_text'],transfer['exact_restored_text'])==restored
    assert sha(fix/'source/candidate'/suffix)==transfer['compiled_sha256']
    assert sha(fix/'source/landing'/suffix)==transfer['landing_sha256']
    for name in landing:
        if name!=transfer['path']:
            suffix=Path(name).relative_to('servo/components/style');assert (fix/'source/candidate'/suffix).read_bytes()==(fix/'source/landing'/suffix).read_bytes()
    baseline=read(repo/'artifacts/css-animation-publication-runtime-v2/RUN.json')
    previous=read(repo/'artifacts/css-registered-token-boundary-fix-v2/RUN.json')
    calibration=read(repo/'artifacts/css-animation-registered-consumer-runtime-v1/candidate/RUN.json')
    assert runtime['complete'] and runtime['stable'] and runtime['exit']==runtime['build']['exit']==0
    assert baseline['stable'] and baseline['phase']=='done'
    assert baseline['rows']==raw_rows(repo/'artifacts/css-animation-publication-runtime-v2/raw.json')
    assert runtime['rows']==raw_rows(fix/'raw.json')
    before={key(r):status(r) for r in previous['rows']+baseline['rows']+calibration['rows']}
    after={key(r):status(r) for r in runtime['rows']}
    assert before.keys()==after.keys() and len(before)==len(runtime['rows'])==343
    changed=[{'test':k[0],'subtest':k[1],'before':before[k],'after':after[k]} for k in before if before[k]!=after[k]]
    assert len(changed)==10 and all(r['before'][0]=='FAIL' and r['after'][0]=='PASS' for r in changed)
    assert all(r['test']=='/css/css-properties-values-api/animation-invalid-inherit-publication.html' for r in changed)
    assert Counter(r['status'] for r in baseline['rows'])=={'FAIL':10,'PASS':6}
    assert Counter(r['status'] for r in runtime['rows'])=={'PASS':341,'FAIL':2}
    assert len(runtime['harness'])==20 and all(r['status']=='OK' for r in runtime['harness'])
    original_fixture=(source/'probe-v2.html').read_bytes();assert sha(source/'probe-v2.html')=='b79063a603b26163c2a271dc915f806db5ad75a52b008047a80e2fdbc9d845c4'
    assert (review/'proposed-final-wpt.html').read_bytes().startswith(original_fixture)
    comparison_pins=runtime['pins_before'] | original
    changed_pins={k:[comparison_pins[k],runtime['pins_after'][k]] for k in comparison_pins if comparison_pins[k]!=runtime['pins_after'][k]}
    assert set(original)|{'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL'} <= set(changed_pins) <= set(original)|{'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL'}
    result={'status':'accepted source/runtime pair for original16; see FINAL-REVIEW.json for added6','changes':changed,'unchanged_historical_status_message_pairs':333,'baseline16':{'FAIL':10,'PASS':6},'candidate343':{'PASS':341,'expected_unchanged_FAIL':2},'harness_OK':20,'comparison_sources':{'same_fixture_paired':16,'earlier_fix81_regression_run':308,'historical_animation_calibration':19},'native_original':original,'native_landing':landing,'native_patch_sha256':sha(fix/'native-only.patch'),'format_transfer_verified':True,'changed_build_pins':changed_pins,'baseline_pin_limit':'properties/mod.rs is authenticated separately by native_original/source snapshot; absent from baseline runtime pins', 'additional_tests':'not assumed paired; separate runtime receipt required','no_isolated_upstream_build_or_browser_claim':True}
    out.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('repo',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.repo.resolve(),a.output.resolve())
