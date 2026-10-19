import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess
from pathlib import Path
import bridge

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
    if len(names) != 15 or len(set(names)) != 15:
        raise ValueError('missing or duplicate theorem audit')
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s', text, re.M):
        raise ValueError('untrusted proof declaration')
    result = run([LEAN, path], log)
    lines = result.stdout.splitlines()
    if result.returncode or result.stderr or len(lines) != len(names):
        raise ValueError('Lean failure or unexpected diagnostics')
    audits = {}
    for name, line in zip(names, lines):
        prefix = f"'ObjectFit.{name}' "
        if line == prefix+'does not depend on any axioms':
            audits[name] = []
        else:
            match = re.fullmatch(re.escape(prefix)+r'depends on axioms: \[([^\]]*)\]', line)
            if not match:
                raise ValueError('unexpected axiom output')
            axioms = match[1].split(', ')
            if any(a not in {'propext', 'Quot.sound'} for a in axioms):
                raise ValueError('unapproved axioms')
            audits[name] = axioms
    return audits


def lean_controls(out):
    original = (BASE/'ObjectFit.lean').read_text()
    changes = {
        'missing-width-uses-height': ('width.getD constraint.width', 'width.getD constraint.height'),
        'missing-height-uses-width': ('height.getD constraint.height', 'height.getD constraint.width'),
        'none-fills': ('| .none => complete constraint width height', '| .none => constraint'),
        'scaledown-max': ('⟨min a.width b.width, min a.height b.height⟩', '⟨max a.width b.width, max a.height b.height⟩'),
        'scaledown-always-none': ('| .scaleDown => minimum (complete constraint width height) constraint', '| .scaleDown => complete constraint width height'),
        'zero-width-is-absent': ('width.getD constraint.width', '(if width = some 0 then constraint.width else width.getD constraint.width)'),
        'positive-none-dispatch-change': ('if fit = .fill then constraint else rest fit', 'if fit = .fill ∨ fit = .none then constraint else rest fit'),
    }
    mutations = []
    for name,(old,new) in changes.items():
        if original.count(old) != 1:
            raise ValueError('ambiguous Lean mutation '+name)
        path = out/('lean-mutation-'+name+'.lean')
        path.write_text(original.replace(old,new))
        result = run([LEAN,path],path.with_suffix('.log'))
        if result.returncode == 0 or 'error' not in result.stdout:
            raise ValueError('Lean semantic mutation accepted '+name)
        mutations.append(name)
    guards = {
        'missing-audit': original.replace('#print axioms none_width\n',''),
        'extra-output': original+'\n#check Nat\n',
        'stderr-output': original+'\n#eval IO.eprintln "diagnostic"\n',
        'sorry': original.replace(':= rfl', ':= by sorry', 1),
        'axiom': original+'\naxiom forged : False\n',
        'syntax': original+'\nthis is not Lean\n',
    }
    rejected = []
    for name,text in guards.items():
        path = out/('lean-guard-'+name+'.lean')
        path.write_text(text)
        try:
            audit_lean(path,path.with_suffix('.log'))
        except ValueError as error:
            rejected.append({'name':name,'reason':str(error)})
        else:
            raise ValueError('Lean diagnostic guard accepted '+name)
    return mutations,rejected


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
        if not re.fullmatch(r'-?\d+ -?\d+ \d+',line):
            raise ValueError('invalid native output '+label)
    return lines


def native_controls(candidate,before,renderer,out,fixtures,baseline):
    original = bridge.source(candidate,renderer)
    changes = {
        'old-no-ratio-fill': (bridge.NEW,bridge.OLD),
        'wrong-default-axis': ('return (aDimensionToCompute == eWidth) ? aDefaultObjectSize.width\n                                         : aDefaultObjectSize.height;',
                               'return (aDimensionToCompute == eWidth) ? aDefaultObjectSize.height\n                                         : aDefaultObjectSize.width;'),
        'zero-means-absent': ('if (specifiedWidth || specifiedHeight)', 'if ((specifiedWidth && *specifiedWidth != 0) || (specifiedHeight && *specifiedHeight != 0))'),
        'none-always-constraint': ('return *noneSize;', 'return aConstraintSize;'),
        'cover-becomes-contain': ('fitType.emplace(nsImageRenderer::COVER)', 'fitType.emplace(nsImageRenderer::CONTAIN)'),
        'scaledown-width-max': ('std::min(constrainedSize->width, noneSize->width)', 'std::max(constrainedSize->width, noneSize->width)'),
        'scaledown-height-max': ('std::min(constrainedSize->height, noneSize->height)', 'std::max(constrainedSize->height, noneSize->height)'),
    }
    records = []
    for name,(old,new) in changes.items():
        if original.count(old) != 1:
            raise ValueError('ambiguous native mutation '+name)
        lines = native_run(original.replace(old,new),out,'native-mutation-'+name,fixtures)
        mismatches = sum(a!=b for a,b in zip(lines,baseline))
        if not mismatches:
            raise ValueError('native mutation accepted '+name)
        records.append({'name':name,'mismatches':mismatches,'compile_exit':0,'run_exit':0})
    diagnostic_guards = {
        'compiler-warning': original+'\n#warning forced diagnostic\n',
        'compiler-error': original+'\n#error forced error\n',
        'runtime-stderr': original.replace('int main() {','int main() { std::cerr << "forced diagnostic";'),
        'runtime-extra-output': original.replace('int main() {','int main() { std::cout << "extra\\n";'),
    }
    guards = []
    for name,text in diagnostic_guards.items():
        try:
            native_run(text,out,'native-guard-'+name,fixtures)
        except ValueError as error:
            guards.append({'name':name,'reason':str(error)})
        else:
            raise ValueError('native diagnostic guard accepted '+name)
    return records,guards


