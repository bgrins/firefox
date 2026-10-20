#!/usr/bin/env python3
import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import os
import stat
from pathlib import PurePosixPath
ROOT=Path(__file__).resolve().parent

def extract(text,signature):
    start=text.index(signature)
    opening=text.index('{',start)
    depth=1
    end=opening+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}')
        end+=1
    return text[start:end]

def authenticate(expected):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            assert k not in out, 'duplicate JSON key'
            out[k] = v
        return out
    for name in ['FILES.json', 'FREEZE.json']:
        assert stat.S_ISREG((ROOT/name).lstat().st_mode), 'nonregular seal'
    raw=(ROOT/'FILES.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==expected,'external manifest pin mismatch'
    manifest=json.loads(raw, object_pairs_hook=unique)
    dirs=set()
    for name,digest in manifest.items():
        p=PurePosixPath(name)
        assert str(p)==name and not p.is_absolute() and '..' not in p.parts and name not in {'FILES.json','FREEZE.json'}, 'invalid manifest path'
        assert isinstance(digest,str) and len(digest)==64 and all(c in '0123456789abcdef' for c in digest), 'invalid digest'
        dirs.update(str(x) for x in p.parents if str(x)!='.')
    actual=set()
    def walk(directory):
        for e in os.scandir(directory):
            p=Path(e.path); rel=p.relative_to(ROOT).as_posix()
            mode=e.stat(follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                assert rel in dirs, 'unexpected directory'
                walk(p)
            else:
                assert stat.S_ISREG(mode), 'nonregular input'
                if rel in {'FILES.json','FREEZE.json'}: continue
                assert rel in manifest and hashlib.sha256(p.read_bytes()).hexdigest()==manifest[rel], 'input mismatch: '+rel
                actual.add(rel)
    walk(ROOT)
    assert actual==set(manifest),'closed capsule roster mismatch'
    freeze=json.loads((ROOT/'FREEZE.json').read_text(), object_pairs_hook=unique)
    assert freeze['files_sha256']==expected and freeze['payload_count']==len(manifest)
    pins=json.loads((ROOT/'CANDIDATE-PINS.json').read_text(), object_pairs_hook=unique)
    for role,files in pins.items():
        for name,digest in files.items():
            assert hashlib.sha256((ROOT/role/name).read_bytes()).hexdigest()==digest, 'source role pin'

def run(output,expected):
    authenticate(expected)
    toolchain=json.loads((ROOT/'TOOLCHAIN.json').read_text())
    assert hashlib.sha256(Path(toolchain['compiler']).read_bytes()).hexdigest()==toolchain['compiler_sha256'],'compiler driver pin changed'
    output=output.resolve()
    assert output != ROOT and ROOT not in output.parents
    output.mkdir(exist_ok=False)
    receipts=[]
    variants=['original','v2','v3','candidate','mutant-position','mutant-svg','mutant-flags','mutant-cache','mutant-self','mutant-dispatch','mutant-overflow','mutant-null-flags','mutant-null-visual']
    reference={}
    previous={}
    with tempfile.TemporaryDirectory(prefix='css-exact-traversal-binaries-') as binary_dir:
        for variant in variants:
            role=variant if variant in ['original','v2','v3'] else 'candidate'
            frame=extract((ROOT/role/'nsIFrame.cpp').read_text(),'Matrix4x4Flagged nsIFrame::GetTransformMatrix(')
            ancestor=extract((ROOT/role/'nsLayoutUtils.cpp').read_text(),'Matrix4x4Flagged nsLayoutUtils::GetTransformToAncestor(')
            wrapper='' if role=='original' else extract((ROOT/role/'nsLayoutUtils.cpp').read_text(),'static nsRect TransformClientRectToAncestor(')
            bindings={name:hashlib.sha256(body.encode()).hexdigest() for name,body in [('frame',frame),('ancestor',ancestor),('wrapper',wrapper)]}
            pristine_frame,pristine_wrapper=frame,wrapper
            if variant=='mutant-position':
                frame=frame.replace('Some(AppUnitTranslation{wideOffsetX, wideOffsetY})','Some(AppUnitTranslation{0, wideOffsetY})')
            if variant=='mutant-svg':
                frame=frame.replace('NS_FRAME_IS_SVG_TEXT | NS_FRAME_SVG_LAYOUT','NS_FRAME_SVG_LAYOUT')
            if variant=='mutant-flags':
                frame=frame.replace('TrackWide && aFlags.isEmpty() &&','TrackWide &&')
            if variant=='mutant-cache':
                wrapper=wrapper.replace('nullptr, &matrix);','nullptr, nullptr);')
            if variant=='mutant-self':
                wrapper=wrapper.replace('if (aFrame == aAncestor) {','if (false) {')
            if variant=='mutant-dispatch':
                dispatch='if (aFlags.isEmpty() && aViewportType == ViewportType::Layout &&\n      aStopAtAncestor.mViewportType == ViewportType::Layout) {'
                assert dispatch in frame
                frame=frame.replace(dispatch,'if (true) {')
            if variant in ['mutant-null-flags','mutant-null-visual']:
                dispatch='if (aFlags.isEmpty() && aViewportType == ViewportType::Layout &&\n      aStopAtAncestor.mViewportType == ViewportType::Layout) {'
                assert frame.count(dispatch)==1
                omitted = ('aViewportType == ViewportType::Layout && aStopAtAncestor.mViewportType == ViewportType::Layout' if variant=='mutant-null-flags' else 'aFlags.isEmpty() && aViewportType == ViewportType::Layout')
                frame=frame.replace(dispatch, 'if ((!aAppUnitTranslation && '+omitted+') || (aFlags.isEmpty() && aViewportType == ViewportType::Layout && aStopAtAncestor.mViewportType == ViewportType::Layout)) {')
            if variant=='mutant-overflow':
                checked='!SafeAdd(wideDocX, int64_t(position.x), &nextX)'
                assert checked in frame
                frame=frame.replace(checked,'(SafeAdd(wideDocX, int64_t(position.x), &nextX), false)')
            assert variant in ['original','v2','v3','candidate'] or frame!=pristine_frame or wrapper!=pristine_wrapper,variant
            v1='' if role=='original' else (ROOT/'v1-helper.cpp').read_text()
            frame=frame.replace('return GetTransformMatrix(aViewportType,', 'fprintf(stderr, "NUMERIC_RESTART\\n"); return GetTransformMatrix(aViewportType,')
            if role!='original':
                seed_end='CheckedInt<int64_t> wideDocX(docOffset.x), wideDocY(docOffset.y);' if role=='v2' else 'int64_t wideDocX = docOffset.x, wideDocY = docOffset.y;'
                assert seed_end in frame
                frame=frame.replace(seed_end,seed_end+\
                    '\n if(aAppUnitTranslation && injectedState){\n'\
                    '  const int slot=(injectedState-1)%4; const int64_t extreme=injectedState>4?INT64_MIN:INT64_MAX;\n'\
                    '  if(slot==0)wideDocX=extreme; if(slot==1)wideDocY=extreme;\n'\
                    '  if(slot==2)wideOffsetX=extreme; if(slot==3)wideOffsetY=extreme;\n }\n')
            opening=frame.index('{')
            frame=frame[:opening+1]+'\n  ++matrixCalls;'+frame[opening+1:]
            source=output/(variant+'.cpp')
            source.write_text('#define CANDIDATE '+str(int(role!='original'))+'\n'+(ROOT/'facade.cpp').read_text()+'\n'+frame+'\n'+ancestor+'\n'+wrapper+'\n'+v1+'\n'+(ROOT/'harness.cpp').read_text())
            for opt in ['-O0','-O2']:
                exe=Path(binary_dir)/'program'
                command=['/usr/bin/clang++','-std=c++20',opt,'-fsanitize=undefined','-fno-sanitize-recover=all','-I',str(ROOT/'include'),str(source),'-o',str(exe)]
                built=subprocess.run(command,capture_output=True,text=True)
                (output/(variant+opt+'-compile.log')).write_text(built.stdout+built.stderr)
                assert built.returncode==0,built.stderr
                ran=subprocess.run([str(exe)],capture_output=True,text=True)
                (output/(variant+opt+'-run.log')).write_text(ran.stdout+ran.stderr)
                success=variant in ['original','v2','v3','candidate','mutant-overflow']
                rows=[r for r in ran.stdout.splitlines() if r.startswith('ROW ')]
                row_differences=0 if variant=='original' else sum(a!=b for a,b in zip(rows,reference.get(opt,[]))) + abs(len(rows)-len(reference.get(opt,[])))
                if success:
                    assert ran.returncode==0,(variant,ran.returncode,ran.stdout[-1000:],ran.stderr)
                else:
                    assert (ran.returncode!=0 and 'FAIL ' in ran.stdout) or (ran.returncode==0 and row_differences>0), (variant,ran.returncode,ran.stdout[-1000:],ran.stderr)
                if variant=='mutant-null-flags': assert 'FAIL 270' in ran.stdout, ran.stdout
                if variant=='mutant-null-visual': assert 'FAIL 277' in ran.stdout, ran.stdout
                rows=[r for r in ran.stdout.splitlines() if r.startswith('ROW ')]
                if variant=='original':reference[opt]=rows
                if variant=='v2':previous[opt]=ran.stdout
                if variant in ['v3','candidate']:assert ran.stdout==previous[opt],'v2/v3/v4 full normal replay mismatch'
                if variant in ['v2','v3','candidate']:assert rows==reference[opt],'fallback matrix/call trace mismatch'
                if variant in ['original','v2','v3','candidate']:
                    for witness in ['grouping','rect-origin','crossdoc-restart']:
                        challenged=subprocess.run([str(exe),witness],capture_output=True,text=True)
                        (output/(variant+opt+'-'+witness+'.log')).write_text(challenged.stdout+challenged.stderr)
                        assert (challenged.returncode==0)==(variant!='original' and witness!='crossdoc-restart')
                        if variant=='original' or witness=='crossdoc-restart':assert 'runtime error: signed integer overflow' in challenged.stderr
                        if variant!='original' and witness=='crossdoc-restart':assert 'NUMERIC_RESTART' in challenged.stderr

                if variant in ['v2','v3','candidate','mutant-overflow']:
                    for number in range(1,9):
                        checked=subprocess.run([str(exe),'injected-'+str(number)],capture_output=True,text=True)
                        (output/(variant+opt+'-injected-'+str(number)+'.log')).write_text(checked.stdout+checked.stderr)
                        killed=variant=='mutant-overflow' and number in [1,5]
                        assert (checked.returncode!=0)==killed,(variant,number,checked.stdout,checked.stderr)
                        if not killed:
                            assert 'NUMERIC_RESTART' in checked.stderr and 'INJECTED_GUARD_PASS' in checked.stdout

                receipts.append({'variant':variant,'optimization':opt,'exit':ran.returncode,'rows':len(rows),'row_differences_from_original':row_differences,'semantic_assertions':[x for x in ran.stdout.splitlines() if x.startswith('FAIL ')],'bindings':bindings,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
    result={'runs':receipts,'scope':'Full extracted GetTransformMatrix/GetTransformToAncestor and CPP-local exact wrapper. Frame/context/matrix/viewport/legacy rectangle providers are explicit facades; actual CheckedInt headers. Instrumentation adds one matrixCalls increment per GetTransformMatrix entry, stderr marker at guarded legacy restart, and conditional test-only signed64 accumulator seed (disabled in normal/domain runs). Injected states check failure sequencing, not caller reachability. No full Gecko/GFX or browser proof.'}
    authenticate(expected)
    (output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'runs':len(receipts),'candidate_rows_per_configuration':len(reference['-O0']),'all_expected_outcomes':True}))

if __name__=='__main__':
    if len(sys.argv)!=4 or sys.argv[1]!='--files-sha256':raise SystemExit('Usage: python3 -I -S -B replay.py --files-sha256 PIN NEW_OUTPUT_DIRECTORY')
    run(Path(sys.argv[3]),sys.argv[2])
