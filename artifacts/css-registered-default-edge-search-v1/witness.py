import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
namespace = {'__file__':str(HERE/'search.py')}
source = (HERE/'search.py').read_text()
assert source.count('start = time.monotonic()') == 1
exec(compile(source.split('start = time.monotonic()')[0], 'saved-algorithm-preparation', 'exec'), namespace)
n = 8
graph = {v:{v-1} if v else {0} for v in range(n)}
flags = (True,)*(n-1)
roots = tuple(range(n))
neighbors = tuple(tuple(sorted(graph[v])) for v in range(n))
result = namespace['record'](graph,flags,roots,neighbors)
assert result['oracle'] == result['staged']
assert all(7 in result['oracle']['edges'][str(v)] for v in range(7))
assert result['oracle']['sccs'] == [list(range(n))]
first_round = {v:set(graph[v]) for v in graph}
first_round[0].add(7)
assert first_round != namespace['algorithms'](n)[0](graph,flags)[0]
result['first_round_extra_edges'] = [[0,7]]
result['additional_defaults_required_after_first_round'] = [[v,7] for v in range(1,7)]
result['scope'] = 'Concrete eight-node closure cascade; no native scheduling/pass-count assertion'
with (HERE/'WITNESS.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
print('Eight-node cascade: first default edge creates cycles enabling six further default edges; exact staged/oracle edge and SCC match')
