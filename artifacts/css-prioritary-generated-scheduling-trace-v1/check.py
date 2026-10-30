import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = 'servo/components/style/properties/cascade.rs'
base = (HERE / 'base' / REL).read_text()
source = (HERE / 'candidate' / REL).read_text()
assert hashlib.sha256(base.encode()).hexdigest() == 'a6f4e611985f25340e339a402169cfea3abbdfa3c683183646c9300ae31c5e4b'
assert base == (ROOT / 'artifacts/css-prioritary-published-rebase-diagnostic-v1/candidate' / REL).read_text()
pattern = r'^[ \t]*/\* CSS_PRIORITY_TRACE_BEGIN \*/\n.*?^[ \t]*/\* CSS_PRIORITY_TRACE_END \*/\n'
blocks = re.findall(pattern, source, flags=re.M | re.S)
assert len(blocks) == 15
assert re.sub(pattern, '', source, flags=re.M | re.S) == base
for block in blocks:
    for forbidden in ['.insert(', '.remove(', 'substitute_variables_if_needed(', 'to_computed_value(', 'get_attr_value_for_cycle_resolution(', 'do_apply_declaration(', 'return;', 'break;', 'continue;']:
        assert forbidden not in block, forbidden
patch = ''.join(difflib.unified_diff(base.splitlines(True), source.splitlines(True), fromfile='a/' + REL, tofile='b/' + REL))
assert (HERE / 'native.patch').read_text() == patch
tool = json.loads((HERE / 'TOOLCHAIN.json').read_text())
assert hashlib.sha256(Path(tool['rustfmt']).read_bytes()).hexdigest() == tool['sha256']
assert hashlib.sha256((ROOT / tool['config_source']).read_bytes()).hexdigest() == tool['config_sha256']
with tempfile.TemporaryDirectory(prefix='css-priority-trace-check-') as temporary:
    scratch = Path(temporary)
    target = scratch / REL
    target.parent.mkdir(parents=True)
    target.write_text(base)
    for reverse in [False, True]:
        command = ['patch', '--fuzz=0'] + (['-R'] if reverse else []) + ['-p1', '-i', str(HERE / 'native.patch')]
        result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
        assert result.returncode == 0, result
        assert target.read_text() == (base if reverse else source)
    target.write_text(source)
    subprocess.run([tool['rustfmt'], '--check', '--config-path', str(ROOT / tool['config_source']), str(target)], check=True, capture_output=True, text=True)
assert not scratch.exists()
print(json.dumps({'marked_trace_blocks': 15, 'removal_reproduces_a6f4_exactly': True, 'added_css_evaluation_calls': 0, 'patch_forward_reverse': True, 'format_check': True, 'scratch_removed': True, 'native_typecheck': False, 'browser_execution': False}))
