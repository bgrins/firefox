import ast
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = HERE / 'check_closure.py'
spec = importlib.util.spec_from_file_location('fixed_root_check', source)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
text = source.read_text()
node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == 'staged')
body = ast.get_source_segment(text, node)
body = body.replace('def staged(base, defaults, order, early_only=False):', 'def staged(base, defaults, order, neighbor_order, early_only=False):')
assert body.count('for w in sorted(edges[v]):') == 1
body = body.replace('for w in sorted(edges[v]):', 'for w in neighbor_order[v]:')
namespace = {'NODES': base.NODES, 'SCHEME': base.SCHEME}
exec(compile(body, 'neighbor-order-stage', 'exec'), namespace)
count = 0
for bits in range(1 << 9):
    graph = {v: {w for w in base.NODES if bits & (1 << (v * 3 + w))} for v in base.NODES}
    choices = [list(itertools.permutations(sorted(graph[v]))) for v in base.NODES]
    for flags in itertools.product((False, True), repeat=2):
        expected = base.oracle(graph, flags)
        for neighbors in itertools.product(*choices):
            assert all(set(neighbors[v]) == graph[v] and len(neighbors[v]) == len(graph[v]) for v in base.NODES)
            for roots in itertools.permutations(base.NODES):
                actual = namespace['staged'](graph, flags, roots, neighbors)
                assert actual == expected, (graph, flags, roots, neighbors, actual, expected)
                count += 1
assert count == 98304
result = {'cases': count, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'original_receipt_sha256': hashlib.sha256((HERE / 'CLOSURE-CHECK.json').read_bytes()).hexdigest(),
          'change': 'all permutations of original per-node neighbor lists; dynamic default edge still visited after original outgoing edges',
          'root_orders': 6, 'default_assignments': 4, 'base_graphs': 512,
          'oracle_unchanged': True, 'added_edges_and_scc_partitions_match': True,
          'native_code_executed': False, 'unbounded_proof': False}
with (HERE / 'NEIGHBOR-ORDER-CHECK.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result))
