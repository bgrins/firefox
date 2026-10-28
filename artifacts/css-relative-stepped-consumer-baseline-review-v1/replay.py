import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'artifacts/css-relative-stepped-consumer-observation-v1'
PROBE = ROOT / 'artifacts/css-relative-stepped-consumer-probe-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def number(value):
    return float(value.removesuffix('px'))

def assess(data):
    old = data['original']
    rows = old['rows']
    ops = ['mod', 'rem', 'round', 'division', 'cancellation', 'zeroProduct']
    expected = [(u, o, b) for u in ['em', 'rem', 'cqw'] for o in ops for b in [10, 0, 10]]
    assert old['count'] == len(rows) == 54
    assert [(r['unit'], r['operation'], r['basis']) for r in rows] == expected
    wrong_width = []
    for i, r in enumerate(rows):
        unit, op, basis = expected[i]
        wanted = 10 if op in ['cancellation', 'zeroProduct'] else (0 if basis == 0 else 10 + 4*basis if op == 'round' else 11 if op == 'division' else 10+basis)
        absolute = 14 if op == 'round' else 10 if op in ['cancellation', 'zeroProduct'] else 11
        assert r['supported'] is True and r['expected'] == wanted
        for role, value in [('resolved', wanted), ('literal', wanted), ('absolute', absolute), ('calibration', basis)]:
            assert r[role]['specified'] and number(r[role]['width']) == r[role]['rect'] == value
        assert number(r['targetFont']) == (basis if unit == 'em' else 16)
        assert number(r['rootFont']) == (basis if unit == 'rem' else 16)
        assert number(r['containerWidth']) == (basis*100 if unit == 'cqw' else 100)
        assert r['target']['specified'] and number(r['target']['width']) == r['target']['rect']
        if number(r['target']['width']) != wanted:
            wrong_width.append([unit, op, basis])
            assert basis == 0 and op in ['mod', 'rem', 'round'] and number(r['target']['width']) == 10
    assert len(wrong_width) == 9
    consumers = data['consumers']; rows = consumers['rows']
    cases = [(op, kind) for op in ['mod','rem','round'] for kind in ['integer','steps','bezier','linear']] + [('sign-only','integer')]
    expected = [(op, kind, b) for op, kind in cases for b in [10,0,10]]
    assert consumers['cases'] == 13 and consumers['count'] == len(rows) == 39
    assert [(r['operation'],r['kind'],r['basis']) for r in rows] == expected
    css_wrong = []; api_wrong = []; api_count = 0
    for i, r in enumerate(rows):
        op, kind, basis = expected[i]
        assert r['property'] == ('z-index' if kind == 'integer' else 'animation-timing-function')
        assert r['supports'] == {'target':True,'resolved':True,'literal':True}
        for role in ['target','resolved','literal','absolute']:
            v=r[role]
            assert v['specified'] and number(v['fontSize']) == number(v['width']) == v['rect'] == basis
            assert v['animationCount'] == (0 if kind=='integer' else 1)
        assert (r['resolved']['computed'],r['resolved']['opacity']) == (r['literal']['computed'],r['literal']['opacity'])
        assert (r['target']['computed'],r['target']['opacity']) == (r['absolute']['computed'],r['absolute']['opacity'])
        different=(r['target']['computed'],r['target']['opacity']) != (r['resolved']['computed'],r['resolved']['opacity'])
        assert different == (basis==0)
        if different: css_wrong.append([op,kind,basis])
        if kind=='integer':
            wanted=2 if basis else 1 if op=='sign-only' else 0
            assert r['expectedInteger']==wanted and int(r['resolved']['computed'])==wanted and r['target']['computed']=='2'
            assert 'api' not in r
            continue
        assert r['easingOracle'].startswith('diagnostic')
        assert set(r['api'])=={'effect','keyframe'}
        for location, group in r['api'].items():
            assert set(group)=={'target','resolved','literal'}
            for role,v in group.items():
                assert v['admitted'] is True and 'error' not in v
                assert v['opacity']==r[role]['opacity']
                assert [k['offset'] for k in v['keyframes']]==[0,1]
                if location=='keyframe':
                    assert v['easing']=='linear' and v['progress']==0.75
                    assert v['keyframes'][0]['easing']==r[role]['computed']
                else:
                    assert v['easing']==r[role]['computed']
                    assert abs(v['progress']-float(v['opacity']))<0.000001
                api_count+=1
            assert group['resolved']==group['literal']
            different=group['target']!=group['resolved']
            assert different==(basis==0)
            if different: api_wrong.append([op,kind,basis,location])
    assert len(css_wrong)==13 and len(api_wrong)==18 and api_count==162
    for rs in [old['rows'],consumers['rows']]:
        for i in range(0,len(rs),3): assert rs[i]==rs[i+2]
    for i in range(0,len(consumers['rows']),3):
        group=consumers['rows'][i:i+3]
        assert len({(r['absolute']['computed'],r['absolute']['opacity']) for r in group})==1
    return {'exact_rows':93,'width_rows':54,'width_discrepancies':wrong_width,'width_controls_all_match':True,
        'consumer_rows':39,'css_zero_discrepancies':css_wrong,'consumer_pixel_literal_and_fixed_controls_match':True,
        'api_objects_admitted':162,'api_effect_comparisons':27,'api_keyframe_comparisons':27,
        'api_zero_discrepancies':api_wrong,'all_nonzero_recovery_samples_equal':True,
        'ordinary_stepped_integer_discrepancies':3,'held_sign_only_discrepancy':1,
        'css_easing_diagnostic_discrepancies':9,'waapi_easing_diagnostic_discrepancies':18,
        'native_repair_executed':False,'new_bug_count':0,'acceptance':False,
        'waapi_invalidation_proved':False,'easing_context_policy_settled':False}

if __name__ == '__main__':
    pre,post=read(RAW/'PRE.json'),read(RAW/'POST.json')
    assert set(post)=={'epoch_sha256','pins'} and all(pre[k]==v for k,v in post.items())
    assert sha(PROBE/'FILES.json')==pre['probe_manifest_sha256']=='c336fafbabecdeadf7ea533223801158cd909be39125d9511e6e41a35ac02f18'
    for n,v in read(PROBE/'FILES.json').items(): assert sha(PROBE/n)==v['sha256']
    report=assess(read(RAW/'raw.json'))
    report.update(saved_epoch_and_six_pins_preserved=True,head=pre['head'],epoch_sha256=pre['epoch_sha256'],independent_live_checks=False)
    pins={str(f.relative_to(ROOT)):sha(f) for f in [RAW/'raw.json',RAW/'PRE.json',RAW/'POST.json',PROBE/'FILES.json']}
    for n,v in [('ASSESSMENT.json',report),('REFERENCES.json',pins)]:
        path=HERE/n
        if path.exists(): assert read(path)==v
        else: path.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report))
