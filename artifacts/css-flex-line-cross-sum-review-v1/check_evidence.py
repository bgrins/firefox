import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S")
sys.dont_write_bytecode=True
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
HERE=Path(__file__).resolve().parent
PINS={'css-flex-line-cross-sum-probe-v1':'af68a3e61020406fe203398ad50d60be8be19ab8eddb8a1995a093c74d8a1342','css-flex-line-cross-sum-fix-v1':'a65108f346c5576e95a1c4fccf61cc0f37d80531827c1eb06a0eb028022853e1'}
PATCH='34a5ec601d2bc24d428160f6cbd5422b584a82cfeea3662fb96e9764135d3798'
CPP='layout/generic/nsFlexContainerFrame.cpp'
WPT='testing/web-platform/tests/css/css-flexbox/flexbox-line-cross-size-sum-overflow.html'
def require(x,msg):
    if not x: raise RuntimeError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    def unique(items):
        d={}
        for k,v in items:
            require(k not in d,'duplicate JSON field');d[k]=v
        return d
    return json.loads(p.read_text(),object_pairs_hook=unique)
def closure(root,pin):
    require(sha(root/'FILES.json')==pin,'manifest pin')
    entries=read(root/'FILES.json')['files'];names=[e['path'] for e in entries]
    require(len(set(names))==len(names),'duplicate path')
    for n in names:
        q=PurePosixPath(n);require(str(q)==n and not q.is_absolute() and '..' not in q.parts and n not in ['FILES.json','FREEZE.json'],'unsafe path')
    files=set();dirs=set()
    for base,ds,fs in os.walk(root,followlinks=False):
        for n in ds+fs:
            p=Path(base)/n;require(not p.is_symlink(),'symlink')
            if p.is_file(): files.add(p.relative_to(root).as_posix())
            elif p.is_dir(): dirs.add(p.relative_to(root).as_posix())
            else: raise RuntimeError('nonregular entry')
    require(files==set(names)|{'FILES.json','FREEZE.json'},'file closure')
    require(dirs=={str(p) for n in names for p in PurePosixPath(n).parents if str(p)!='.'},'directory closure')
    for e in entries: require(sha(root/e['path'])==e['sha256'],'file pin '+e['path'])
    seal=read(root/'FREEZE.json');require(seal.get('manifest_sha256',seal.get('files_sha256'))==pin,'freeze binding')
    return {'files':len(entries),'directories':len(dirs),'manifest_sha256':pin,'freeze_sha256':sha(root/'FREEZE.json')}
