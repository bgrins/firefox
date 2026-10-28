import importlib.util
import json
from pathlib import Path
import signal
import subprocess
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cleanup', HERE / 'wpt_cleanup.py')
c = importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class Process:
    pid = 99999991
    def poll(self): return None
    def wait(self, timeout):
        assert timeout == 45
        events.append('grace45')
        raise subprocess.TimeoutExpired('fake', timeout)
class Control:
    @staticmethod
    def terminate(process):
        events.append('terminate-wrapper')
        return {'owned_group_absent': True}
    @staticmethod
    def group_members(pgid): return list(members)
with tempfile.TemporaryDirectory(prefix='css-lh-cleanup-control-') as scratch:
    output = Path(scratch) / 'wpt';output.mkdir()
    temporary = Path(tempfile.mkdtemp(prefix='css-line-height-wpt-', dir='/private/tmp'))
    events, members = [], [99999992]
    (output/'COMMAND.json').write_text(json.dumps({'wrapper_manifest_sha256':'test','phase':'original-1','temporary_root':str(temporary)}))
    (output/'PROCESS.json').write_text(json.dumps({'pid':99999992,'pgid':99999992}))
    def signal_group(pgid, sig):
        events.append(('signal', pgid, int(sig)))
        if pgid == 99999992:members.clear()
    try:
        with patch.object(c.os, 'killpg', signal_group):
            result=c.finish(Process(),output,'original',{'wpt_manifest':'test'},Control)
        assert result['forced_child_cleanup'] and result['restoration_safe'] and temporary.exists()
        assert not result['temporary_root_removed'] and result['retained_temporary_root']==str(temporary)
        assert events.index('grace45') < events.index('terminate-wrapper')
        assert ('signal',99999992,int(signal.SIGTERM)) in events
        (output/'PROCESS.json').unlink()
        try:c.finish(None,output,'original',{'wpt_manifest':'test'},Control)
        except FileNotFoundError:pass
        else:raise AssertionError('uncertified command-without-process accepted')
        (output/'COMMAND.json').unlink()
        result=c.finish(None,output,'original',{'wpt_manifest':'test'},Control)
        assert result['no_browser_launch_certified'] and result['restoration_safe']
        alias = Path(scratch) / 'alias';alias.symlink_to(output)
        try:c.no_launch(alias)
        except AssertionError:pass
        else:raise AssertionError('accepted symlink output')
    finally:
        temporary.rmdir()
assert not Path(scratch).exists()
print(json.dumps({'forced_child_recovery':True,'grace_before_forcing':True,'unknown_temporary_directory_retained':True,'ambiguous_launch_rejected':True,'no_launch_accepted':True,'real_processes_signaled':False,'scratch_removed':True}))
