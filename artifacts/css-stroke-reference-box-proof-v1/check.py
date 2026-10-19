import argparse
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
    if len(names) != 14 or len(set(names)) != 14:
        raise ValueError('missing or duplicate theorem audit')
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s', text, re.M):
        raise ValueError('untrusted proof declaration')
    result = run([LEAN, path], log)
    lines = result.stdout.splitlines()
    if result.returncode or result.stderr or len(lines) != len(names):
        raise ValueError('Lean failure or unexpected diagnostics')
    audits = {}
    for name, line in zip(names, lines):
        prefix = f"'ReferenceBox.{name}' "
        if line == prefix+'does not depend on any axioms':
            audits[name] = []
        else:
            match = re.fullmatch(re.escape(prefix)+r'depends on axioms: \[([^\]]*)\]', line)
            if not match:
                raise ValueError('unexpected axiom output')
            axioms = match[1].split(', ')
            if any(a != 'propext' for a in axioms):
                raise ValueError('unapproved axioms')
            audits[name] = axioms
    return audits


def lean_controls(out):
    original = (BASE/'ReferenceBox.lean').read_text()
    changes = {
        'stroke-as-content': ('if b = .fill ∨ b = .content then content else border', 'if b = .fill ∨ b = .content ∨ b = .stroke then content else border'),
        'fill-as-border': ('if b = .fill ∨ b = .content then content else border', 'if b = .content then content else border'),
        'swap-payloads': ('then content else border', 'then border else content'),
        'ignore-svg': ('if svg then svgProvider b else cssPayload b content border', 'if svg then cssPayload b content border else cssPayload b content border'),
        'always-unzoom': ('if needed then unzoom value else value', 'if needed then unzoom value else unzoom value'),
        'cache-overwrite-hit': ('if state.cached then state else ⟨true, resolved⟩', 'if state.cached then ⟨true, resolved⟩ else ⟨true, resolved⟩'),
        'cache-miss-retains-old': ('if state.cached then state else ⟨true, resolved⟩', 'if state.cached then state else ⟨true, state.value⟩'),
    }
    mutations = []
    for name, (old, new) in changes.items():
        if original.count(old) != 1:
            raise ValueError('ambiguous Lean mutation '+name)
        path = out/('lean-mutation-'+name+'.lean')
        path.write_text(original.replace(old,new))
        result = run([LEAN,path],path.with_suffix('.log'))
        if result.returncode == 0 or 'error' not in result.stdout:
            raise ValueError('Lean semantic mutation accepted '+name)
        mutations.append(name)
    guards = {
        'missing-audit': original.replace('#print axioms selector_contract\n',''),
        'extra-output': original+'\n#check Nat\n',
        'stderr-output': original+'\n#eval IO.eprintln "diagnostic"\n',
        'sorry': original.replace(':= rfl', ':= by sorry', 1),
        'axiom': original+'\naxiom forged : False\n',
        'syntax': original+'\nthis is not Lean\n',
    }
    rejected = []
    for name, text in guards.items():
        path = out/('lean-guard-'+name+'.lean')
        path.write_text(text)
        try:
            audit_lean(path,path.with_suffix('.log'))
        except ValueError as error:
            rejected.append({'name':name,'reason':str(error)})
        else:
            raise ValueError('Lean diagnostic guard accepted '+name)
    return mutations,rejected


def native_run(source, out, label, fixtures, expected='expected'):
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
    return sum(line != f[expected] for line,f in zip(lines,fixtures))


