import hashlib, json, os, pathlib, shutil, signal, subprocess, time
runtime = pathlib.Path("artifacts/css-stock-firefox-masked-nine-runtime-1")
out = pathlib.Path("artifacts/css-stock-firefox-masked-nine-root-cleanup-v1.json")
assert not out.exists()
tmp = json.loads((runtime / "TEMPORARY.json").read_text())
binding = json.loads((runtime / "BINDING.json").read_text())
path = pathlib.Path(tmp["path"])
profile = tmp["profile"]
assert path.parent == pathlib.Path("/private/tmp") and path.name.startswith("css-stock-firefox-")
assert not path.is_symlink() and profile == str(path / "profile")
s = path.stat()
assert [s.st_dev, s.st_ino] == tmp["identity"]
assert not (path / "profile/user.js").exists()
def census():
    rows = subprocess.check_output(["ps", "-axo", "pid=,ppid=,pgid=,command="], text=True)
    return [dict(pid=int(f[0]), ppid=int(f[1]), pgid=int(f[2]), command=f[3])
            for line in rows.splitlines() if len(f := line.split(None, 3)) == 4]
rows = census()
main = [r for r in rows if r["command"].startswith("/Applications/Firefox.app/Contents/MacOS/firefox ") and "--profile " + profile + " " in r["command"]]
assert len(main) == 1
main = main[0]
assert main["pid"] == main["pgid"] == 506
assert binding["run_id"] in main["command"] and binding["nonce"] in main["command"]
group = [r for r in rows if r["pgid"] == main["pgid"]]
assert all(r == main or (r["ppid"] == main["pid"] and r["command"].startswith("/Applications/Firefox.app/Contents/MacOS/plugin-container.app/") and "-profile " + profile + " " in r["command"]) for r in group)
original = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in runtime.iterdir() if p.is_file()}
receipt = dict(original_runtime_hashes=original, before=group, temporary=tmp, original_runner_cleanup_succeeded=False)
out.write_text(json.dumps(receipt, indent=2) + "\n")
os.killpg(main["pgid"], signal.SIGTERM)
for _ in range(40):
    rows = census()
    remaining = [r for r in rows if r["pgid"] == main["pgid"] or (r["command"].startswith("/Applications/Firefox.app/") and profile in r["command"])]
    if not remaining: break
    time.sleep(.25)
assert not remaining, remaining
s = path.stat()
assert [s.st_dev, s.st_ino] == tmp["identity"] and not path.is_symlink()
assert not (path / "profile/user.js").exists()
shutil.rmtree(path)
assert not path.exists()
assert original == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in runtime.iterdir() if p.is_file()}
receipt.update(root_cleanup_succeeded=True, remaining_processes=remaining, temporary_removed=True, original_runtime_unchanged=True)
out.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({k:v for k,v in receipt.items() if k not in ("before", "original_runtime_hashes")}, indent=2))
