import importlib.util
import json
import math
from pathlib import Path
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('review_audit', HERE / 'audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
cases = [(0x3f800000, 3), (0x7f7fffff, 3), (0xbf800000, 3),
         (0x3f800000, 0x3eaaaaab), (0x80000001, 2), (1, 2), (0x7f7fffff, 0x7f000000)]
with tempfile.TemporaryDirectory(prefix='round-specific-witness-') as directory:
    executable = Path(directory) / 'helper'
    subprocess.run(['rustc', '--edition=2021', '-C', 'opt-level=2', str(HERE / 'helper.rs'), '-o', str(executable)], check=True)
    output = subprocess.check_output([str(executable)], input=b''.join(struct.pack('<II', *pair) for pair in cases))
rows = []
for (a, b), values in zip(cases, struct.iter_unpack('<9I', output)):
    exact = audit.oracle(a, b)
    assert list(values[2::2]) == exact
    value = struct.unpack('<f', struct.pack('<I', a))[0]
    step = abs(struct.unpack('<f', struct.pack('<I', b))[0])
    remainder = struct.unpack('<f', struct.pack('<I', values[0]))[0]
    row = {'a': f'{a:08x}', 'b': f'{b:08x}', 'remainder': f'{values[0]:08x}',
           'candidate': [f'{x:08x}' for x in values[2::2]], 'exact': [f'{x:08x}' for x in exact],
           'early_exact_multiple_return': remainder == 0,
           'trace': 'Python binary64 arithmetic follows the extracted branch; result bits come from compiled Rust.'}
    if remainder != 0:
        toward = math.copysign(value - remainder, value)
        lower, upper = (toward - step, toward) if value < 0 else (toward, toward + step)
        row.update(f64_bounds_equal=lower == upper, f64_lower=lower.hex(), f64_upper=upper.hex())
    rows.append(row)
assert not executable.exists()
(HERE / 'WITNESSES.json').write_text(json.dumps(rows, indent=2) + '\n')
print('Seven compiled witness pairs match the exact oracle; trace preserves copysign and early return.')
