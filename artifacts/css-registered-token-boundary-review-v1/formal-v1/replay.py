import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
assert sys.flags.isolated and sys.flags.no_site
p=argparse.ArgumentParser()
p.add_argument('--producer',type=Path,required=True)
p.add_argument('--capsule',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
source=a.producer.resolve(); capsule=a.capsule.resolve(); output=a.output.resolve()
assert not capsule.exists() and not output.exists()
assert not capsule.is_relative_to(source) and not output.is_relative_to(source) and not output.is_relative_to(capsule)
for name, expected in {'FREEZE.json':'32a1de6a2fdc8030830cd67606fb64c07ce98aafb79674c825aba1717cd24dae','MANIFEST.json':'227ebc6df874c8263a0189a786bfd15491767e0fdb56c3a75272f8172a2d96e3','check.py':'52138d2c442fb0496d06f82567a8c6e24bf9f5aef36c86abd818a4edd00934ec'}.items():
 assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected
manifest=json.loads((source/'MANIFEST.json').read_text())
for name, expected in manifest.items():
 path=PurePosixPath(name)
 assert str(path)==name and not path.is_absolute() and '..' not in path.parts
 assert stat.S_ISREG((source/name).lstat().st_mode)
 assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected
for name in list(manifest)+['FREEZE.json','MANIFEST.json']:
 dest=capsule/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,dest)
subprocess.run([sys.executable,'-I','-S',str(capsule/'check.py'),'--output',str(output)],check=True)
