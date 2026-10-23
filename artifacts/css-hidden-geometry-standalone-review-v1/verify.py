import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S verify.py EXPECTED_FILES_SHA256')
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import stat

root = Path(__file__).resolve().parent
def check(ok, label):
    if not ok:
        raise RuntimeError(label)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
check(len(sys.argv) == 2 and sha(root / 'FILES.json') == sys.argv[1], 'EXTERNAL_PIN')
files = json.loads((root / 'FILES.json').read_text())['files']
expected_dirs = {str(p) for n in files for p in Path(n).parents if str(p) != '.'}
seen_files, seen_dirs = set(), set()
for p in root.rglob('*'):
    name = str(p.relative_to(root))
    mode = p.lstat().st_mode
    if stat.S_ISDIR(mode):
        seen_dirs.add(name)
    else:
        check(stat.S_ISREG(mode), 'NONREGULAR:' + name)
        seen_files.add(name)
check(seen_files == set(files) | {'FILES.json'} and seen_dirs == expected_dirs, 'ROSTER')
for name, digest in files.items():
    check(sha(root / name) == digest, 'HASH:' + name)
for role in ['branch', 'upstream']:
    old = (root / (role + '.cpp')).read_text()
    new = (root / (role + '-candidate.cpp')).read_text()
    start = old.index('std::tuple<nscoord, nsReflowStatus> nsFlexContainerFrame::ReflowChildren(')
    seam = '  if (HidesContentForLayout()) {\n    return {0, nsReflowStatus()};\n  }'
    check(old[start:].count(seam) == 1, 'UNIQUE_SEAM')
    replacement = seam.replace('    return', '    MarkPrincipalChildrenDirty();\n    return')
    check(new == old[:start] + old[start:].replace(seam, replacement, 1), 'ONLY_ONE_LINE')
    source = (root / 'source' / role / 'layout/generic/nsIFrame.cpp').read_text()
    begin = source.index('void nsIFrame::MarkSubtreeDirty()')
    end = source.index('/* virtual */', begin)
    check(source[begin:end] == (root / (role + '-dirty-helpers.cpp.txt')).read_text(), 'HELPER_SLICE')
check((root / 'branch-dirty-helpers.cpp.txt').read_bytes() ==
      (root / 'upstream-dirty-helpers.cpp.txt').read_bytes(), 'SAME_HELPERS')
records = json.loads((root / 'APPLICABILITY.json').read_text())
check(len(records) == 2 and all(r['exact_forward_reverse'] and
      all(c['exit'] == 0 for c in r['commands']) for r in records), 'ROUNDTRIPS')
print(json.dumps({'status': 'SOURCE_RECOMMENDATION_ONLY_RUNTIME_GATES_PENDING',
                  'files': len(files), 'exact_native_delta_lines': 1,
                  'source_bases': len(records), 'dependency_on_98_or_101': False}))
