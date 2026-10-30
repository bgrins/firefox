from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
HERE = Path(__file__).resolve().parent
RUSTC = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
source = (HERE / 'candidate/servo/components/style/custom_properties.rs').read_text()
start = source.index("enum SubstitutionInput<'a>")
end = source.index('\n\nfn apply_substituted_value', start)
assert source[start:end] in (HERE / 'borrow-after.rs').read_text()
with tempfile.TemporaryDirectory(prefix='css-selected-color-borrow-') as temp:
    temp = Path(temp)
    for name in ('borrow-common.rs','borrow-before.rs','borrow-after.rs'):
        shutil.copyfile(HERE / name, temp / name)
    results = {}
    commands = [('before', [str(RUSTC),'--edition=2024',str(temp/'borrow-before.rs'),'-o',str(temp/'before')]),
                ('after', [str(RUSTC),'--edition=2024','--test',str(temp/'borrow-after.rs'),'-o',str(temp/'after')])]
    for name, command in commands:
        result = subprocess.run(command,capture_output=True,text=True)
        (HERE / (name + '-compile.log')).write_text(result.stdout+result.stderr)
        results[name] = {'exit':result.returncode,'command':command}
        if name == 'before': assert result.returncode != 0 and 'E0502' in result.stderr
        else: assert result.returncode == 0, result.stderr
    result = subprocess.run([str(temp/'after')],capture_output=True,text=True)
    (HERE/'borrow-tests.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0 and '5 passed' in result.stdout, result
    results['tests'] = {'exit':result.returncode,'passed':5}
    results['scratch'] = str(temp)
assert not temp.exists()
results.update(scratch_removed=True, native_compile=False, scope='Lifetime analogue with exact input enum; fake context/substitution computation, not Stylo type checking', compiler_sha256=hashlib.sha256(RUSTC.read_bytes()).hexdigest())
(HERE/'BORROW-CHECK.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
