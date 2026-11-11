#!/usr/bin/env python3
import difflib, hashlib, json, subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
paths = sorted(str(x.relative_to(P / "candidate")) for x in (P / "candidate").rglob("*") if x.is_file())
native = ["layout/style/ServoStyleSet.cpp", "layout/style/ServoStyleSet.h", "servo/ports/geckolib/glue.rs"]
def delta(before, after, names):
    out = ""
    for name in names:
        a, b = before(name), after(name)
        aa, bb = a.read_text() if a.exists() else "", b.read_text()
        if aa == bb: continue
        out += "diff --git a/" + name + " b/" + name + "\n"
        if not a.exists(): out += "new file mode 100644\n"
        out += "".join(difflib.unified_diff(aa.splitlines(True), bb.splitlines(True), fromfile="a/" + name if a.exists() else "/dev/null", tofile="b/" + name))
    return out
prereq = lambda n: P / "prerequisite" / n
candidate = lambda n: P / "candidate" / n
production = lambda n: P / "native" / n if n in native else prereq(n)
(P / "native.patch").write_text(delta(prereq, production, native))
(P / "extension.patch").write_text(delta(prereq, candidate, paths))
(P / "driver.patch").write_text(delta(production, candidate, paths))
roles = [{"path": n, "before_sha256": sha(prereq(n)) if prereq(n).exists() else None, "after_sha256": sha(candidate(n)), "role": "production_and_temporary_driver" if n.endswith("glue.rs") else "production" if n in native else "temporary_driver_or_test"} for n in paths if not prereq(n).exists() or prereq(n).read_bytes() != candidate(n).read_bytes()]
(P / "ROLES.json").write_text(json.dumps(roles, indent=2) + "\n")
r = subprocess.run(["node", str(P / "inventory.cjs")], cwd=P.parent.parent, capture_output=True, check=True)
(P / "ASSERTIONS.json").write_bytes(r.stdout)
