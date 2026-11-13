from pathlib import Path
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys, time

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
for previous in (base / "proof-attempts").glob("*/*-PID.json"):
    pgid = json.loads(previous.read_text())["pgid"]
    assert not inspect_group(pgid), ("Prior owned group remains", pgid)
attempt = base / "proof-attempts" / str(time.time_ns())
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

result = dict(exit=1, development_only=True, proofs_checked=0, native_cells_checked=0)
try:
    run("Target", True)
    run("Controls", True)
    run("Proof", True)
    run("ControlProof", True)
    run("Types", False)
    run("ProofTypes", False)
    run("Audit", False)
    assert all(sha(base / name) == digest for name, digest in inputs["source"].items())
    for name in ["target", "proof", "controlproof"]:
        assert (attempt / (name + ".log")).read_bytes() == b""
    warning_blocks = []
    for line, col, binder in [(59, 7, "b"), (59, 22, "c"), (60, 12, "b"), (60, 27, "c")]:
        warning_blocks.append(str(attempt / "Controls.lean") + ":" + str(line) + ":" + str(col) + ": warning: Variable name `" + binder + "` is not explicitly referenced.\n\nHint: The binding can be removed (if unused) or named `_` (if used implicitly). Alternatively, prefix the name with `_` to silence this warning:\n  [apply] _" + binder + "\n\nNote: This linter can be disabled with `set_option linter.unusedVariables false`\n")
    assert (attempt / "controls.log").read_text() == "".join(warning_blocks)
    audit_plan = json.loads((base / "AUDIT-PLAN.json").read_text())
    inherited = json.loads((base / "INHERITED-AUDIT.json").read_text())
    observed = {}
    audit_text = (attempt / "audit.log").read_text()
    assert audit_text.endswith("\n")
    for line in audit_text.splitlines():
        match = re.fullmatch(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]+)\])", line)
        assert match, line
        name = match[1]
        assert name not in observed
        axes = match[2].split(", ") if match[2] else []
        assert len(set(axes)) == len(axes)
        assert set(axes) <= set(audit_plan["allowed_new_axioms"])
        if name in inherited:
            assert axes == inherited[name]
        observed[name] = axes
    assert list(observed) == audit_plan["names"]
    (attempt / "OBSERVED-AXIOMS.json").write_text(json.dumps(observed, indent=2) + "\n")
    assert sha(attempt / "types.log") == preparation["protected_types_sha256"]
    proof_types = (attempt / "prooftypes.log").read_text()
    for name in audit_plan["new_theorems"]:
        assert name in proof_types
    result.update(exit=0, obligation_fields=15, control_fields=6,
                  proofs_checked=len(audit_plan["new_theorems"]),
                  declaration_audits=len(observed), source_unchanged=True,
                  types_sha256=sha(attempt / "types.log"),
                  proof_types_sha256=sha(attempt / "prooftypes.log"),
                  independent_final_review_pending=True)
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
