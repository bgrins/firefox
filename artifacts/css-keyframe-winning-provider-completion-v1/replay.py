import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
RUSTC = Path('/Users/bgrins/.cargo/bin/rustc')


def run(command, output):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (HERE / output).write_bytes(result.stdout)
    return {'command': command, 'exit': result.returncode, 'log': output}


def main():
    assert not (HERE / 'REPLAY.json').exists()
    receipts = [run([str(RUSTC), '--version', '--verbose'], 'rustc-version.log')]
    scratch = Path(tempfile.mkdtemp(prefix='winning-provider-completion-'))
    try:
        binary = scratch / 'scheduler-tests'
        receipts.append(run([str(RUSTC), '--edition=2024', '--test', '-C', 'codegen-units=1',
                             str(HERE / 'scheduler_tests.rs'), '-o', str(binary)], 'compile.log'))
        assert receipts[-1]['exit'] == 0
        receipts.append(run([str(binary), '--test-threads=1'], 'tests.log'))
        assert receipts[-1]['exit'] == 0
        tests = (HERE / 'tests.log').read_text()
        assert len(re.findall(r'^test .* \.\.\. ok$', tests, re.M)) == 13
        core = json.dumps(str(HERE / 'winning_provider_completion.rs'))
        cases = {
            'incomplete-publication': (f'''#[path = {core}] mod scheduler;
use scheduler::*;
use std::collections::HashMap;
fn main() {{
 let mut work = WinningProviders::<(), u32, u32, ()>::new((), HashMap::new());
 assert!(work.admit(1, Winner::Pending(())).is_ok());
 let Err(incomplete) = work.resolve_all(|_,_,_,_| Evaluation::<u32,u32,(),()>::Error(())) else {{ panic!() }};
 let _ = incomplete.into_parts();
}}
''', 'E0599', 'no method named `into_parts`'),
            'forged-completion': (f'''#[path = {core}] mod scheduler;
use scheduler::*;
use std::collections::HashMap;
fn main() {{
 let _ = CompleteProviders::<(),u32,u32,()> {{ context: (), values: HashMap::new(), effects: Vec::new() }};
}}
''', 'E0451', 'are private'),
        }
        for name, (source, code, message) in cases.items():
            path = scratch / (name + '.rs')
            path.write_text(source)
            (HERE / (name + '.rs.txt')).write_text(source)
            receipts.append(run([str(RUSTC), '--edition=2024', '-Awarnings', '--emit=metadata',
                                 str(path), '-o', str(scratch / (name + '.rmeta'))], name + '.log'))
            log = (HERE / (name + '.log')).read_text()
            assert receipts[-1]['exit'] == 1 and message in log
            assert re.findall(r'^error\[(E\d+)\]:', log, re.M) == [code]
            assert not re.search(r'overflow|failed to resolve|couldn.t read|warning:', log, re.I)
        original = scratch / 'transport'
        shutil.copytree(HERE / 'original', original)
        for reverse, manifest in [(False, 'POSTIMAGES.json'), (True, 'PREIMAGES.json')]:
            command = ['patch', '--batch', '-p1'] + (['-R'] if reverse else [])
            result = subprocess.run(command, cwd=original, input=(HERE / 'native.patch').read_bytes(),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            log = 'reverse.log' if reverse else 'forward.log'
            (HERE / log).write_bytes(result.stdout)
            receipts.append({'command': command, 'exit': result.returncode, 'log': log})
            assert result.returncode == 0
            for name, expected in json.loads((HERE / manifest).read_text()).items():
                path = original / name
                assert (hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None) == expected
    finally:
        shutil.rmtree(scratch)
    (HERE / 'REPLAY.json').write_text(json.dumps({
        'status': 'ISOLATED_SCHEDULER_AND_TRANSPORT_PASS', 'tests': 13,
        'typed_publication_refusals': 2, 'receipts': receipts,
        'scratch_removed': not scratch.exists(), 'native_adapter_compiled': False,
        'css_endpoint_resolver_invoked': False, 'browser_execution': False,
        'native_live_changes': False,
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
