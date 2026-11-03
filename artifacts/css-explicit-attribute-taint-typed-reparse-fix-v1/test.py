import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
source = (HERE / 'candidate/servo/components/style/custom_properties.rs').read_text()
start = source.index("fn substitute_internal<'a>(")
end = source.index('\n/// Replace var(), env(), and attr() functions, returning', start)
body = source[start:end]
assert body == (HERE / 'SUBSTITUTE-CANDIDATE.rs').read_text()
support = (HERE / 'TestSupport.rs').read_text()
mutants = {
    'omitted-explicit': body.replace('    substitution.attr_tainted |= variable_value.explicitly_attr_tainted;\n', ''),
    'syntactic-attr': body.replace('variable_value.explicitly_attr_tainted;', 'variable_value.is_attr_tainted();'),
    'overwrite-child': body.replace('substitution.attr_tainted |=', 'substitution.attr_tainted ='),
    'recover-invalid': body.replace('    )?;', '    ).unwrap_or_default();'),
}
records = []
scratch = Path(tempfile.mkdtemp(prefix='explicit-taint-reparse-', dir='/private/tmp'))
try:
    for name, method in [('candidate', body), *mutants.items()]:
        path = scratch / (name + '.rs')
        path.write_text(support + '\n' + method)
        executable = scratch / name
        compile_result = subprocess.run(['rustc', '--edition=2021', '--test', str(path), '-o', str(executable)], capture_output=True, text=True)
        assert compile_result.returncode == 0, compile_result.stderr
        result = subprocess.run([str(executable)], capture_output=True, text=True)
        (HERE / (name + '.log')).write_text(compile_result.stdout + compile_result.stderr + result.stdout + result.stderr)
        assert result.returncode == (0 if name == 'candidate' else 101), (name, result.stdout, result.stderr)
        records.append({'name': name, 'compile_exit': compile_result.returncode, 'exit': result.returncode,
                        'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
finally:
    shutil.rmtree(scratch)
    report = {'records': records, 'scratch': str(scratch), 'scratch_removed': not scratch.exists(),
              'method_sha256': hashlib.sha256(body.encode()).hexdigest(),
              'support_sha256': hashlib.sha256(support.encode()).hexdigest(),
              'scope': 'Exact substitute_internal with delegated chunk/type facades; no CSS parser/native refinement'}
    (HERE / 'TEST-RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
