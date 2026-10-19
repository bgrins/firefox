import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import bridge
import fixtures
import lean_cases

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
TOOLCHAIN=json.loads((BASE/'TOOLCHAIN-v1.json').read_text())
LEAN=Path(TOOLCHAIN['lean'])
CLANG=Path(TOOLCHAIN['clang'])


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command,log,input_text=None):
    r=subprocess.run([str(x) for x in command],input=input_text,capture_output=True,text=True)
    log.write_text(r.stdout+r.stderr)
    return r


def authenticate(manifest,replacements=None):
    replacements=replacements or {}
    for name,expected in manifest.items():
        p=replacements.get(name,ROOT/name)
        if not p.is_file() or digest(p)!=expected:
            raise ValueError('source identity mismatch: '+name)


def audit_lean(path,log):
    source=path.read_text()
    names=re.findall(r'^#print axioms (\w+)$',source,re.M)
    if len(names)!=34 or len(set(names))!=34:
        raise ValueError('theorem audit inventory mismatch')
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s',source,re.M):
        raise ValueError('untrusted declaration')
    r=run([LEAN,path],log)
    if r.returncode or r.stderr or len(r.stdout.splitlines())!=len(names):
        raise ValueError('Lean compilation or diagnostic rejection')
    audits={}
    for name,line in zip(names,r.stdout.splitlines()):
        prefix=f"'Collapse.{name}' "
        if line==prefix+'does not depend on any axioms':
            audits[name]=[]
        else:
            m=re.fullmatch(re.escape(prefix)+r'depends on axioms: \[([^\]]*)\]',line)
            if not m:
                raise ValueError('unexpected axiom audit')
            values=m[1].split(', ')
            if any(a not in {'propext','Quot.sound','Classical.choice'} for a in values):
                raise ValueError('unapproved axiom')
            audits[name]=values
    return audits


def lean_controls(out):
    original=(BASE/'Collapse.lean').read_text()
    changes={
        'signed-positive-min':('⟨max a.positive b.positive, min a.negative b.negative⟩','⟨min a.positive b.positive, min a.negative b.negative⟩'),
        'signed-negative-max':('⟨max a.positive b.positive, min a.negative b.negative⟩','⟨max a.positive b.positive, max a.negative b.negative⟩'),
        'unknown-positive':('| none => false','| none => true'),
        'ignore-minimum':('|| positive d.minimum','|| false'),
        'ignore-end-padding':('d.paddingEnd != 0','false'),
        'ignore-hidden':('old && (hidden || !separates d)','old && !separates d'),
        'admit-after-nonempty':('if child.through then','if true then'),
        'early-guard':('else finishFrame revised f (childrenWith revised children)','else if revised && !f.hidden && separates f.dimensions then fallbackFrame revised f else finishFrame revised f (childrenWith revised children)'),
        'clearance-zero-absent':('| .clearance _ _ => ⟨[], false⟩','| .clearance amount rest => if amount == 0 then childrenWith revised rest else ⟨[], false⟩'),
    }
    rejected=[]
    for name,(old,new) in changes.items():
        if original.count(old)!=1: raise ValueError('ambiguous Lean mutation '+name)
        p=out/('lean-mutation-'+name+'.lean');p.write_text(original.replace(old,new))
        r=run([LEAN,p],p.with_suffix('.log'))
        if not r.returncode or 'error' not in r.stdout: raise ValueError('Lean semantic mutation accepted '+name)
        rejected.append(name)
    diagnostic={
        'missing-audit':original.replace('#print axioms join_comm\n',''),
        'extra-output':original+'\n#check Nat\n',
        'stderr':original+'\n#eval IO.eprintln "diagnostic"\n',
        'axiom':original+'\naxiom forged : False\n',
        'sorry':original.replace(':= rfl',':= by sorry',1),
        'syntax':original+'\ninvalid Lean input\n',
    }
    guards=[]
    for name,text in diagnostic.items():
        p=out/('lean-guard-'+name+'.lean');p.write_text(text)
        try: audit_lean(p,p.with_suffix('.log'))
        except ValueError as e: guards.append(dict(name=name,reason=str(e)))
        else: raise ValueError('Lean diagnostic accepted '+name)
    return rejected,guards


