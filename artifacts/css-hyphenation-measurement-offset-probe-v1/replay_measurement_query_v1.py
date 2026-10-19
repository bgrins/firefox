import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
root=Path.cwd()
package=root/'artifacts/css-hyphenation-spacing-consumer-proof-v1/exports/measurement-query-v1'
out=root/'artifacts/css-hyphenation-measurement-offset-probe-v1/root-measurement-query-v1'
assert hashlib.sha256((package/'MANIFEST.json').read_bytes()).hexdigest()=='3fa792df328a3210e16640112359efe3b52be5ee3daeb086f9cd2650afe40eea'
assert hashlib.sha256((package/'FREEZE.json').read_bytes()).hexdigest()=='fb3e98a94334bf9faaac9ac2cd73d3b7660b17d7434218a28460925bca21ac2a'
with tempfile.TemporaryDirectory(prefix='root-measurement-query-',dir='/private/tmp') as tmp:
    source=Path(tmp)/'source'
    shutil.copytree(package,source)
    command=['python3','-I','-S','-B',str(source/'check.py'),'--manifest-sha','3fa792df328a3210e16640112359efe3b52be5ee3daeb086f9cd2650afe40eea','--lean',str(root/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'),'--output',str(out)]
    result=subprocess.run(command,cwd=tmp)
    (out.parent/'root-measurement-query-v1-process.json').write_text(json.dumps({'command':command,'exit_code':result.returncode,'relocated_source':True},indent=2)+'\n')
    raise SystemExit(result.returncode)
