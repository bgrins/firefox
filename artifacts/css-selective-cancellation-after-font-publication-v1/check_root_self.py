import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('root_self_evidence_check', HERE / 'evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
binding = read(HERE / 'PAIR-BINDING.json')
roles = read(ROOT / binding['source']['directory'] / 'SOURCE-ROLES.json')['roles']
sources = {path: row['candidate_sha256'] for path, row in roles.items()}
snapshot = ROOT / 'artifacts/css-root-font-cancellation-selective-handoff-candidate-browser-runtime-v1/ARCHIVE-SNAPSHOT.json'
actual = evidence.verify_root_self(ROOT, binding, snapshot, sources)
policy = read(ROOT / binding['root_self_policy']['path'])
page, = read(ROOT / policy['roster'])
original = ROOT / 'artifacts/css-root-self-animation-isolation-archived-original-runtime-v1/raw.jsonl'
candidate = ROOT / binding['root_self_runtime']['directory'] / 'raw.jsonl'
old, old_end = evidence.signatures(evidence.events(original), page, 14)
new, new_end = evidence.signatures(evidence.events(candidate), page, 14)
negative = []
def reject(label, fn):
    try:
        fn()
    except (AssertionError, KeyError):
        negative.append(label)
    else:
        raise AssertionError(label)
for label, mutate in [('missing callback', lambda x:x.pop()), ('changed known FAIL', lambda x:next(r for r in x if r['status']=='FAIL').update(message='changed')), ('changed prior PASS', lambda x:next(r for r in x if r['status']=='PASS').update(message='changed')), ('promoted known failure', lambda x:next(r for r in x if r['status']=='FAIL').update(status='PASS'))]:
    bad = copy.deepcopy(new);mutate(bad)
    reject(label,lambda:evidence.require_root_self_signatures(old,bad,old_end,new_end))
reject('changed ending',lambda:evidence.require_root_self_signatures(old,new,old_end,dict(new_end,message='changed')))
assert read(HERE/'POLICY.json')['enabled_modes']==[] and binding['font_native_receipt'] is None
before = (HERE/'EVIDENCE-BEFORE-ROOT-SELF.py').read_text()
after = (HERE/'evidence.py').read_text()
for name in ('require_font_receipt','verify_font_history','signatures','compare_lane','archived'):
    import ast
    def body(source):
        node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
        return ast.get_source_segment(source,node)
    assert body(before)==body(after),name
print(json.dumps({'actual':actual,'negative_controls':negative,'old_full_replay_not_repeated':True,'tested':{n:sha(HERE/n) for n in ['evidence.py','PAIR-BINDING.json','POLICY.json','check_root_self.py']},'root_self_only_saved_replay':True,'live_actions':False},sort_keys=True))
