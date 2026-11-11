import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def main():
    capsule = Path(__file__).resolve().parent
    repository = capsule.parents[1]
    sources = json.loads((capsule / "SOURCES.json").read_text())
    context = repository / sources["context_report"]
    assert hashlib.sha256(context.read_bytes()).hexdigest() == sources["context_report_sha256"]
    with tempfile.TemporaryDirectory(prefix="css-origin-copy-") as directory:
        work = Path(directory)
        for name, expected in sources["files"].items():
            original = subprocess.check_output([
                "git", "-C", str(repository), "-c", "core.fsmonitor=false",
                "show", sources["revision"] + ":" + name,
            ])
            assert hashlib.sha256(original).hexdigest() == expected
            assert (capsule / "base" / name).read_bytes() == original
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(original)
        patch = (capsule / "native.patch").read_bytes()
        forward = subprocess.run(["patch", "-p1", "--batch"], input=patch, cwd=work,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        for name in sources["files"]:
            assert (work / name).read_bytes() == (capsule / "candidate" / name).read_bytes()
        reverse = subprocess.run(["patch", "-R", "-p1", "--batch"], input=patch, cwd=work,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        for name in sources["files"]:
            assert (work / name).read_bytes() == (capsule / "base" / name).read_bytes()
        assert not list(work.rglob("*.rej"))
    receipt = {
        "status": "PASS", "git_objects": len(sources["files"]),
        "patch_sha256": hashlib.sha256(patch).hexdigest(),
        "forward": forward.stdout.decode(), "reverse": reverse.stdout.decode(),
        "scratch_removed": not work.exists(), "native_compilation": False,
        "browser_execution": False, "semantic_acceptance": False,
    }
    (capsule / "CHECK.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
