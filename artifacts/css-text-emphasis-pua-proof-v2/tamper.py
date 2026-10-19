import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def run_tamper_controls(root, output):
    root=Path(root);output=Path(output);output.mkdir(parents=True)
    original=json.loads((root/'INPUTS.json').read_text())
    names=[r['path'] for r in original['inputs']]+['INPUTS.json']
    marker='UNAUTHENTICATED_PACKAGE_EXECUTED'
    results=[]
    variants=['clean','modified-listed','shadow-package','extra-module','shadow-bytecode','duplicate-path','escaping-path','absolute-path','noncanonical-path','symlink-file','symlink-directory','root-symlink','shadow-stdlib-module']
    for variant in variants:
        capsule=output/variant;capsule.mkdir()
        for name in names:
            target=capsule/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((root/name).read_bytes())
        manifest=json.loads((capsule/'INPUTS.json').read_text())
        if variant=='modified-listed':
            with (capsule/'generate_native.py').open('a') as file:file.write('\nprint('+repr(marker)+')\n')
        elif variant=='shadow-package':
            (capsule/'generate_native').mkdir();(capsule/'generate_native/__init__.py').write_text('print('+repr(marker)+')\nraise SystemExit(73)\n')
        elif variant=='shadow-stdlib-module':(capsule/'json.py').write_text('print('+repr(marker)+')\nraise SystemExit(73)\n')
        elif variant=='extra-module':(capsule/'unexpected.py').write_text('print('+repr(marker)+')\n')
        elif variant=='shadow-bytecode':(capsule/'generate_native.pyc').write_bytes(b'unlisted-bytecode')
        elif variant=='duplicate-path':manifest['inputs'].append(dict(manifest['inputs'][0]))
        elif variant in ('escaping-path','absolute-path','noncanonical-path'):
            row=dict(manifest['inputs'][0])
            row['path']={'escaping-path':'../outside.py','absolute-path':'/private/tmp/outside.py','noncanonical-path':'./generate_native.py'}[variant]
            manifest['inputs'].append(row)
        elif variant=='symlink-file':
            (capsule/'generate_native.py').unlink();(capsule/'generate_native.py').symlink_to(root/'generate_native.py')
        elif variant=='symlink-directory':
            shutil.rmtree(capsule/'sources/gfx');(capsule/'sources/gfx').symlink_to(root/'sources/gfx',target_is_directory=True)
        if variant in ('duplicate-path','escaping-path','absolute-path','noncanonical-path'):
            (capsule/'INPUTS.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
        digest=hashlib.sha256((capsule/'INPUTS.json').read_bytes()).hexdigest()
        destination=capsule/'must-not-exist'
        check=capsule/'check.py'
        if variant=='root-symlink':
            alias=output/'root-symlink-alias';alias.symlink_to(capsule,target_is_directory=True);check=alias/'check.py'
        command=[sys.executable,'-I','-S','-B',str(check),'--manifest-sha',digest,'--output',str(destination)]
        if variant=='clean':command.append('--authenticate-only')
        process=subprocess.run(command,capture_output=True,text=True)
        row=dict(case=variant,exit=process.returncode,stdout=process.stdout,stderr=process.stderr,output_created=destination.exists(),marker_executed=marker in process.stdout,manifest_sha256=digest)
        assert not row['marker_executed'] and not row['output_created'],row
        if variant=='clean':assert process.returncode==0,row
        else:assert process.returncode==1 and 'REJECTED:' in process.stderr,row
        results.append(row)
    (output/'RESULT.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    return results