def source_controls(manifest,before,candidate,renderer,out):
    identities = []
    for name in manifest:
        path = out/('source-guard-'+str(len(identities)))
        path.write_bytes((ROOT/name).read_bytes()+b'\nmutation\n')
        try:
            authenticate(manifest,{name:path})
        except ValueError:
            identities.append(name)
        else:
            raise ValueError('identity guard accepted')
    changes = {
        'missing-dimension-helper': ('return (aDimensionToCompute == eWidth)', 'return (aDimensionToCompute != eWidth)'),
        'none-helper': ('if (specifiedWidth || specifiedHeight)', 'if (specifiedWidth && specifiedHeight)'),
        'positive-dispatch': ('aObjectFit == StyleObjectFit::Cover', 'aObjectFit == StyleObjectFit::Contain'),
        'positioning-caller': ('imageTopLeftPt += aConstraintRect.TopLeft();', 'imageTopLeftPt -= aConstraintRect.TopLeft();'),
    }
    preservation_guards = []
    for name,(old,new) in changes.items():
        if old not in candidate:
            raise ValueError('missing preservation marker')
        try:
            bridge.preservation(before,candidate.replace(old,new,1),renderer)
        except ValueError:
            preservation_guards.append(name)
        else:
            raise ValueError('preservation guard accepted')
    return identities,preservation_guards


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    manifest = json.loads((BASE/'SOURCE-v1.json').read_text())
    authenticate(manifest)
    for key,path in [('lean',LEAN),('clang',CLANG)]:
        if digest(path) != TOOLCHAIN[key+'_sha256']:
            raise ValueError('toolchain identity mismatch')
    before = (BASE/'native-before.cpp').read_text()
    candidate = (BASE/'native-candidate.cpp').read_text()
    renderer = (BASE/'renderer.cpp').read_text()
    preserved = bridge.preservation(before,candidate,renderer)
    audits = audit_lean(BASE/'ObjectFit.lean',out/'lean.log')
    lean_mutations,lean_guards = lean_controls(out)
    fixtures = bridge.fixtures()
    (out/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    actual = native_run(bridge.source(candidate,renderer),out,'candidate',fixtures)
    old = native_run(bridge.source(before,renderer),out,'original',fixtures)
    candidate_mismatches = sum(got != f['candidate_expected'] for got,f in zip(actual,fixtures) if f['ratio'] is None)
    original_mismatches = sum(got != f['original_expected'] for got,f in zip(old,fixtures) if f['ratio'] is None)
    positive_mismatches = sum(a!=b for a,b,f in zip(actual,old,fixtures) if f['ratio'] is not None)
    if candidate_mismatches or original_mismatches or positive_mismatches:
        raise ValueError('native oracle or preservation disagreement')
    native_mutations,native_guards = native_controls(candidate,before,renderer,out,fixtures,actual)
    identities,preservation_guards = source_controls(manifest,before,candidate,renderer,out)
    authenticate(manifest)
    receipt = {'result':'PASS','source_manifest_sha256':digest(BASE/'SOURCE-v1.json'),
        'native_extractions':preserved,'theorem_axioms':audits,'lean_exit':0,
        'lean_semantic_mutations_rejected':lean_mutations,'lean_diagnostic_guards':lean_guards,
        'native_cases':len(fixtures),'domains':dict(Counter(f['domain'] for f in fixtures)),
        'candidate_no_ratio_oracle_mismatches':candidate_mismatches,'original_no_ratio_oracle_mismatches':original_mismatches,
        'positive_ratio_before_after_differences':positive_mismatches,
        'candidate_compile_exit':0,'candidate_run_exit':0,'original_compile_exit':0,'original_run_exit':0,
        'original_normative_counterexamples':sum(f['normative_oracle'] and a!=b for f,a,b in zip(fixtures,actual,old)),
        'original_counterexamples_by_domain':dict(Counter(f['domain'] for f,a,b in zip(fixtures,actual,old) if f['normative_oracle'] and a!=b)),
        'excluded_scaledown_boundary_changes':sum(f['domain']=='absent-both-boundary' and f['fit']==4 and a!=b for f,a,b in zip(fixtures,actual,old)),
        'fixtures_sha256':digest(out/'fixtures.json'),'native_mutations':native_mutations,'native_diagnostic_guards':native_guards,
        'source_guards':identities,'preservation_guards':preservation_guards,
        'limitations':['Lean natural-number optional-size model, not compiled C++ proof','ScaleDown ordered-choice theorem requires at most one supplied natural dimension',
                       'full exact sizing functions compiled with Maybe/Size/AspectRatio adapters','positive-ratio arithmetic opaque; only before/after preservation checked',
                       'no-ratio arithmetic-provider calls must remain zero','two-present no-ratio ScaleDown fixtures operational boundary only',
                       'source intrinsic-data/ratio relationship, callers, image decode/viewport/painting not proved']}
    (out/'RECEIPT-v1.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
