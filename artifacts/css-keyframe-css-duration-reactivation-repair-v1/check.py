import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output.resolve()
    assert not output.exists()
    output.mkdir()
    for path, digest in json.loads((HERE / "REFERENCES.json").read_text()).items():
        path = ROOT / path
        assert sha(path) == digest
        if path.name == "FILES.json":
            for name, expected in json.loads(path.read_text()).items():
                assert sha(path.parent / name) == expected
    maps = json.loads((HERE / "SOURCE-MAPS.json").read_text())
    pins = json.loads((ROOT / "artifacts/css-keyframe-dependency-diagnostic-runtime-v1/FINAL-PINS.json").read_text())
    for name, digest in maps["original"].items():
        assert sha(HERE / "original" / name) == digest == pins[name]
    for name, digest in maps["candidate"].items():
        assert sha(HERE / "candidate" / name) == digest
    for name, digest in maps["new_wpt"].items():
        assert sha(HERE / "candidate" / name) == digest
        assert sha(HERE / "css-duration-reactivation.html") == digest
    assert sha(HERE / "gecko-wpt.patch") == maps["patch_sha256"]
    source = "servo/components/style/matching.rs"
    before = (HERE / "original" / source).read_text()
    after = (HERE / "candidate" / source).read_text()
    needle = "            tasks.insert(UpdateAnimationsTasks::CSS_ANIMATIONS);\n"
    assert before.count(needle) == 1
    assert after == before.replace(needle, needle + "            tasks.insert(UpdateAnimationsTasks::EFFECT_PROPERTIES);\n")
    scratch = output / "transport"
    shutil.copytree(HERE / "original", scratch)
    environment = dict(os.environ)
    for key in ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"]:
        environment.pop(key, None)
    environment["GIT_CEILING_DIRECTORIES"] = str(output)
    commands = []
    try:
        for extra in [["--check"], []]:
            command = ["git", "apply", *extra, str(HERE / "gecko-wpt.patch")]
            result = subprocess.run(command, cwd=scratch, env=environment, capture_output=True, text=True)
            commands.append({"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
            assert result.returncode == 0, result.stderr
        expected = maps["candidate"] | maps["new_wpt"]
        assert {str(path.relative_to(scratch)): sha(path) for path in scratch.rglob("*") if path.is_file()} == expected
    finally:
        shutil.rmtree(scratch)
    html = (HERE / "css-duration-reactivation.html").read_text()
    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    assert len(scripts) == 1
    script = output / "probe-script.js"
    script.write_text(scripts[0])
    syntax = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True)
    assert syntax.returncode == 0, syntax.stderr
    collector = 'const fs=require("fs"),vm=require("vm");const names=[];vm.runInNewContext(fs.readFileSync(process.argv[1],"utf8"),{promise_test:(_,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));'
    inert = subprocess.run(["node", "-e", collector, str(script)], capture_output=True, text=True)
    assert inert.returncode == 0, inert.stderr
    names = json.loads(inert.stdout)
    assert len(names) == len(set(names)) == 6
    assert names == json.loads((HERE / "ROSTER.json").read_text())
    check = {"status": "CSS_DURATION_REACTIVATION_STATIC_CHECK_PASS", "original_source_joins": 1,
             "transported_paths": sorted(expected), "inert_registered_cases": len(names),
             "syntax_exit_code": syntax.returncode, "transport_removed": not scratch.exists(),
             "native_compilation": False, "callbacks_executed": False, "browser_run": False}
    (output / "TRANSPORT.json").write_text(json.dumps(commands, indent=2) + "\n")
    (output / "CHECK.json").write_text(json.dumps(check, indent=2) + "\n")
    print(json.dumps(check, indent=2))


if __name__ == "__main__":
    main()
