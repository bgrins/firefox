import hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((root/'MANIFEST.json').read_text())
freeze=json.loads((root/'FREEZE.json').read_text())
assert sha(root/'MANIFEST.json')==freeze['manifest_sha256']
assert sha(root/'REPORT.md')==freeze['report_sha256']
paths=list(root.rglob('*'))
assert not any(p.is_symlink() for p in paths)
actual={str(p.relative_to(root)) for p in paths if p.is_file()}-{'MANIFEST.json','FREEZE.json'}
assert actual==set(manifest)
for name,digest in manifest.items():
 p=pathlib.PurePosixPath(name)
 assert not p.is_absolute() and '..' not in p.parts
 assert sha(root/name)==digest,name
print(json.dumps({'status':'PASS','research_inputs':len(manifest),'scope':'integrity only; see REPORT.md'}))
