import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S, without optimization')
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parent

def require(value, message):
    if not value:
        raise ValueError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)

def authenticate(expected):
    for name in ('FILES.json', 'FREEZE.json'):
        require(stat.S_ISREG((ROOT / name).lstat().st_mode), 'nonregular seal')
    require(digest(ROOT / 'FILES.json') == expected, 'external manifest mismatch')
    files = read('FILES.json')
    require(isinstance(files, dict) and files, 'bad manifest')
    directories = set()
    for name, value in files.items():
        require(isinstance(name, str) and isinstance(value, str), 'bad row')
        path = PurePosixPath(name)
        require(str(path) == name and not path.is_absolute() and
                '..' not in path.parts and name not in ('FILES.json', 'FREEZE.json'),
                'unsafe manifest path')
        require(len(value) == 64 and all(c in '0123456789abcdef' for c in value), 'bad digest')
        directories.update(str(parent) for parent in path.parents if str(parent) != '.')
    found = set()
    def walk(directory):
        for entry in os.scandir(directory):
            path = Path(entry.path)
            relative = path.relative_to(ROOT).as_posix()
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                require(relative in directories, 'unexpected directory: ' + relative)
                walk(path)
            else:
                require(stat.S_ISREG(mode), 'nonregular input: ' + relative)
                if relative in ('FILES.json', 'FREEZE.json'):
                    continue
                require(relative in files, 'unexpected file: ' + relative)
                require(digest(path) == files[relative], 'input hash mismatch: ' + relative)
                found.add(relative)
    walk(ROOT)
    require(found == set(files), 'missing input')
    freeze = read('FREEZE.json')
    require(freeze['FILES_sha256'] == expected and
            freeze['check_sha256'] == digest(ROOT / 'check.py'), 'seal mismatch')
    return files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--files-sha256', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    files = authenticate(args.files_sha256)
    output = Path(args.output)
    require(output.is_absolute() and not output.exists() and not output.is_symlink(),
            'output must be new absolute path')
    output = output.resolve()
    require(output != ROOT and ROOT not in output.parents, 'output must be outside source')
    toolchain = read('TOOLCHAIN.json')
    lean = Path(toolchain['lean'])
    require(digest(lean) == toolchain['sha256'], 'Lean executable mismatch')
    inputs = read('INPUTS.json')
    predecessor = read('predecessor/FILES.json')
    require(digest(ROOT / 'predecessor/FILES.json') == inputs['producer']['FILES_sha256'],
            'predecessor manifest mismatch')
    require(digest(ROOT / 'predecessor/FREEZE.json') == inputs['producer']['FREEZE_sha256'],
            'predecessor seal mismatch')
    require(digest(ROOT / 'predecessor/REVIEW-FILES.json') == inputs['review']['FILES_sha256'],
            'review manifest mismatch')
    for name, value in inputs['copied_modules'].items():
        require(digest(ROOT / 'lean' / name) == value == predecessor['lean/' + name],
                'changed inherited proof')
    require(digest(ROOT / 'predecessor/IndependentChallenges.lean') ==
            inputs['independent_challenges_sha256'] ==
            read('predecessor/REVIEW-FILES.json')['capsule/Challenges.lean'],
            'independent challenge transfer mismatch')
    require(digest(ROOT / 'predecessor/SOURCE-BINDINGS.json') ==
            predecessor['SOURCE-BINDINGS.json'], 'inherited source bindings mismatch')
    prior_bindings = read('predecessor/SOURCE-BINDINGS.json')
    for row in read('SOURCE-PINS.json'):
        require(digest(ROOT / row['file']) == row['sha256'] == predecessor[row['file']],
                'source role pin mismatch')
    for roster in ('SOURCE-BINDINGS.json', 'STORAGE-DECLARATIONS.json'):
        for row in read(roster):
            require(row['file'] in predecessor, 'unknown source binding file')
            start, end = row['start_byte_utf8'], row['end_byte_utf8']
            data = (ROOT / row['file']).read_bytes()
            require(type(start) is int and type(end) is int and 0 <= start < end <= len(data),
                    'invalid source slice')
            selected = data[start:end]
            require(selected == row['text'].encode() and
                    hashlib.sha256(selected).hexdigest() == row['sha256'], 'source slice mismatch')
            if roster == 'SOURCE-BINDINGS.json':
                require(row in prior_bindings, 'changed inherited source binding')
    modules = ['Deletion', 'PropertyPhase', 'Representation', 'Ownership',
               'RefinementWitnesses', 'NestedWitness', 'BoundaryMutants', 'Audit']
    names = []
    for module in modules[:-1]:
        text = (ROOT / 'lean' / (module + '.lean')).read_text()
        require(not re.search(r'\b(sorry|admit|axiom|unsafe)\b', text), 'unsupported proof escape')
        namespace = 'Destruction.' if module in modules[:2] else 'Destruction.Ownership.'
        names.extend({'module': module, 'name': namespace + name}
                     for name in re.findall(r'^theorem (\w+)', text, re.M))
    require(names == read('AUDIT-NAMES.json'), 'audit roster mismatch')
    require(re.findall(r'^#print axioms (\S+)$', (ROOT / 'lean/Audit.lean').read_text(), re.M) ==
            [row['name'] for row in names], 'audit commands mismatch')
    output.mkdir(parents=True)
    proof = output / 'proof'
    proof.mkdir()
    env = os.environ.copy()
    env['LEAN_PATH'] = str(proof)
    env.pop('LEAN_OPTS', None)
    commands = []
    def invoke(label, source, target=None, cwd=None):
        command = [str(lean)]
        if target:
            command += ['-o', str(target)]
        command.append(str(source))
        working = cwd or ROOT / 'lean'
        result = subprocess.run(command, cwd=working, env=env, text=True, capture_output=True)
        (output / (label + '.stdout')).write_text(result.stdout)
        (output / (label + '.stderr')).write_text(result.stderr)
        commands.append({'label': label, 'command': command, 'cwd': str(working),
                         'exit': result.returncode, 'LEAN_PATH': str(proof)})
        (output / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
        return result
    for module in modules:
        result = invoke(module, ROOT / 'lean' / (module + '.lean'), proof / (module + '.olean'))
        require(result.returncode == 0 and not result.stderr, 'Lean compilation failed: ' + module)
        require(module == 'Audit' or not result.stdout, 'unexpected Lean output: ' + module)
    audit = (output / 'Audit.stdout').read_text()
    observed = re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)", audit)
    require(observed == [row['name'] for row in names], 'printed axiom roster mismatch')
    for group in re.findall(r'depends on axioms:\s*\[([^]]*)\]', audit):
        require(set(re.findall(r'[A-Za-z][A-Za-z0-9_.]*', group)) <=
                {'propext', 'Classical.choice', 'Quot.sound'}, 'unexpected axiom')
    for mutation in read('FALSECLAIMS.json'):
        copied = proof / (mutation + '.lean')
        copied.write_bytes((ROOT / 'falseclaims' / (mutation + '.lean')).read_bytes())
        result = invoke(mutation, copied, cwd=proof)
        require(result.returncode != 0 and 'decide' in result.stdout and
                'false' in result.stdout and not result.stderr,
                'mutation did not fail by intended semantic decision: ' + mutation)
    authenticate(args.files_sha256)
    report = {'result': 'PASS', 'inputs': len(files), 'modules': len(modules),
              'audits': len(names), 'semantic_falseclaim_controls': len(read('FALSECLAIMS.json')),
              'inherited_audits': sum(row['module'] in modules[:2] for row in names),
              'storage_declarations': len(read('STORAGE-DECLARATIONS.json')),
              'source_bindings': len(read('SOURCE-BINDINGS.json')),
              'FILES_sha256': args.files_sha256,
              'scope': 'selected world ownership preservation; native decoding/event completeness/capture lifetime open'}
    (output / 'RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
