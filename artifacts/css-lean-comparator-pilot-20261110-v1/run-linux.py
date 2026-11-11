import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--check-export", type=Path)
    parser.add_argument("--check-export-sha256")
    args = parser.parse_args()
    if bool(args.check_export) != bool(args.check_export_sha256):
        parser.error("the optional approved export requires its reviewed SHA-256")
    approved_export = args.check_export.resolve() if args.check_export else None
    if approved_export:
        assert hashlib.sha256(approved_export.read_bytes()).hexdigest() == args.check_export_sha256
    if platform.system() != "Linux":
        raise SystemExit("Linux with working bubblewrap is required; no fallback exists")
    if not shutil.which("bwrap"):
        raise SystemExit("bubblewrap is absent; nothing was executed")
    source_pins = json.loads((ROOT / "SOURCE-ONLY.json").read_text())
    for name, expected in source_pins.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    tool = args.toolchain.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, PATH=str(tool / "bin") + os.pathsep + os.environ["PATH"])
    for name in ["LAKE_CHECK_EXPORT", "COMPARATOR_BWRAP", "LEAN_PATH"]:
        env.pop(name, None)
    version = subprocess.check_output([str(tool / "bin/lean"), "--version"], env=env, text=True)
    assert "4.35.0-rc4" in version and "c29b6dda4f7c20e3eeaa717c4e565663c5cfa364" in version, version
    (out / "TOOLCHAIN.json").write_text(json.dumps({
        "version": version,
        "binaries": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (tool / "bin").iterdir() if p.is_file()},
        "status": "Linux binary hashes recorded here; reviewer must approve this toolchain independently",
    }, indent=2) + "\n")
    results = []
    with tempfile.TemporaryDirectory(prefix="css-comparator-linux-") as temporary:
        scratch = Path(temporary)
        for variant in ["good", "changed-predicate", "extra-premise", "forbidden-axiom"]:
            project = scratch / variant
            shutil.copytree(ROOT / "project", project)
            shutil.copy(ROOT / "variants" / (variant + ".lean"), project / "Solution.lean")
            command_args = [str(tool / "bin/lake"), "comparator", "--paranoid",
                            "--config", str(ROOT / "project/comparator.json")]
            result = subprocess.run(command_args, cwd=project, env=env, capture_output=True, timeout=600)
            stem = variant + "-comparator"
            (out / (stem + ".stdout")).write_bytes(result.stdout)
            (out / (stem + ".stderr")).write_bytes(result.stderr)
            expected = 0 if variant == "good" else 1
            results.append({"variant": variant, "command": command_args, "cwd": str(project),
                            "exit": result.returncode, "expected": expected})
            (out / "COMMANDS.json").write_text(json.dumps(results, indent=2) + "\n")
            assert result.returncode == expected, (stem, result.returncode)
            if variant != "good":
                reason = {"changed-predicate": "Const does not match between challenge and target",
                          "extra-premise": "theorem statement do not match",
                          "forbidden-axiom": "Illegal axiom detected: 'NumericDigits.forbidden'"}[variant]
                assert reason in result.stderr.decode(), stem
        if approved_export:
            command = [str(tool / "bin/lake"), "check", "--paranoid", "--from-export", str(approved_export)]
            result = subprocess.run(command, cwd=scratch, env=env, capture_output=True, timeout=600)
            (out / "approved-export-check.stdout").write_bytes(result.stdout)
            (out / "approved-export-check.stderr").write_bytes(result.stderr)
            results.append({"command": command, "exit": result.returncode, "expected": 0,
                            "export_sha256": args.check_export_sha256})
            (out / "COMMANDS.json").write_text(json.dumps(results, indent=2) + "\n")
            assert result.returncode == 0
    (out / "REPORT.json").write_text(json.dumps({
        "official_commands_completed": len(results), "temporary_builds_removed": not scratch.exists(),
        "boundary": "Protect this package/config/toolchain and reviewer process from proof workers externally; hashes are not an access boundary",
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
