import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:raise RuntimeError('Require python3 -I -S without optimization')
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def require(c,s):
    if not c:raise RuntimeError(s)
def load(root,name,path):
    spec=importlib.util.spec_from_file_location(name,root/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def run(root,out,tool,core,collect_headers=False):
    out.mkdir();rows=core.cases();negatives=core.negative_cases();write(out/'CASES.json',rows);write(out/'NEGATIVE-CASES.json',negatives)
    require(rows==json.loads((root/'CASES.json').read_text()),'case roster')
    require(negatives==json.loads((root/'NEGATIVE-CASES.json').read_text()),'negative case roster')
    generator=load(root,'generator','native/generate.py');extractor=load(root,'extractor','source_extract.py');mutations=load(root,'mutations','mutations.py')
    for variant in ['combined-before','combined-after','standalone-before','standalone-after']:
        records=extractor.selected(variant)
        require(records==json.loads((root/'bindings'/(variant+'.json')).read_text()),'source extraction '+variant)
        for record in records:
            data=(root/record['path']).read_bytes();start=record['start_byte'];body=record['body'].encode()
            require(data[start:start+len(body)]==body and sha(body)==record['sha256'],'byte extraction')
    work=out/'lean';work.mkdir();modules=[]
    def visit(name):
        if name in modules:return
        source=(root/'lean'/(name+'.lean')).read_text()
        for dep in re.findall(r'^import (\w+)$',source,re.M):
            if dep!='Std':visit(dep)
        modules.append(name)
    visit('WideWitnesses');names=[]
    for name in modules:
        source=(root/'lean'/(name+'.lean')).read_text();(work/(name+'.lean')).write_text(source)
        require(not re.search(r'\b(sorry|admit|axiom|native_decide|implemented_by)\b',source),'forbidden proof source '+name)
        names.extend(name+'.'+n for n in re.findall(r'^theorem (\w+)',source,re.M))
    roster=json.loads((root/'AUDITS.json').read_text())
    require(names==roster['declarations'] and set(roster['allowed_axioms'])=={'propext','Classical.choice','Quot.sound'},'axiom roster/policy')
    env={'PATH':'/usr/bin:/bin','LEAN_PATH':str(work)};commands=[]
    def lean(name,run=False):
        command=[tool['lean'],*(['--run'] if run else ['-o',str(work/(name+'.olean'))]),str(work/(name+'.lean'))]
        p=subprocess.run(command,cwd=work,env=env,text=True,capture_output=True)
        (work/(name+'.stdout')).write_text(p.stdout);(work/(name+'.stderr')).write_text(p.stderr)
        commands.append({'name':name,'command':command,'exit':p.returncode});write(out/'LEAN-COMMANDS.json',commands)
        require(p.returncode==0 and "declaration uses 'sorry'" not in p.stdout+p.stderr,'Lean '+name)
        return p.stdout
    for name in modules:lean(name)
    (work/'Audit.lean').write_text('import WideWitnesses\n'+'\n'.join('#print axioms '+name for name in names)+'\n')
    text=lean('Audit');audits={}
    for line in text.splitlines():
        match=re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]",line)
        if match:name,axes=match[1],([] if not match[2] else match[2].split(', '))
        else:
            match=re.fullmatch(r"'([^']+)' does not depend on any axioms",line);require(match is not None,'audit grammar');name,axes=match[1],[]
        require(name not in audits and set(axes)<=set(roster['allowed_axioms']),'unsupported axiom');audits[name]=axes
    require(list(audits)==names,'audit roster completeness');write(out/'AUDITS.json',audits)

    challenges={
      'false-normalization':'example : WidenedInsets.referenceEnd 100 200 20 10 = 140 := by decide +kernel',
      'false-clamp-safety':'example : WideCallers.AbsoluteSafe WideWitnesses.clampFrame := by decide +kernel',
      'false-old-domain':'example : StickyNumeric.Admitted (WideNormalization.oldEndExpression 6000 600 (-1073741823) (-1073741823)) := by decide +kernel'}
    proof_controls=[]
    for name,body in challenges.items():
        path=work/(name+'.lean');path.write_text('import WideWitnesses\n'+body+'\n')
        p=subprocess.run([tool['lean'],str(path)],cwd=work,env=env,capture_output=True,text=True)
        (work/(name+'.log')).write_text(p.stdout+p.stderr)
        require(p.returncode!=0 and 'error:' in p.stdout+p.stderr,'false kernel challenge accepted '+name)
        proof_controls.append({'name':name,'exit':p.returncode,'rejected':True})
    for name,body,forbidden in [
      ('extra-axiom','axiom unauthorized : False\ntheorem challenge : False := unauthorized','unauthorized'),
      ('sorry-axiom','theorem challenge : False := by sorry','sorryAx')]:
        path=work/(name+'.lean');path.write_text('import WideWitnesses\n'+body+'\n#print axioms challenge\n')
        p=subprocess.run([tool['lean'],str(path)],cwd=work,env=env,capture_output=True,text=True)
        (work/(name+'.log')).write_text(p.stdout+p.stderr)
        require(p.returncode==0 and forbidden in p.stdout,'axiom control did not reach kernel '+name)
        lines=[line for line in p.stdout.splitlines() if 'depends on axioms:' in line]
        require(len(lines)==1,'axiom control print roster')
        axes=re.fullmatch(r"'challenge' depends on axioms: \[([^]]*)\]",lines[0])[1].split(', ')
        require(not set(axes)<=set(roster['allowed_axioms']),'unauthorized axiom accepted')
        proof_controls.append({'name':name,'exit':p.returncode,'rejected_axioms':axes})
    write(out/'PROOF-CONTROLS.json',proof_controls)
    leanrows={};expected={}
    for profile in ['combined-after','standalone-after']:
        name=profile.replace('-','_')
        (work/(name+'.lean')).write_text(core.lean_source(rows+negatives,profile));text=lean(name,True)
        got=[json.loads(line) for line in text.splitlines()];require(len(got)==len(rows)+len(negatives),'Lean rows')
        leanrows[profile]=got[:len(rows)];expected[profile]=[core.expected(c,profile) for c in rows]
        for c,actual,expect in zip(rows,got,expected[profile]):
            require(actual['safe'] and actual['debug'] and actual['preparation_safe'] and actual['preparation_match'] and actual['sizes_valid'],'positive domain '+str(c['id']))
            for key,value in expect.items():
                if key not in ['original_offsets','trace']:require(actual[key]==value,'independent Lean/Python '+profile+' '+str(c['id'])+' '+key)
        require(all(not a['safe'] and a['old_safe'] for a in got[len(rows):]),'negative caller admission')
        write(out/(profile+'-LEAN.json'),got)
    native=out/'native';native.mkdir();native_commands=[];headers_seen={};results={};mutant_results={}
    jobs=[(v,mode,None) for v in ['combined-before','combined-after','standalone-before','standalone-after'] for mode in ['debug','optimized']]
    jobs += [('combined-after','optimized',m) for m in mutations.MUTANTS]
    for variant,mode,mutation in jobs:
        label=mode+'-'+(mutation or variant);folder=native/label;folder.mkdir()
        text=generator.generate(variant,'driver.cpp',mutation);(folder/'source.cpp').write_text(text)
        command=[tool['compiler'],'-isysroot',tool['sdk'],'-std=c++20','-fsanitize=undefined','-fno-sanitize-recover=all',
            *(['-O0'] if mode=='debug' else ['-O2','-DNDEBUG']),'-MD','-MF',str(folder/'deps.d'),str(folder/'source.cpp'),'-o',str(folder/'probe')]
        p=subprocess.run(command,env={'PATH':'/usr/bin:/bin','TMPDIR':str(folder)},capture_output=True,text=True)
        (folder/'compile.log').write_text(p.stdout+p.stderr);record={'name':label,'command':command,'compile_exit':p.returncode,'variant':variant,'source_sha256':sha(text.encode()),'input_sha256':sha((root/'inputs'/(variant+'.cpp')).read_bytes())};native_commands.append(record);write(out/'NATIVE-COMMANDS.json',native_commands)
        require(p.returncode==0,'native compile '+label)
        deps=(folder/'deps.d').read_text().replace('\\\n',' ').split(':',1)[1].split();headers=sorted(set(deps)-{str(folder/'source.cpp')})
        if mode not in headers_seen:headers_seen[mode]=headers
        require(headers==headers_seen[mode],'header closure disagreement')
        if not collect_headers:require(headers==json.loads((root/'CPP-HEADERS.json').read_text())['configurations'][mode],'header closure')
        profile=variant.replace('before','after');ref=leanrows[profile]
        selected=[c for c,a in zip(rows,ref) if 'after' in variant or a['old_safe']]
        input_text=core.corpus.input_text(selected);(folder/'input.txt').write_text(input_text)
        p=subprocess.run([str(folder/'probe')],input=input_text,env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True)
        (folder/'stdout.jsonl').write_text(p.stdout);(folder/'stderr.log').write_text(p.stderr);record['run_exit']=p.returncode;write(out/'NATIVE-COMMANDS.json',native_commands)
        require(p.returncode==0 and not p.stderr,'native execution '+label)
        got=[json.loads(line) for line in p.stdout.splitlines()];require(len(got)==len(selected),'native row count')
        differences=[]
        for c,a in zip(selected,got):
            exp=core.expected(c,variant)
            require(a['id']==c['id'],'native row identity')
            for key,value in exp.items():
                if a.get(key)!=value:differences.append({'id':c['id'],'field':key,'native':a.get(key),'expected':value})
        if mutation:
            require(differences,'semantic mutant survived '+mutation);mutant_results[mutation]={'differences':len(differences),'first':differences[0]}
        else:require(not differences,'native comparison '+label+': '+str(differences[:1]))
        results[label]={'rows':len(got),'sha256':sha(p.stdout.encode())}
        if not mutation:
            p=subprocess.run([str(folder/'probe')],input=core.corpus.input_text(negatives),env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True)
            (folder/'negative.stdout').write_text(p.stdout);(folder/'negative.stderr').write_text(p.stderr)
            require(p.returncode!=0 and 'signed integer overflow' in p.stderr and '1073801223 - -1073740223' in p.stderr,'retained clamp diagnostic '+label)
            record['negative_exit']=p.returncode;write(out/'NATIVE-COMMANDS.json',native_commands)
    write(out/'MUTANTS.json',mutant_results)
    write(out/'CPP-HEADERS.json',{'configurations':headers_seen,'entries':[{'path':p,'sha256':sha(Path(p).read_bytes())} for p in sorted(set().union(*map(set,headers_seen.values())))]})
    cleanup=[]
    for p in sorted(out.rglob('*')):
        if p.is_file() and (p.name=='probe' or p.suffix in ['.olean','.ilean','.ir'] or p.name.endswith(('.olean.private','.olean.server'))):
            cleanup.append({'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())});p.unlink()
    write(out/'CLEANUP.json',cleanup)
    return {'complete':True,'cases':len(rows),'Lean_reference_rows':sum(map(len,leanrows.values())),'audited_results':len(names),'native_runs':8,'proof_controls':len(proof_controls),'native_semantic_mutants':len(mutant_results),'retained_negative_runs':8,'results':results}
