import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE.parent / "css-number-document-transfer-20261110-v1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(exist_ok=False)
    manifest = json.loads((SOURCE / "SOURCE-ONLY.json").read_text())
    assert sha((SOURCE / "SOURCE-ONLY.json").read_bytes()) == "45851e7ad67daa48022c5c1388250fdd129a9858e6c00c52376abd3fe14c2330"
    for name, digest in manifest.items():
        assert sha((SOURCE / name).read_bytes()) == digest
    preserved = json.loads((SOURCE / "PRESERVED.json").read_text())
    authenticated, installed = [], {}
    for record in preserved["records"]:
        data = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show",
            record["origin_commit"] + ":" + record["origin_path"]], cwd=ROOT / record["origin_repository"])
        assert sha(data) == record["source_sha256"]
        if record["transform"] == "identity":
            transported = data
        else:
            assert record["transform"] == "exact import-line map"
            transported = "".join("import " + preserved["number_import_map"].get(line[7:].strip(), line[7:].strip()) + "\n"
                if line.startswith("import ") else line for line in data.decode().splitlines(keepends=True)).encode()
        target = record["installed"]
        assert transported == (SOURCE / target).read_bytes()
        assert sha(transported) == record["installed_sha256"]
        if target in installed:
            assert installed[target] == sha(transported)
        installed[target] = sha(transported)
        authenticated.append(record)
    commands = {}
    own = ["ParserSchema", "ParserReader", "ParserCodecLaws", "ParserEncoder", "ParserEncoderLaws",
           "ParserDocument", "ParserDocumentLaws", "NumberDocument", "NumberDocumentLaws", "Fixture"]
    modules = preserved["modules"] + [n + ".lean" for n in own]
    with tempfile.TemporaryDirectory(prefix="number-document-review-") as directory:
        work = Path(directory)
        def run(label, command):
            p = subprocess.run([str(x) for x in command], cwd=work, capture_output=True,
                               env=dict(os.environ, LEAN_PATH=str(work)))
            output = p.stdout + p.stderr
            (out / (label + ".log")).write_bytes(output)
            commands[label] = {"exit": p.returncode, "sha256": sha(output)}
            assert p.returncode == 0 and not re.search(rb"\b(?:error|warning):", output), output.decode()
            return output.decode()
        version = run("version", [args.lean.resolve(), "--version"])
        assert "version 4.35.0-rc4," in version
        for name in modules:
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, target)
            run("build-" + name.replace("/", "-"), [args.lean.resolve(), "-o", name[:-5] + ".olean", name])
        boundary = (HERE / "Boundary.lean").read_text()
        assert not re.search(r"\b(?:sorry|admit|axiom|native_decide|unsafe)\b", boundary)
        (work / "Boundary.lean").write_text(boundary)
        run("boundary", [args.lean.resolve(), "-o", "Boundary.olean", "Boundary.lean"])
        names = re.findall(r"(?m)^theorem (\w+)", boundary)
        assert len(names) == 12
        (work / "Audit.lean").write_text("import Boundary\n" + "".join(
            "#print axioms NumberDocumentReview." + name + "\n" for name in names))
        output = run("audit", [args.lean.resolve(), "Audit.lean"])
        audits = {}
        for line in re.sub(r",\n\s*", ", ", output).splitlines():
            m = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            assert m, line
            axioms = set(m[3].split(", ")) if m[3] else set()
            assert axioms <= {"propext", "Quot.sound", "Classical.choice"}
            assert m[1] not in audits
            audits[m[1]] = sorted(axioms)
        assert set(audits) == {"NumberDocumentReview." + name for name in names}
    for name, digest in manifest.items():
        assert sha((SOURCE / name).read_bytes()) == digest
    result = {"status": "pass", "source_manifest_sha256": sha((SOURCE / "SOURCE-ONLY.json").read_bytes()),
              "authenticated_origin_records": authenticated, "unique_preserved_inputs": installed,
              "compiled_modules": modules, "independent_audits": audits,
              "boundary_sha256": sha((HERE / "Boundary.lean").read_bytes()),
              "commands": commands, "temporary_build_removed": True,
              "canonical_or_native_changes": False}
    (out / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: {len(authenticated)} origins, {len(modules)} source modules, {len(audits)} independent boundary audits")


if __name__ == "__main__":
    main()
