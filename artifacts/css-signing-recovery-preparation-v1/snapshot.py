import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_text())
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1", GIT_LITERAL_PATHSPECS="1")
for key in ("GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
    ENV.pop(key, None)


def git(*args, env=ENV, body=None):
    return subprocess.check_output(
        ["git", "-c", "core.fsmonitor=false", "-c", "core.splitIndex=false", *args],
        cwd=ROOT, env=env, input=body,
    )


def safe(name):
    path = Path(name)
    if path.is_absolute() or not path.parts or any(p in ("..", ".git") for p in path.parts):
        raise RuntimeError("unsafe path " + name)
    for parent in (ROOT / path).parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise RuntimeError("symlink parent " + name)
    return ROOT / path


def body_mode(name):
    path = safe(name)
    if not path.exists() and not path.is_symlink():
        return None, None
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode):
        return os.fsencode(os.readlink(path)), "120000"
    if not stat.S_ISREG(mode):
        raise RuntimeError("not a regular file/symlink " + name)
    before = path.stat()
    body = path.read_bytes()
    after = path.stat()
    fields = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if fields(before) != fields(after):
        raise RuntimeError("changed while reading " + name)
    return body, "100755" if mode & 0o111 else "100644"


def index_observation():
    path = Path(git("rev-parse", "--path-format=absolute", "--git-path", "index").decode().strip())
    return {"path": str(path), "sha256": sha(path.read_bytes()) if path.exists() else None}


