import sys
sys.dont_write_bytecode=True
import importlib.util,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('seal',ROOT/'seal.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'outer-controls-v1');out.mkdir();results=[]
for name,reseal_capsule,reason in [('nested-unlisted-cache',False,'unexpected file: cache.pyc'),('nested-resealed-cache',True,'nested capsule pin FILES.json')]:
    clone=out/'disposable';clone.mkdir();shutil.copy2(ROOT/'check.py',clone/'check.py');shutil.copytree(ROOT/'capsule',clone/'capsule');(clone/'capsule/cache.pyc').write_bytes(b'extra')
    if reseal_capsule:m.seal(clone/'capsule')
    pin=m.seal(clone)
    p=subprocess.run([sys.executable,'-I','-S',str(clone/'check.py'),'--manifest-sha',pin,'--verify-only'],capture_output=True,text=True)
    (out/(name+'.log')).write_text(p.stdout+p.stderr)
    if not p.returncode or reason not in p.stdout+p.stderr:raise RuntimeError('wrong outer rejection')
    results.append({'name':name,'exit':p.returncode,'reason':reason,'outer_resealed':True,'capsule_resealed':reseal_capsule,'manifest':pin});shutil.rmtree(clone)
(out/'RESULT.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
