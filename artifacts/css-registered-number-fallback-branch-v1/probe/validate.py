import json
from pathlib import Path
def summarize(value):
    cases=json.loads((Path(__file__).parent/'CASES.json').read_text())
    assert isinstance(value['userAgent'],str) and value['userAgent']
    assert value['registrationRules']==['CSSPropertyRule']
    rows=value['rows'];assert [r['id'] for r in rows]==[c['id'] for c in cases]
    for row,case in zip(rows,cases):
        assert all(row[k]==v for k,v in case.items())
        assert row['observed']==row['repeat']
        assert isinstance(row['computed'],str)
    return {'userAgent':value['userAgent'],'rows':rows,
            'discrepancies':[r['id'] for r in rows if r['observed']!=r['expected']],
            'calibration_failures':[r['id'] for r in rows if r.get('calibration') and r['observed']!=r['expected']]}
