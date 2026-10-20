import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
PROPOSAL=HERE
GIT=["git","-c","core.fsmonitor=false"]
SOURCE="servo/components/style/properties_and_values/value.rs"
TEST="testing/web-platform/tests/css/css-properties-values-api/registered-token-boundaries.html"

def git(*args,env=None,data=None):
    return subprocess.check_output(GIT+list(args),cwd=ROOT,env=env,input=data)

def sha(data):
    return hashlib.sha256(data).hexdigest()

head=git("rev-parse","HEAD").decode().strip()
initial_index=git("write-tree").decode().strip()
patch=PROPOSAL/"native.patch"
assert sha(patch.read_bytes())=='effba29493b878434c63dfd4380d5e8d0b7e233cd104b6425794945fba5840cf'
test=HERE/"landing.html"
transfer={"final_sha256": '99bfdbf9f19063de13e609ac4d5ae2b3ebeb22484e84dde289f43a8d1178ac0e'}
assert sha(test.read_bytes())==transfer["final_sha256"]
result={}
for label,base,expected in [("stack",head,'fd2b72943646fe84c22a16e21f21b8f890fc2782bc77e7db54d93db4d125ee93'),
 ("standalone","976279105b2e78b8666a959eb3f25c9176cefaf8",None)]:
    with tempfile.TemporaryDirectory(prefix="token-boundary-package-",dir="/private/tmp") as tmp:
        env={**os.environ,"GIT_INDEX_FILE":str(Path(tmp)/"index")}
        git("read-tree",base,env=env)
        git("apply","--cached","--check",str(patch),env=env)
        git("apply","--cached",str(patch),env=env)
        actual_source=git("show",":"+SOURCE,env=env)
        if expected is not None:
            assert sha(actual_source)==expected
        else:
            (HERE/"value.upstream-candidate.rs").write_bytes(actual_source)
        expected=sha(actual_source)
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
assert git("rev-parse","HEAD").decode().strip()==head and git("write-tree").decode().strip()==initial_index
result["scope"]="Two-file local and upstream alternatives. Source apply/reverse only; no isolated upstream runtime. Main HEAD/index preserved."
(HERE/"PACKAGING.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
