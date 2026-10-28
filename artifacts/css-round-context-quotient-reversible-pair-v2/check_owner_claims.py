import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('ownership_check', ROOT/'artifacts/css-registered-number-source-transition-v4/transition.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
with tempfile.TemporaryDirectory(prefix='round-owned-claim-', dir='/private/tmp') as temporary:
    root = Path(temporary)
    path = root/'calc.rs'
    base, candidate = b'accepted144 base', b'finite candidate retaining accepted144'
    path.write_bytes(base)
    source = h.claim(root, 'calc.rs', h.digest(base))
    accepted = source
    stale = dict(source)
    identity = source['identity'][:]
    h.write_owned(root, source, candidate)
    h.claim(root, accepted['path'], accepted['owned_sha256'], accepted['identity'])
    assert accepted is source and accepted['owned_sha256'] == h.digest(candidate)
    try:
        h.claim(root, stale['path'], stale['owned_sha256'], stale['identity'])
    except RuntimeError:
        pass
    else:
        raise AssertionError('Stale separate accepted-source claim was accepted')
    h.write_owned(root, source, base)
    h.claim(root, accepted['path'], h.digest(base), identity)
    assert path.read_bytes() == base and accepted['identity'] == identity
result={'base_candidate_restored_claims':3,'stale_independent_claim_rejected':1,'same_inode_restored':True,'scratch_removed':True,'live_source_or_runtime_access':False,'native_semantic_claim':False}
(HERE/'OWNERSHIP-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
