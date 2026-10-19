import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess
from pathlib import Path
import bridge
import fixtures as fixture_module

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
TOOLCHAIN = json.loads((BASE/'TOOLCHAIN-v1.json').read_text())
LEAN = Path(TOOLCHAIN['lean'])
CLANG = Path(TOOLCHAIN['clang'])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, log, input_text=None):
    result = subprocess.run([str(c) for c in command], input=input_text, capture_output=True, text=True)
    log.write_text(result.stdout + result.stderr)
    return result


def authenticate(manifest, replacements=None):
    replacements = replacements or {}
    for name, expected in manifest.items():
        path = replacements.get(name, ROOT/name)
        if not path.is_file() or digest(path) != expected:
            raise ValueError('identity mismatch: '+name)


def audit_lean(path, log):
    text = path.read_text()
    names = re.findall(r'^#print axioms ([A-Za-z_][A-Za-z_0-9]*)$', text, re.M)
    if len(names) != 21 or len(set(names)) != 21:
        raise ValueError('missing or duplicate theorem audit')
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s', text, re.M):
        raise ValueError('untrusted proof declaration')
    result = run([LEAN, path], log)
    lines = result.stdout.splitlines()
    if result.returncode or result.stderr or len(lines) != len(names):
        raise ValueError('Lean failure or unexpected diagnostics')
    audits = {}
    for name, line in zip(names, lines):
        prefix = f"'AbsposMargins.{name}' "
        if line == prefix+'does not depend on any axioms':
            audits[name] = []
        else:
            match = re.fullmatch(re.escape(prefix)+r'depends on axioms: \[([^\]]*)\]', line)
            if not match:
                raise ValueError('unexpected axiom output')
            axioms = match[1].split(', ')
            if any(a not in {'propext', 'Quot.sound', 'Classical.choice'} for a in axioms):
                raise ValueError('unapproved axioms')
            audits[name] = axioms
    return audits


def native_run(source,out,label,fixtures):
    path = out/(label+'.cpp')
    path.write_text(source)
    binary = out/label
    command = [CLANG,'-std=c++17','-O1','-Wall','-Wextra','-Werror',
               '-fsanitize=undefined,implicit-integer-truncation','-fno-sanitize-recover=all',path,'-o',binary]
    compiled = run(command,out/(label+'-compile.log'))
    if compiled.returncode or compiled.stdout or compiled.stderr:
        raise ValueError('C++ compilation failed or diagnosed '+label)
    result = run([binary],out/(label+'-run.log'),'\n'.join(f['input'] for f in fixtures)+'\n')
    if result.returncode or result.stderr:
        raise ValueError('C++ execution failed or diagnosed '+label)
    lines = result.stdout.splitlines()
    if len(lines) != len(fixtures):
        raise ValueError('C++ output count mismatch '+label)
    for line in lines:
        if not re.fullmatch(r'-?\d+(?: -?\d+){18}',line):
            raise ValueError('invalid native output '+label)
    return lines


def lean_controls(out):
    original = (BASE/'Margins.lean').read_text()
    changes = {
        'ignore-provenance': ('a.autoProvenance || b.autoProvenance || a.unresolvedSentinel || b.unresolvedSentinel','a.unresolvedSentinel || b.unresolvedSentinel'),
        'no-auto-evaluates': ('if start.isAuto || finish.isAuto then','if true then'),
        'floor-after-fixed': ('max 0 (cb - (startInset + endInset)) - fixedSum - kid','max 0 (cb - (startInset + endInset) - fixedSum) - kid'),
        'omit-floor': ('max 0 (cb - (startInset + endInset)) - fixedSum - kid','cb - (startInset + endInset) - fixedSum - kid'),
        'wrong-safe-axis': ('if axis = .inline ∧ residual < 0','if axis = .block ∧ residual < 0'),
        'wrong-negative-division': ('if 0 ≤ r then r / 2 else -((-r) / 2)','r / 2'),
        'wrong-remainder': ('else ⟨half residual, residual - half residual⟩','else ⟨half residual, residual + half residual⟩'),
        'overwrite-fixed': ('| .fixed a, .auto => ⟨a, residual⟩','| .fixed _, .auto => ⟨0, residual⟩'),
    }
    mutations=[]
    for name,(old,new) in changes.items():
        if original.count(old)!=1: raise ValueError('ambiguous Lean mutation '+name)
        path=out/('lean-mutation-'+name+'.lean');path.write_text(original.replace(old,new))
        result=run([LEAN,path],path.with_suffix('.log'))
        if result.returncode==0 or 'error' not in result.stdout: raise ValueError('Lean mutation accepted '+name)
        mutations.append(name)
    guards={'missing-audit':original.replace('#print axioms zero_split\n',''),
            'extra-output':original+'\n#check Nat\n',
            'stderr-output':original+'\n#eval IO.eprintln "diagnostic"\n',
            'sorry':original.replace(':= rfl',':= by sorry',1),
            'axiom':original+'\naxiom forged : False\n',
            'syntax':original+'\nthis is not Lean\n'}
    rejected=[]
    for name,text in guards.items():
        path=out/('lean-guard-'+name+'.lean');path.write_text(text)
        try: audit_lean(path,path.with_suffix('.log'))
        except ValueError as error: rejected.append({'name':name,'reason':str(error)})
        else: raise ValueError('Lean diagnostic guard accepted '+name)
    return mutations,rejected


