import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import bridge

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
TOOLS = json.loads((BASE/'TOOLCHAIN-v1.json').read_text())
THEOREMS = ['positive_slope_bounds','negative_slope_bounds','endpoint_containment',
            'first_endpoint','second_endpoint','product_bound','subtraction_ranges',
            'all_intermediates_representable','wide_evaluation_exact','old_defined_compatibility',
            'translation_invariance','common_offset_difference_bound',
            'common_reflection_difference_bound','rounding_anchor_counterexample','old_product_counterexample']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, log, stdin=None):
    p=subprocess.run([str(x) for x in command],input=stdin,text=True,capture_output=True)
    log.write_text(p.stdout+p.stderr)
    return p


def authenticate(manifest,replacements=None):
    replacements=replacements or {}
    for name,expected in manifest.items():
        p=replacements.get(name,ROOT/name)
        if not p.is_file() or digest(p)!=expected:
            raise ValueError('source identity mismatch: '+name)


def mutate(source,old,new):
    if source.count(old)!=1:
        raise ValueError('ambiguous mutation: '+old)
    return source.replace(old,new,1)


def audit_lean(path,log):
    source=path.read_text()
    if re.findall(r'^#print axioms (\w+)$',source,re.M)!=THEOREMS:
        raise ValueError('theorem audit inventory changed')
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s',source,re.M):
        raise ValueError('untrusted proof declaration')
    p=run([TOOLS['lean'],path],log)
    if p.returncode or p.stderr or len(p.stdout.splitlines())!=len(THEOREMS):
        raise ValueError('Lean failure or unexpected diagnostic')
    audits={}
    for name,line in zip(THEOREMS,p.stdout.splitlines()):
        prefix=f"'PolygonInterpolation.{name}' "
        if line==prefix+'does not depend on any axioms':
            audits[name]=[]
            continue
        match=re.fullmatch(re.escape(prefix)+r'depends on axioms: \[([^\]]+)\]',line)
        if not match:
            raise ValueError('unexpected axiom report')
        values=match[1].split(', ')
        if not set(values)<={'propext','Quot.sound','Classical.choice'}:
            raise ValueError('unapproved axiom')
        audits[name]=values
    return audits


def lean_controls(out):
    source=(BASE/'Interpolation.lean').read_text()
    changes={
        'floor-instead-of-truncate':('(n * dx).tdiv d','(n * dx) / d'),
        'drop-offset-factor':('(n * dx).tdiv d','dx.tdiv d'),
        'wrong-denominator':('(n * dx).tdiv d','(n * dx).tdiv (d+1)'),
        'wrong-anchor':('x1 + delta (y - y1) (x2 - x1) (y2 - y1)','x2 + delta (y - y1) (x2 - x1) (y2 - y1)'),
        'remove-y-difference-bound':('y2 - y1 ≤ 2147483646 ∧','True ∧'),
        'wide-model-narrow-product':('if fits64 product ∧ fits32 step','if fits32 product ∧ fits32 step'),
        'translated-y-wrong-sign':('(y+ty) =\n      interpolate','(y-ty) =\n      interpolate'),
    }
    rejected=[]
    for name,(old,new) in changes.items():
        path=out/('lean-mutation-'+name+'.lean');path.write_text(mutate(source,old,new))
        p=run([TOOLS['lean'],path],path.with_suffix('.log'))
        if not p.returncode or 'error:' not in p.stdout:
            raise ValueError('Lean semantic mutation accepted: '+name)
        rejected.append(name)
    guards={
        'missing-audit':source.replace('#print axioms first_endpoint\n',''),
        'extra-output':source+'\n#check Nat\n',
        'stderr-output':source+'\n#eval IO.eprintln "unexpected diagnostic"\n',
        'sorry':source.replace(':= by decide',':= by sorry',1),
        'axiom':source+'\naxiom fabricated : False\n',
        'syntax':source+'\nthis is not Lean\n',
    }
    diagnostics=[]
    for name,value in guards.items():
        path=out/('lean-guard-'+name+'.lean');path.write_text(value)
        try:
            audit_lean(path,path.with_suffix('.log'))
        except ValueError:
            diagnostics.append(name)
        else:
            raise ValueError('Lean diagnostic guard accepted: '+name)
    return rejected,diagnostics


def compile_source(source,out,name):
    path=out/(name+'.cpp');path.write_text(source);binary=out/name
    p=run([TOOLS['clang'],'-std=c++20','-O1','-Wall','-Wextra','-Werror',
           '-fsanitize=undefined,implicit-integer-truncation','-fno-sanitize-recover=all',path,'-o',binary],
          out/(name+'-compile.log'))
    if p.returncode or p.stdout or p.stderr:
        raise ValueError('compile error or diagnostic: '+name)
    return binary


def native_run(binary,rows,out,name,mode='new'):
    p=run([binary,mode],out/(name+'-run.log'),''.join(' '.join(map(str,row))+'\n' for row in rows))
    if p.returncode or p.stderr:
        raise ValueError('native error or diagnostic: '+name)
    actual=[int(line) for line in p.stdout.splitlines()]
    if len(actual)!=len(rows):
        raise ValueError('native output count')
    return sum(value!=bridge.expected(row) for value,row in zip(actual,rows))


def require_overflow(binary,row,out,name,mode='new'):
    p=run([binary,mode],out/(name+'.log'),' '.join(map(str,row))+'\n')
    if not p.returncode or 'signed integer overflow' not in p.stderr:
        raise ValueError('missing UBSan premise rejection: '+name)
    return {'name':name,'rejected':'signed integer overflow'}


