from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false"]


def git(*args, **kwargs):
    return subprocess.run(GIT + list(args), cwd=ROOT, check=True,
                          capture_output=True, **kwargs)


def text(*args):
    return git(*args, text=True).stdout.strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("phase", choices=["research", "native"])
    args = parser.parse_args()
    plan = json.loads((HERE / "NATIVE-PLAN.json").read_text())
    item = next(x for x in plan["items"] if x["slug"] == args.slug)
    position = plan["items"].index(item)
    predecessor = None
    if args.phase == "native":
        predecessor = HERE / (args.slug + "-research-RESULT.json")
    elif position:
        predecessor = HERE / (plan["items"][position - 1]["slug"] + "-native-RESULT.json")
    expected_parent = plan["base"]
    if predecessor:
        previous = json.loads(predecessor.read_text())
        assert previous["status"] == "COMMITTED_AND_VERIFIED"
        expected_parent = previous["commit"]
    assert text("rev-parse", "HEAD") == expected_parent
    assert not text("diff", "--cached", "--name-only"), "Index must be empty"
    assert text("config", "--get", "commit.gpgsign") == "true"
    assert text("config", "--get", "gpg.format") == "ssh"
    signing_key = text("config", "--get", "user.signingkey")
    assert signing_key.startswith("ssh-ed25519 ")
    receipt = HERE / (args.slug + "-" + args.phase + "-RESULT.json")
    assert not receipt.exists(), "Do not retry an existing publication attempt implicitly"
    if args.phase == "research":
        research = json.loads((HERE / (args.slug + "-RESEARCH.json")).read_text())
        pins = research["files"]
        assert pins and all(name.startswith("artifacts/") for name in pins)
        for name, row in pins.items():
            assert sha(ROOT / name) == row["sha256"], name
        subject = research["subject"]
        pathspec = HERE / (args.slug + "-research-pathspec")
        pathspec.write_bytes(b"\0".join(name.encode() for name in pins) + b"\0")
        git("add", "-f", "--pathspec-from-file=" + str(pathspec), "--pathspec-file-nul")
        expected_paths = set(pins)
    else:
        patch = ROOT / item["patch"]
        assert sha(patch) == item["sha256"]
        pins = {name: {"sha256": sha(ROOT / name)} for name in item["paths"]}
        git("apply", "--cached", "--check", str(patch))
        git("apply", "--cached", str(patch))
        git("diff", "--cached", "--check")
        subject = item["native_subject"]
        expected_paths = set(item["paths"])
    staged = set(text("diff", "--cached", "--name-only").splitlines())
    assert staged and staged <= expected_paths
    if args.phase == "native":
        assert staged == expected_paths
    expected_tree = text("write-tree")
    message = HERE / (args.slug + "-" + args.phase + "-message.txt")
    message.write_text(subject + "\n")
    result = dict(status="ATTEMPTING", parent=expected_parent, tree=expected_tree,
                  subject=subject, staged_paths=sorted(staged), signing_enabled=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    log = HERE / (args.slug + "-" + args.phase + "-commit.log")
    with log.open("xb") as output:
        process = subprocess.run(GIT + ["commit", "-F", str(message)], cwd=ROOT,
                                 stdout=output, stderr=subprocess.STDOUT)
    result["commit_exit"] = process.returncode
    result["commit_log_sha256"] = sha(log)
    if process.returncode:
        result["status"] = "COMMIT_FAILED"
        result["head_unchanged"] = text("rev-parse", "HEAD") == expected_parent
        result["index_preserved"] = text("write-tree") == expected_tree
        receipt.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(dict(status=result["status"], log=str(log),
                              head_unchanged=result["head_unchanged"],
                              index_preserved=result["index_preserved"])), flush=True)
        return process.returncode
    commit = text("rev-parse", "HEAD")
    result.update(status="COMMITTED_PENDING_VERIFICATION", commit=commit)
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    assert text("rev-parse", "HEAD^") == expected_parent
    assert text("rev-parse", "HEAD^{tree}") == expected_tree
    assert text("log", "-1", "--format=%s") == subject
    assert not text("diff", "--cached", "--name-only")
    for name, row in pins.items():
        assert sha(ROOT / name) == row["sha256"], name
    with tempfile.TemporaryDirectory(prefix="css-signature-check-") as td:
        allowed = Path(td) / "allowed_signers"
        allowed.write_text("local-css-author " + signing_key + "\n")
        verified = git("-c", "gpg.ssh.allowedSignersFile=" + str(allowed),
                       "verify-commit", commit, text=True)
        (HERE / (args.slug + "-" + args.phase + "-signature.log")).write_text(
            verified.stdout + verified.stderr)
    result.update(status="COMMITTED_AND_VERIFIED",
                  signature_verified_against_configured_key=True, worktree_inputs_unchanged=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(status=result["status"], commit=commit, subject=subject,
                          files=len(staged))), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
