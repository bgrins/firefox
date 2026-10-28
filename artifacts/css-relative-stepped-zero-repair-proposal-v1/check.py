from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

here = Path(__file__).resolve().parent
native = "servo/components/style/values/generics/calc.rs"
wpt = "testing/web-platform/tests/css/css-values/relative-stepped-zero-basis.html"
scratch = Path(tempfile.mkdtemp(prefix="css-stepped-check-", dir="/private/tmp"))
records = []
try:
    target = scratch / native
    target.parent.mkdir(parents=True)
    shutil.copyfile(here / "base" / native, target)
    for reverse in (False, True, False):
        command = ["patch", "-p1", "--fuzz=0", "--batch"] + (["-R"] if reverse else [])
        result = subprocess.run(command, cwd=scratch, input=(here / "fix.patch").read_text(), text=True, capture_output=True)
        records.append(dict(command=command, exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
        assert result.returncode == 0 and "offset" not in result.stdout and "fuzz" not in result.stdout
        assert target.read_bytes() == (here / ("base" if reverse else "candidate") / native).read_bytes()
        if reverse:
            assert not (scratch / wpt).exists()
        else:
            assert (scratch / wpt).read_bytes() == (here / "candidate" / wpt).read_bytes()
    patch = (here / "native.patch").read_text().splitlines()
    assert sum(line.startswith("@@") for line in patch) == 2
    assert not any(line.startswith("-") and not line.startswith("---") for line in patch)
    script = re.search(r"<script>\n(.*)\n</script>", (here / "candidate" / wpt).read_text(), re.S).group(1)
    js = scratch / "fixture.js"
    js.write_text(script)
    result = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    js.write_text("const names=[];global.promise_test=(_,name)=>names.push(name);\n" + script + "\nprocess.stdout.write(JSON.stringify(names));\n")
    result = subprocess.run(["node", str(js)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == json.loads((here / "TARGET-SUBTESTS.json").read_text())[wpt]
    result = subprocess.run(["rustfmt", "--edition", "2024", "--config", "skip_children=true,match_block_trailing_comma=true", "--emit", "stdout", str(target)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
finally:
    shutil.rmtree(scratch)
(here / "TRANSPORT.json").write_text(json.dumps(records, indent=2) + "\n")
(here / "CHECK.json").write_text(json.dumps(dict(exact_forward_reverse_reapply=True, no_offsets_or_fuzz=True, native_added_hunks=2, native_removed_lines=0, rustfmt_parse=True, entire_file_format_check=False, javascript_syntax=True, enumerated_test_count=18, callbacks_executed=False, browser_executed=False, native_compiled=False, scratch_removed=True), indent=2) + "\n")
roles = {}
for name in (native, wpt):
    before = here / "base" / name
    after = here / "candidate" / name
    roles[name] = dict(base=hashlib.sha256(before.read_bytes()).hexdigest() if before.exists() else None, candidate=hashlib.sha256(after.read_bytes()).hexdigest())
(here / "SOURCE-ROLES.json").write_text(json.dumps(roles, indent=2) + "\n")