def native_controls(candidate, before, out, fixtures):
    original = bridge.source(candidate)
    changes = {
        'old-stroke-return': (bridge.extract(candidate), bridge.extract(before)),
        'content-uses-border': ('mFrame->GetContentRectRelativeToSelf()', 'mFrame->GetRect()'),
        'border-retains-frame-origin': ('MaybeUnzoom({0, 0, rect.Width(), rect.Height()})', 'MaybeUnzoom(rect)'),
        'border-height-from-width': ('rect.Width(), rect.Height()', 'rect.Width(), rect.Width()'),
        'skip-unzoom': ('mNeedsUnzooming ? zoom.Unzoom(aBox) : aBox', '(mNeedsUnzooming && false) ? zoom.Unzoom(aBox) : aBox'),
        'always-unzoom': ('mNeedsUnzooming ? zoom.Unzoom(aBox) : aBox', '(mNeedsUnzooming || true) ? zoom.Unzoom(aBox) : aBox'),
        'svg-uses-content': ('MaybeUnzoom(GetSVGBox(mFrame))', 'MaybeUnzoom(mFrame->GetContentRectRelativeToSelf())'),
        'cache-recomputes': ('if (mIsCached)', 'if (mIsCached && !mFrame)'),
        'cache-never-marked': ('mIsCached = true;', 'mIsCached = false;'),
    }
    records = []
    for name,(old,new) in changes.items():
        if original.count(old) != 1:
            raise ValueError('ambiguous native mutation '+name)
        mismatches = native_run(original.replace(old,new),out,'native-mutation-'+name,fixtures)
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
    for name,source in diagnostic_guards.items():
        try:
            native_run(source,out,'native-guard-'+name,fixtures)
        except ValueError as error:
            guards.append({'name':name,'reason':str(error)})
        else:
            raise ValueError('native diagnostic guard accepted '+name)
    return records,guards


def source_controls(manifest,before,candidate,out):
    rejected = []
    for name in manifest:
        path = out/('source-guard-'+str(len(rejected)))
        path.write_bytes((ROOT/name).read_bytes()+b'\nmutation\n')
        try:
            authenticate(manifest,{name:path})
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('identity guard accepted')
    changes = {
        'svg-provider-edit': ('static nsRect GetSVGBox(', 'static nsRect GetSVGBoxAltered('),
        'downstream-edit': ('float ProcessTranslatePart(', 'float ProcessTranslatePartAltered('),
        'cache-edit': ('if (mIsCached)', 'if (!mIsCached)'),
        'disabled-continuation-edit': ('#ifndef UNIFIED_CONTINUATIONS', '#if 1'),
    }
    preservation_guards = []
    for name,(old,new) in changes.items():
        if old not in candidate:
            raise ValueError('missing preservation marker')
        try:
            bridge.preservation(before,candidate.replace(old,new,1))
        except ValueError:
            preservation_guards.append(name)
        else:
            raise ValueError('preservation guard accepted')
    return rejected,preservation_guards


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
    preserved = bridge.preservation(before,candidate)
    audits = audit_lean(BASE/'ReferenceBox.lean',out/'lean.log')
    lean_mutations,lean_guards = lean_controls(out)
    fixtures = bridge.fixtures()
    (out/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    mismatches = native_run(bridge.source(candidate),out,'candidate',fixtures)
    old_mismatches = native_run(bridge.source(before),out,'original',fixtures,'original_expected')
    if mismatches or old_mismatches:
        raise ValueError('native oracle disagreement')
    native_mutations,native_guards = native_controls(candidate,before,out,fixtures)
    identities,preservation_guards = source_controls(manifest,before,candidate,out)
    authenticate(manifest)
    receipt = {'result':'PASS','source_manifest_sha256':digest(BASE/'SOURCE-v1.json'),
        'native_extraction':preserved,'theorem_axioms':audits,'lean_exit':0,
        'lean_semantic_mutations_rejected':lean_mutations,'lean_diagnostic_guards':lean_guards,
        'native_cases':len(fixtures),'native_candidate_mismatches':mismatches,'original_oracle_mismatches':old_mismatches,
        'candidate_compile_exit':0,'candidate_run_exit':0,'original_compile_exit':0,'original_run_exit':0,
        'original_spec_counterexamples':sum(f['expected']!=f['original_expected'] for f in fixtures),
        'fixtures_sha256':digest(out/'fixtures.json'),'native_mutations':native_mutations,'native_diagnostic_guards':native_guards,
        'source_guards':identities,'preservation_guards':preservation_guards,
        'limitations':['arbitrary-payload Lean model, not compiled C++ proof','finite exact-function C++ tests with frame/style/rectangle/unzoom adapters',
                       'SVG provider opaque','UNIFIED_CONTINUATIONS undefined','geometry and zoom arithmetic not proved',
                       'cache contract assumes fixed frame inputs and pure providers; no invalidation freshness theorem',
                       'no whole transform, caller, paint or browser theorem']}
    (out/'RECEIPT-v1.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
