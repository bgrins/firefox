import json, math, re, sys
UNITS = ('rem', 'rlh')
ORDERS = ('variation-first', 'width-first', 'opacity-first')
PHASES = ('initial', 'root-change', 'seek-quarter', 'seek-half', 'recreate-same-target', 'new-target')
NUMBER = re.compile(r'^"wdth"\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)$', re.I)
def close(a, b, tolerance=0.03):
    return isinstance(a, (float, int)) and math.isfinite(a) and abs(a-b) <= tolerance

def assess(data):
    assert data['schema'] == 'animation-root-unit-invalidation-v1'
    assert data['cleanup'] is True and data['errors'] == []
    assert len(data['frames']) == 6
    expected_frames = {(u,o) for u in UNITS for o in ORDERS}
    assert {(f['unit'],f['order']) for f in data['frames']} == expected_frames
    output=[]; controls=[]
    for frame in data['frames']:
        unit,order=frame['unit'],frame['order']
        assert frame['compatMode']=='CSS1Compat'
        assert frame['supports']=={'variation':[True,True],'width':True,'opacity':True}
        assert [(r['phase'],r['timing']) for r in frame['rows']]==[(p,t) for p in PHASES for t in ('first','settled')]
        for row in frame['rows']:
            phase,timing=row['phase'],row['timing'];initial=phase=='initial'
            size,line=(23,37) if initial else (31,47)
            progress=0.25 if phase=='seek-quarter' else 0.5
            base=size if unit=='rem' else line
            expected=(1+2*progress)*base;old=(1+2*progress)*(23 if unit=='rem' else 37)
            assert row['rootSize']==size and row['rootLine']==line and row['progress']==progress
            assert close(row['expectedCurrent'],expected) and close(row['expectedOriginal'],old)
            for name in ('variationAnimation','widthAnimation','opacityAnimation','literalVariationAnimation','literalWidthAnimation'):
                a=row[name];p=0.5 if name.startswith('literal') else progress
                assert a['playState']=='paused' and a['progress']==p and a['currentTime']==p*1000 and len(a['keyframes'])==2
            match=NUMBER.fullmatch(row['variationRaw']);variation=float(match[1]) if match else None
            assert row['variationValue']==variation
            assert row['widthRaw'].endswith('px');width=float(row['widthRaw'][:-2]);assert close(width,row['widthValue'],1e-6)
            opacity=float(row['opacityRaw']);assert close(opacity,row['opacityRatioValue'],1e-9)
            expected_controls={'staticVariationValue':2*base,'staticWidthValue':2*base,'rootReference':base,'absoluteVariationValue':30,'literalVariationValue':30,'literalWidthValue':30,'opacity':0.6,'staticOpacityRatioValue':2*base/1000}
            errors=[key for key,value in expected_controls.items() if not close(row[key],value,1e-5 if 'Opacity' in key or key=='opacity' else 0.03)]
            for key,value in {'rootFontSize':f'{size}px','rootLineHeight':f'{line}px','parentFontSize':'30px','childFontSize':'60px'}.items():
                if row[key]!=value:errors.append(key)
            static=NUMBER.fullmatch(row['staticVariationRaw'])
            assert static and close(float(static[1]),row['staticVariationValue'],1e-6)
            def classify(value):
                if errors:return 'uncalibrated'
                now,before=close(value,expected),close(value,old)
                return 'both' if now and before else 'current-root' if now else 'original-root' if before else 'other'
            output.append({'unit':unit,'order':order,'phase':phase,'timing':timing,'variation':variation,'width':width,'opacity_scaled':opacity*1000,'expected_current':expected,'expected_original':old,'classifications':{'variation':classify(variation),'width':classify(width),'opacity':classify(opacity*1000)}})
            if errors:controls.append({'unit':unit,'order':order,'phase':phase,'timing':timing,'errors':errors})
    return {'schema':'animation-root-unit-invalidation-assessment-v1','rows':output,'rows_count':len(output),'calibrated':not controls,'control_failures':controls,'inference':'Timing and cached-value observations only; no automatic bug or native-fix acceptance','native_acceptance':False}

if __name__=='__main__':
    print(json.dumps(assess(json.load(open(sys.argv[1]))),indent=2))
