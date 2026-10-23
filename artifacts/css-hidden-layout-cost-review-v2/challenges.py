import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S")
sys.dont_write_bytecode = True
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'source'
spec=importlib.util.spec_from_file_location('cleanup',SOURCE/'cleanup.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
results={}
for name,listing in [('empty',''),('malformed','123 123 501 S'),('nonnumeric','abc 123 501 S Thu Oct 22 12:00:00 2026'),('negative','123 -1 501 S Thu Oct 22 12:00:00 2026')]:
    with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout=listing)):
        try: m.members(123)
        except (ValueError,RuntimeError): results[name]='rejected'
        else: raise RuntimeError('bad listing accepted: '+name)
with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout='12 12 501 S Thu Oct 22 12:00:00 2026')):
    if m.members(123)!=[]: raise RuntimeError('unrelated group retained')
    results['valid_nonempty_listing_other_group']='empty selected group'
class Process:
    pid=123
    returncode=0
    def poll(self): return self.returncode
    def wait(self,timeout): return self.returncode
base={'pid':124,'pgid':123,'uid':os.getuid(),'state':'S','birth':'known','sid':123,'currentPgid':123}
for field,value in [('uid',os.getuid()+1),('sid',124),('currentPgid',124)]:
    bad=dict(base); bad[field]=value
    with patch.object(m,'members',return_value=[bad]),patch.object(m.os,'killpg') as signal:
        r=m.terminate_owned(Process(),[base])
        if r['terminal'] or not r['errors'] or signal.called: raise RuntimeError('ownership mismatch signalled')
        results['mismatch_'+field]='rejected without signal'
with patch.object(m,'members',side_effect=PermissionError('inspection denied')),patch.object(m.os,'killpg') as signal:
    r=m.terminate_owned(Process(),[base])
    if r['terminal'] or r['noLiveGroup'] or signal.called: raise RuntimeError('inspection failure accepted')
    results['inspection_denied']='rejected without signal'
print(json.dumps({'status':'PASS','controls':results,'scope':'Mocks only; no browser, child process or real signals.'},indent=2))
