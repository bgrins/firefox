import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S')
sys.dont_write_bytecode = True
import ast
import io
import json
from pathlib import Path
from urllib.parse import urlsplit
HERE=Path(__file__).resolve().parent
source=ast.parse((HERE/'run.py').read_text())
node=next(n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='Handler')
receipts=[];posts=[]
env={'BaseHTTPRequestHandler':object,'urlsplit':urlsplit,'HERE':HERE,'json':json,
     'request_receipt':receipts.append,'progress_count':0,'posts':posts}
exec(compile(ast.Module(body=[node],type_ignores=[]),'extracted-handler','exec'),env)
Handler=env['Handler']
def request(method,path,data=b''):
    h=Handler();h.path=path;h.headers={'Content-Length':str(len(data))};h.rfile=io.BytesIO(data);h.wfile=io.BytesIO()
    h.status=[];h.send_error=h.status.append;h.send_response=h.status.append;h.send_header=lambda *a:None;h.end_headers=lambda:None
    getattr(h,'do_'+method)()
    return h
results={}
r=request('GET','/');assert r.status==[200] and receipts[-1]['route']=='/';results['GET_before_script']='recorded'
r=request('POST','/progress',json.dumps({'sequence':0,'stage':'script-start'}).encode());assert r.status==[204] and env['progress_count']==1 and not posts;results['startup_progress']='accepted separately from results'
for name,value in [('duplicate',{'sequence':0,'stage':'script-start'}),('boolean',{'sequence':True,'stage':'config-ready'}),('wrong_stage',{'sequence':1,'stage':'unknown'}),('not_object',[])]:
    r=request('POST','/progress',json.dumps(value).encode());assert r.status==[400] and env['progress_count']==1;results[name]='rejected'
r=request('POST','/progress',b'{');assert r.status==[400];results['invalid_json']='rejected'
r=request('POST','/progress',b' '*4097);assert r.status==[413];results['oversize']='rejected'
r=request('POST','/progress',json.dumps({'sequence':1,'stage':'config-ready'}).encode());assert r.status==[204] and env['progress_count']==2;results['next_sequence']='accepted'
env['progress_count']=300
r=request('POST','/progress',json.dumps({'sequence':300,'stage':'batch-begin'}).encode());assert r.status==[400];results['progress_bound']='rejected'
r=request('POST','/result',json.dumps({'complete':False,'error':'synthetic'}).encode());assert r.status==[204] and len(posts)==1;results['result_endpoint']='unchanged separate receipt'
assert any(r.get('event')=='progress-persisted' for r in receipts)
print(json.dumps({'status':'PASS','tests':results,'scope':'AST-extracted handler with memory streams; no server/browser/process launched.'},indent=2))
