from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
HERE = Path(__file__).resolve().parent
RUSTC = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
source = (HERE / 'candidate/servo/components/style/custom_properties.rs').read_text()
start = source.index("enum SubstitutionInput<'a, 'b>")
end = source.index('\n\nfn apply_substituted_value', start)
assert source[start:end] in (HERE / 'lifetime-after.rs').read_text()
with tempfile.TemporaryDirectory(prefix='css-selected-color-lifetime-') as temp:
    temp = Path(temp)
    for name in ('lifetime-common.rs','lifetime-before.rs','lifetime-after.rs'):
        shutil.copyfile(HERE / name, temp / name)
    results = {}
    commands = [('before', [str(RUSTC),'--edition=2024',str(temp/'lifetime-before.rs'),'-o',str(temp/'before')]),
                ('after', [str(RUSTC),'--edition=2024','--test',str(temp/'lifetime-after.rs'),'-o',str(temp/'after')])]
    for name, command in commands:
        result = subprocess.run(command,capture_output=True,text=True)
        (HERE / (name + '-compile.log')).write_text(result.stdout+result.stderr)
        results[name] = {'exit':result.returncode,'command':command}
        if name == 'before': assert result.returncode != 0 and 'E0106' in result.stderr
        else: assert result.returncode == 0, result.stderr
    result = subprocess.run([str(temp/'after')],capture_output=True,text=True)
    (HERE/'lifetime-tests.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0 and '6 passed' in result.stdout, result
    results['tests'] = {'exit':result.returncode,'passed':6}
    results['scratch'] = str(temp)
assert not temp.exists()
results.update(scratch_removed=True, native_compile=False, scope='Exact tracker declaration and input enum; substituted ElementContext methods and AttributeReferences storage, fake computation, not Stylo type checking', compiler_sha256=hashlib.sha256(RUSTC.read_bytes()).hexdigest())
(HERE/'LIFETIME-CHECK.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
