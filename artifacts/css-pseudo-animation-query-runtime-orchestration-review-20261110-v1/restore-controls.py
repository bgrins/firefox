import hashlib,importlib.util,json,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
AUTHOR=HERE.parent/'css-pseudo-animation-query-runtime-20261110-v1'
spec=importlib.util.spec_from_file_location('reviewed_runner',AUTHOR/'run.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
results=[]
for active in [False,True]:
 with tempfile.TemporaryDirectory(prefix='query-restore-review-') as name:
  root=Path(name);r.ROOT=root;r.APP=root/'app';r.TEST_TREE=root/'installed-tests'
  r.APP.mkdir();r.TEST_TREE.mkdir();(r.APP/'binary').write_text('retained');(r.TEST_TREE/'test').write_text('original test');(r.TEST_TREE/'link').symlink_to('test')
  source=root/'source.cpp';source.write_text('original source');fixture=root/'fixture.html';metadata=root/'fixture.html.ini';extra=root/'all-tests.pkl';extra.write_text('original metadata');generated=root/'test-installs.pkl';(root/'mozconfig').write_text('configuration')
  output=root/'output';output.mkdir();backups=output/'backups';backups.mkdir()
  app=r.bundle.scan(r.APP);tree=r.bundle.scan(r.TEST_TREE);extras={'all-tests.pkl':r.bundle.entry(extra)}
  appmap=r.bundle.backup(r.APP,app,backups/'app');treemap=r.bundle.backup(r.TEST_TREE,tree,backups/'mochitest');extramap=r.bundle.backup(root,extras,backups/'extras')
  sources=root/'runner/source';sources.mkdir(parents=True);(sources/'source.cpp').write_bytes(source.read_bytes());r.HERE=root/'runner'
  role={'source.cpp':{'base':r.sha(source)}};retained={'binaries':{'app/binary':r.sha(r.APP/'binary')}};plan={'head':'f'*40,'mozconfig_sha256':r.sha(root/'mozconfig')}
  indexbytes=b'fixed test index';index=hashlib.sha256(indexbytes).hexdigest()
  def git(*args):
   if args==('rev-parse','HEAD'):return (plan['head']+'\n').encode()
   if args==('ls-files','--stage','-z'):return indexbytes
   if args in [('diff','--name-only'),('diff','--cached','--name-only')]:return b''
   raise AssertionError(args)
  r.git=git;r.verify_test_inputs=lambda: None
  source.write_text('candidate source');fixture.write_text('temporary fixture');touched={'source.cpp':r.sha(source)};installed={fixture:r.sha(fixture)}
  (r.APP/'binary').write_text('candidate binary');(r.TEST_TREE/'test').write_text('changed installed test');(r.TEST_TREE/'new').write_text('new installed test');(r.TEST_TREE/'link').unlink();(r.TEST_TREE/'link').symlink_to('new');extra.write_text('changed metadata');generated.write_text('generated metadata')
  r.process.ACTIVE={123:object()} if active else {};errors=[]
  r.restore('candidate',output,plan,role,retained,{fixture:root/'fixture-origin'},[metadata],touched,installed,app,extras,backups,appmap,extramap,index,0,errors,tree,treemap,['test-installs.pkl'])
  if active:
   assert errors and backups.exists() and source.read_text()=='candidate source' and fixture.exists() and generated.exists()
   assert r.bundle.semantic(r.bundle.scan(r.TEST_TREE))!=r.bundle.semantic(tree)
  else:
   assert errors==[] and not backups.exists() and not fixture.exists() and not generated.exists(), errors
   assert source.read_text()=='original source' and extra.read_text()=='original metadata'
   assert r.bundle.semantic(r.bundle.scan(r.APP))==r.bundle.semantic(app)
   assert r.bundle.semantic(r.bundle.scan(r.TEST_TREE))==r.bundle.semantic(tree)
   assert json.loads((output/'RESTORED.json').read_text())['test_metadata_restored']
  results.append({'active_process_control':active,'passed':True,'errors':errors})
print(json.dumps({'status':'PASS','isolated_synthetic_only':True,'live_source_app_git_browser_operations':False,'controls':results},indent=2))
