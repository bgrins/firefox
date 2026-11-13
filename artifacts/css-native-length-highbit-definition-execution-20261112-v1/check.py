from pathlib import Path
import hashlib, importlib.util, json, os, shutil, subprocess, sys, time

base = Path(__file__).resolve().parent

def load_local(name):
    spec = importlib.util.spec_from_file_location(name, base / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

lifecycle = load_local("lifecycle")
inspect_group, settle_group = lifecycle.inspect_group, lifecycle.settle_group
preflight = load_local("preflight").preflight
repo = base.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
preflight_result = preflight()
preparation = json.loads((base / "PREPARATION.json").read_text())
lean = repo / preparation["lean"]["path"]
assert base == repo / preparation["execution_capsule"], "Run only in the approved fresh execution copy"
for previous in (base / "definition-attempts").glob("*/*-PID.json"):
    pgid = json.loads(previous.read_text())["pgid"]
    assert not inspect_group(pgid), ("Prior owned group remains", pgid)
attempt = base / "definition-attempts" / str(time.time_ns())
attempt.mkdir(parents=True)
cache = attempt / "lib"
cache.mkdir()
for name in preparation["files"]:
    (attempt / name).write_bytes((base / name).read_bytes())
(attempt / "PREPARATION.json").write_bytes((base / "PREPARATION.json").read_bytes())
env = dict(os.environ, LEAN_PATH=str(cache), PYTHONDONTWRITEBYTECODE="1")
inputs = dict(source=preparation["files"], preparation_sha256=sha(base / "PREPARATION.json"),
              lean_sha256=sha(lean), limits=preparation["limits"],
              stdlib="Installed pinned Lean distribution; fresh owned user-module cache",
              environment=dict(LEAN_PATH=str(cache), PYTHONDONTWRITEBYTECODE="1"),
              preflight=preflight_result)
(attempt / "INPUTS.json").write_text(json.dumps(inputs, indent=2) + "\n")
records = []
active = None

def run(module, output):
    global active
    name = module.lower()
    argv = [str(lean), "-j1", "-M2048", "--root=" + str(attempt)]
    if output:
        argv += ["-o", str(cache / (module + ".olean"))]
    argv += [str(attempt / (module + ".lean"))]
    started = time.monotonic()
    peak = 0
    reason = None
    process = None
    settled = None
    with (attempt / (name + ".log")).open("x") as log:
        try:
            process = subprocess.Popen(argv, cwd=attempt, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            active = process
            (attempt / (name + "-PID.json")).write_text(json.dumps(dict(pid=process.pid, pgid=process.pid)) + "\n")
            while process.poll() is None:
                rss = sum(rss for _, rss in inspect_group(process.pid))
                peak = max(peak, rss)
                if rss > 2147483648:
                    reason = "rss-limit"
                    break
                if time.monotonic() - started > 60:
                    reason = "timeout"
                    break
                time.sleep(.1)
        except BaseException as error:
            reason = repr(error)
        finally:
            if process is not None:
                settled = settle_group(process)
                if settled["group_absent"]:
                    try:
                        process.wait(timeout=2)
                    except BaseException as error:
                        reason = reason or repr(error)
                if settled["cleanup_signals"]:
                    reason = reason or "cleanup-signals-required"
                if settled["inspection_errors"]:
                    reason = reason or "inspection-error"
                if not settled["group_absent"]:
                    reason = reason or "absence-unconfirmed"
                if settled["group_absent"] and process.poll() is not None:
                    active = None
    record = dict(module=module, argv=argv, executable_sha256=sha(lean),
                  exit=process.returncode if process else None,
                  seconds=time.monotonic() - started, peak_rss_bytes=peak,
                  termination_reason=reason, log_sha256=sha(attempt / (name + ".log")),
                  **(settled or dict(group_absent=process is None, inspection_errors=[], cleanup_signals=[])))
    records.append(record)
    (attempt / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
    assert record["exit"] == 0 and record["group_absent"] and not record["inspection_errors"] and reason is None, module

result = dict(exit=1, definition_only=True, proofs_checked=0, native_cells_checked=0)
try:
    run("Target", True)
    run("Controls", True)
    run("Types", False)
    run("Audit", False)
    assert all(sha(base / name) == digest for name, digest in inputs["source"].items())
    assert (attempt / "target.log").read_bytes() == b""
    assert (attempt / "controls.log").read_bytes() == b""
    expected = json.loads((base / "AUDIT-EXPECTED.json").read_text())
    wanted = "".join("'" + name + "' does not depend on any axioms\n" for name in expected)
    assert (attempt / "audit.log").read_text() == wanted
    names = json.loads((base / "DECLARATIONS.json").read_text())
    text = (attempt / "types.log").read_text()
    for family, fields in [("Obligations", names["obligations"]), ("Controls", names["controls"])]:
        for field in fields:
            assert "CssNativeHighBit." + family + "." + field in text
    result.update(exit=0, fields_elaborated=15, controls_elaborated=6,
                  declaration_audits=50, source_unchanged=True,
                  types_sha256=sha(attempt / "types.log"), types_need_independent_review=True)
except BaseException as error:
    result["failure"] = repr(error)
finally:
    if active is None and all(record["group_absent"] for record in records):
        assert not cache.is_symlink()
        assert all(not f.is_symlink() for f in cache.rglob("*"))
        result["removed_owned_compiler_bytes"] = sum(f.stat().st_size for f in cache.rglob("*") if f.is_file())
        shutil.rmtree(cache)
    else:
        result["cleanup_held"] = "Owned process group not authoritatively absent or leader not reaped"
    (attempt / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(attempt=str(attempt), **result)))
sys.exit(result["exit"])
