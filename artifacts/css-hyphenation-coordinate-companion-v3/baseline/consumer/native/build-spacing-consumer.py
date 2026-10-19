import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'development-build/full'
TARGET=OUT/'spacing-consumer'
TARGET.mkdir(exist_ok=True)
records=[]
def run(name,args,data=None):
 r=subprocess.run(list(map(str,args)),input=data,capture_output=True,timeout=180)
 (TARGET/(name+'.stdout')).write_bytes(r.stdout)
 (TARGET/(name+'.stderr')).write_bytes(r.stderr)
 records.append({'name':name,'args':list(map(str,args)),'exit':r.returncode})
 (TARGET/'BUILD.json').write_text(json.dumps(records,indent=2)+'\n')
 assert r.returncode==0,(name,r.stderr.decode())
 return r.stdout
run('extract',[sys.executable,ROOT/'native/extract-spacing-consumer.py'])
args=next(r['args']for r in json.loads((OUT/'commands.json').read_text())if r['name']=='compile-provider')
args=args[:args.index('-c')]
run('compile',args+['-I'+str(OUT),TARGET/'spacing.cpp','-licucore','-o',TARGET/'spacing'])
raw=(OUT/'hyphen-consumer-matrix-input.txt').read_bytes()
actual=run('fixed-matrix',[TARGET/'spacing'],raw)
expected=(OUT/'hyphen-consumer-matrix-output.txt').read_bytes()
assert actual==expected
result={'cases':len(raw.splitlines()),'unchanged_matrix':True,'input_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(actual).hexdigest(),'binary_sha256':hashlib.sha256((TARGET/'spacing').read_bytes()).hexdigest(),'status':'complete spacing/measurement native fixture compatibility; remaining font/style/autospace/caller provider admission open'}
(TARGET/'REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
