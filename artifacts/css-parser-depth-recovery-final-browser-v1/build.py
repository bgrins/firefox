import hashlib, json, os, subprocess, time
from pathlib import Path
root = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
v = json.loads((here / "candidate-build-input.json").read_text())
for n, expected in v["fixed"].items():
    assert (h(root / n) if (root / n).exists() else None) == expected, n
v["binaries"] = {n: h(root / n) for n in v["binaries"]}
(here / "candidate-build-before.json").write_text(json.dumps(v, indent=2) + "\n")
env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")
commands = [
    ("clean-parser", ["/Users/bgrins/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo", "--config", "objdir-full.noindex/.cargo/config.toml", "clean", "--offline", "-p", "cssparser", "--release", "--target", "aarch64-apple-darwin", "--target-dir", "objdir-full.noindex"]),
    ("force-rust", ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "build", "--allow-subdirectory-build", "toolkit/library/rust/force-cargo-library-build"]),
    ("link", ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "build", "binaries"]),
]
receipts = []
for phase, command in commands:
    log = here / ("candidate-" + phase + ".log")
    started = time.time()
    with log.open("w") as out:
        result = subprocess.run(command, cwd=root, env=env, stdout=out, stderr=subprocess.STDOUT)
    receipts.append(dict(phase=phase, command=command, exit_code=result.returncode, started=started, ended=time.time(), log_sha256=h(log)))
    (here / "candidate-build-result.json").write_text(json.dumps(receipts, indent=2) + "\n")
    if result.returncode:
        raise SystemExit(result.returncode)
for n, expected in v["fixed"].items():
    assert (h(root / n) if (root / n).exists() else None) == expected, n
v["binaries"] = {n: h(root / n) for n in v["binaries"]}
(here / "candidate-build-after.json").write_text(json.dumps(v, indent=2) + "\n")
