import hashlib,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROPOSAL=ROOT/'artifacts/css-flex-table-caption-cache-repair-v1'
SOURCE=ROOT/'layout/generic/nsFlexContainerFrame.cpp'
TEST=ROOT/'testing/web-platform/tests/css/css-flexbox/table-caption-percentage-height-resize.html'
G=['git','-c','core.fsmonitor=false']
def git(*a):return subprocess.check_output(G+list(a),cwd=ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(HERE/n).write_text(json.dumps(d,indent=2)+'\n')
before=SOURCE.read_bytes();head=git('rev-parse','HEAD');index=git('diff','--cached','--binary')
assert not TEST.exists()
assert sha(SOURCE)==json.loads((PROPOSAL/'PROPOSAL-PINS.json').read_text())['source/nsFlexContainerFrame.cpp']
state={'status':'running'};save('STATE.json',state)
try:
 git('apply','--check',str(PROPOSAL/'native.patch'));git('apply',str(PROPOSAL/'native.patch'))
 TEST.write_bytes((PROPOSAL/TEST.name).read_bytes())
 (HERE/'candidate-before.cpp').write_bytes(SOURCE.read_bytes());(HERE/TEST.name).write_bytes(TEST.read_bytes())
 commands=[('format',['./mach','lint','-l','clang-format','--fix',str(SOURCE.relative_to(ROOT))]),('wpt-lint',['./mach','lint','-l','wpt','--warnings','--include-third-party',str(TEST.relative_to(ROOT))]),('reviewers',['./mach','file-info','reviewers',str(SOURCE.relative_to(ROOT))])]
 for name,command in commands:
  with (HERE/(name+'.log')).open('w') as log:r=subprocess.run(command,cwd=ROOT,env={**os.environ,'MOZ_SKIP_PATH_PERFORMANCE_CHECK':'1'},stdout=log,stderr=subprocess.STDOUT)
  state[name]={'command':command,'exit':r.returncode};save('STATE.json',state)
 (HERE/'candidate-after.cpp').write_bytes(SOURCE.read_bytes())
 state['format_unchanged']=SOURCE.read_bytes()==(HERE/'candidate-before.cpp').read_bytes()
 state['test_unchanged']=TEST.read_bytes()==(HERE/TEST.name).read_bytes()
finally:
 SOURCE.write_bytes(before);TEST.unlink(missing_ok=True)
 state.update(status='terminal',source_restored=SOURCE.read_bytes()==before,head_unchanged=git('rev-parse','HEAD')==head,index_unchanged=git('diff','--cached','--binary')==index)
 save('STATE.json',state)
print(json.dumps(state,indent=2))
assert all(state[k]['exit']==0 for k in ['format','wpt-lint','reviewers'])
assert all(state[k] for k in ['test_unchanged','source_restored','head_unchanged','index_unchanged'])
