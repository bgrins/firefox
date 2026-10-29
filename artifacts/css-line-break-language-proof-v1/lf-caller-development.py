import hashlib,itertools,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'development-build/lf-caller';OUT.mkdir(exist_ok=True)
records=json.loads((ROOT/'development-build/language-range/adaptations.json').read_text())
rows=[]
for width,mode,word,line,capital in itertools.product([8,16],range(4),range(3),range(5),[False,True]):
    for sizes in [(3,),(1,2)]:
        identity=f'lfcaller-{width}-{mode}-{word}-{line}-{int(capital)}-'+''.join(map(str,sizes))
        tokens=[identity,width,0,len(sizes),1,line,word];offset=0
        for size in sizes:
            part=[65,10,65][offset:offset+size];offset+=size
            tokens += [size,1,1,mode+2,*part,*([0]*size),0,0,0,0,4+2*capital]
        rows.append(' '.join(map(str,tokens)))
inputs='\n'.join(rows)+'\n';(ROOT/'evidence/lf-caller-input.txt').write_text(inputs)
dictionary=next((ROOT/'source').rglob('hyph_en_US.hyf'));summaries=[]
for variant in ['original','candidate']:
    source=ROOT/'development-build/language-range'/f'{variant}.cpp';text=source.read_text()
    matches=list(re.finditer(r'nsresult nsLineBreaker::AppendText\([^)]*\) \{',text,re.S));assert len(matches)==2
    for match in reversed(matches):
        width=16 if 'char16_t' in match[0] else 8
        trace='\n {std::ostringstream event;event<<"caller append '+str(width)+' "<<aFlags<<" "<<(aSink?1:0)<<" "<<aLength;for(uint32_t i=0;i<aLength;++i)event<<" "<<unsigned(aText[i]);language_trace(event.str().c_str());}\n'
        text=text[:match.end()]+trace+text[match.end():]
    target=OUT/f'{variant}.cpp';target.write_text(text)
    old=next(r for r in records if r.get('variant')==variant)
    command=[str(target) if value==str(source) else str(OUT/variant) if value==str(source.with_suffix('')) else value for value in old['command']]
    compiled=subprocess.run(command,capture_output=True,text=True);(OUT/f'{variant}-build.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    result=subprocess.run([OUT/variant,dictionary],input=inputs,capture_output=True,text=True);assert result.returncode==0 and not result.stderr
    (ROOT/f'evidence/lf-caller-{variant}.txt').write_text(result.stdout)
    glyphs={line.split()[0]:re.search(r' GLYPHS (\d*) FINISHES',line)[1] for line in result.stdout.splitlines() if ' GLYPHS ' in line};assert len(glyphs)==len(rows)
    differences=[]
    for width,mode,word,line,capital in itertools.product([8,16],range(4),range(3),range(5),[False,True]):
        prefix=f'lfcaller-{width}-{mode}-{word}-{line}-{int(capital)}-'
        if glyphs[prefix+'3']!=glyphs[prefix+'12']:differences.append({'case':prefix,'whole':glyphs[prefix+'3'],'split':glyphs[prefix+'12']})
    summaries.append({'variant':variant,'cases':len(rows),'differences':differences,'generated_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'input_generated_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'command':command})
receipt={'status':'actual TransformText/style/skip-map/scanner admission diagnostics, no consumer equivalence theorem',
  'input_sha256':hashlib.sha256(inputs.encode()).hexdigest(),'variants':summaries,
  'limits':['frame/ancestor topology and styles supplied by range fixture','complete actual TransformText and scanner accumulation/setup/flush execute','real segmentation provider executes','ordinary refcount/heap/font/shaping facade boundary','ReflowText and intrinsic-size consumers not executed']}
(ROOT/'evidence/LF-CALLER-DEVELOPMENT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps([{k:(len(v) if k=='differences' else v) for k,v in row.items() if k in {'variant','cases','differences'}} for row in summaries]))
