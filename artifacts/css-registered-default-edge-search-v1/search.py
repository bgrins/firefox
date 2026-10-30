import ast
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-registered-selected-color-cyclic-default-review-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((SOURCE / 'FILES.json').read_text())
assert sha(SOURCE / 'FILES.json') == '44bb3702725b01cbe554d2271e0bf0583f7a9e2eb3c6724f978fb9c174cbbd54'
for name, pin in manifest.items():
    assert sha(SOURCE / name) == pin['sha256']
    assert (SOURCE / name).stat().st_size == pin['bytes']
text = (SOURCE / 'check_closure.py').read_text()
functions = {node.name: ast.get_source_segment(text, node) for node in ast.parse(text).body if isinstance(node, ast.FunctionDef)}
oracle_source = functions['oracle'].replace('(0, 1)', 'CUSTOM')
staged_source = functions['staged'].replace('(0, 1)', 'CUSTOM')
assert functions['oracle'].count('(0, 1)') == 1
assert functions['staged'].count('(0, 1)') == 2
staged_source = staged_source.replace('def staged(base, defaults, order, early_only=False):', 'def staged(base, defaults, order, neighbor_order, early_only=False):')
assert staged_source.count('for w in sorted(edges[v]):') == 1
staged_source = staged_source.replace('for w in sorted(edges[v]):', 'for w in neighbor_order[v] + tuple(sorted(edges[v] - set(neighbor_order[v]))):')
compiled = {}
def algorithms(n):
    if n not in compiled:
        namespace = {'NODES': range(n), 'SCHEME': n - 1, 'CUSTOM': range(n - 1)}
        exec(compile(oracle_source+'\n\n'+staged_source, 'generalized-saved-functions', 'exec'), namespace)
        compiled[n] = namespace
    return compiled[n]['oracle'], compiled[n]['staged']

def encode(result):
    edges, groups = result
    return {'edges': {str(v): sorted(edges[v]) for v in edges}, 'sccs': sorted([sorted(group) for group in groups])}

def mismatch(graph, flags, roots, neighbors, early=False):
    oracle, staged = algorithms(len(graph))
    return staged(graph, flags, roots, neighbors, early) != oracle(graph, flags)

def record(graph, flags, roots, neighbors):
    oracle, staged = algorithms(len(graph))
    return {'n':len(graph), 'target':len(graph)-1, 'base':{str(v):sorted(graph[v]) for v in graph}, 'eligible':list(flags), 'root_order':list(roots), 'neighbor_orders':[list(x) for x in neighbors], 'oracle':encode(oracle(graph,flags)), 'staged':encode(staged(graph,flags,roots,neighbors))}

def minimize(graph, flags, roots, neighbors):
    graph = {v:set(values) for v, values in graph.items()}
    flags = list(flags)
    attempts = 0
    changed = True
    while changed:
        changed = False
        for v in graph:
            for w in sorted(graph[v]):
                trial = {u:set(values) for u,values in graph.items()}
                trial[v].remove(w)
                order = tuple(tuple(x for x in row if x in trial[u]) for u,row in enumerate(neighbors))
                attempts += 1
                if mismatch(trial,flags,roots,order):
                    graph, neighbors, changed = trial, order, True
        for v in range(len(flags)):
            if not flags[v]: continue
            trial = flags.copy(); trial[v] = False; attempts += 1
            if mismatch(graph,trial,roots,neighbors): flags,changed = trial,True
    return {'case':record(graph,flags,roots,neighbors), 'attempts':attempts, 'minimality':'greedy edge/eligibility deletion fixed point; vertex count and orders retained'}

start = time.monotonic()
deadline = start + 45
case_count = 0
unique_inputs = set()
family_counts = {}
size_counts = {}

def check(graph, flags, label, seed):
    global case_count
    n = len(graph)
    rng = random.Random(seed)
    variants = [(tuple(range(n)), tuple(tuple(sorted(graph[v])) for v in range(n))),
                (tuple(reversed(range(n))), tuple(tuple(sorted(graph[v], reverse=True)) for v in range(n)))]
    for _ in range(4):
        roots = list(range(n)); rng.shuffle(roots)
        neighbors = []
        for v in range(n):
            row = sorted(graph[v]); rng.shuffle(row); neighbors.append(tuple(row))
        variants.append((tuple(roots),tuple(neighbors)))
    unique_inputs.add(json.dumps([[[v,w] for v in graph for w in sorted(graph[v])],list(flags),n]))
    oracle, staged = algorithms(n)
    expected = oracle(graph,flags)
    for roots,neighbors in dict.fromkeys(variants):
        if time.monotonic() > deadline: raise TimeoutError('45-second bounded search exhausted')
        assert sorted(roots)==list(range(n))
        assert all(len(neighbors[v])==len(graph[v]) and set(neighbors[v])==graph[v] for v in graph)
        case_count += 1
        family_counts[label] = family_counts.get(label,0)+1
        size_counts[n] = size_counts.get(n,0)+1
        if staged(graph,flags,roots,neighbors) != expected:
            failure = {'family':label,'seed':seed,'case_number':case_count,'original':record(graph,flags,roots,neighbors),'minimized':minimize(graph,flags,roots,neighbors)}
            (HERE/'COUNTEREXAMPLE.json').write_text(json.dumps(failure,indent=2)+'\n')
            return False
    return True

