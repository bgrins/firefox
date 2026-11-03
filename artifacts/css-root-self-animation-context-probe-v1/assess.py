import json, math, re, sys
VARIATION = re.compile(r'^"wdth"\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)$', re.I)
def numeric(raw, property):
    if property == 'fontSize':
        assert raw.endswith('px')
        result = float(raw[:-2])
    else:
        match = VARIATION.fullmatch(raw)
        assert match
        result = float(match[1])
    assert math.isfinite(result) and result > 0
    return result

def close(a, b):
    return isinstance(a, (int, float)) and math.isfinite(a) and abs(a-b) < .04

def animation(a):
    assert a['targetIsRoot'] is True and a['progress'] == .5
    assert a['playState'] == 'paused' and a['currentTime'] == 500
    assert len(a['keyframes']) == 2

def assess(data):
    assert data['schema'] == 'root-self-animation-context-v1'
    assert data['cleanup'] is True and data['errors'] == []
    expected = {(u, p, s, l) for u in ('rem','rlh') for p in ('fontVariationSettings','fontSize') for s,l in ((23,37),(31,47))}
    assert len(data['cases']) == 8
    assert {(c['unit'],c['property'],c['size'],c['line']) for c in data['cases']} == expected
    rows=[]; failed=[]
    for c in data['cases']:
        assert c['compatMode'] == c['referenceCompatMode'] == 'CSS1Compat'
        assert c['supports'] == [True, True]
        initial=c['initial'];reference=c['referenceInitial']
        for key in ('rem','rlh'):
            assert close(initial[key],reference[key]) and initial[key] > 0
        assert initial['lineHeight'] == reference['lineHeight'] == 'normal'
        assert close(numeric(initial['fontSize'],'fontSize'),initial['rem'])
        assert close(numeric(reference['fontSize'],'fontSize'),reference['rem'])
        animation(c['literalInfo']);animation(c['inheritedControlInfo'])
        assert close(numeric(c['literalRaw'],c['property']),30)
        assert close(numeric(c['inheritedControlRaw'],'fontSize'),2*initial['rem'])
        assert c['underlying'] == {'fontSize':f"{c['size']}px",'lineHeight':f"{c['line']}px",'writingMode':'horizontal-tb','textOrientation':'mixed'}
        assert close(numeric(c['ordinarySizeRaw'],'fontSize'),c['ordinarySizeValue'])
        assert close(numeric(c['ordinaryVariationRaw'],'fontVariationSettings'),c['ordinaryVariationValue'])
        expected_initial=2*initial[c['unit']]
        underlying=2*(c['size'] if c['unit']=='rem' else c['line'])
        calibrated=close(c['ordinarySizeValue'],expected_initial)
        if not calibrated:failed.append({'unit':c['unit'],'property':c['property'],'size':c['size'],'control':'ordinary root font-size','value':c['ordinarySizeValue'],'expected_initial':expected_initial})
        assert [s['timing'] for s in c['samples']] == ['first','settled']
        for s in c['samples']:
            animation(s['animation']);value=numeric(s['raw'],c['property']);assert close(value,s['value'])
            a,b=close(value,expected_initial),close(value,underlying)
            label='uncalibrated' if not calibrated else 'both' if a and b else 'initial-reference' if a else 'underlying-root' if b else 'other'
            rows.append({'unit':c['unit'],'property':c['property'],'size':c['size'],'line':c['line'],'timing':s['timing'],'value':value,'initial_reference':expected_initial,'underlying_root':underlying,'classification':label,'ordinary_variation':c['ordinaryVariationValue'],'ordinary_font_size':c['ordinarySizeValue'],'stable':close(c['samples'][0]['value'],c['samples'][1]['value'])})
    return {'rows':rows,'rows_count':len(rows),'calibrated':not failed,'control_failures':failed,'native_cause_proved':False,'candidate_acceptance':False,'inference':'Root context diagnostic, not proof of a particular setter or repair; first/settled differences retained'}
if __name__ == '__main__':
    print(json.dumps(assess(json.load(open(sys.argv[1]))),indent=2))
