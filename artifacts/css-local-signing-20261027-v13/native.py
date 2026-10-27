import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0');GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args):return subprocess.check_output(GIT+list(args),cwd=ROOT,env=ENV)
def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def run(args,log):
 with (HERE/log).open('x') as f:subprocess.run(args,cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
validation=read(HERE/'raw-validation-receipt.json')
assert validation['signature_verified']
assert git('rev-parse','HEAD').decode().strip()==validation['commit']
acceptance=read(ROOT/'artifacts/css-attr-raw-nested-validation-v2/ACCEPTANCE.json')
assert acceptance['fix']==138 and acceptance['status']=='READY_FOR_STANDALONE_SIGNED_COMMIT'
helper=ROOT/'artifacts/css-attr-raw-nested-partial-commit-v2/check.py'
base=[sys.executable,'-I','-S','-B',str(helper)]
epoch=HERE/'CURRENT-EPOCH.json';digest=hashlib.sha256(epoch.read_bytes()).hexdigest()
plan=HERE/'native-plan';binding=HERE/'native-binding'
run(base+['prepare',str(plan),validation['commit'],str(epoch),digest],'native-prepare.log')
run(base+['bind',str(binding),str(epoch),digest,str(plan)],'native-bind.log')
p=read(plan/'PLAN.json');b=read(binding/'BINDING.json')
assert hashlib.sha256((plan/'staged.patch').read_bytes()).hexdigest()==b['staged_patch_sha256']
assert not git('diff','--cached','--name-only')
assert git('rev-parse','HEAD').decode().strip()==p['parent']
assert git('config','--get','commit.gpgsign').strip()==b'true'
git('apply','--cached','--check',str(plan/'staged.patch'));git('apply','--cached',str(plan/'staged.patch'))
assert git('write-tree').decode().strip()==p['tree']
message=HERE/'native-fix-message.txt';message.write_text('No bug - Keep nested raw attribute reads out of typed dependency cycles. r?#firefox-style-system-reviewers\n')
run(GIT+['commit','--file',str(message)],'native-fix-commit.log')
run(base+['verify-after',str(binding),str(plan)],'native-fix-verification.log')
receipt=read(binding/'RECEIPT.json');save(HERE/'native-fix-receipt.json',receipt)
current=read(binding/'POST-EPOCH.json')
assert current['raw_attribute_transition']['role']=='candidate' and current['raw_attribute_transition']['compiled']
current['raw_attribute_transition'].update(accepted=True,fix=138,commit=receipt['commit'])
epoch.write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
print('Signed native fix138',receipt['commit'],flush=True)
