import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('caller_capture', HERE / 'baseline.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
receipt = m.core.read(m.ROOT / m.binding['native_receipt'])
view = m.native_head_view(receipt)
assert view['head'] == receipt['commit'] and view['epoch_sha256'] == m.binding['current_epoch_sha256']
assert view['epoch_sha256'] != receipt['epoch_sha256'] and 'committed' not in receipt
assert view['authority_kind'] == 'internal-observed-head-from-native-receipt-and-raw-refresh'
negatives = 0
for key, value in [('stage', 'other'), ('commit', '0' * 40), ('parent', '0' * 40), ('signature_verified', False), ('files', []), ('accepted', True), ('accepted_fix_increment', 1), ('app_rebuilt', True)]:
    changed = copy.deepcopy(receipt); changed[key] = value
    try: m.native_head_view(changed)
    except AssertionError: negatives += 1
    else: raise AssertionError(key)
for key, value in [('current_epoch_sha256', '0' * 64), ('refresh_manifest_sha256', '0' * 64), ('refresh_binding', None)]:
    original = m.binding[key]; m.binding[key] = value
    try: m.validate_refresh(receipt)
    except (AssertionError, RuntimeError): negatives += 1
    else: raise AssertionError(key)
    finally: m.binding[key] = original
assert set(m.binding['additional_sources']) == {'servo/components/style/properties/mod.rs'}
for name, row in m.binding['additional_sources'].items():
    assert m.core.sha(m.ROOT / row['base_capture']) == row['base_sha256']
expected = m.validate_refresh(receipt)
print(json.dumps({'references': len(m.binding['references']), 'native_receipt_preserved': True,
                  'derived_epoch': view['epoch_sha256'], 'refreshed_raw': expected['index']['raw_index'],
                  'negative_checks': negatives, 'additional_source_capture_pending': True, 'saved_only': True}))
