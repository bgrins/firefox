#!/usr/bin/env python3
import hashlib,json,pathlib
P=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 n=P/'inputs/native'
 assert sha(n/'FILES.json')=='1631d0bad4dbd5c654c233fb9747c8c18e80105be8c1c4fe507d6a8aae13cf3b','native manifest pin'
 assert sha(n/'FREEZE.json')=='68dd474d92b91a32b6827b3584bd1f92f4a3ef7e8b10c3d80d2c4348bee40c2b','native freeze pin'
 manifest=json.loads((n/'FILES.json').read_text())['files'];expected={x['path'] for x in manifest}|{'FILES.json','FREEZE.json'}
 actual={str(x.relative_to(n)) for x in n.rglob('*') if not x.is_dir()}
 assert actual==expected,'native closed file roster'
 dirs={str(p) for f in expected for p in pathlib.Path(f).parents if str(p)!='.'}
 assert {str(x.relative_to(n)) for x in n.rglob('*') if x.is_dir()}==dirs,'native closed directory roster'
 for x in manifest:
  f=n/x['path'];assert not f.is_symlink() and sha(f)==x['sha256'] and f.stat().st_size==x['bytes'],x['path']
 for x in json.loads((P/'PROVIDERS.json').read_text()):
  assert sha(P/'inputs/providers'/pathlib.Path(x['path']).name)==x['sha256'],x['path']
 assert sha(P/'inputs/nested-result.json')=='3a0f6848b4c9496aecf7cd10845aca03e15bb24a481554afd59961bdfce8cd63'
 print('Authenticated native closed roster, provider hashes, and nested receipt')
if __name__=='__main__':check()
