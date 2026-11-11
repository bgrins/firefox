import copy
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tomllib

HERE = Path(__file__).resolve().parent
SOURCE = HERE.with_name('css-number-native-feature-sensitivity-20261110-v1')
OLD = HERE.with_name('css-number-native-differential-review-20261110-v1') / 'execution'


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    schema = runpy.run_path(str(SOURCE / 'strict_model.py'))
    cases = json.loads((SOURCE / 'inputs/CASES.json').read_text())
    rows = schema['read'](SOURCE / 'inputs/model-rows.jsonl', cases)
    rejected = []
    changes = [
        ('string-code', lambda x: x[0][2][0].__setitem__(0, '48')),
        ('null-observation', lambda x: x[0].__setitem__(2, None)),
        ('tuple-row', lambda x: x.__setitem__(0, tuple(x[0]))),
        ('true-initial-error', lambda x: x[0].__setitem__(1, True)),
        ('true-final-error', lambda x: x[0].__setitem__(3, True)),
        ('wrong-input', lambda x: x[0].__setitem__(0, x[0][0] + 'x')),
        ('extra-row-field', lambda x: x[0].append(False)),
        ('null-flag', lambda x: x[0][2].__setitem__(5, None)),
    ]
    for label, change in changes:
        changed = copy.deepcopy(rows)
        change(changed)
        try:
            schema['validate'](changed, cases)
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError(label)
    dependencies = json.loads((SOURCE / 'DEPENDENCIES.json').read_text())
    lock = tomllib.loads((SOURCE / 'inputs/root-Cargo.lock').read_text())
    for name, record in dependencies['package_records'].items():
        assert [p for p in lock['package'] if p['name'] == name and p['version'] == record['version']] == [record]
    command = [sys.executable, '-I', str(SOURCE / 'compare.py'),
               '--plain', str(OLD / 'native-plain.stdout'),
               '--instrumented', str(OLD / 'native-instrumented.stdout'),
               '--plain-trace', str(OLD / 'native-plain.stderr'),
               '--trace', str(OLD / 'native-instrumented.stderr'),
               '--model', str(OLD / 'model-rows.stdout'),
               '--out', str(HERE / 'HISTORICAL-STRICT-COMPARISON.json')]
    result = subprocess.run(command, capture_output=True)
    (HERE / 'compare.stdout').write_bytes(result.stdout)
    (HERE / 'compare.stderr').write_bytes(result.stderr)
    assert result.returncode == 0
    actual = json.loads((HERE / 'HISTORICAL-STRICT-COMPARISON.json').read_text())
    assert actual.pop('model_json_exact_types_checked') is True
    assert actual == json.loads((OLD / 'COMPARISON.json').read_text())
    report = dict(status='PASS', strict_model_rows=len(rows), additional_refusals=rejected,
                  exact_root_lock_records=len(dependencies['package_records']),
                  retained_comparison_identical_after_schema_gate=True,
                  native_execution=False, cargo_execution=False,
                  source_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in SOURCE.glob('*.py')})
    (HERE / 'INDEPENDENT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
