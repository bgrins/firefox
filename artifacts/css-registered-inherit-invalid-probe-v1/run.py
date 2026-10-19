from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
files=['servo/components/style/custom_properties.rs','servo/components/style/properties/cascade.rs','servo/components/style/stylist.rs','servo/components/style/properties_and_values/value.rs','testing/web-platform/tests/css/css-properties-values-api/registered-inherit-invalid.html','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']
pins={f:sha(root/f) for f in files}
cmd=['./mach','wpt','--headless','--processes=1','--log-raw='+str(here/'raw.json'),files[4]]
with (here/'wpt.log').open('w') as out:result=subprocess.run(cmd,cwd=root,env={**os.environ,'MOZ_SKIP_PATH_PERFORMANCE_CHECK':'1'},stdout=out,stderr=subprocess.STDOUT)
assert all(sha(root/f)==pin for f,pin in pins.items())
(here/'RUN.json').write_text(json.dumps({'command':cmd,'exit':result.returncode,'pins':pins,'stable_after':True,'scope':'Current shared-tree fix71 build; diagnostic only, no paired repair or isolated base.'},indent=2)+'\n')
print('test exit',result.returncode)
