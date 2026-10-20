import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S without optimization")
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib, json, os, stat
ROOT = Path(__file__).resolve().parent

def need(value, message):
    if not value:
        raise RuntimeError(message)

def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result

def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for seal in ["FILES.json", "FREEZE.json"]:
    need(stat.S_ISREG((ROOT / seal).lstat().st_mode), "nonregular seal")
freeze = read("FREEZE.json")
need(sha(ROOT / "FILES.json") == freeze["files_sha256"], "manifest hash")
need(sha(ROOT / "check.py") == freeze["checker_sha256"], "checker hash")
rows = read("FILES.json")
expected = {"FILES.json", "FREEZE.json"}
dirs = set()
for row in rows:
    need(set(row) == {"path", "bytes", "sha256"}, "manifest schema")
    path = Path(row["path"])
    need(not path.is_absolute() and str(path) == row["path"] and ".." not in path.parts, "unsafe path")
    need(row["path"] not in expected, "duplicate path")
    expected.add(row["path"])
    dirs.update(str(d) for d in path.parents if str(d) != ".")
seen = set()
def walk(directory):
    for entry in os.scandir(directory):
        rel = str(Path(entry.path).relative_to(ROOT))
        mode = entry.stat(follow_symlinks=False).st_mode
        if stat.S_ISDIR(mode):
            need(rel in dirs, "unexpected directory: " + rel)
            walk(entry.path)
        else:
            need(stat.S_ISREG(mode), "nonregular file: " + rel)
            seen.add(rel)
walk(ROOT)
need(seen == expected, "file roster")
for row in rows:
    path = ROOT / row["path"]
    need(path.stat().st_size == row["bytes"] and sha(path) == row["sha256"], "input mismatch: " + row["path"])
nested = ROOT / "capsule"
need(sha(nested / "FILES.json") == "ebb17cee7ce3276c4682363b5a122c3dbe3917fc93f95498beb57326e10fd01e", "producer manifest identity")
need(sha(nested / "FREEZE.json") == "be1b75847632553611bca6111c1ba2022d6c34b7d92d39beb0fcbf21a45e9ff4", "producer seal identity")
nested_rows = read("capsule/FILES.json")
nested_expected = {"FILES.json", "FREEZE.json"} | {row["path"] for row in nested_rows}
nested_dirs = {str(d) for name in nested_expected for d in Path(name).parents if str(d) != "."}
nested_seen = set()
def walk_nested(directory):
    for entry in os.scandir(directory):
        rel = str(Path(entry.path).relative_to(nested))
        mode = entry.stat(follow_symlinks=False).st_mode
        if stat.S_ISDIR(mode):
            need(rel in nested_dirs, "unexpected nested producer directory: " + rel)
            walk_nested(entry.path)
        else:
            need(stat.S_ISREG(mode), "nonregular nested producer file: " + rel)
            nested_seen.add(rel)
walk_nested(nested)
need(nested_seen == nested_expected, "nested producer file roster")
for row in nested_rows:
    path = nested / row["path"]
    need(path.stat().st_size == row["bytes"] and sha(path) == row["sha256"], "nested producer input mismatch")
need(read("replay-v2/RESULT.json") == read("replay/RESULT.json"), "corrected replay result differs")
result = read("replay-v2/RESULT.json")
need(result["audits"] == 39, "audit count")
need(read("CHALLENGE-COMMAND.json")["exit"] == 0, "independent challenges")
need(read("SEMANTIC-MUTATION-COMMAND.json")["exit"] == 0, "semantic mutation witness")
guards = read("GUARDS.json")
need(len(guards) == 19, "guard count")
for row in guards:
    if "exit" in row:
        need(row["exit"] != 0 and not row["output_created"], "guard unexpectedly accepted")
        need("REVIEW_SHADOW_EXECUTED" not in row["stderr"], "shadow import executed")
    else:
        need(row["rejected"] is True, "case accepted")
for row in read("CLEANUP.json")["removed"] + read("CLEANUP-V2.json")["removed"]:
    need(not (ROOT / row["path"]).exists(), "compiler product retained")
print(json.dumps({"status": "PASS", "authenticated_inputs": len(rows), "audits": 39, "independent_kernel_examples": 8, "semantic_mutation_theorems": 2, "negative_controls": 19}))
