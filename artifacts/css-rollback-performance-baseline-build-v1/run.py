import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
config = json.loads((HERE / "CONFIG.json").read_bytes())
env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1", MOZ_SKIP_PATH_PERFORMANCE_CHECK="1", MOZCONFIG=str(ROOT / "mozconfig"), MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"))
git = lambda *args: subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT, env=env)
assert git("rev-parse", "HEAD").decode().strip() == config["head"]
assert not git("diff", "HEAD", "--name-only")
assert all(sha(ROOT/n) == h for n,h in config["sources"].items())
assert all(sha(ROOT/n) == h for n,h in config["helper_hashes"].items())
assert not any(os.environ.get(n) for n in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_TARGET_DIR", "RUSTC_WRAPPER"))
helpers = {}
for name, path in config["helpers"].items():
 spec = importlib.util.spec_from_file_location(name, ROOT/path)
 module = importlib.util.module_from_spec(spec)
 spec.loader.exec_module(module)
 helpers[name] = module
lock = ROOT / "artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock"
with lock.open("x") as f: json.dump({"pid":os.getpid(),"operation":"committed-rollback-baseline-build"},f)
identity = (lock.stat().st_dev, lock.stat().st_ino)
stop = [False]
for sig in (signal.SIGINT, signal.SIGTERM): signal.signal(sig, lambda *_:stop.__setitem__(0,True))
owned, errors = {}, []
build = HERE / "build"
build.mkdir()
started = time.monotonic()
try:
 helpers["phase_helper"].run(ROOT,ROOT/"objdir-full.noindex",build,env,lambda:stop[0] or time.monotonic()-started > config["timeout_seconds"],owned,helpers["process_helper"],["/Users/bgrins/venvs/firefox/bin/python","./mach","build","binaries","-j2"],errors)
 assert not owned and not errors and not stop[0]
 assert git("rev-parse","HEAD").decode().strip() == config["head"] and not git("diff","HEAD","--name-only")
 assert all(sha(ROOT/n) == h for n,h in config["sources"].items())
 receipt={"terminal_exit":0,"head":config["head"],"sources":config["library_sources"],"all_source_pins":config["sources"],"binaries":{n:sha(ROOT/n) for n in config["binary_paths"]},"elapsed_seconds":time.monotonic()-started,"scope":"Fresh committed ArcSlice plus A+B+D baseline; no C overlay","build_result_sha256":sha(build/"build-RESULT.json"),"build_log_sha256":sha(build/"build.log")}
 with (HERE/"RECEIPT.json").open("x") as f:json.dump(receipt,f,indent=2)
 print(json.dumps(receipt,indent=2))
except BaseException:
 with (HERE/"FAILURE.txt").open("x") as f:f.write(traceback.format_exc())
 raise
finally:
 assert not owned, "Owned processes still active; preserve lock"
 assert (lock.stat().st_dev,lock.stat().st_ino)==identity
 lock.unlink()