EARLY='''    if (!startSideMarginIsAuto && !endSideMarginIsAuto) {
      return;
    }

'''


def native_controls(candidate,reflow,out,fixtures,baseline):
    original=bridge.source(candidate,reflow)
    old_math='''      const nscoord stretchFitSize = std::max(
          0, aCBSize.Size(aAxis, outerWM) - aOffsets.StartEnd(aAxis, outerWM) -
                 aMargin.StartEnd(aAxis, outerWM));
      availMarginSpace = stretchFitSize - aKidSize.Size(aAxis, outerWM);'''
    new_math='''      const nscoord insetModifiedSize = std::max(
          0, aCBSize.Size(aAxis, outerWM) - aOffsets.StartEnd(aAxis, outerWM));
      availMarginSpace = insetModifiedSize - aMargin.StartEnd(aAxis, outerWM) -
                         aKidSize.Size(aAxis, outerWM);'''
    changes={
        'missing-provenance':('(aAxis == LogicalAxis::Inline ? aIInsetAuto : aBInsetAuto)', '(aAxis == LogicalAxis::Inline ? (aIInsetAuto && false) : (aBInsetAuto && false))'),
        'swapped-caller-flags':('offsets, iInsetAuto, bInsetAuto);','offsets, bInsetAuto, iInsetAuto);'),
        'caller-requires-both-auto':('const bool iInsetAuto = iStartInsetAuto || iEndInsetAuto;','const bool iInsetAuto = iStartInsetAuto && iEndInsetAuto;'),
        'restored-margin-clamp':(new_math,old_math),
        'wrong-negative-block-split':('aMargin.BStart(aContainingBlockWM) = aAvailMarginSpace / 2;','aMargin.BStart(aContainingBlockWM) = std::max(0, aAvailMarginSpace / 2);'),
        'wrong-block-remainder':('aAvailMarginSpace - aMargin.BStart(aContainingBlockWM);','aAvailMarginSpace + aMargin.BStart(aContainingBlockWM);'),
        'no-computed-margin-write':('aKidReflowInput.SetComputedLogicalMargin(outerWM, aMargin);',''),
        'no-property-write':('if (propValue) {','if (propValue && false) {'),
        'no-auto-does-arithmetic':(EARLY,''),
    }
    records=[]
    for name,(old,new) in changes.items():
        if original.count(old)!=1: raise ValueError('ambiguous native mutation '+name)
        selected=[(f,b) for f,b in zip(fixtures,baseline) if name!='no-auto-does-arithmetic' or f['family']!='large-no-auto']
        lines=native_run(original.replace(old,new),out,'native-mutation-'+name,[f for f,_ in selected])
        mismatches=sum(a!=b for a,(_,b) in zip(lines,selected))
        if not mismatches: raise ValueError('native mutation accepted '+name)
        records.append({'name':name,'cases':len(selected),'mismatches':mismatches,'compile_exit':0,'run_exit':0})
    diagnostic_guards={
        'compiler-warning':original+'\n#warning forced diagnostic\n',
        'compiler-error':original+'\n#error forced error\n',
        'runtime-stderr':original.replace('int main() {','int main() { std::cerr << "forced diagnostic";'),
        'runtime-extra-output':original.replace('int main() {','int main() { std::cout << "extra\\n";'),
    }
    guards=[]
    for name,text in diagnostic_guards.items():
        try: native_run(text,out,'native-guard-'+name,fixtures)
        except ValueError as error: guards.append({'name':name,'reason':str(error)})
        else: raise ValueError('native diagnostic guard accepted '+name)
    large=[f for f in fixtures if f['family']=='large-no-auto']
    try: native_run(original.replace(EARLY,''),out,'native-guard-large-unused-residual',large)
    except ValueError as error:
        text=(out/'native-guard-large-unused-residual-run.log').read_text()
        if 'signed integer overflow' not in text: raise ValueError('wrong large-residual guard failure')
        guards.append({'name':'large-unused-residual','reason':str(error),'diagnostic':'signed integer overflow','scope':'isolated margin helper; downstream full reflow not assessed'})
    else: raise ValueError('large unused residual guard accepted')
    return records,guards


