import importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
LAB=HERE.parent/'css-pseudo-animation-composed-recascade-runtime-20261110-v1'
def load(p):return json.loads(p.read_text())
def module(n):
 s=importlib.util.spec_from_file_location(n,LAB/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('analyze');base=m.parse(LAB/'baseline1/wpt-raw.jsonl');candidate=m.parse(LAB/'candidate1/wpt-raw.jsonl');assert base==load(LAB/'baseline1/TEST-RESULTS.json');assert candidate==load(LAB/'candidate1/TEST-RESULTS.json');assert m.compare(base,candidate)==load(LAB/'candidate1/COMPARISON.json')
for name,result in [('driver','DRIVER'),('recascade','RECASCADE'),('composed','COMPOSED')]:
 m=module(name+'-analyze');args=[LAB/'candidate1'/(name+'-raw.jsonl')]
 if name=='composed':args.append(1)
 r=m.parse(*args);assert r==load(LAB/'candidate1'/(result+'-RESULTS.json'))
print(json.dumps({'status':'PASS','exact_saved_results_reproduced':['WPT baseline','WPT candidate','comparison','query','recascade','composed']}))
