import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('native_capture', HERE / 'baseline.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
receipt = m.core.read(m.ROOT / m.binding['native_receipt'])
view = m.native_head_view(receipt)
assert view['head'] == receipt['commit'] and view['epoch_sha256'] == receipt['epoch_sha256']
assert 'committed' not in receipt and view['authority_kind'] == 'internal-observed-head-from-native-receipt'
for key, value in [('stage', 'other'), ('commit', '0' * 40), ('parent', '0' * 40), ('signature_verified', False), ('files', []), ('accepted', True), ('accepted_fix_increment', 1), ('app_rebuilt', True)]:
    changed = copy.deepcopy(receipt)
    changed[key] = value
    try:
        m.native_head_view(changed)
    except AssertionError:
        pass
    else:
        raise AssertionError(key)
old = (m.ROOT / 'artifacts/css-font-size-form-diagnostic-current-capture-v1/capture_current.py').read_text()
expected = old.replace("checkpoint = baseline.read(receipt_path)\n", "checkpoint = baseline.read(receipt_path)\nassert receipt_name == baseline.binding['native_receipt']\n").replace("'checkpoint': checkpoint, 'snapshot': snapshot,", "'checkpoint': checkpoint, 'authority_kind': 'signed-native-publication', 'snapshot': snapshot,")
assert (HERE / 'capture_current.py').read_text() == expected
print(json.dumps({'references': len(m.binding['references']), 'native_schema_negatives': 8, 'exact_capture_delta': True, 'saved_only': True}))