def head_entries(head, paths):
    result = {}
    if not paths:
        return result
    for record in git("ls-tree", "-r", "-z", head, "--", *paths).split(b"\0"):
        if not record:
            continue
        meta, name = record.split(b"\t", 1)
        mode, kind, oid = meta.decode().split()
        result[os.fsdecode(name)] = {"mode": mode, "kind": kind, "oid": oid}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=Path(__file__).with_name("INPUTS.json"))
    args = parser.parse_args()
    config = read(args.inputs)
    if not config.get("ready") or not config.get("expected_head") or not config.get("output"):
        raise RuntimeError("disabled: root must bind the completed signing HEAD and absent output")
    head = config["expected_head"]
    assert git("rev-parse", "HEAD").decode().strip() == head
    allow_ref = config["allowlist"]
    assert sha(safe(allow_ref["path"]).read_bytes()) == allow_ref["sha256"]
    allow = set(read(safe(allow_ref["path"])))
    for name in allow:
        safe(name)
    output_name = config["output"]
    assert output_name.startswith("artifacts/")
    output = safe(output_name)
    assert not output.exists() and not output.is_symlink()
    output.mkdir()
    save = lambda name, value: (output / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    before_index = index_observation()
    save("INDEX-BEFORE.json", before_index)
    (output / "staged.patch").write_bytes(git("diff", "--cached", "--binary", "--full-index", "--no-renames", "--no-ext-diff", "--no-textconv"))
    changed = set(os.fsdecode(n) for n in git("diff", "--name-only", "-z", "--no-renames", head, "--").split(b"\0") if n)
    entries = head_entries(head, sorted(changed | allow))
    unexpected = changed - set(entries) - allow
    if unexpected:
        raise RuntimeError("new staged additions outside the source allowlist: " + repr(sorted(unexpected)))
    additions = {n for n in allow - set(entries) if safe(n).exists() or safe(n).is_symlink()}
    allowed_values = {n: body_mode(n) for n in sorted(allow)}
    save("ALLOWLIST-CURRENT.json", {n: None if b is None else {"sha256": sha(b), "mode": m} for n, (b, m) in allowed_values.items()})
    selected = sorted(changed | additions)
    values = {n: body_mode(n) for n in selected}
    pre = {}
    for name in selected:
        entry = entries.get(name)
        if entry is None:
            pre[name] = None
            continue
        assert entry["kind"] == "blob", "nested gitlinks require a separate checkpoint"
        pre[name] = {"mode": entry["mode"], "sha256": sha(git("cat-file", "blob", entry["oid"]))}
    post = {n: None if b is None else {"mode": m, "sha256": sha(b)} for n, (b, m) in values.items()}
    save("PREIMAGES.json", pre)
    save("POSTIMAGES.json", post)
    save("SOURCE-PINS.json", {n: None if v is None else v["sha256"] for n, v in post.items()})
    objects = git("rev-parse", "--path-format=absolute", "--git-path", "objects").decode().strip()
    with tempfile.TemporaryDirectory(prefix="signing-recovery-") as temporary:
        temporary = Path(temporary)
        (temporary / "objects").mkdir()
        scratch = dict(ENV, GIT_INDEX_FILE=str(temporary / "index"),
                       GIT_OBJECT_DIRECTORY=str(temporary / "objects"), GIT_ALTERNATE_OBJECT_DIRECTORIES=objects)
        git("read-tree", head, env=scratch)
        for name, (body, mode) in values.items():
            if body is None:
                git("update-index", "--force-remove", "--", name, env=scratch)
            else:
                oid = git("hash-object", "-w", "--stdin", env=scratch, body=body).decode().strip()
                git("update-index", "--add", "--cacheinfo", mode, oid, name, env=scratch)
        tree = git("write-tree", env=scratch).decode().strip()
        patch = git("diff", "--cached", "--binary", "--full-index", "--no-renames", "--no-ext-diff", "--no-textconv", head, "--", *selected, env=scratch)
        (output / "unfinished.patch").write_bytes(patch)
        if patch:
            git("apply", "--cached", "--reverse", str(output / "unfinished.patch"), env=scratch)
            assert git("write-tree", env=scratch).decode().strip() == git("rev-parse", head + "^{tree}").decode().strip()
            git("apply", "--cached", str(output / "unfinished.patch"), env=scratch)
            assert git("write-tree", env=scratch).decode().strip() == tree
        save("BASE.json", {"commit": head, "paths": len(selected), "allowlisted_additions": len(additions),
                           "patch_sha256": sha(patch), "tree": tree, "accepted_fix_increment": 0})
    artifact_selection = {}
    artifact_excluded = {}
    for ref in config["artifact_manifests"]:
        manifest = safe(ref["path"])
        assert sha(manifest.read_bytes()) == ref["sha256"]
        names = {str(manifest.relative_to(ROOT)): ref["sha256"]}
        for relative, pin in read(manifest).items():
            pin = pin["sha256"] if isinstance(pin, dict) else pin
            name = str((manifest.parent / relative).relative_to(ROOT))
            assert sha(safe(name).read_bytes()) == pin
            names[name] = pin
        old = head_entries(head, sorted(names))
        for name, pin in names.items():
            body, mode = body_mode(name)
            assert body is not None and sha(body) == pin
            if name in old and old[name]["mode"] == mode and sha(git("cat-file", "blob", old[name]["oid"])) == pin:
                artifact_excluded[name] = pin
            else:
                artifact_selection[name] = {"sha256": pin, "mode": mode}
    save("ARTIFACT-SELECTION.json", artifact_selection)
    save("ARTIFACT-ALREADY-COMMITTED.json", artifact_excluded)
    for name, pin in artifact_selection.items():
        body, mode = body_mode(name)
        assert mode == pin["mode"] and sha(body) == pin["sha256"]
    assert allowed_values == {n: body_mode(n) for n in sorted(allow)}
    assert values == {n: body_mode(n) for n in selected}
    assert changed == set(os.fsdecode(n) for n in git("diff", "--name-only", "-z", "--no-renames", head, "--").split(b"\0") if n)
    assert additions == {n for n in allow - set(entries) if safe(n).exists() or safe(n).is_symlink()}
    assert git("rev-parse", "HEAD").decode().strip() == head
    after_index = index_observation()
    save("INDEX-AFTER.json", after_index)
    assert before_index == after_index
    save("CHECK.json", {"status": "SIGNING_RECOVERY_SNAPSHOT_PASS", "exact_patch_roundtrip": True,
                        "source_bodies_and_modes_preserved": True, "main_index_preserved": True,
                        "temporary_index_and_objects_removed": True, "accepted_fix_increment": 0,
                        "unrelated_untracked_selected": False, "artifact_paths": len(artifact_selection)})
    save("FILES.json", {str(p.relative_to(output)): sha(p.read_bytes()) for p in sorted(output.rglob("*")) if p.is_file()})


if __name__ == "__main__":
    main()
