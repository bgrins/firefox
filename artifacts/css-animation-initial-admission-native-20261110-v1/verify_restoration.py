import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Run with python -I and without -O")
    before = json.loads((HERE / "runtime1/BEFORE.json").read_text())
    helper = ROOT / "artifacts/css-round-context-quotient-reversible-pair-v2/bundle.py"
    assert sha(helper) == before["bundle_helper_sha256"]
    spec = importlib.util.spec_from_file_location("bundle", helper)
    bundle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bundle)
    assert all(
        sha(ROOT / path) == value["base"] for path, value in before["sources"].items()
    )
    assert bundle.semantic(
        bundle.scan(ROOT / "objdir-full.noindex/dist/Nightly.app")
    ) == bundle.semantic(before["app"])
    assert bundle.semantic({
        p: bundle.entry(ROOT / p) for p in before["extras"]
    }) == bundle.semantic(before["extras"])
    assert all(
        sha(ROOT / path) == value for path, value in before["baseline_binaries"].items()
    )
    git = ["git", "-c", "core.fsmonitor=false"]

    def output(*args):
        return subprocess.check_output([*git, *args], cwd=ROOT)

    assert output("rev-parse", "HEAD").decode().strip() == before["head"]
    assert (
        hashlib.sha256(output("ls-files", "--stage", "-z")).hexdigest()
        == before["index"]
    )
    assert not output("diff", "--name-only").strip()
    assert not output("diff", "--cached", "--name-only").strip()
    assert not (HERE / "runtime1/backups").exists()
    assert not (
        ROOT
        / "testing/web-platform/tests/css/css-animations/initial-animation-admission.html"
    ).exists()
    ps = subprocess.check_output(["ps", "-axo", "pgid=,stat=,pid="], text=True)
    receipts = [
        json.loads(p.read_text()) for p in (HERE / "runtime1").glob("*.process.json")
    ]
    assert receipts and all(
        r["state"] == "terminal" and r["group_absent"] for r in receipts
    )
    groups = [r["pgid"] for r in receipts]
    assert not [
        line
        for line in ps.splitlines()
        if (parts := line.split())
        and int(parts[0]) in groups
        and not parts[1].startswith("Z")
    ]
    with tempfile.TemporaryDirectory() as scratch:
        allowed = Path(scratch) / "allowed_signers"
        allowed.write_text(
            output("config", "--get", "user.email").decode().strip()
            + " "
            + output("config", "--get", "user.signingkey").decode().strip()
            + "\n"
        )
        subprocess.run(
            [
                *git,
                "-c",
                "gpg.ssh.allowedSignersFile=" + str(allowed),
                "verify-commit",
                before["head"],
            ],
            cwd=ROOT,
            check=True,
        )
    report = {
        "sources": 8,
        "full_application_and_extras_match": True,
        "baseline_binaries_match": True,
        "head_and_index_unchanged": True,
        "tracked_tree_clean": True,
        "owned_process_groups_absent": groups,
        "backup_and_temporary_fixture_absent": True,
        "checkpoint_signature_verified": before["head"],
    }
    (HERE / "ROOT-RESTORATION.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
