import ast
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'artifacts/css-integer-stored-range-history-rewrite-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((SOURCE / 'DRAFT-FILES.json').read_text())
assert all(sha(SOURCE / n) == v for n, v in manifest.items())
main = next(n for n in ast.parse((SOURCE / 'rewrite.py').read_text()).body
            if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = None
for node in ast.walk(main):
    if isinstance(node, ast.With):
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Assign) and ast.unparse(stmt).startswith('state = h.index_state('):
                tail = node.body[i:]
assert tail and len(tail) == 8
published = []
state = dict(head='c' * 40, entries='entries', cached_diff='empty', working_diff='unchanged', raw_index='raw')

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

ns = dict(h=SimpleNamespace(index_state=lambda *args: copy.deepcopy(state),
          semantic_index=lambda s: {k: v for k, v in s.items() if k != 'raw_index'}),
          ROOT=Path('/inert'), env={}, before=dict(index=copy.deepcopy(state), nested_index={'unchanged': True}),
          epoch={'semantic_index': {'head': 'c' * 40}}, copy=copy,
          guards=SimpleNamespace(verify_current=lambda *args: {'nested_index': {'unchanged': True}}),
          save=lambda n, v: published.append((n, copy.deepcopy(v))),
          result={'published': True, 'new_tip': 'd' * 40}, key='ssh-ed25519 inert',
          digest=lambda b: hashlib.sha256(b).hexdigest(), need=need)
exec(compile(ast.Module(body=tail, type_ignores=[]), '<actual-success-tail>', 'exec'), ns)
assert ns['result']['status'] == 'FIX121_METADATA_HISTORY_REWRITE_VERIFIED'
assert published[0][1]['semantic_index']['head'] == 'c' * 40
assert ns['result']['new_tip'] == 'd' * 40
record = dict(status='BRANCH_HEAD_ADMISSION_GAP_REPRODUCED', script_sha256=sha(SOURCE / 'rewrite.py'),
              draft_manifest_sha256=sha(SOURCE / 'DRAFT-FILES.json'), actual_tail_statements=len(tail),
              scenario='HEAD switched to another branch at carrier before publication; original branch update succeeds',
              reported_new_tip=ns['result']['new_tip'], accepted_actual_head=state['head'],
              reported_status=ns['result']['status'], git_calls=0, live_state_reads=False,
              scope='Actual success tail AST with inert index/guard boundaries; no Git transaction executed.')
(HERE / 'REPRODUCTION.json').write_text(json.dumps(record, indent=2) + '\n')
(HERE / 'ACTUAL-TAIL.py').write_text('\n'.join(ast.unparse(n) for n in tail) + '\n')
print(json.dumps(record))
