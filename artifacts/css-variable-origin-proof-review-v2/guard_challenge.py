import json,runpy,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
capsule=root/'relocated-source'
mode=sys.argv[1]
out=root/('guard-existing-tool-'+mode+'-output')
called=[]
def dispatch(command,**kwargs):
 called.append([str(x) for x in command])
 raise RuntimeError('INDEPENDENT_DISPATCH_SENTINEL_NO_TOOL_EXECUTION')
subprocess.run=dispatch
sys.argv=[str(capsule/'check.py'),'--output',str(out),'--lean','/usr/bin/true']
try:
 runpy.run_path(str(capsule/'check.py'),run_name='__main__')
except BaseException as e:
 record={'optimize':sys.flags.optimize,'isolated':sys.flags.isolated,'no_site':sys.flags.no_site,'exception':repr(e),'output_created':out.exists(),'dispatched':called,'scope':'subprocess interception before any Lean/Rust execution; /usr/bin/true fails pinned tool identity in normal mode'}
 (root/('guard-existing-tool-'+mode+'.json')).write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record))
