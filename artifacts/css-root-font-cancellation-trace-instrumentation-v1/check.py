import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
paths = sorted(str(p.relative_to(HERE / 'candidate')) for p in (HERE / 'candidate').rglob('*') if p.is_file())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def erase(s):
    s = re.sub(r'^\s*eprintln!\("RFTC[^\n]*\n', '\n', s, flags=re.M)
    s = re.sub(r'^[ \t]*fprintf\(stderr, "RFTC.*?;\n', '', s, flags=re.M | re.S)
    s = s.replace('#include <cstdio>\n', '').replace('#include "nsThreadUtils.h"\n', '')
    s = re.sub(r'\n[ \t]*\n', '\n', s)
    for fragment in [
        '    if has_animations || data.hint.intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT) {\n    }\n',
        '    if propagated_hint.intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT) || !child_restyle_hint.is_empty() {\n    }\n',
        '        if is_root {\n        }\n',
        '        if propagated_hint.intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT) {\n        }\n',
    ]:
        s = s.replace(fragment, '')
    s = s.replace('        let child_hint = child_data.as_ref().map(|d| d.hint);\n', '')
    s = s.replace('        let should_traverse = D::element_needs_traversal(child, flags, child_data.map(|d| &*d));\n', '')
    s = s.replace('        if should_traverse {\n            note_child(child_node);', '        if D::element_needs_traversal(child, flags, child_data.map(|d| &*d)) {\n            note_child(child_node);')
    s = s.replace('                let root_size = new_primary_style.effective_zoom.unzoom(size.px());\n                device.set_root_font_size(root_size);', '                device.set_root_font_size(new_primary_style.effective_zoom.unzoom(size.px()));')
    return '\n'.join(line for line in s.splitlines() if line.strip())

for name in paths:
    assert erase((HERE / 'candidate' / name).read_text()) == '\n'.join(line for line in (HERE / 'parent' / name).read_text().splitlines() if line.strip()), name
assert (HERE / 'candidate/servo/components/style/data.rs').read_bytes() == (HERE / 'parent/servo/components/style/data.rs').read_bytes()
roundtrips = []
scratch = Path(tempfile.mkdtemp(prefix='css-cancel-trace-patch-', dir='/private/tmp'))
try:
    for role, patch in [('base', 'native.patch'), ('parent', 'INSTRUMENTATION.patch')]:
        directory = scratch / role
        shutil.copytree(HERE / role, directory)
        for reverse in [False, True]:
            command = ['patch', '-p1', '--batch', '-i', str(HERE / patch)]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=directory, text=True, capture_output=True)
            assert result.returncode == 0, result.stdout + result.stderr
            expected = role if reverse else 'candidate'
            for name in paths:
                assert (directory / name).read_bytes() == (HERE / expected / name).read_bytes(), name
        roundtrips.append({'base': role, 'patch': patch, 'forward_and_reverse_exact': True})
finally:
    shutil.rmtree(scratch)
print(json.dumps({'logging_erasure_matches_parent': True, 'unchanged_font_unit_data_candidate': True, 'roundtrips': roundtrips, 'scratch': str(scratch), 'scratch_removed': not scratch.exists(), 'native_typecheck': False, 'browser_run': False, 'tested_inputs': {name: sha(HERE / name) for name in ['native.patch', 'INSTRUMENTATION.patch', 'check.py']}}, sort_keys=True))
