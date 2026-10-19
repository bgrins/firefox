import argparse, hashlib, json, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--replay', type=pathlib.Path)
a = p.parse_args()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
f = json.loads((ROOT/'FREEZE.json').read_text())
assert sha(ROOT/'MANIFEST.json') == f['manifest_sha256'], 'manifest integrity failure'
m = json.loads((ROOT/'MANIFEST.json').read_text())
for n, expected in m.items():
    path = pathlib.PurePosixPath(n)
    assert not path.is_absolute() and '..' not in path.parts
    assert sha(ROOT/n) == expected, 'input integrity failure: '+n
assert len(m) == f['inputs']
for path in (ROOT/'lean').glob('*.lean'):
    assert not re.search(r'\b(sorry|admit|native_decide|axiom)\b', path.read_text()), path
for name in ['parser.rs','tokenizer.rs','rules_and_declarations.rs']:
    assert sha(ROOT/'source/third_party/rust/cssparser/src'/name) == sha(ROOT/'vendor/cssparser/src'/name)
print(json.dumps({'authentication':'PASS','inputs':len(m)}), flush=True)
if a.replay:
    subprocess.run(['python3', str(ROOT/'replay.py'), '--output', str(a.replay.resolve())], check=True)
