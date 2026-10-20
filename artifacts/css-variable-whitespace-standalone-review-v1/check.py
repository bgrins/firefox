import sys
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):raise RuntimeError('use -I -S without optimization')
from pathlib import Path
import hashlib,json,os,stat
r=Path(__file__).resolve().parent
m=json.loads((r/'FILES.json').read_text());actual=set()
for base,dirs,files in os.walk(r):
 for n in dirs:
  if not stat.S_ISDIR((Path(base)/n).lstat().st_mode):raise RuntimeError('invalid directory')
 for n in files:
  p=Path(base)/n
  if not stat.S_ISREG(p.lstat().st_mode):raise RuntimeError('invalid file')
  actual.add(p.relative_to(r).as_posix())
if actual!=set(m)|{'FILES.json','FREEZE.json'}:raise RuntimeError('roster mismatch')
for n,h in m.items():
 if hashlib.sha256((r/n).read_bytes()).hexdigest()!=h:raise RuntimeError('hash mismatch '+n)
f=json.loads((r/'FREEZE.json').read_text())
if hashlib.sha256((r/'FILES.json').read_bytes()).hexdigest()!=f['files_sha256']:raise RuntimeError('seal mismatch')
import runpy
patch_text=runpy.run_path(str(r/'patch_text.py'))['patch_text']
base=(r/'upstream-custom_properties.rs').read_text()
for row in json.loads((r/'AUDIT.json').read_text()):
 folder=r/str(row['fix']);patch=(folder/'standalone-native-wpt.patch').read_text();parts=patch.split('diff --git ')[1:]
 if len(parts)!=2:raise RuntimeError('patch roster')
 native=(folder/'candidate.rs').read_text();test=(folder/'test.html').read_text()
 if patch_text(base,parts[0])!=native or patch_text(native,parts[0],True)!=base:raise RuntimeError('native roundtrip')
 if patch_text('',parts[1])!=test or patch_text(test,parts[1],True)!='':raise RuntimeError('test roundtrip')
 if hashlib.sha256(patch.encode()).hexdigest()!=row['patch_sha256']:raise RuntimeError('patch pin')
 if row['isolated_upstream_runtime']:raise RuntimeError('unsupported runtime claim')
if not all(x['matches_reviewed_pair'] for x in json.loads((r/'INTEGRATION-SOURCE-CHECK.json').read_text())):raise RuntimeError('integration transfer')
print('PASS standalone exact inventories/apply/reverse; isolated runtime NOT RUN')
