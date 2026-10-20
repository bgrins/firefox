import hashlib,json,pathlib,sys
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError("use python3 -I -S")
r=pathlib.Path(__file__).resolve().parent
files=json.loads((r/"FILES.json").read_text())
actual={p.relative_to(r).as_posix() for p in r.rglob("*") if p.is_file()}
if actual != set(files)|{"FILES.json","FREEZE.json"}: raise RuntimeError("roster")
for name,digest in files.items():
    p=r/name
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest: raise RuntimeError(name)
f=json.loads((r/"FREEZE.json").read_text())
if hashlib.sha256((r/"FILES.json").read_bytes()).hexdigest()!=f["files_sha256"]: raise RuntimeError("manifest")
run=json.loads((r/"runtime-v1/RUN.json").read_text())
raw=json.loads((r/"runtime-v1/raw.json").read_text())
assert run["complete"] and run["stable_pins"] and run["callback_received"]
assert run["pins_before"]==run["pins_after"]
rows=raw["rows"]
assert len(rows)==len({x["label"] for x in rows})==24
bad={"escaped-space:set","escaped-space:reset","escaped-space-outer-whitespace:set","escaped-space-outer-whitespace:reset"}
assert {x["label"] for x in rows if x["failures"]}==bad
assert all(x["supported"] for x in rows)
assert [x for x in rows if x["failures"]]==run["failed_rows"]
for x in rows:
    assert bool(x["failures"]) == (x["actual"]!=x["expected"])
    if x["label"] in bad:
        assert x["actual"]=="x\ufffd" and x["expected"]=="x\\ "
for name,digest in run["pins_before"].items():
    prefix="artifacts/css-variable-escaped-space-audit-v1/"
    if name.startswith(prefix): assert hashlib.sha256((r/name[len(prefix):]).read_bytes()).hexdigest()==digest
assert not (r/"runtime-v1/profile").exists()
print(json.dumps({"status":"PASS","states":24,"discrepancies":4,"controls":20,"stable":True,"WPT_proposal":"unexecuted"}))
