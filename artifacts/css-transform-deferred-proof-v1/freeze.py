import hashlib
import json
import sys
from pathlib import Path
from check import errors
from expectations import EXPECTED_AXIOMS, EXPECTED_ERRORS

BASE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review(folder, live):
    report_path = folder / "report.json"
    report = json.loads(report_path.read_text())
    if report["status"] != "pass" or report["live_native_verified"] is not live:
        raise ValueError("Wrong gate status/mode")
    if report["inputs"] != report["inputs_after"]:
        raise ValueError("Unstable inputs")
    pins = {str(report_path): sha(report_path)}
    for name, digest in report["inputs"].items():
        if sha(Path(name)) != digest:
            raise ValueError("Changed gate input: " + name)
        pins[name] = digest
    names = ["positive", *EXPECTED_ERRORS]
    if [item["name"] for item in report["calls"]] != names:
        raise ValueError("Compiler call inventory")
    for call in report["calls"]:
        name = call["name"]
        source_path = folder / name / "Deferred.lean"
        stdout_path = folder / name / "stdout.log"
        stderr_path = folder / name / "stderr.log"
        for path, key in ((source_path, "source_sha256"), (stdout_path, "stdout_sha256"),
                          (stderr_path, "stderr_sha256")):
            if sha(path) != call[key]:
                raise ValueError("Changed compiler artifact")
            pins[str(path)] = call[key]
        stdout = stdout_path.read_text()
        if stderr_path.read_text():
            raise ValueError("Unexpected stderr")
        inventory = errors(source_path.read_text(), source_path, stdout)
        if inventory != call["errors"]:
            raise ValueError("Diagnostic receipt mismatch")
        if name == "positive":
            if call["exit_code"] != 0 or stdout != EXPECTED_AXIOMS:
                raise ValueError("Positive terminal receipt mismatch")
        elif call["exit_code"] != 1 or inventory != EXPECTED_ERRORS[name]:
            raise ValueError("Negative terminal receipt mismatch")
    binding = folder / "source-binding.json"
    pins[str(binding)] = sha(binding)
    return pins


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--verify":
        capsule = json.loads((BASE / "PROOF-v1.json").read_text())
        for name, digest in capsule["pins"].items():
            if sha(Path(name)) != digest:
                raise ValueError("Changed capsule input: " + name)
        print(json.dumps({"status": "pass", "pins": len(capsule["pins"])}))
        return
    if len(sys.argv) != 3:
        raise ValueError("Usage: freeze.py LIVE_DIRECTORY SNAPSHOT_DIRECTORY; or --verify")
    live, snapshot = [Path(p).resolve() for p in sys.argv[1:]]
    pins = {**review(live, True), **review(snapshot, False)}
    capsule = {"status": "pass", "scope": "Conditional manually bridged transform model",
               "live_report": str(live / "report.json"), "snapshot_report": str(snapshot / "report.json"),
               "pins": pins}
    path = BASE / "PROOF-v1.json"
    if path.exists():
        raise ValueError("Refusing to replace capsule")
    path.write_text(json.dumps(capsule, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "pass", "pins": len(pins), "capsule_sha256": sha(path)}))


if __name__ == "__main__":
    main()
