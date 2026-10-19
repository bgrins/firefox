import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
root=Path.cwd()
package=root/'artifacts/css-attr-namespace-index-admission-v1'
out=root/'artifacts/css-attr-reload-browser-v1/root-index-replay-v1'
assert hashlib.sha256((package/'FREEZE.json').read_bytes()).hexdigest()=='671d30e17d372ff0c2bd78dae1159825d41ab561733b52ff793e10cf4542d6a4'
freeze=json.loads((package/'FREEZE.json').read_text())
with tempfile.TemporaryDirectory(prefix='root-attr-index-',dir='/private/tmp') as tmp:
    source=Path(tmp)/'source'
    for name in [*freeze['files'],'FREEZE.json']:
        target=source/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(package/name,target)
    command=['python3','-I','-S','-B',str(source/'replay.py'),'--lean',str(root/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'),'--output',str(out)]
    result=subprocess.run(command,cwd=tmp)
    (out.parent/'root-index-replay-v1-process.json').write_text(json.dumps({'command':command,'exit_code':result.returncode,'relocated_source':True},indent=2)+'\n')
    raise SystemExit(result.returncode)
