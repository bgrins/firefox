from pathlib import Path
import argparse, hashlib, importlib.util, io, json, os, re, subprocess, tarfile, tempfile
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
LIB = ROOT / "artifacts/css-spec-lean"
r = json.loads((P / "SOURCES.json").read_text())
h = lambda b: hashlib.sha256(b).hexdigest()

def theorems(path):
    scopes, names = [], []
    for line in path.read_text().splitlines():
        line = line.strip()
        opening = re.fullmatch(r"namespace (\S+)", line)
        closing = re.fullmatch(r"end(?: (\S+))?", line)
        theorem = re.match(r"theorem (\S+)", line)
        if opening:
            scopes.append(opening[1])
        elif closing:
            assert scopes and closing[1] in [None, scopes[-1]]
            scopes.pop()
        elif theorem:
            names.append(".".join(scopes + [theorem[1]]))
    assert not scopes
    return names

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    patch = (P / "library.patch").read_bytes()
    assert h(patch) == r["patch_sha256"]
    origin_receipt = json.loads((P / "ORIGIN.json").read_text())
    for name, digest in origin_receipt["files"].items():
        committed = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", origin_receipt["commit"] + ":" + name], cwd=ROOT)
        assert h(committed) == digest and (ROOT / name).read_bytes() == committed, name
    commands = {}
    def run(name, command, cwd, reject=False):
        proc = subprocess.run([str(x) for x in command], cwd=cwd,
                              env=dict(os.environ, LEAN_PATH=str(cwd)), capture_output=True, text=True)
        text = proc.stdout + proc.stderr
        (out / (name + ".log")).write_text(text)
        commands[name] = {"exit": proc.returncode, "sha256": h(text.encode())}
        if reject:
            assert proc.returncode != 0, name
        else:
            assert proc.returncode == 0 and not re.search(r"warning:|error:|\bsorry\b", text), (name, text)
        return text
    version = run("version", [lean, "--version"], out)
    assert "version 4.35.0-rc4," in version
    origin = ROOT / r["origin_capsule"]
    origin_pins = json.loads((origin / "LIBRARY.json").read_text())
    with tempfile.TemporaryDirectory(prefix="streaming-library-", dir=out) as directory:
        work = Path(directory)
        archive = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "archive", r["base_revision"]], cwd=LIB)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(work, filter="data")
        for name, pin in r["files"].items():
            target = work / name
            if pin["base_sha256"]:
                assert h(target.read_bytes()) == pin["base_sha256"], name
            else:
                assert not target.exists(), name
        run("patch-apply", ["git", "apply", P / "library.patch"], work)
        for name, pin in r["files"].items():
            assert (work / name).read_bytes() == (P / "candidate" / name).read_bytes(), name
            assert h((work / name).read_bytes()) == pin["candidate_sha256"], name
        for name, digest in origin_pins["sha256"].items():
            assert h((work / name).read_bytes()) == digest, name
        run("coverage-only", ["python3", "check.py", "--coverage-only"], work)
        spec = importlib.util.spec_from_file_location("library_check", work / "check.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        modules = []
        def visit(module):
            if module in modules or module == "Lean": return
            path = work / (module.replace(".", "/") + ".lean")
            for dep in re.findall(r"^import (\S+)", path.read_text(), re.M): visit(dep)
            modules.append(module)
        for module in ["CssSemantics.CssStreamingPipelineLaws", "CssSemantics.CssStreamingExamples", "CssSemantics.CssDomStringInputExamples", "CssSemantics.CssCodePointInputExamples", "CssSemantics.CssInputExamples"]:
            visit(module)
        names, hashes = [], {}
        for module in modules:
            file = module.replace(".", "/") + ".lean"
            path = work / file
            text = path.read_text()
            assert not re.search(r"\bsorry\b|\badmit\b|^axiom |^unsafe ", text, re.M), file
            hashes[file] = h(path.read_bytes())
            names += theorems(path)
            run("build-" + module, [lean, "-o", file[:-5] + ".olean", file], work)
        assert len(names) == len(set(names))
        assert set(r["new_theorems"]) <= set(names)
        imports = ''.join("import " + m + "\n" for m in modules)
        (work / "ScopedAudit.lean").write_text(imports + ''.join("#print axioms " + n + "\n" for n in names))
        audits = checker.parse_axiom_audit(run("axioms", [lean, "ScopedAudit.lean"], work))
        assert set(audits) == set(names)
        groups = ["CssSemantics.CssInputExamples", "CssSemantics.CodePointInputExamples", "CssSemantics.DomStringExamples", "CssSemantics.StreamingExamples"]
        (work / "ScopedExamples.lean").write_text(imports + "def main : IO Unit := do\n" + ''.join('  for (name, ok) in ' + g + '.checks do\n    IO.println s!"PASS {name}: {ok}"\n' for g in groups))
        observations = run("examples", [lean, "--run", "ScopedExamples.lean"], work).splitlines()
        prefixes = ("input ", "codepoint input ", "DOMString ", "streaming ")
        expected = [(name, ok) for name, ok in checker.EXECUTABLE_CASES if name.startswith(prefixes) and not name.startswith("input trace ")]
        assert observations == ["PASS " + name + ": " + str(ok).lower() for name, ok in expected]
        assert [name for name, _ in expected if name.startswith("streaming ")] == r["new_examples"]
        audit_file = work / "tests/Audit.lean"
        audit_original = audit_file.read_text()
        audit_file.write_text(audit_original.replace("#print axioms " + r["new_theorems"][0] + "\n", ""))
        rejection = run("missing-audit-control", ["python3", "check.py", "--coverage-only"], work, reject=True)
        assert "Axiom audit does not cover the exact named theorem set" in rejection
        audit_file.write_text(audit_original)
        coverage_file = work / "coverage.json"
        coverage_original = coverage_file.read_text()
        drift = json.loads(coverage_original)
        drift["features"][-1]["theorems"].append("CssSemantics.Streaming.not_a_theorem")
        coverage_file.write_text(json.dumps(drift))
        rejection = run("unknown-coverage-control", ["python3", "check.py", "--coverage-only"], work, reject=True)
        assert "Unknown coverage theorem" in rejection
        coverage_file.write_text(coverage_original)
        run("coverage-restored", ["python3", "check.py", "--coverage-only"], work)
        for name, pin in r["files"].items(): assert h((work / name).read_bytes()) == pin["candidate_sha256"], name
    report = {"status": "PASS", "base_revision": r["base_revision"], "patch_sha256": r["patch_sha256"], "modules": modules, "source_hashes": hashes, "audits": audits, "new_theorem_count": len(r["new_theorems"]), "observation_names": [name for name, _ in expected], "new_observation_count": len(r["new_examples"]), "commands": commands, "temporary_build_removed": True, "clean_affected_closure_checked": True, "global_static_coverage_checked": True, "full_library_gate_run": False, "browser_gate_run": False, "origin_semantic_mutations_rerun": False}
    (out / "REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS {len(modules)} clean modules; {len(audits)} audits ({len(r['new_theorems'])} new); {len(expected)} observations ({len(r['new_examples'])} new); two integration controls; global static coverage")
if __name__ == "__main__": main()