# This gate checks that parameterization leaves the sealed three-node behavior unchanged.
legacy = {'__name__':'saved_checker'}
exec(compile(text,str(SOURCE/'check_closure.py'),'exec'),legacy)
compatibility = 0
for bits in range(512):
    graph = {v:{w for w in range(3) if bits & (1 << (v*3+w))} for v in range(3)}
    neighbors = tuple(tuple(sorted(graph[v])) for v in range(3))
    for flags in itertools.product((False,True),repeat=2):
        oracle,staged = algorithms(3)
        assert oracle(graph,flags)==legacy['oracle'](graph,flags)
        for roots in itertools.permutations(range(3)):
            assert staged(graph,flags,roots,neighbors)==legacy['staged'](graph,flags,roots)
            compatibility += 1
negative = {0:{1},1:{0},2:set()}
negative_orders = ((1,),(0,),())
assert mismatch(negative,(True,False),(0,1,2),negative_orders,True)
assert not mismatch(negative,(True,False),(0,1,2),negative_orders)
negative_receipt = record(negative,(True,False),(0,1,2),negative_orders)
negative_receipt['early_only'] = encode(algorithms(3)[1](negative,(True,False),(0,1,2),negative_orders,True))

completed = True
for n in range(4,9):
    target = n-1
    families = {}
    chain = {v:set() for v in range(n)}
    chain[0].add(0)
    for v in range(1,n): chain[v].add(v-1)
    families['default-cascade-chain'] = chain
    pairs = {v:set() for v in range(n)}
    for v in range(0,n-2,2): pairs[v].add(v+1);pairs[v+1].add(v)
    for v in range(1,n-1): pairs[v].add(v-1)
    pairs[target].add(n-2)
    families['nested-scc-chain'] = pairs
    ring = {v:{(v+1)%n} for v in range(n)}
    families['target-inclusive-ring'] = ring
    branches = {v:set() for v in range(n)}
    branches[0].add(0)
    for v in range(1,n-1): branches[v].add(0);branches[target].add(v)
    families['default-cascade-branches'] = branches
    disconnected = {v:set() for v in range(n)}
    for v in range(n-1): disconnected[v].add(v)
    families['target-isolated-self-cycles'] = disconnected
    acyclic = {v: set(range(v+1,n)) for v in range(n)}
    families['dense-acyclic'] = acyclic
    for family,graph in families.items():
        for flag_bits in range(1 << (n-1)):
            flags = tuple(bool(flag_bits & (1<<v)) for v in range(n-1))
            if not check(graph,flags,family,100000*n+flag_bits): completed=False;break
        if not completed: break
    if not completed: break
    for index in range(1000):
        seed = 0xC010000 + n*10000 + index
        rng = random.Random(seed)
        density = (.08,.20,.40,.65,.9)[index%5]
        graph = {v:{w for w in range(n) if rng.random()<density} for v in range(n)}
        flags = tuple(rng.choice((False,True)) for _ in range(n-1))
        if not check(graph,flags,'seeded-density-'+str(density),seed): completed=False;break
    if not completed: break

result = {'completed_planned_search':completed,'counterexample_found':not completed,'vertices':[4,5,6,7,8], 'target':'n-1, ineligible; all other vertices independently eligible', 'compatibility_cases':compatibility, 'larger_graph_order_cases':case_count,'unique_base_and_eligibility_inputs':len(unique_inputs),'by_vertices':size_counts,'by_family':family_counts,'maximum_orders_per_input':6,'random_graphs_per_size':1000,'seed_formula':'0xC010000 + n*10000 + index; index 0..999','elapsed_seconds':time.monotonic()-start,'wall_limit_seconds':45,'early_only_negative_control':negative_receipt,'native_execution':False,'unbounded_equivalence_proved':False,'scratch_created':False,'source_sha256':sha(SOURCE/'check_closure.py'),'source_manifest_sha256':sha(SOURCE/'FILES.json')}
with (HERE/'RESULT.json').open('x') as stream: json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('early_only_negative_control','by_family')}))
