import difflib
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
native = ['servo/components/style/custom_properties.rs', 'servo/components/style/properties/cascade.rs', 'servo/components/style/properties/mod.rs']
test = 'testing/web-platform/tests/css/css-values/attr-typed-fallback-eligibility.html'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip()
patch = []
records = {}
for name in native:
    before = (here / 'baseline-v1-sources' / name.replace('/', '__')).read_text()
    after = (here / 'candidate-v1-sources' / name.replace('/', '__')).read_text()
    assert (root / name).read_text() == after
    original = subprocess.check_output(['git', 'show', head + ':' + name], cwd=root).decode()
    candidate = original
    old, new = before.splitlines(True), after.splitlines(True)
    changes = []
    for tag, i, j, k, l in reversed(difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes()):
        if tag == 'equal':
            continue
        # Include surrounding unchanged lines to locate insertions unambiguously.
        lo, hi = max(0, i - 3), min(len(old), j + 3)
        a = ''.join(old[lo:hi])
        b = ''.join(old[lo:i] + new[k:l] + old[j:hi])
        if name.endswith('cascade.rs') and 'PropertyIdRef' in b and i < 30:
            a = '    PropertyDeclarationId, PropertyFlags, ShorthandsWithPropertyReferencesCache, StyleBuilder,\n    property_counts,\n'
            b = '    PropertyDeclarationId, PropertyFlags, PropertyIdRef, ShorthandsWithPropertyReferencesCache,\n    StyleBuilder, property_counts,\n'
        assert original.count(a) == 1, (name, tag, a)
        pos = original.index(a)
        prefix = ''.join(old[lo:i]) if not (name.endswith('cascade.rs') and i < 30) else ''
        suffix = ''.join(old[j:hi]) if not (name.endswith('cascade.rs') and i < 30) else ''
        start, end = pos + len(prefix), pos + len(a) - len(suffix)
        replacement = b[len(prefix):len(b)-len(suffix) if suffix else None]
        candidate = candidate[:start] + replacement + candidate[end:]
        changes.append({'old': a, 'new': b})
    patch.append('diff --git a/' + name + ' b/' + name + '\n')
    patch.extend(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    records[name] = {'head_sha256': hashlib.sha256(original.encode()).hexdigest(), 'candidate_sha256': hashlib.sha256(candidate.encode()).hexdigest(), 'changes': changes}
patch.append('diff --git a/' + test + ' b/' + test + '\nnew file mode 100644\n')
patch.extend(difflib.unified_diff([], (root / test).read_text().splitlines(True), fromfile='/dev/null', tofile='b/' + test))
output = ''.join(patch)
(here / 'native-wpt-v1.patch').write_text(output)
(here / 'PATCH-ISOLATION-v1.json').write_text(json.dumps({'head':head, 'patch_sha256':hashlib.sha256(output.encode()).hexdigest(), 'native_files':records, 'scope':'Same reviewed semantic hunks; import context adapted to committed HEAD, excluding shared experimental changes. No clean-base build claimed.'}, indent=2) + '\n')
print(hashlib.sha256(output.encode()).hexdigest())
