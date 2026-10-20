import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import stat
import subprocess

ROOT = Path(__file__).resolve().parent
NATIVE_MANIFEST = "9c0ec1eab8320b7c046957cebbe8899aa513b1c70a44ecd6a510828a67a22450"
LEAN_MANIFEST = "f1ad96d1e41dbf587664a02e9f11cf3630afa2d591de17aaebd53312f99ef3b5"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON field")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def closure(root, expected):
    require(sha(root / "FILES.json") == expected, "external manifest identity")
    entries = read(root / "FILES.json")["files"]
    names = [entry["path"] for entry in entries]
    require(len(names) == len(set(names)), "duplicate path")
    for name in names:
        q = PurePosixPath(name)
        require(not q.is_absolute() and str(q) == name and ".." not in q.parts
                and name not in ["FILES.json", "FREEZE.json"], "manifest path")
    files, directories = set(), set()
    for base, dirs, leaves in os.walk(root, followlinks=False):
        for name in dirs + leaves:
            path = Path(base) / name
            relative = path.relative_to(root).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISREG(mode):
                files.add(relative)
            elif stat.S_ISDIR(mode):
                directories.add(relative)
            else:
                raise RuntimeError("nonregular capsule entry: " + relative)
    require(files == set(names) | {"FILES.json", "FREEZE.json"}, "closed files")
    expected_dirs = {str(parent) for name in names for parent in PurePosixPath(name).parents if str(parent) != "."}
    require(directories == expected_dirs, "closed directories")
    for item in entries:
        require(sha(root / item["path"]) == item["sha256"], "file hash: " + item["path"])
    seal = read(root / "FREEZE.json")
    require(seal.get("manifest_sha256", seal.get("files_sha256")) == expected, "freeze binding")
    return len(entries)


def tools():
    require(sha(ROOT / "LEAN-TOOLCHAIN.json") == LEAN_MANIFEST, "Lean inventory identity")
    lean = read(ROOT / "LEAN-TOOLCHAIN.json")
    prefix = Path(lean["root"])
    actual_files, actual_dirs = set(), set()
    for directory in ["bin", "lib"]:
        actual_dirs.add(directory)
        for base, dirs, leaves in os.walk(prefix / directory, followlinks=False):
            for name in dirs + leaves:
                p = Path(base) / name
                relative = str(p.relative_to(prefix))
                if p.is_symlink() or p.is_file():
                    actual_files.add(relative)
                elif p.is_dir():
                    actual_dirs.add(relative)
                else:
                    raise RuntimeError("nonregular toolchain entry")
    require(actual_files == {e["path"] for e in lean["entries"]}, "Lean file closure")
    require(actual_dirs == set(lean["directories"]), "Lean directory closure")
    for entry in lean["entries"]:
        p = prefix / entry["path"]
        require(p.is_symlink() == ("symlink" in entry), "Lean link type")
        if p.is_symlink():
            require(os.readlink(p) == entry["symlink"], "Lean link target")
            require(prefix in p.resolve().parents, "Lean link escape")
        require(sha(p) == entry["sha256"], "Lean toolchain file " + entry["path"])
    headers = read(ROOT / "NATIVE-HEADERS.json")
    for entry in headers["entries"]:
        require(sha(Path(entry["path"])) == entry["sha256"], "native header identity")
    return prefix / "bin/lean", len(lean["entries"]), {e["path"] for e in headers["entries"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    count = closure(ROOT, options.manifest_sha)
    closure(ROOT / "native-source", NATIVE_MANIFEST)
    out = options.output.resolve()
    require(not out.exists() and out != ROOT and ROOT not in out.parents, "new external output required")
    lean, lean_files, headers = tools()
    out.mkdir(parents=True)
    commands = []

    def command(name, argv):
        with (out / (name + ".log")).open("w") as log:
            result = subprocess.run(argv, cwd=out, stdout=log, stderr=subprocess.STDOUT)
        commands.append({"name": name, "argv": argv, "exit": result.returncode})
        (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
        require(result.returncode == 0, "failed " + name)

    py = [sys.executable, "-I", "-S"]
    command("native", py + [str(ROOT / "native-source/check.py"), "--manifest-sha", NATIVE_MANIFEST, "--out", str(out / "native")])
    actual_headers = set()
    for dep in (out / "native").glob("*/deps.d"):
        for name in shlex.split(dep.read_text().split(":", 1)[1].replace("\\\n", "")):
            p = Path(name).resolve()
            if out / "native" not in p.parents:
                actual_headers.add(str(p))
    require(actual_headers == headers, "native dependency closure")
    command("proof", py + [str(ROOT / "check_lean.py"), "--lean", str(lean), "--output", str(out / "proof")])
    command("calibration", py + [str(ROOT / "calibrate.py"), "--lean", str(lean), "--output", str(out / "calibration"),
                                 "--source-capsule", str(ROOT / "native-source"), "--native", str(out / "native")])
    command("lifecycle-mutants", py + [str(ROOT / "challenge_lifecycle.py"), "--lean", str(lean),
                                       "--output", str(out / "lifecycle-mutants"), "--calibration", str(out / "calibration"),
                                       "--source-capsule", str(ROOT / "native-source")])
    require(len(read(out / "proof/RESULT.json")["audits"]) == 59, "proof roster")
    require(read(out / "calibration/RESULT.json")["full_observation_comparisons"] == 5136, "calibration count")
    require(len(read(out / "lifecycle-mutants/RESULT.json")["records"]) == 6, "model control roster")
    require(closure(ROOT, options.manifest_sha) == count, "capsule drift")
    require(tools() == (lean, lean_files, headers), "toolchain drift")
    result = {"status": "PASS_REVIEW_PENDING", "source_files": count, "lean_toolchain_files": lean_files,
              "native_headers": len(headers), "audits": 59, "cases": 856, "complete_comparisons": 5136,
              "native_mutants": 7, "model_lifecycle_mutants": 5,
              "scope": "Conditional positional algebra and lifecycle-model projection substitution; finite native calibration. Graph/provider/native correspondence and final independent acceptance remain separate."}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