def native_run(source,out,label,fs):
    p=out/(label+'.cpp');p.write_text(source)
    binary=out/label
    compiled=run([CLANG,'-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=undefined,implicit-integer-truncation','-fno-sanitize-recover=all',p,'-o',binary],out/(label+'-compile.log'))
    if compiled.returncode or compiled.stdout or compiled.stderr:
        raise ValueError('native compile/diagnostic failure '+label)
    r=run([binary],out/(label+'-run.log'),'\n'.join(f['input'] for f in fs)+'\n')
    if r.returncode or r.stderr: raise ValueError('native run/diagnostic failure '+label)
    lines=r.stdout.splitlines()
    if len(lines)!=len(fs): raise ValueError('native output count mismatch '+label)
    for f,line in zip(fs,lines):
        parts=line.split(' |')
        if len(parts)!=2 or len(parts[0].split())!=9+2*len(f['lines']): raise ValueError('native output schema mismatch')
        if any(not re.fullmatch(r'-?\d+',x) for x in parts[0].split()) or any(not re.fullmatch(r'[SEILF]\d+',x) for x in parts[1].split()):
            raise ValueError('native output token mismatch')
    return lines


def native_controls(source,out,fs,baseline):
    changes={
        'unknown-sentinel-positive':('aSize != NS_UNCONSTRAINEDSIZE && aSize > 0','aSize > 0'),
        'ignore-minimum':('isPositiveSize(aRI.ComputedMinBSize())','false'),
        'ignore-end-padding':('borderPadding.BEnd(wm) != 0','false'),
        'ignore-start-padding':('borderPadding.BStart(wm) != 0','false'),
        'remove-hidden-exception':('!aRI.mFrame->IsHiddenByContentVisibilityOfInFlowParentForLayout()','true'),
        'admit-next-sibling':('if (!isEmpty) {','if (false) {'),
        'signed-positive-overwrite':('if (aCoord > mMostPos)','if (aCoord > 0)'),
        'signed-negative-overwrite':('else if (aCoord < mMostNeg)','else if (aCoord < 0)'),
        'overwrite-first-fragment-output':('if (!isEmpty) {\n          if (!setBlockIsEmpty && aBlockIsEmpty) {','if (!isEmpty) {\n          if (aBlockIsEmpty) {'),
        'drop-overflow-pass':('overflowLines <= 1','overflowLines <= 0'),
        'drop-next-in-flow':('block = static_cast<nsBlockFrame*>(block->GetNextInFlow())','block = nullptr'),
        'ignore-clearance-frame':('if (kid == aClearanceFrame)','if (false)'),
        'drop-retry':('*aMayNeedRetry = true;','*aMayNeedRetry = false;'),
        'drop-dirty-return':('return dirtiedLine;','return dirtiedLine && false;'),
    }
    early='''  if (aBlockIsEmpty && !aRI.mFrame->IsHiddenByContentVisibilityOfInFlowParentForLayout() &&
      (aRI.ComputedBSize() != NS_UNCONSTRAINEDSIZE && aRI.ComputedBSize() > 0)) {
    *aBlockIsEmpty = false;
    return false;
  }
'''
    changes['early-positive-return']=('  bool dirtiedLine = false;\n',early+'  bool dirtiedLine = false;\n')
    records=[]
    for name,(old,new) in changes.items():
        if source.count(old)!=1: raise ValueError('ambiguous native mutation '+name)
        lines=native_run(source.replace(old,new),out,'native-mutation-'+name,fs)
        differences=[f['name'] for f,a,b in zip(fs,lines,baseline) if a!=b]
        if not differences: raise ValueError('native mutation undetected '+name)
        records.append(dict(name=name,mismatches=len(differences),witnesses=differences[:6],compile_exit=0,run_exit=0))
    diagnostics={
        'compiler-warning':source+'\n#warning forced diagnostic\n',
        'compiler-error':source+'\n#error forced error\n',
        'stderr':source.replace('int main() {','int main() { std::cerr << "forced";'),
        'extra-output':source.replace('int main() {','int main() { std::cout << "extra\\n";'),
    }
    guards=[]
    for name,text in diagnostics.items():
        try: native_run(text,out,'native-guard-'+name,fs)
        except ValueError as e: guards.append(dict(name=name,reason=str(e)))
        else: raise ValueError('native diagnostic accepted '+name)
    return records,guards


