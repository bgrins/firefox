import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OBS=ROOT/'artifacts/css-linear-second-stop-crash-observation-v1'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={}
for label in ['control','second-position']:
 d=OBS/'direct-release'/label
 for n in ['probe.html','PROCESS.json','OBSERVATION.json','CLEANUP.json','LOG.json','browser.log']:
  pins[str((d/n).relative_to(ROOT))]=sha(d/n)
 log=(d/'browser.log').read_text(); rec=read(d/'LOG.json'); obs=read(d/'OBSERVATION.json'); cleanup=read(d/'CLEANUP.json'); process=read(d/'PROCESS.json')
 assert rec=={'sha256':sha(d/'browser.log'),'bytes':(d/'browser.log').stat().st_size}
 assert process['command'][0]=='/Applications/Firefox.app/Contents/MacOS/firefox' and process['command'][-1]==(d/'probe.html').as_uri()
 assert process['pid']==process['group'] and process['pid']>0
 assert obs['start_seen'] and not obs['panic_seen'] and not obs['observation_deadline_reached']
 assert 'LINEAR_PROBE_START' in log and 'panicked at' not in log
 assert cleanup['owned_group_absent'] and cleanup['profile_removed']
 if label=='control':
  assert obs['return_seen'] and obs['exit_before_cleanup'] is None
  assert 'LINEAR_PROBE_RETURN ""' in log
  assert 'A content process crashed' not in log
 else:
  assert not obs['return_seen'] and obs['exit_before_cleanup']==cleanup['exit_after_cleanup']==245
  assert 'LINEAR_PROBE_RETURN' not in log
  assert 'A content process crashed and MOZ_CRASHREPORTER_SHUTDOWN is set' in log
  assert 'exited on signal 11' in log
  assert log.index('LINEAR_PROBE_START')<log.index('A content process crashed')
for n in ['run_direct.py','RELEASE-BINARY-PRE.json','RELEASE-OUTCOME.json']:
 pins[str((OBS/n).relative_to(ROOT))]=sha(OBS/n)
proposal=ROOT/'artifacts/css-linear-second-position-guard-proposal-v1'
pins[str((proposal/'FILES.json').relative_to(ROOT))]=sha(proposal/'FILES.json')
report={'direct_release_content_crash_confirmed':True,'single_position_control_returned':True,'crash_parent_exit_before_cleanup':245,'content_signal':11,'rust_panic_text_present':False,'cleanup_receipts_group_absent_and_profile_removed':True,'mcp_timeout_is_crash_proof':False,'native_root_cause':'Source-consistent masked second endpoint followed by unresolved percentage unwrap; no captured native stack proves the exact release instruction.','security_or_memory_corruption_claim':False,'independent_browser_execution':False,'live_process_census':False,'new_fix_acceptance':False}
for n,v in [('ASSESSMENT.json',report),('REFERENCES.json',pins)]:
 p=HERE/n
 if p.exists(): assert read(p)==v
 else:p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
print(json.dumps(report))
