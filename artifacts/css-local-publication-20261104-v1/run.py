import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
recipe_path = (ROOT / sys.argv[1]).resolve()
assert recipe_path.is_relative_to(ROOT / "artifacts")
recipe = json.loads(recipe_path.read_bytes())
out = recipe_path.parent / recipe_path.stem
out.mkdir()
env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1", GIT_LITERAL_PATHSPECS="1")
git = lambda *args: subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT, env=env)
head = git("rev-parse", "HEAD").decode().strip()
assert head == recipe["head"]
assert not git("diff", "--cached", "--name-only")
assert git("config", "--get", "commit.gpgsign").decode().strip().lower() == "true"
assert not (ROOT / "artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock").exists()
objects = {}
for name, digest in recipe["files"].items():
 path = ROOT / name
 assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT)
 data = path.read_bytes()
 assert hashlib.sha256(data).hexdigest() == digest, name
 objects[name] = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
paths = out / "paths.bin"
paths.write_bytes(b"\0".join(n.encode() for n in objects) + b"\0")
git("add", "-f", "--pathspec-from-file=" + str(paths), "--pathspec-file-nul")
staged = set(git("diff", "--cached", "--name-only", "-z").decode().rstrip("\0").split("\0"))
assert staged and staged <= set(objects)
index = {}
for entry in git("ls-files", "--stage", "-z").split(b"\0"):
 if not entry: continue
 info, name = entry.split(b"\t", 1)
 mode, oid, stage = info.decode().split()
 if name.decode() in objects:
  assert stage == "0" and oid == objects[name.decode()], name
  index[name.decode()] = oid
assert set(index) == set(objects)
message = out / "message.txt"
message.write_text(recipe["message"] + "\n")
control = ROOT / "artifacts/css-keyframe-typed-attribute-demand-runtime-v1/process_control.py"
assert hashlib.sha256(control.read_bytes()).hexdigest() == "b57e5e2506b89d48e30c958b2aa04e375e853e3ec68386afe3071a349c1d969a"
spec = importlib.util.spec_from_file_location("publication_cleanup", control)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
timed_out = False
with (out / "commit.log").open("x") as stream:
 process = subprocess.Popen(["git", "-c", "core.fsmonitor=false", "commit", "-F", str(message)], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
 try:
  code = process.wait(timeout=45)
 except subprocess.TimeoutExpired:
  timed_out, code = True, None
 finally:
  cleanup = module.terminate(process)
  assert cleanup["owned_group_absent"]
after = git("rev-parse", "HEAD").decode().strip()
signed = b"\ngpgsig " in git("cat-file", "-p", after)
result = {"before":head,"after":after,"exit":code,"timeout":timed_out,"pid":process.pid,"cleanup":cleanup,"selected_files":len(objects),"changed_files":len(staged),"signature_present":signed,"commit_created":after!=head}
if code == 0:
 assert after != head and signed and not git("diff", "--cached", "--name-only")
 assert set(git("diff-tree", "--no-commit-id", "--name-only", "-r", after).decode().splitlines()) == staged
with (out / "RESULT.json").open("x") as stream:json.dump(result,stream,indent=2)
print(json.dumps(result,indent=2))
raise SystemExit(0 if code == 0 and after != head else 1)