def source_controls(manifest,before,candidate,out):
    identities=[]
    for i,name in enumerate(manifest):
        p=out/('identity-'+str(i));p.write_bytes((ROOT/name).read_bytes()+b'\nidentity mutation\n')
        try: authenticate(manifest,{name:p})
        except ValueError: identities.append(name)
        else: raise ValueError('source identity mutation accepted')
    guards=[]
    changes={'outside-function':('/* This Source Code Form','/* Mutated Source Code Form'),
             'clearance':('if (kid == aClearanceFrame)','if (kid != aClearanceFrame)'),
             'sibling':('if (isEmpty) {','if (!isEmpty) {'),
             'guard':('borderPadding.BEnd(wm) != 0','borderPadding.BEnd(wm) == 0')}
    for name,(old,new) in changes.items():
        if old not in candidate: raise ValueError('missing preservation marker')
        try: bridge.preservation(before,candidate.replace(old,new,1))
        except ValueError: guards.append(name)
        else: raise ValueError('preservation mutation accepted')
    return identities,guards


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((BASE/'SOURCE-v1.json').read_text());authenticate(manifest)
    for key,path in [('lean',LEAN),('clang',CLANG)]:
        if digest(path)!=TOOLCHAIN[key+'_sha256']: raise ValueError('toolchain identity mismatch')
    before=(BASE/'native-before.cpp').read_text();candidate=(BASE/'native-candidate.cpp').read_text()
    preserved=bridge.preservation(before,candidate)
    audits=audit_lean(BASE/'Collapse.lean',out/'lean.log')
    lm,lg=lean_controls(out)
    fs=fixtures.fixtures();(out/'fixtures.json').write_text(json.dumps(fs,indent=2)+'\n')
    old=native_run(bridge.source(before),out,'original',fs)
    current=native_run(bridge.source(candidate),out,'candidate',fs)
    for key,outputs in [('original_expected',old),('candidate_expected',current)]:
        bad=[f['name'] for f,o in zip(fs,outputs) if o!=f[key]]
        if bad: raise ValueError('native reference mismatch '+str(bad[:5]))
    model=out/'ModelCases.lean';model.write_text(lean_cases.render((BASE/'Collapse.lean').read_text(),fs))
    r=run([LEAN,model],out/'model-cases.log')
    expected=(out/'lean.log').read_text().splitlines()+lean_cases.expected(fs)
    if r.returncode or r.stderr or r.stdout.splitlines()!=expected:
        raise ValueError('Lean executable model/native fixture mismatch')
    nm,ng=native_controls(bridge.source(candidate),out,fs,current)
    sg,pg=source_controls(manifest,before,candidate,out)
    authenticate(manifest)
    receipt=dict(result='PASS',source_manifest_sha256=digest(BASE/'SOURCE-v1.json'),native_preservation=preserved,
        theorem_axioms=audits,lean_exit=0,lean_semantic_mutations_rejected=lm,lean_diagnostic_guards=lg,
        native_cases=len(fs),domains=dict(Counter(f['domain'] for f in fs)),original_compile_exit=0,original_run_exit=0,
        candidate_compile_exit=0,candidate_run_exit=0,original_reference_mismatches=0,candidate_reference_mismatches=0,
        operational_before_after_changes=sum(a!=b for a,b in zip(old,current)),
        changed_domains=dict(Counter(f['domain'] for f,a,b in zip(fs,old,current) if a!=b)),
        lean_normal_tree_evaluations=len(lean_cases.expected(fs)),lean_model_native_mismatches=0,
        fixtures_sha256=digest(out/'fixtures.json'),native_semantic_mutations=nm,native_diagnostic_guards=ng,
        source_identity_guards=sg,preservation_guards=pg,
        limitations=['Lean pure finite normal-tree model, not compiled C++ proof','ReflowInput sizes, style eligibility, hidden flags and wrapper descent supplied by adapters',
            'exact full native function and exact CollapsingMargin class, with finite adapter providers','Writing modes normalized to supplied logical inputs; physical conversion not proved',
            'overflow/next-in-flow output initialization preserved in finite operational fixtures, not all-fragment emptiness theorem',
            'fragment consumption, min/max/box-sizing provider correctness, global IsSelfEmpty and whole browser outside proof',
            'endpoint witness modeled as ten times pixel-valued expression at integral bases; floating-point parser evaluation not proved'])
    (out/'RECEIPT-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__=='__main__': main()
