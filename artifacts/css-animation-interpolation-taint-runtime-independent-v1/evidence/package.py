import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
PROPOSAL=ROOT/"artifacts/css-animation-interpolation-taint-proposal-v1"
GIT=["git","-c","core.fsmonitor=false"]
SOURCE="servo/components/style/properties_and_values/value.rs"
TEST="testing/web-platform/tests/css/css-values/registered-number-interpolation-attr-taint.html"

def git(*args,env=None,data=None):
    return subprocess.check_output(GIT+list(args),cwd=ROOT,env=env,input=data)

def sha(data):
    return hashlib.sha256(data).hexdigest()

head=git("rev-parse","HEAD").decode().strip()
assert not git("diff","--cached","--name-only").strip()
patch=PROPOSAL/"native.patch"
assert sha(patch.read_bytes())=="f71bde0368680e8cdfd39c9df1fc5e0ab3e302a4b76fe1eea7f46b35b7b562f8"
test=HERE/"landing.html"
transfer=json.loads((HERE/"HELP-LINK-TRANSFER.json").read_text())
assert sha(test.read_bytes())==transfer["final_sha256"]
result={}
for label,base,expected in [("stack",head,"485c097931bcb385bc0ada6679c3429f6f300ffae5f03c75268458feb3316fa0"),
 ("standalone","976279105b2e78b8666a959eb3f25c9176cefaf8","6dc7d9fca764de3f4b462913413aa73015b5de2e439adf278bbfcd0397699747")]:
    with tempfile.TemporaryDirectory(prefix="interpolation-package-",dir="/private/tmp") as tmp:
        env={**os.environ,"GIT_INDEX_FILE":str(Path(tmp)/"index")}
        git("read-tree",base,env=env)
        git("apply","--cached","--check",str(patch),env=env)
        git("apply","--cached",str(patch),env=env)
        assert sha(git("show",":"+SOURCE,env=env))==expected
        blob=git("hash-object","-w","--stdin",data=test.read_bytes()).decode().strip()
        git("update-index","--add","--cacheinfo","100644,"+blob+","+TEST,env=env)
        tree=git("write-tree",env=env).decode().strip()
        paths=git("diff","--name-only",base,tree).decode().splitlines()
        assert sorted(paths)==sorted([SOURCE,TEST])
        data=git("diff","--binary","--full-index",base,tree,"--",SOURCE,TEST)
        out=HERE/(label+"-native-wpt.patch");out.write_bytes(data)
        git("apply","--cached","--reverse","--check",str(out),env=env)
        git("apply","--cached","--reverse",str(out),env=env)
        assert git("write-tree",env=env).decode().strip()==git("rev-parse",base+"^{tree}").decode().strip()
        result[label]={"base":base,"patch":str(out.relative_to(ROOT)),"sha256":sha(data),
          "paths":paths,"pins":{SOURCE:expected,TEST:transfer["final_sha256"]},"candidate_tree":tree,"exact_apply_reverse":True}
assert git("rev-parse","HEAD").decode().strip()==head and not git("diff","--cached","--name-only").strip()
result["scope"]="Two-file local and upstream alternatives. Source apply/reverse only; no isolated upstream runtime. Main HEAD/index preserved."
(HERE/"PACKAGING.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
