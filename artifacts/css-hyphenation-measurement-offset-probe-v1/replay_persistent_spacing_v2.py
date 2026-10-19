import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
root=Path.cwd()
package=root/'artifacts/css-hyphenation-spacing-state-proof-v1/exports/persistent-spacing-v2'
out=root/'artifacts/css-hyphenation-measurement-offset-probe-v1/root-persistent-spacing-v2'
assert hashlib.sha256((package/'MANIFEST.json').read_bytes()).hexdigest()=='50f92a674faf606f42c65cf923c075373f4b807ace613b74cf8d542939a99b64'
assert hashlib.sha256((package/'FREEZE.json').read_bytes()).hexdigest()=='277a2555c8c0107aa4aa042de5a91d773cc4a8b55bb632b6d26e64a41155c56b'
with tempfile.TemporaryDirectory(prefix='root-persistent-spacing-',dir='/private/tmp') as tmp:
    source=Path(tmp)/'source'
    shutil.copytree(package,source)
    command=['python3','-I','-S','-B',str(source/'check.py'),'--manifest-sha','50f92a674faf606f42c65cf923c075373f4b807ace613b74cf8d542939a99b64','--lean',str(root/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'),'--output',str(out)]
    result=subprocess.run(command,cwd=tmp)
    (out.parent/'root-persistent-spacing-v2-process.json').write_text(json.dumps({'command':command,'exit_code':result.returncode,'relocated_source':True},indent=2)+'\n')
    raise SystemExit(result.returncode)
