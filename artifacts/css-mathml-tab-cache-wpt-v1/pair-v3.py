from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parents[2]
here=Path(__file__).resolve().parent
native=root/'layout/generic/nsTextFrame.cpp'
patch=root/'artifacts/css-mathml-tab-cache-design-v1/proposal/leading-origin.patch'
env={**os.environ,'MOZCONFIG':str(root/'mozconfig'),'MOZ_SKIP_PATH_PERFORMANCE_CHECK':'1'}
records=[]
def save():
 (here/'pair-v3-progress.json').write_text(json.dumps(records,indent=2)+'\n')
def run(command,log,expected):
 with (here/log).open('w') as out:
  proc=subprocess.run(command,cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT)
 records.append({'command':command,'log':log,'exit_code':proc.returncode});save()
 assert proc.returncode==expected,(log,proc.returncode)
assert native.read_bytes()==(here/'native-candidate-v1.cpp').read_bytes()
run(['git','apply','--reverse',str(patch)],'restore-original-v3.log',0)
assert native.read_bytes()==(here/'native-original-v1.cpp').read_bytes()
run(['/Users/bgrins/venvs/firefox/bin/python','./mach','build','binaries'],'build-original-v3.log',0)
run(['python3',str(here/'run_wpt_v3.py'),'baseline-v3'],'baseline-v3-driver.log',1)
receipt=json.loads((here/'baseline-v3-receipt.json').read_text());assert receipt['suite_end_count']==1 and receipt['all_inputs_unchanged']
run(['git','apply',str(patch)],'restore-candidate-v4.log',0)
assert native.read_bytes()==(here/'native-candidate-v1.cpp').read_bytes()
run(['/Users/bgrins/venvs/firefox/bin/python','./mach','build','binaries'],'build-candidate-v4.log',0)
run(['python3',str(here/'run_wpt_v3.py'),'candidate-v4'],'candidate-v4-driver.log',0)
print('Original/candidate full boundary pair completed.')
