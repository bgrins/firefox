#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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

def run(output):
    output=output.resolve()
    assert output != ROOT and ROOT not in output.parents
    output.mkdir(exist_ok=False)
    receipts=[]
    variants=['original','candidate','mutant-position','mutant-svg','mutant-flags','mutant-cache','mutant-self']
    reference={}
    with tempfile.TemporaryDirectory(prefix='css-exact-traversal-binaries-') as binary_dir:
        for variant in variants:
            role='original' if variant=='original' else 'candidate'
            frame=extract((ROOT/role/'nsIFrame.cpp').read_text(),'Matrix4x4Flagged nsIFrame::GetTransformMatrix(')
            ancestor=extract((ROOT/role/'nsLayoutUtils.cpp').read_text(),'Matrix4x4Flagged nsLayoutUtils::GetTransformToAncestor(')
            wrapper='' if role=='original' else extract((ROOT/role/'nsLayoutUtils.cpp').read_text(),'static nsRect TransformClientRectToAncestor(')
            bindings={name:hashlib.sha256(body.encode()).hexdigest() for name,body in [('frame',frame),('ancestor',ancestor),('wrapper',wrapper)]}
            if variant=='mutant-position':
                frame=frame.replace('Some(nsPoint(x.value(), y.value()))','Some(nsPoint(0, y.value()))')
            if variant=='mutant-svg':
                frame=frame.replace('!(*aOutAncestor)->IsInSVGTextSubtree()','true').replace('!IsInSVGTextSubtree()','true')
            if variant=='mutant-flags':
                frame=frame.replace('aAppUnitTranslation && aFlags.isEmpty() &&','aAppUnitTranslation &&')
            if variant=='mutant-cache':
                wrapper=wrapper.replace('nullptr, &matrix);','nullptr, nullptr);')
            if variant=='mutant-self':
                wrapper=wrapper.replace('if (aFrame == aAncestor) {','if (false) {')
            opening=frame.index('{')
            frame=frame[:opening+1]+'\n  ++matrixCalls;'+frame[opening+1:]
            source=output/(variant+'.cpp')
            source.write_text('#define CANDIDATE '+str(int(role=='candidate'))+'\n'+(ROOT/'facade.cpp').read_text()+'\n'+frame+'\n'+ancestor+'\n'+wrapper+'\n'+(ROOT/'harness.cpp').read_text())
            for opt in ['-O0','-O2']:
                exe=Path(binary_dir)/'program'
                command=['/usr/bin/clang++','-std=c++20',opt,'-fsanitize=undefined','-fno-sanitize-recover=all','-I',str(ROOT/'include'),str(source),'-o',str(exe)]
                built=subprocess.run(command,capture_output=True,text=True)
                (output/(variant+opt+'-compile.log')).write_text(built.stdout+built.stderr)
                assert built.returncode==0,built.stderr
                ran=subprocess.run([str(exe)],capture_output=True,text=True)
                (output/(variant+opt+'-run.log')).write_text(ran.stdout+ran.stderr)
                success=variant in ['original','candidate']
                assert (ran.returncode==0)==success,(variant,ran.returncode,ran.stdout[-1000:],ran.stderr)
                rows=[r for r in ran.stdout.splitlines() if r.startswith('ROW ')]
                if variant=='original':reference[opt]=rows
                if variant=='candidate':assert rows==reference[opt],'fallback matrix/call trace mismatch'
                receipts.append({'variant':variant,'optimization':opt,'exit':ran.returncode,'rows':len(rows),'bindings':bindings,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
    result={'runs':receipts,'scope':'Full extracted GetTransformMatrix/GetTransformToAncestor and CPP-local exact wrapper. Frame/context/matrix/viewport/legacy rectangle providers are explicit facades; actual CheckedInt headers. Instrumentation adds one matrixCalls increment per GetTransformMatrix entry. No full Gecko/GFX or browser proof.'}
    (output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'runs':len(receipts),'candidate_rows_per_configuration':len(reference['-O0']),'all_expected_outcomes':True}))

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python3 -I -S -B replay.py NEW_OUTPUT_DIRECTORY')
    run(Path(sys.argv[1]))
