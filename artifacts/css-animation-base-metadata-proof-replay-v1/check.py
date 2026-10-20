import hashlib,json,pathlib,sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
root=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(name): return json.loads((root/name).read_text())
manifest=read('MANIFEST.json');freeze=read('FREEZE.json')
assert sha(root/'MANIFEST.json')==freeze['manifest_sha256']
paths=list(root.rglob('*'));assert not any(p.is_symlink() for p in paths)
assert {str(p.relative_to(root)) for p in paths if p.is_file()}==set(manifest)|{'MANIFEST.json','FREEZE.json'}
for name,digest in manifest.items():
 assert not pathlib.PurePosixPath(name).is_absolute() and '..' not in pathlib.PurePosixPath(name).parts
 assert sha(root/name)==digest,name
assert sha(root/'SOURCE-FREEZE.json')==read('SOURCE.json')['FREEZE.json']
assert sha(root/'SOURCE-MANIFEST.json')==read('SOURCE.json')['MANIFEST.json']
for tag in ('canonical','relocated'):
 d=read(tag+'/CHECK.json');assert d['axiom_reports']==23 and d['inputs']==49 and d['source_bindings']==14
 assert all(c['exit']==0 for c in d['commands'])
 assert d['mutations'][0]['observed']=='|'.join(['true']*10)
 assert d['mutations'][1]['observed']=='false|false|false|false|true|true|true|true|true|true'
 assert all(m['compiled'] for m in d['mutations'])
for g in read('GUARDS.json'):
 assert g['exit']!=0 and not g['output_created']
 assert g['expected_reason'] in (root/(g['id']+'-guard.log')).read_text()
assert len(read('GUARDS.json'))==8
assert not any(p.suffix in ('.olean','.o','.dylib') for p in paths)
print(json.dumps(dict(status='PASS',inputs=len(manifest),audits=23,guards=8,removed_bytes=read('CLEANUP.json')['total_bytes'])))
