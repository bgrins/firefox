import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('use -I -S without optimization')
sys.dont_write_bytecode = True
import json

def oracle(cases):
    result=[]
    def listing(xs):return ','.join(map(str,xs))
    for i,c in enumerate(cases):
        ordered=dict.fromkeys(c['initial'] if c['kind']==0 else [])
        fields=[str(i),listing(ordered),listing(ordered)]
        for op,x in c['ops']:
            reply=-1
            if op==0:ordered[x]=None;reply=2
            if op==1:
                reply=int(x in ordered);ordered.pop(x,None)
            if op==2:ordered.clear()
            if op==3:reply=3
            bits=''.join('1' if q in ordered and q not in (5,6) else '0' for q in range(12))
            fields.extend([listing(ordered),listing(ordered),str(reply),bits])
        result.append('|'.join(fields))
    return '\n'.join(result)+'\n'

def validate(root,out,lean):
    cases=json.loads((root/'native/CASES.json').read_text());alphabet=json.loads((root/'native/ALPHABET.json').read_text())
    if len({tuple(x) for x in alphabet})!=len(alphabet):raise RuntimeError('atom identity roster')
    expected=oracle(cases);candidate=(out/'candidate.txt').read_text()
    if lean!=expected or candidate!=expected:raise RuntimeError('native/model/reference calibration mismatch')
    expected_rows=expected.splitlines();original=(out/'original.txt').read_text().splitlines()
    if len(original)!=21:raise RuntimeError('original case count')
    oracles=json.loads((root/'evidence/ORACLES.json').read_text());ids={'a':0,'b':1,'A':2,'absent':3}
    bad=[]
    for i,(o,c,actual,want) in enumerate(zip(oracles,cases,original,expected_rows)):
        wanted_op=[[2,0]] if o['operation']=='clear' else [[1,ids[o['operation'][-1]]]]
        if not(c['name']==o['subtest'] and c['initial']==[ids[x] for x in o['initial']] and c['ops']==wanted_op and c['wpt']):raise RuntimeError('WPT case identity')
        fields=want.split('|')
        if fields[1]!=','.join(str(ids[x]) for x in o['initial_order']) or fields[3]!=','.join(str(ids[x]) for x in o['updated_order']):raise RuntimeError('independent WPT ordered oracle')
        if o['delete_return'] is not None and fields[5]!=str(int(o['delete_return'])):raise RuntimeError('deletion return')
        actual_fields=actual.split('|')
        status='PASS' if [actual_fields[2],*actual_fields[4:]]==[fields[2],*fields[4:]] else 'FAIL'
        if set(actual_fields[1].split(','))!=set(fields[1].split(',')):raise RuntimeError('initial native membership')
        if status!=o['original_expected_status']:raise RuntimeError('original discrepancy')
        if status=='FAIL':bad.append(o['subtest'])
    for file,original_run in [('original-v1.jsonl',True),('candidate-v1.jsonl',False)]:
        rows=[json.loads(x) for x in (root/'evidence/browser'/file).read_text().splitlines()]
        statuses=[x for x in rows if x.get('action')=='test_status']
        if len(statuses)!=21 or len({x['subtest'] for x in statuses})!=21:raise RuntimeError('browser status roster')
        by_name={x['subtest']:x for x in statuses}
        for o in oracles:
            status=o['original_expected_status'] if original_run else 'PASS'
            row=by_name[o['subtest']]
            if row['status']!=status:raise RuntimeError('browser oracle mismatch')
            if status=='FAIL' and 'expected false but got true' not in row.get('message',''):raise RuntimeError('unexpected failure stage')
    mutants={}
    for name in ['reverse-order','omit-native-delete']:
        rows=(out/(name+'.txt')).read_text().splitlines()
        if len(rows)!=21:raise RuntimeError('mutant row count')
        diff=[i for i,(actual,want) in enumerate(zip(rows,expected_rows)) if actual!=want]
        if not diff:raise RuntimeError('undistinguished compiled mutant')
        mutants[name]=diff
    return dict(cases=len(cases),original_disagreements=bad,native_mutants=mutants,scope='source-shaped controls; substituted provider implementation; historical browser correlation')
