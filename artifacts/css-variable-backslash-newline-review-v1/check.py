import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S without optimization')
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/'css-variable-backslash-newline-root-v1'
for name,digest in json.loads((HERE/'INPUTS.json').read_text()).items():
    if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:raise RuntimeError(name)
def read(path):return json.loads(path.read_text())
def raw(path):return [json.loads(line) for line in path.read_text().splitlines()]
def outcomes(events):
    result={}
    for r in events:
        if r.get('action')!='test_status':continue
        key=(r['test'],r['subtest'])
        if key in result:raise RuntimeError('duplicate outcome')
        result[key]=(r['status'],r.get('message',''))
    return result
base=outcomes(raw(ROOT/'baseline-wpt-raw.json'))
full=raw(ROOT/'candidate-wpt-v1/raw.json');after=outcomes(full)
assert len(base)==32 and len(after)==467
assert sum(v[0]=='FAIL' for v in base.values())==16
for key,value in base.items():
    expected='FAIL' if key[1].startswith(('LF,','CR,','FF,','CRLF,')) and not key[1].endswith('"/**/"') else 'PASS'
    assert value[0]==expected and after[key][0]=='PASS'
prior=read(HERE.parent/'css-variable-escaped-whitespace-root-v1/candidate-wpt-v1/RUN.json')
old=outcomes(prior['rows']);assert len(old)==435
assert {k:after[k] for k in old}==old
assert set(after)==set(old)|set(base)
assert sum(r.get('action')=='test_end' and r.get('status')=='OK' for r in full)==24
run=read(ROOT/'candidate-wpt-v1/RUN.json');assert run['before']==run['after'] and run['complete'] and run['exit']==0
assert outcomes(run['rows'])==after
assert 'Your build was successful!' in (ROOT/'build.log').read_text()
assert '0 problems (0 errors, 0 warnings, 0 fixed)' in (ROOT/'wpt-lint.log').read_text()

def patch_sections(text):
    sections={};current=None
    for line in text.splitlines(keepends=True):
        if line.startswith('diff --git '):current=line.split(' b/',1)[1].strip();sections[current]=[]
        elif current is not None:sections[current].append(line)
    return sections

def apply(original,lines):
    src=original.splitlines(keepends=True);output=[];pos=0;i=0
    while i<len(lines):
        h=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i])
        if not h:i+=1;continue
        start,count=int(h[1]),int(h[2] or '1');target=0 if start==0 else start-1
        assert target>=pos;output+=src[pos:target];pos=target;i+=1;consumed=0;added=0
        while i<len(lines) and not lines[i].startswith('@@'):
            line=lines[i]
            if line.startswith((' ','-')):
                assert src[pos]==line[1:];pos+=1;consumed+=1
            if line.startswith((' ','+')):output.append(line[1:]);added+=1
            i+=1
        assert consumed==count and added==int(h[4] or '1')
    output+=src[pos:];return ''.join(output)
for label in ['head','standalone']:
    sections=patch_sections((ROOT/(label+'-native-wpt.patch')).read_text())
    source='servo/components/style/custom_properties.rs';test='testing/web-platform/tests/css/css-variables/trailing-backslash-newline.html'
    assert set(sections)=={source,test}
    a=(ROOT/('package-'+label)/'original.rs').read_text();b=(ROOT/('package-'+label)/'candidate.rs').read_text()
    assert apply(a,sections[source])==b
    assert hashlib.sha256(apply('',sections[test]).encode()).hexdigest()==run['before'][test]
rows={v:[json.loads(l) for l in (HERE/'native-receipts'/(v+'.jsonl')).read_text().splitlines()] for v in ['baseline','tested','head','upstream']}
cases=read(HERE/'CASES.json')
assert len(cases)==73
for v,rs in rows.items():assert len(rs)==73 and [r['index'] for r in rs]==list(range(73)) and all(r['status']=='OK' for r in rs)
for i,c in enumerate(cases[:56]):
    suffix=i%7
    expected=c['css'] if suffix in [0,1,2,6] else c['css'].rstrip(' \t')
    assert bytes.fromhex(rows['tested'][i]['css_hex']).decode()==expected
    standalone=expected[:-1] if suffix==6 else expected
    for v in ['head','upstream']:assert bytes.fromhex(rows[v][i]['css_hex']).decode()==standalone
    if suffix in [0,1]:assert bytes.fromhex(rows['baseline'][i]['css_hex']).decode()==c['css'].rstrip('\n\r\f \t')
for i in [58,59]:
    assert bytes.fromhex(rows['tested'][i]['css_hex']).decode()==cases[i]['css']
    for v in ['head','upstream']:assert bytes.fromhex(rows[v][i]['css_hex']).decode()==cases[i]['css'][:-1]
final=read(ROOT/'FINAL-WPT.json');finalraw=raw(ROOT/'final-wpt-raw.json');frows=outcomes(finalraw)
assert len(frows)==30 and all(v[0]=='PASS' for v in frows.values())
assert final['before']==final['after'] and final['complete'] and final['exit']==0
assert sum(r.get('action')=='test_end' and r.get('status')=='OK' for r in finalraw)==1
removed=set(base)-set(frows)
assert {k[1] for k in removed}==set(final['removed_controls']) and len(removed)==2
assert sum(base[k][0]=='FAIL' for k in frows)==16
oldtest=apply('',patch_sections((ROOT/'head-native-wpt.patch').read_text())[test])
for label in ['head','standalone']:
    sections=patch_sections((ROOT/(label+'-native-wpt-v2.patch')).read_text())
    assert set(sections)=={source,test}
    a=(ROOT/('package-'+label+'-v2')/'original.rs').read_text();b=(ROOT/('package-'+label+'-v2')/'candidate.rs').read_text()
    assert apply(a,sections[source])==b
    newtest=apply('',sections[test])
    assert hashlib.sha256(newtest.encode()).hexdigest()==final['before'][test]
    # Compare only token case entries; other fixture bytes must remain exact.
    oldline=next(line for line in oldtest.splitlines(True) if '["x' in line and '"x "' in line)
    newline=next(line for line in newtest.splitlines(True) if '["x' in line and '"x "' not in line)
    assert oldtest.replace(oldline,newline)==newtest
print(json.dumps({'status':'ACCEPTED_NATIVE_WPT_SCOPED','final_baseline_fail':16,'final_baseline_pass':14,'final_candidate_pass':30,'unchanged_prior':435,'prior_matrix_total':467,'prior_harness_ok':24,'native_variants':4,'cases_per_variant':73,'standalone_prior_escaped_whitespace_bug_preserved':True,'source_translation_proved':False}))