def statuses(root):
    rows=[json.loads(line) for line in (root/'raw.json').read_text().splitlines()]
    subs={}
    for e in rows:
        if e.get('action')=='test_status':
            key=(e['test'],e['subtest']);require(key not in subs,'duplicate subtest');subs[key]=(e['status'],e.get('message',''))
    return rows,subs

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--artifacts',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    arts=args.artifacts.resolve();out=args.output.resolve();require(not out.exists(),'new output')
    auth={n:closure(arts/n,pin) for n,pin in PINS.items()};out.mkdir(parents=True)
    fix=arts/'css-flex-line-cross-sum-fix-v1';probe=arts/'css-flex-line-cross-sum-probe-v1'
    package=read(fix/'PACKAGING.json');require(sha(fix/'fix-candidate-v1.patch')==PATCH==package['patch_sha256'],'patch pin')
    require(sha(fix/'candidate.cpp')==package['candidate_sha256'] and sha(fix/'wpt-v1.html')==package['wpt_sha256'],'package source pin')
    change=read(fix/'SOURCE-CHANGE.json');before=(fix/'before.cpp').read_text();after=before
    for a,b in change['replacements']:
        require(after.count(a)==1,'replacement identity');after=after.replace(a,b)
    require(after==(fix/'candidate.cpp').read_text(),'exact two source replacements')
    require(sha(HERE/'working-candidate.cpp')==sha(fix/'candidate.cpp') and sha(HERE/'before.cpp')==sha(fix/'before.cpp'),'working snapshot identity')
    require(sha(HERE/'LineSum.lean')==sha(probe/'LineSum.lean'),'proof source identity')
    allruns=[];allsubs=[]
    for phase in ['baseline-wpt-v1','candidate-wpt-v1']:
        r=read(fix/phase/'RUN.json');require(r['complete'] and r['stable_pins'] and r['before']==r['after'],'run stability')
        for f in (fix/phase/'inputs').rglob('*'):
            if f.is_file():require(sha(f)==r['before'][f.relative_to(fix/phase/'inputs').as_posix()],'captured input pin')
        rows,subs=statuses(fix/phase);require(len(subs)==144,'WPT roster')
        require(all(v[0] in ['PASS','FAIL'] for v in subs.values()),'numeric range prerequisite not admitted')
        require([e['status'] for e in rows if e.get('action')=='test_end']==['OK'],'harness result')
        allruns.append(r);allsubs.append(subs)
    require(set(allsubs[0])==set(allsubs[1]),'paired case identity')
    fixed=[k for k in allsubs[0] if allsubs[0][k][0]=='FAIL' and allsubs[1][k][0]=='PASS']
    same=[k for k in allsubs[0] if allsubs[0][k]==allsubs[1][k]]
    require(len(fixed)==96 and len(same)==48 and all(v[0]=='PASS' for v in allsubs[1].values()),'paired results')
    require(all('Auto block size clamps the sum' in allsubs[0][k][1] for k in fixed),'failures occur at final oracle')
    changed=[k for k in allruns[0]['before'] if allruns[0]['before'][k]!=allruns[1]['before'][k]]
    require(CPP in changed and len(changed)==3 and all(k==CPP or '/Contents/MacOS/' in k for k in changed),'paired changed inputs')
    require(allruns[0]['before'][CPP]==sha(fix/'before.cpp') and allruns[1]['before'][CPP]==sha(fix/'candidate.cpp'),'tested CPP identities')
    require(allruns[0]['before'][WPT]==allruns[1]['before'][WPT]==sha(fix/'wpt-v1.html'),'tested WPT identity')
    regression,sub=statuses(fix/'regressions-v1');ends=[e for e in regression if e.get('action')=='test_end'];known=[e for e in ends if e['status']=='FAIL']
    require(len(ends)==27 and len(sub)==914 and all(v[0]=='PASS' for v in sub.values()),'regression subtests')
    require(Counter(e['status'] for e in ends)=={'PASS':20,'OK':6,'FAIL':1},'regression ends')
    require(len(known)==1 and known[0]['test'].endswith('/content-height-with-scrollbars.html') and 'FAIL' in known[0]['known_intermittent'],'known intermittent identity')
    rr=read(fix/'regressions-v1/RUN.json');require(rr['complete'] and rr['stable_pins'] and rr['exit']==0,'regression receipt')
    discovery=[]
    for phase in ['release','candidate']:
        d=read(probe/phase/'RESULT.json');require(d['stable'] and d['before']==d['after'] and d['profile_removed'],'discovery stability')
        require(len(d['observations'])==1,'discovery response count');rows=d['observations'][0]['rows'];require(len(rows)==40,'discovery case count')
        require(all(x['calibrated'] and x['stable'] and x['definiteControl']==100 for x in rows),'discovery controls')
        require(sum(not x['matched'] for x in rows)==11,'discovery failures');discovery.append(rows)
    require(discovery[0]==discovery[1],'release/development discovery equality')
    applications=[]
    patch=fix/'fix-candidate-v1.patch'
    require(re.findall(r'^\+\+\+ b/(.+)$',patch.read_text(),re.M)==[CPP,WPT],'standalone paths')
    for check in package['checks']:
        native=subprocess.run(['git','show',check['base']+':'+CPP],cwd=arts.parent,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        require(native.returncode==0,'read frozen Git base')
        require(hashlib.sha256(native.stdout).hexdigest()==check['before_sha256'],'base identity')
        with tempfile.TemporaryDirectory(prefix='flex-line-patch-independent-') as tmp:
            tree=Path(tmp);(tree/CPP).parent.mkdir(parents=True);(tree/WPT).parent.mkdir(parents=True);(tree/CPP).write_bytes(native.stdout)
            run=subprocess.run(['/usr/bin/patch','-p1','-f','-F0','-i',str(patch)],cwd=tree,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            (out/(check['base']+'-apply.log')).write_text(run.stdout);require(run.returncode==0,'patch application')
            require(sha(tree/CPP)==check['after_sha256']==sha(fix/('standalone-'+check['base'][:12]+'.cpp')),'standalone native identity')
            require(sha(tree/WPT)==package['wpt_sha256'],'standalone WPT identity')
            run=subprocess.run(['/usr/bin/patch','-R','-p1','-f','-F0','-E','-i',str(patch)],cwd=tree,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            (out/(check['base']+'-reverse.log')).write_text(run.stdout);require(run.returncode==0,'reverse application')
            require(sha(tree/CPP)==check['before_sha256'] and not (tree/WPT).exists(),'reverse restoration')
            applications.append({'base':check['base'],'before_sha256':check['before_sha256'],'after_sha256':check['after_sha256'],'apply_reverse':True})
    result={'status':'PASS','authentication':auth,'patch_sha256':PATCH,'paired':{'cases':144,'fixed':96,'unchanged_status_and_message':48,'all_numeric_prerequisites_admitted':True,'changed_input_pins':changed},'regressions':{'subtests_pass':914,'reftests_pass':20,'harnesses_ok':6,'known_intermittent':known,'all_pass_claim':False,'baseline_comparison':False},'discovery':{'identical_cases':40,'failures':11},'standalone':applications,'temporary_patch_trees_removed':True,'browser_and_builds':'Retained producer evidence authenticated/recounted, not independently rerun'}
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','paired_cases':144,'fixed':96,'standalone_bases':len(applications)}))
if __name__=='__main__':main()
