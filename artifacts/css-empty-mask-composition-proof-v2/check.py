import argparse
import hashlib
import json
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

import bridge
import fixtures
import lean_cases

BASE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, log, stdin=None):
    result = subprocess.run([str(x) for x in command], input=stdin, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=120)
    log.write_text(result.stdout)
    return result


def native_differences(output, cases, label):
    rows = output.splitlines()
    if len(rows) != len(cases):
        return [{'kind':'row-count','actual':len(rows),'expected':len(cases)}]
    bad = []
    for index,(line,case) in enumerate(zip(rows,cases)):
        values,events = line.split('|')
        actual = [Fraction(x) for x in values.split()]
        trace = case['trace'] if case['kind']=='callee' else case['traces'][label]
        if actual != case[label] or events != ''.join(x+';' for x in trace):
            bad.append(index)
    return bad


def safe_model(text):
    assert not re.search(r'\b(sorry|axiom|admit|unsafe)\b',text), 'untrusted model declaration'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--skip-mutations',action='store_true')
    args=parser.parse_args()
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False)
    inputs=json.loads((BASE/'REPLAY-INPUTS-v2.json').read_text())
    for path,digest in inputs.items():
        assert sha(BASE/path)==digest,path
    tool=json.loads((BASE/'TOOLCHAIN-v1.json').read_text())
    for key in ['lean','compiler']:
        assert sha(Path(tool[key]))==tool[key+'_sha256'],key
    assert sha(Path(tool['sdk'])/'SDKSettings.json')==tool['sdk_settings_sha256']
    compiler=[tool['compiler'],'-isysroot',tool['sdk'],'-std=c++17','-O1','-Wall','-Werror',
              '-fsanitize=undefined,implicit-integer-truncation','-fno-sanitize-recover=all']
    model=(BASE/'Mask.lean').read_text();safe_model(model)
    theorems=re.findall(r'^theorem (\w+)',model,re.M)
    audit=out/'Audit.lean';audit.write_text(model+'\n'+'\n'.join('#print axioms Mask.'+x for x in theorems)+'\n')
    result=run([tool['lean'],audit],out/'lean-audit.log')
    assert result.returncode==0,result.stdout
    assert len(re.findall(r"'Mask\.",result.stdout))==len(theorems),result.stdout
    assert 'sorryAx' not in result.stdout and 'Lean.ofReduceBool' not in result.stdout
    for names in re.findall(r'depends on axioms: \[(.*?)\]', result.stdout):
        assert set(names.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}, names
    cases=fixtures.fixtures()
    input_text='\n'.join(case['input'] for case in cases)+'\n'
    (out/'native-input.txt').write_text(input_text)
    differences={}
    for candidate in [False,True]:
        label='candidate' if candidate else 'original'
        source=out/(label+'.cpp');source.write_text(bridge.generate(candidate))
        binary=out/label
        result=run(compiler+[source,'-o',binary],out/(label+'-compile.log'))
        assert result.returncode==0,result.stdout
        result=run([binary],out/(label+'-run.log'),input_text)
        assert result.returncode==0,result.stdout[:1000]
        differences[label]=native_differences(result.stdout,cases,label)
        assert not differences[label],differences[label][:10]
    case_file=out/'Cases.lean';case_file.write_text(model+lean_cases.generate(cases))
    result=run([tool['lean'],case_file],out/'lean-cases.log')
    assert result.returncode==0,result.stdout[:2000]
    lean_rows=result.stdout.splitlines();assert len(lean_rows)==len(cases)
    for index,(line,case) in enumerate(zip(lean_rows,cases)):
        values=[Fraction(x) for x in line.split()]
        expected=case['candidate'] if case['kind']=='callee' else [case['candidate'][1]]
        assert values==expected,(index,values,expected)
    semantic=[];diagnostic=[];lean_mutations=[]
    if not args.skip_mutations:
        source=bridge.generate(True)
        annotation='const gfxMatrix& aToUserSpace'
        assert source.count(annotation)==1
        annotated=source.replace(annotation,annotation+' [[clang::lifetimebound]]')
        lifetime_good=out/'diagnostic-lifetime-good.cpp';lifetime_good.write_text(annotated)
        result=run(compiler+[lifetime_good,'-o',out/'diagnostic-lifetime-good'],out/'diagnostic-lifetime-good-compile.log')
        assert result.returncode==0,result.stdout
        lifetime=out/'diagnostic-lifetime.cpp'
        old='Matrix userSpace;\n      SVGMaskFrame::MaskParams params(&target,&frame,userSpace,opacity,StyleMaskMode(mode),img);'
        assert source.count(old)==1
        lifetime.write_text(annotated.replace(old,'SVGMaskFrame::MaskParams params(&target,&frame,Matrix(),opacity,StyleMaskMode(mode),img);'))
        result=run(compiler+[lifetime,'-o',out/'diagnostic-lifetime'],out/'diagnostic-lifetime-compile.log')
        assert result.returncode!=0 and '-Wdangling' in result.stdout and 'temporary' in result.stdout,result.stdout[:2000]
        diagnostic.append('annotated named-matrix fixture compiles; old temporary rejected by Clang dangling diagnostic')
        substitutions=[
          ('missing-initialization','*aMaskAreaIsEmpty = false;',''),
          ('failure-classified-empty','*aMaskAreaIsEmpty = false;','*aMaskAreaIsEmpty = true;'),
          ('missing-empty-classification','*aMaskAreaIsEmpty = true;','*aMaskAreaIsEmpty = false;'),
          ('missing-clear','} else if (maskAreaIsEmpty &&','} else if (false && maskAreaIsEmpty &&'),
          ('wrong-subtract-operator','compositionOp == CompositionOp::OP_OUT','compositionOp == CompositionOp::OP_OVER'),
          ('wrong-intersect-operator','compositionOp == CompositionOp::OP_IN','compositionOp == CompositionOp::OP_XOR'),
          ('bottom-in','? CompositionOp::OP_OVER','? CompositionOp::OP_IN'),
          ('lost-target-origin','ClearRect(Rect(aMaskDT->GetRect()))','ClearRect(Rect{0,0,aMaskDT->GetRect().w,aMaskDT->GetRect().h})'),
          ('lost-transform-restore','aMaskDT->SetTransform(tmp);','aMaskDT->SetTransform(Matrix(tmp.x*0,tmp.y*0));'),
          ('break-after-clear','aMaskDT->ClearRect(Rect(aMaskDT->GetRect()));','aMaskDT->ClearRect(Rect(aMaskDT->GetRect())); break;'),
          ('wrong-svg-operator-map','return CompositionOp::OP_OUT;','return CompositionOp::OP_OVER;'),
        ]
        for label,old,new in substitutions:
            assert old in source,label
            mutated=out/(label+'.cpp');mutated.write_text(source.replace(old,new))
            binary=out/label
            result=run(compiler+[mutated,'-o',binary],out/(label+'-compile.log'))
            assert result.returncode==0,(label,result.stdout)
            selected=[case for case in cases if case['kind']=='callee'] if label=='missing-initialization' else cases
            selected_input='\n'.join(case['input'] for case in selected)+'\n'
            (out/(label+'-input.txt')).write_text(selected_input)
            result=run([binary],out/(label+'-run.log'),selected_input)
            assert result.returncode==0,(label,result.stdout[:1000])
            bad=native_differences(result.stdout,selected,'candidate');assert bad,label
            semantic.append({'name':label,'input_count':len(selected),'comparison_mismatches':len(bad),'first':bad[0]})
        changes=[
          ('zero-add','| .add => s + d * (1 - s)','| .add => s'),
          ('zero-out','| .subtract => s * (1 - d)','| .subtract => d'),
          ('zero-in','| .intersect => s * d','| .intersect => d'),
          ('zero-xor','| .exclude => s * (1 - d) + d * (1 - s)','| .exclude => s'),
          ('failure-clears','| .failure _ => d','| .failure _ => 0'),
          ('bottom-uses-declared','if bottom then Op.add else op','if bottom then op else op'),
        ]
        for label,old,new in changes:
            assert old in model
            path=out/(label+'.lean');path.write_text(model.replace(old,new))
            result=run([tool['lean'],path],out/(label+'.log'))
            assert result.returncode!=0 and ('unsolved goals' in result.stdout or 'failed' in result.stdout or 'mismatch' in result.stdout),(label,result.stdout)
            lean_mutations.append(label)
        broken=out/'diagnostic-native.cpp';broken.write_text(source.replace('maskArea.IsEmpty()', 'maskArea.missing_probe_member()'))
        result=run(compiler+[broken,'-o',out/'diagnostic-native'],out/'diagnostic-native.log')
        assert result.returncode!=0 and 'missing_probe_member' in result.stdout
        diagnostic.append('native compilation requires expected provider API')
        bad_import=out/'diagnostic-import.lean';bad_import.write_text('import MissingMaskProofModule\n')
        result=run([tool['lean'],bad_import],out/'diagnostic-import.log')
        assert result.returncode!=0 and 'MissingMaskProofModule' in result.stdout
        diagnostic.append('Lean missing import is not a semantic rejection')
        for label,payload in [('sorry','theorem forged : False := by sorry'),('axiom','axiom forged : False')]:
            try:safe_model(model+'\n'+payload)
            except AssertionError:diagnostic.append('forbidden '+label)
            else:raise AssertionError(label)
        shadow=out/'source-guard';shadow.mkdir();shutil.copyfile(BASE/'SOURCE-v1.json',shadow/'SOURCE-v1.json');shutil.copytree(BASE/'source',shadow/'source')
        changed=shadow/'source/candidate-SVGMaskFrame.cpp';changed.write_text(changed.read_text()+'\n')
        saved=bridge.BASE;bridge.BASE=shadow
        try:
            bridge.generate(True)
        except AssertionError as error:
            assert 'candidate-SVGMaskFrame.cpp' in str(error)
            diagnostic.append('source identity mismatch rejected before extraction')
        else:raise AssertionError('source guard')
        finally:bridge.BASE=saved
    changed_stacks=sum(case['kind']=='stack' and case['candidate'][1]!=case['original'][1] for case in cases)
    receipt={'status':'PASS','lean_theorems':len(theorems),'native_cases_per_variant':len(cases),
             'lean_executable_cases':len(cases),'original_vs_candidate_alpha_changes':changed_stacks,
             'native_semantic_mutations':semantic,'lean_semantic_mutations':lean_mutations,
             'diagnostic_controls':diagnostic,'input_count':len(inputs),'input_manifest_sha256':sha(BASE/'REPLAY-INPUTS-v2.json'),
             'toolchain_sha256':sha(BASE/'TOOLCHAIN-v1.json'),
             'native_input_sha256':sha(out/'native-input.txt'),
             'native_candidate_output_sha256':sha(out/'candidate-run.log'),
             'lean_output_sha256':sha(out/'lean-cases.log')}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
