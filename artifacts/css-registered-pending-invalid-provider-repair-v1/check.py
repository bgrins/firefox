import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = "servo/components/style/custom_properties.rs"
WPT = "testing/web-platform/tests/css/css-properties-values-api/registered-pending-provider-defaults.html"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for path, expected in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert digest(ROOT / path) == expected, path
roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())[NATIVE]
for role, expected in roles.items():
    assert digest(HERE / role / NATIVE) == expected
subprocess.run(["rustfmt", "--check", "--edition", "2024", "--config-path",
                str(ROOT / "servo/rustfmt.toml"), str(HERE / "candidate" / NATIVE)], check=True)
with tempfile.TemporaryDirectory(prefix="pending-provider-static-") as tmp:
    scratch = Path(tmp)
    source = scratch / NATIVE
    source.parent.mkdir(parents=True)
    shutil.copyfile(HERE / "base" / NATIVE, source)
    for options, role in [([], "candidate"), (["-R"], "base")]:
        result = subprocess.run(["patch", "--fuzz=0", "-p1", *options, "-i",
                                 str(HERE / "native.patch")], cwd=scratch,
                                text=True, capture_output=True, check=True)
        assert "offset" not in result.stdout and "fuzz" not in result.stdout
        assert source.read_bytes() == (HERE / role / NATIVE).read_bytes()
    for options, role in [([], "candidate"), (["-R"], "base")]:
        result = subprocess.run(["patch", "--fuzz=0", "-p1", *options, "-i",
                                 str(HERE / "fix.patch")], cwd=scratch,
                                text=True, capture_output=True, check=True)
        assert "offset" not in result.stdout and "fuzz" not in result.stdout
        assert source.read_bytes() == (HERE / role / NATIVE).read_bytes()
        if role == "candidate":
            assert (scratch / WPT).read_bytes() == (HERE / "candidate" / WPT).read_bytes()
        else:
            assert not (scratch / WPT).exists()
    html = (HERE / "candidate" / WPT).read_text()
    js = scratch / "fixture.js"
    js.write_text(html.split("<script>")[1].split("</script>")[0])
    subprocess.run(["node", "--check", str(js)], check=True)
    enum = scratch / "enumerate.js"
    enum.write_text('const fs=require("fs"),vm=require("vm");const names=[];'
                    'vm.runInNewContext(fs.readFileSync(process.argv[2],"utf8"),'
                    '{test:(fn,name)=>names.push(name)});'
                    'process.stdout.write(JSON.stringify(names));')
    result = subprocess.run(["node", str(enum), str(js)], text=True,
                            capture_output=True, check=True)
    names = json.loads(result.stdout)
    assert names == json.loads((HERE / "TARGET-SUBTESTS.json").read_text())
    assert len(names) == len(set(names)) == 32
print(json.dumps({"references": "authenticated", "patch": "exact forward and reverse",
                  "rustfmt": "passed", "javascript": "syntax and 32 identities only",
                  "temporary_directory": "removed", "native_compiled": False,
                  "browser_executed": False}))