def source_controls(manifest,before,candidate,hbefore,hcandidate,out):
    identities=[]
    for name in manifest:
        path=out/('source-guard-'+str(len(identities)));path.write_bytes((ROOT/name).read_bytes()+b'\nmutation\n')
        try: authenticate(manifest,{name:path})
        except ValueError: identities.append(name)
        else: raise ValueError('identity guard accepted')
    changes={
        'caller-axis-edit':('const bool iInsetAuto = iStartInsetAuto || iEndInsetAuto;','const bool iInsetAuto = bStartInsetAuto || bEndInsetAuto;'),
        'property-write-edit':('*propValue = aMargin.GetPhysicalMargin(outerWM);','*propValue = {};'),
        'unrelated-offset-edit':('void AbsoluteContainingBlock::ResolveSizeDependentOffsets(', 'void AbsoluteContainingBlock::ResolveSizeDependentOffsetsChanged('),
    }
    guards=[]
    for name,(old,new) in changes.items():
        if old not in candidate: raise ValueError('preservation mutation missing')
        try: bridge.preservation(before,candidate.replace(old,new,1),hbefore,hcandidate)
        except ValueError: guards.append(name)
        else: raise ValueError('preservation guard accepted')
    try: bridge.preservation(before,candidate,hbefore,hcandidate+'\nextra\n')
    except ValueError: guards.append('unrelated-header-edit')
    else: raise ValueError('header guard accepted')
    return identities,guards


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((BASE/'SOURCE-v1.json').read_text());authenticate(manifest)
    for key,path in [('lean',LEAN),('clang',CLANG)]:
        if digest(path)!=TOOLCHAIN[key+'_sha256']: raise ValueError('toolchain identity mismatch')
    before=(BASE/'native-before.cpp').read_text();candidate=(BASE/'native-candidate.cpp').read_text()
    hbefore=(BASE/'header-before.h').read_text();hcandidate=(BASE/'header-candidate.h').read_text()
    reflow=(BASE/'ReflowInput.cpp').read_text()
    preserved=bridge.preservation(before,candidate,hbefore,hcandidate)
    preserved['inline_split_sha256']=hashlib.sha256(bridge.extract(reflow,bridge.INLINE).encode()).hexdigest()
    preserved['block_split_sha256']=hashlib.sha256(bridge.extract(reflow,bridge.BLOCK).encode()).hexdigest()
    audits=audit_lean(BASE/'Margins.lean',out/'lean.log')
    lean_mutations,lean_guards=lean_controls(out)
    fixtures=fixture_module.fixtures();(out/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    actual=native_run(bridge.source(candidate,reflow),out,'candidate',fixtures)
    old=native_run(bridge.source(before,reflow),out,'original',fixtures)
    if any(a!=f['candidate_expected'] for a,f in zip(actual,fixtures)): raise ValueError('candidate mismatch')
    if any(a!=f['original_expected'] for a,f in zip(old,fixtures)): raise ValueError('original mismatch')
    mutations,guards=native_controls(candidate,reflow,out,fixtures,actual)
    identities,preservation_guards=source_controls(manifest,before,candidate,hbefore,hcandidate,out)
    authenticate(manifest)
    value_differences=Counter(f['family'] for f,a,b in zip(fixtures,actual,old) if a.split()[:12]!=b.split()[:12])
    receipt={'result':'PASS','source_manifest_sha256':digest(BASE/'SOURCE-v1.json'),'native_extraction':preserved,
             'theorem_axioms':audits,'lean_exit':0,'lean_mutations':lean_mutations,'lean_diagnostic_guards':lean_guards,
             'native_cases':len(fixtures),'families':dict(Counter(f['family'] for f in fixtures)),
             'candidate_oracle_mismatches':0,'original_oracle_mismatches':0,
             'candidate_compile_exit':0,'candidate_run_exit':0,'original_compile_exit':0,'original_run_exit':0,
             'before_after_margin_value_differences':dict(value_differences),
             'value_changes_with_no_auto_insets':sum(a.split()[:12]!=b.split()[:12] and not any(f['inset_auto']) for f,a,b in zip(fixtures,actual,old)),
             'value_changes_with_auto_insets':sum(a.split()[:12]!=b.split()[:12] and any(f['inset_auto']) for f,a,b in zip(fixtures,actual,old)),
             'fixtures_sha256':digest(out/'fixtures.json'),'native_mutations':mutations,'native_diagnostic_guards':guards,
             'source_guards':identities,'preservation_guards':preservation_guards,
             'limitations':['Lean Int margin model, not compiled C++ proof','initial automatic margins assumed zero',
                            'all evaluated native sums/subtractions must fit int32; no whole reflow overflow claim',
                            'exact caller provenance block only; earlier numeric offset resolution supplied by adapter',
                            'anchor/style providers and logical/physical geometry mapping adapted, not proved',
                            'full helper/property synchronization and exact splitting bodies exercised finitely',
                            'no browser, layout, positioning or invalidation theorem']}
    (out/'RECEIPT-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__=='__main__': main()