def native_controls(source,rows,out):
    old=bridge.BINDING['candidate_return']
    changes={
        'wrong-anchor':(old,old.replace('return aP1.x','return aP2.x')),
        'reverse-horizontal-difference':(old,old.replace('aP2.x - aP1.x','aP1.x - aP2.x')),
        'offset-plus-one':(old,old.replace('aY - aP1.y,','aY - aP1.y + 1,')),
        'denominator-plus-one':('/ int64_t(aDiv);','/ (int64_t(aDiv) + 1);'),
        'truncate-whole-value':(old,'return (int64_t(aP1.x) * (aP2.y - aP1.y) + int64_t(aY - aP1.y) * (aP2.x - aP1.x)) / (aP2.y - aP1.y);'),
    }
    small=[row for row in rows if all(-5<=v<=5 for v in row)]
    small.append((5,0,4,2,1))
    rejected=[]
    for name,(a,b) in changes.items():
        binary=compile_source(mutate(source,a,b),out,'native-mutation-'+name)
        count=native_run(binary,small,out,'native-mutation-'+name)
        if not count:
            raise ValueError('native semantic mutation accepted: '+name)
        rejected.append({'name':name,'mismatches':count})
    narrow=mutate(source,'int64_t(aMult1) * int64_t(aMult2)','int64_t(aMult1 * aMult2)')
    binary=compile_source(narrow,out,'native-mutation-late-widening')
    rejected.append(require_overflow(binary,(0,0,600000,600000,12000),out,'late-widening'))
    return rejected


def source_controls(manifest,candidate,out):
    identities=[];path=out/'identity-guard-input'
    for name in manifest:
        path.write_bytes((ROOT/name).read_bytes()+b'\nchanged\n')
        try:
            authenticate(manifest,{name:path})
        except ValueError:
            identities.append(name)
        else:
            raise ValueError('identity guard accepted')
    preservation=[]
    for name,old,new in [
        ('wrong-helper',bridge.BINDING['candidate_return'],bridge.BINDING['original_return']),
        ('remove-y-assertion','aP1.y <= aY && aY <= aP2.y','true'),
        ('remove-horizontal-assertion','aP1.y != aP2.y','true'),
        ('unrelated-source','// Solve for x in the linear equation:','// Altered formula description:'),
    ]:
        if old not in candidate:
            raise ValueError('missing preservation target')
        try:
            bridge.validate(candidate.replace(old,new,1))
        except ValueError:
            preservation.append(name)
        else:
            raise ValueError('preservation guard accepted')
    return identities,preservation


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    out=parser.parse_args().out.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((BASE/'SOURCE-v1.json').read_text());authenticate(manifest)
    for name in ['lean','clang']:
        if digest(Path(TOOLS[name]))!=TOOLS[name+'_sha256']:
            raise ValueError('toolchain executable identity changed')
    candidate=(ROOT/bridge.BINDING['native_path']).read_text()
    helper=(ROOT/bridge.BINDING['helper_path']).read_text()
    extracted=bridge.snippets(candidate,helper)
    for name,value in extracted.items():
        if (BASE/name).read_text()!=value+'\n':
            raise ValueError('checked-in extraction drift')
    audits=audit_lean(BASE/'Interpolation.lean',out/'lean.log')
    lean_mutations,lean_diagnostics=lean_controls(out)
    rows=bridge.fixtures();old_rows=[r for r in rows if bridge.old_defined(r)]
    (out/'fixtures.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
    source=bridge.source(candidate,helper);binary=compile_source(source,out,'native')
    if native_run(binary,rows,out,'candidate') or native_run(binary,old_rows,out,'original','old'):
        raise ValueError('native/oracle mismatch')
    mutations=native_controls(source,rows,out)
    overflows=[require_overflow(binary,(0,0,600000,600000,12000),out,'original-overflow','old'),
               require_overflow(binary,(bridge.MIN,0,bridge.MAX,2,1),out,'out-of-domain-subtraction')]
    diagnostics=[]
    for name,value in {
        'compiler-warning':source+'\n#warning deliberate diagnostic\n',
        'compiler-syntax':source+'\nthis is not C++;\n',
        'runtime-stderr':source.replace('if (argc != 2) return 2;','if (argc != 2) return 2; std::cerr << "unexpected diagnostic";'),
    }.items():
        try:
            guarded=compile_source(value,out,'native-guard-'+name)
            native_run(guarded,rows[:1],out,'native-guard-'+name)
        except ValueError:
            diagnostics.append(name)
        else:
            raise ValueError('native diagnostic guard accepted')
    identities,preservation=source_controls(manifest,candidate,out)
    authenticate(manifest)
    receipt={'result':'PASS','source_manifest_sha256':digest(BASE/'SOURCE-v1.json'),
        'theorem_axioms':audits,'lean_mutations':lean_mutations,'lean_diagnostic_guards':lean_diagnostics,
        'native_bounded_cases':len(rows),'original_defined_cases':len(old_rows),
        'native_mutations':mutations,'overflow_controls':overflows,'native_diagnostic_guards':diagnostics,
        'identity_guards':identities,'preservation_guards':preservation,
        'extracted_sources':{n:bridge.sha(s) for n,s in extracted.items()},
        'fixture_sha256':digest(out/'fixtures.json'),
        'limits':['bounded final-coordinate differences <= 2*(2^30-1)',
                  'inclusive sorted y; representable endpoints; defined upstream resolution/preprocessing',
                  'integer model and finite native bridge, not full C++ or layout semantics',
                  'not arbitrary full-int32 endpoints, NaN handling, full polygon or rasterization proof']}
    (out/'RECEIPT-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
