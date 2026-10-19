import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(expected):
    manifest = BASE / 'MANIFEST.json'
    if sha(manifest) != expected:
        raise ValueError('manifest identity mismatch')
    pins = json.loads(manifest.read_text())['files']
    if any(p.is_symlink() for p in BASE.rglob('*')
           if p.relative_to(BASE).parts[0] != 'development'):
        raise ValueError('source closure contains a symlink')
    actual = {str(p.relative_to(BASE)) for p in BASE.rglob('*') if p.is_file()
              and p.relative_to(BASE).parts[0] != 'development'
              and str(p.relative_to(BASE)) not in {'MANIFEST.json', 'FREEZE.json'}}
    if actual != set(pins):
        raise ValueError('source closure differs from manifest')
    for name, digest in pins.items():
        p = BASE / name
        if p.is_symlink() or sha(p) != digest:
            raise ValueError('source identity mismatch: ' + name)
    return pins


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(command, log):
    result = subprocess.run([str(x) for x in command], capture_output=True)
    log.write_bytes(result.stdout + result.stderr)
    if result.returncode or result.stdout or result.stderr:
        raise ValueError('compile failed or emitted diagnostics: ' + str(log))


def replay(output, lean):
    provenance = json.loads((BASE / 'SOURCE-PROVENANCE.json').read_text())
    lean_expected = next(v for k, v in provenance['retained_externals'].items()
                         if k.endswith('/bin/lean'))
    if sha(lean) != lean_expected:
        raise ValueError('Lean executable differs from accepted toolchain')
    cxx = Path(shutil.which('clang++')).resolve()
    tool = json.loads((BASE / 'source/artifacts/css-sigma-proof-v1/TOOLCHAIN-v1.json').read_text())
    if sha(cxx) != tool['clang_driver_sha256']:
        raise ValueError('clang executable differs from accepted toolchain')
    output.mkdir(parents=True, exist_ok=False)
    root = output / 'worktree'
    shutil.copytree(BASE / 'source', root)
    original = root / 'artifacts/css-sigma-proof-v1'
    icu = root / 'intl/icu/source/common'
    includes = root / 'objdir-full.noindex/dist/include'
    (includes / 'mozilla').mkdir(parents=True)
    for p in (root / 'mfbt').glob('*.h'):
        shutil.copyfile(p, includes / 'mozilla' / p.name)
    for p in (icu / 'unicode').glob('*.h'):
        q = includes / 'unicode' / p.name
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
    obj = root / 'objdir-full.noindex/config/external/icu/common/ucase.o'
    obj.parent.mkdir(parents=True)
    command = [cxx, '-std=c++20', '-O2', '-ffunction-sections', '-fdata-sections',
               '-DU_STATIC_IMPLEMENTATION', '-DU_COMMON_IMPLEMENTATION',
               '-I', icu, '-MMD', '-MF', output / 'ucase.d', '-c', icu / 'ucase.cpp',
               '-o', obj]
    run(command, output / 'ucase-build.log')
    dependency_text = (output / 'ucase.d').read_text().replace('\\\n', ' ')
    dependencies = dependency_text.split(':', 1)[1].split()
    for name in dependencies:
        p = Path(name).resolve()
        relative = p.relative_to(root)
        if sha(p) != sha(BASE / 'source' / relative):
            raise ValueError('ICU dependency differs from pinned source: ' + name)
    module = load('check', original / 'check.py')
    module.ROOT, module.BASE, module.LEAN, module.ICU_OBJECT = root, original, lean, obj
    bridge = load('bridge', original / 'bridge.py')
    bridge.ROOT, bridge.BASE, bridge.OBJECT = root, original, obj
    paths = {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file()}
    module.authenticate(paths)
    axioms = module.audit_lean(original / 'Sigma.lean', output / 'lean.log')
    mutations, guards = module.lean_controls(output)
    record = {'lean_audits': axioms, 'lean_mutations': mutations, 'diagnostic_guards': guards}
    record['native'] = bridge.check(output)
    record['source_identity_controls'] = module.identity_controls(paths, output)
    module.authenticate(paths)
    historical = json.loads((BASE / 'provenance/css-sigma-proof-v1/root-replay-v1/PROOF-v1.json').read_text())
    for field in ['lean_audits', 'lean_mutations', 'diagnostic_guards', 'source_identity_controls']:
        if record[field] != historical[field]:
            raise ValueError('accepted semantic result changed: ' + field)
    for field in ['icu_codepoints', 'checks', 'preserved_non_sigma_native_tokens',
                  'native_mutations', 'preservation_controls']:
        if record['native'][field] != historical['native'][field]:
            raise ValueError('accepted native semantic result changed: ' + field)
    record['packaging'] = {
        'historical_semantic_fields_equal': True,
        'compiler': str(cxx), 'compiler_sha256': sha(cxx),
        'lean': str(lean), 'lean_sha256': sha(lean),
        'icu_object_built_from_source_sha256': sha(obj),
        'historical_icu_object_sha256': next(v for k, v in provenance['retained_externals'].items()
                                             if k.endswith('/ucase.o')),
        'icu_compile_command': [str(x) for x in command],
        'icu_dependencies': {str(Path(p).relative_to(root)): sha(Path(p)) for p in dependencies},
        'source_snapshot': 'historical pinned caller snapshots; no live Gecko reads',
        'scope': 'Packaging replay of accepted Sigma model/helper checks; no expanded native or caller theorem.'}
    (output / 'RESULT.json').write_text(json.dumps(record, indent=2) + '\n')
    return {'native_decisions': record['native']['checks'],
            'icu_codepoints': record['native']['icu_codepoints'],
            'lean_audits': len(axioms), 'historical_semantic_fields_equal': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--authenticate-only', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--lean', type=Path)
    args = parser.parse_args()
    authenticate(args.manifest_sha256)
    if args.authenticate_only:
        print('authenticated source closure')
        return
    if args.output is None or args.lean is None:
        parser.error('--output and --lean are required for replay')
    output = args.output.resolve()
    if output == BASE or BASE in output.parents:
        raise ValueError('output must be outside the frozen capsule')
    result = replay(output, args.lean.resolve())
    authenticate(args.manifest_sha256)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
