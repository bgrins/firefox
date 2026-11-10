from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, tempfile
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
OWNER = ROOT / "artifacts/css-typed-codec-20261110-v1"
h = lambda b: hashlib.sha256(b).hexdigest()

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--lean", required=True, type=Path)
    a.add_argument("--out", required=True, type=Path)
    args = a.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    files = sorted([str(x.relative_to(OWNER)) for x in OWNER.glob("*.lean")] +
                   [str(x.relative_to(OWNER)) for x in (OWNER / "CssSemantics").glob("*.lean")] +
                   ["escape.json", "EXPECTED.json", "PARSER-EXPECTED.json"])
    pins = {n: h((OWNER / n).read_bytes()) for n in files}
    logs = {}
    def run(name, argv, work, fail=False):
        proc = subprocess.run([str(x) for x in argv], cwd=work, env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
        text = proc.stdout + proc.stderr
        (out / (name + ".log")).write_text(text)
        logs[name] = {"exit": proc.returncode, "sha256": h(text.encode())}
        if fail:
            assert proc.returncode != 0, name
        else:
            assert proc.returncode == 0 and not re.search(r"warning:|error:|\bsorry\b", text), (name, text)
        return text
    version = run("version", [lean, "--version"], out)
    assert "version 4.35.0-rc4," in version
    with tempfile.TemporaryDirectory(prefix="typed-codec-review-", dir=out) as directory:
        work = Path(directory)
        for n in files:
            dest = work / n
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(OWNER / n, dest)
        modules = []
        def visit(module):
            if module in modules or module.split(".")[0] in ["Lean", "Init", "Std"]: return
            path = work / (module.replace(".", "/") + ".lean")
            for dep in re.findall(r"^import (\S+)", path.read_text(), re.M): visit(dep)
            modules.append(module)
        for module in ["Runner", "RuntimeCheck", "Cases", "JsonLaws", "ParserBoundary"]: visit(module)
        names = []
        for module in modules:
            file = module.replace(".", "/") + ".lean"
            path = work / file
            text = path.read_text()
            assert not re.search(r"\bsorry\b|\badmit\b|^axiom |^unsafe ", text, re.M), file
            if module not in ["Runner", "RuntimeCheck", "ParserBoundary"]:
                scopes = []
                for raw in text.splitlines():
                    line = raw.strip()
                    opening = re.fullmatch(r"namespace (\S+)", line)
                    closing = re.fullmatch(r"end(?: (\S+))?", line)
                    theorem = re.match(r"(?:@\[[^]]+\] )?theorem (\S+)", line)
                    if opening: scopes.append(opening[1])
                    elif line == "mutual": scopes.append(None)
                    elif closing:
                        assert scopes and closing[1] in [None, scopes[-1]], (file,line)
                        scopes.pop()
                    elif theorem: names.append(".".join([scope for scope in scopes if scope is not None] + [theorem[1]]))
                assert not scopes
                run("build-" + module.replace(".", "-"), [lean, "-o", file[:-5] + ".olean", file], work)
        assert len(names) == len(set(names))
        (work / "Audit.lean").write_text("import Cases\nimport JsonLaws\n" + ''.join("#print axioms " + name + "\n" for name in names))
        audit_text = run("axioms", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", audit_text).splitlines():
            m = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            assert m, line
            axioms = set(m[3].split(", ")) if m[3] else set()
            assert axioms <= {"propext", "Quot.sound", "Classical.choice"}, line
            assert m[1] not in audits
            audits[m[1]] = sorted(axioms)
        assert set(audits) == set(names)
        expected = json.loads((work / "EXPECTED.json").read_text())
        inputs = [row["input"] for row in expected]
        for runner in ["Runner", "RuntimeCheck"]:
            observed = [json.loads(x) for x in run(runner, [lean, "--run", runner + ".lean", "escape.json", *inputs], work).splitlines()]
            assert observed == expected, runner
        parser_expected = json.loads((work / "PARSER-EXPECTED.json").read_text())
        parser_rows = [json.loads(x) for x in run("parser", [lean, "--run", "ParserBoundary.lean", *[row["text"] for row in parser_expected]], work).splitlines()]
        assert parser_rows == [row["value"] for row in parser_expected]
        source = json.loads((work / "escape.json").read_text())
        for name, change in [
            ("wrong-result", lambda doc: doc.update(program={"op":"ret", "args":[{"op":"nat", "args":[1]}]})),
            ("extra-envelope-field", lambda doc: doc.update(code="arbitrary Lean")),
            ("cyclic-alias", lambda doc: doc["definitions"].update(hexExpr={"op":"use", "args":["hexExpr"]})),
        ]:
            doc = json.loads(json.dumps(source)); change(doc)
            (work / "invalid.json").write_text(json.dumps(doc))
            failure = run(name, [lean, "--run", "Runner.lean", "invalid.json", "41!"], work, fail=True)
            assert "document refused" in failure
    assert pins == {n: h((OWNER / n).read_bytes()) for n in files}, "Author inputs changed during replay"
    report = {"status":"PASS", "files":pins, "modules":modules, "audits":audits, "runtime_rows_each":len(expected), "parser_rows":len(parser_rows), "independent_invalid_documents":3, "logs":logs, "scratch_objects_removed":True, "native_or_browser_gate":False}
    (out / "REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS {len(modules)} modules; {len(audits)} audited declarations; {len(expected)} rows each runner; {len(parser_rows)} parser cases;3 rejected actual JSON documents")
if __name__ == "__main__": main()
