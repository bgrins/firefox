import argparse
import hashlib
import json
from pathlib import Path
import runpy
import tempfile
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    commands = []
    version = "Lean 4.35.0-rc4 c29b6dda4f7c20e3eeaa717c4e565663c5cfa364"
    with tempfile.TemporaryDirectory(prefix="css-comparator-orchestration-") as temporary:
        scratch = Path(temporary)
        tool = scratch / "tool"
        (tool / "bin").mkdir(parents=True)
        (tool / "bin/lean").write_text("non-executable placeholder; every subprocess is mocked")
        export = scratch / "approved.ndjson"
        export.write_text("mock payload, never submitted to any checker")
        digest = hashlib.sha256(export.read_bytes()).hexdigest()
        receipts = scratch / "receipts"

        def mock_run(argv, **options):
            assert "--inadvisably-no-sandbox" not in argv
            commands.append(argv)
            if argv[1] == "check":
                assert argv == [str((tool / "bin/lake").resolve()), "check", "--paranoid", "--from-export", str(export.resolve())]
                return SimpleNamespace(returncode=0, stdout=b"mock", stderr=b"")
            variant = options["cwd"].name
            reason = {"good": "", "changed-predicate": "Const does not match between challenge and target",
                      "extra-premise": "theorem statement do not match",
                      "forbidden-axiom": "Illegal axiom detected: 'NumericDigits.forbidden'"}[variant]
            return SimpleNamespace(returncode=0 if variant == "good" else 1,
                                   stdout=b"mock", stderr=reason.encode())

        argv = [str(ROOT / "run-linux.py"), "--toolchain", str(tool), "--out", str(receipts),
                "--check-export", str(export), "--check-export-sha256", digest]
        with patch("sys.argv", argv), patch("platform.system", return_value="Linux"), \
             patch("shutil.which", return_value="mock-bwrap"), \
             patch("subprocess.check_output", return_value=version), \
             patch("subprocess.run", side_effect=mock_run):
            runpy.run_path(str(ROOT / "run-linux.py"), run_name="__main__")
        report = json.loads((receipts / "REPORT.json").read_text())
        rows = json.loads((receipts / "COMMANDS.json").read_text())
        assert len(commands) == report["official_commands_completed"] == 5
        assert rows[-1]["export_sha256"] == digest
        assert rows[-1]["exit"] == 0
        assert report["temporary_builds_removed"]
    (out / "REPORT.json").write_text(json.dumps({
        "status": "Python orchestration mock passed",
        "calls_intercepted": len(commands), "native_commands_run": 0,
        "optional_export_hash_recorded": True, "temporary_files_removed": not scratch.exists(),
        "boundary": "Not a Linux, bubblewrap, comparator, checker, proof, or protection acceptance run",
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
