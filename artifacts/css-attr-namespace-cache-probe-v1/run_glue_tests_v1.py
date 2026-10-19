import hashlib,json,os,subprocess
from pathlib import Path
root=Path.cwd()
here=root/'artifacts/css-attr-namespace-cache-probe-v1'
paths=['servo/components/style/custom_properties.rs','servo/components/style/properties/cascade.rs','servo/ports/geckolib/glue.rs','layout/inspector/tests/test_getSubstitutedValue.html','layout/inspector/tests/test_getComputationSteps.html','layout/inspector/tests/mochitest.toml','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']
def pins():
 return {name:hashlib.file_digest((root/name).open('rb'),'sha256').hexdigest() for name in paths}
before=pins()
command=['/Users/bgrins/venvs/firefox/bin/python','./mach','mochitest','--headless',*paths[3:5]]
with (here/'glue-mochitest-v1.log').open('w') as stream:
 result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'MOZCONFIG':str(root/'mozconfig'),'MOZ_SKIP_PATH_PERFORMANCE_CHECK':'1'})
after=pins()
record={'command':command,'exit_code':result.returncode,'pins_before':before,'pins_after':after,'all_inputs_unchanged':before==after}
(here/'glue-mochitest-v1.json').write_text(json.dumps(record,indent=2)+'\n')
assert before==after
raise SystemExit(result.returncode)
