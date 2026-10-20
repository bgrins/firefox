import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PINS = [
    ("", "d6b3ef9b8571f713ba7151d537eac0ba555a47101ec50a38e7f6f841168ce9fe", "d5858692c2788124acd3ecde09bdac2e0e24bef0c47a03aa2ca6ee3490a23e6c"),
    ("capsule", "d4bf53b145428c217963d389d7aa2a00fc51ec695f7862486b0d215a7387abec", "6a534cc526b57456aa467cc724c45c77e31a5153d9b3cd843f53d26afc5fcdae"),
    ("capsule/native-source", "9c0ec1eab8320b7c046957cebbe8899aa513b1c70a44ecd6a510828a67a22450", None),
]
MODULES = ["MaskedSticky", "StickyComposition", "StickyLifecycle", "StickyIndexed", "StickyMachineLifecycle", "StickyUpdate", "StickyJoined", "StickyAdmission", "ReviewChallenges", "StickyJoinedChallenges"]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}

def require(value, message):
    if not value:
        raise RuntimeError(message)

def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def read(p):
    def unique(items):
        d = {}
        for k, v in items:
            require(k not in d, "duplicate JSON key")
            d[k] = v
        return d
    return json.loads(p.read_text(), object_pairs_hook=unique)

def closure(root, pin, freeze=None):
    require(sha(root / "FILES.json") == pin, "manifest identity: " + str(root))
    if freeze:
        require(sha(root / "FREEZE.json") == freeze, "freeze identity")
    entries = read(root / "FILES.json")["files"]
    names = [e["path"] for e in entries]
    require(len(set(names)) == len(names), "duplicate path")
    for n in names:
        p = PurePosixPath(n)
        require(str(p) == n and not p.is_absolute() and ".." not in p.parts and n not in {"FILES.json", "FREEZE.json"}, "invalid path")
    files, dirs = set(), set()
    for base, ds, fs in os.walk(root, followlinks=False):
        for name in ds + fs:
            p = Path(base) / name
            n = p.relative_to(root).as_posix()
            mode = p.lstat().st_mode
            if stat.S_ISREG(mode):
                files.add(n)
            elif stat.S_ISDIR(mode):
                dirs.add(n)
            else:
                raise RuntimeError("nonregular entry: " + n)
    require(files == set(names) | {"FILES.json", "FREEZE.json"}, "closed files: " + str(root))
    expected_dirs = {str(p) for n in names for p in PurePosixPath(n).parents if str(p) != "."}
    require(dirs == expected_dirs, "closed directories: " + str(root))
    for e in entries:
        require(sha(root / e["path"]) == e["sha256"], "file identity: " + e["path"])
        if "bytes" in e:
            require((root / e["path"]).stat().st_size == e["bytes"], "file size")
    seal = read(root / "FREEZE.json")
    require(seal.get("manifest_sha256", seal.get("files_sha256")) == pin, "freeze binding")
    return {"files": len(entries), "directories": len(dirs), "manifest_sha256": pin, "freeze_sha256": sha(root / "FREEZE.json")}

def authenticate(root):
    result = {rel: closure(root / rel, pin, freeze) for rel, pin, freeze in PINS}
    for entry in read(root / "SOURCE-JOIN.json")["entries"]:
        src = entry["source"]
        data = (root / "capsule/native-source" / src["file"]).read_bytes()[src["start_byte"]:src["end_byte"]]
        require(hashlib.sha256(data).hexdigest() == src["sha256"], "source join body")
    return result

def audit(log, names):
    text = log.read_text()
    pattern = re.compile(r"'([A-Za-z0-9_.]+)' (?:depends on axioms: \[([^]]*)\]|(does not depend on any axioms))\n")
    entries, pos = {}, 0
    while pos < len(text):
        m = pattern.match(text, pos)
        require(m is not None, "unparsed axiom output: " + text[pos:pos+200])
        name, content, empty = m.groups()
        values = [] if empty or not content else [v.strip() for v in content.split(",")]
        require(name not in entries, "duplicate axiom declaration")
        require(set(values) <= ALLOWED, "forbidden axioms: " + str(values))
        entries[name] = values
        pos = m.end()
    require(list(entries) == names, "axiom roster")
    return entries

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--producer", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.producer.resolve()
    out = args.output.resolve()
    require(not out.exists() and root not in out.parents and out != root, "new external output")
    auth = authenticate(root)
    out.mkdir(parents=True)
    (out / "AUTHENTICATION.json").write_text(json.dumps(auth, indent=2) + "\n")
    inventory = read(root / "capsule/LEAN-TOOLCHAIN.json")
    prefix = Path(inventory["root"])
    actual_files, actual_dirs = set(), {"bin", "lib"}
    for sub in ["bin", "lib"]:
        for base, dirs, files in os.walk(prefix / sub, followlinks=False):
            for n in dirs + files:
                p = Path(base) / n
                rel = p.relative_to(prefix).as_posix()
                if p.is_symlink() or p.is_file():
                    actual_files.add(rel)
                elif p.is_dir():
                    actual_dirs.add(rel)
                else:
                    raise RuntimeError("toolchain special file")
    require(actual_files == {e["path"] for e in inventory["entries"]} and actual_dirs == set(inventory["directories"]), "toolchain closure")
    for e in inventory["entries"]:
        p = prefix / e["path"]
        require(p.is_symlink() == ("symlink" in e), "toolchain link type")
        if p.is_symlink():
            require(os.readlink(p) == e["symlink"] and prefix in p.resolve().parents, "toolchain symlink")
        require(sha(p) == e["sha256"], "toolchain identity: " + e["path"])
    lean = prefix / "bin/lean"
    commands = []
    names = []
    for module in MODULES:
        names += [("Review" if module == "ReviewChallenges" else module) + "." + n for n in re.findall(r"^theorem (\w+)", (root / "capsule/lean" / (module + ".lean")).read_text(), re.M)]
    require(names == read(root / "capsule/AUDIT-ROSTER.json")["declarations"], "producer declaration roster")
    own_names = ["IndependentReview." + n for n in re.findall(r"^theorem (\w+)", (HERE / "IndependentChallenges.lean").read_text(), re.M)]
    controls = []
    with tempfile.TemporaryDirectory(prefix="sentinel-independent-") as tmp:
        work = Path(tmp)
        env = {k:v for k,v in os.environ.items() if not k.startswith("LEAN_")}
        env["LEAN_PATH"] = str(work)
        for module in MODULES:
            shutil.copyfile(root / "capsule/lean" / (module + ".lean"), work / (module + ".lean"))
        shutil.copyfile(HERE / "IndependentChallenges.lean", work / "IndependentChallenges.lean")
        def compile(module, expect=0):
            cmd = [str(lean), "-o", str(work / (module + ".olean")), str(work / (module + ".lean"))]
            with (out / (module + ".log")).open("w") as f:
                proc = subprocess.run(cmd, cwd=work, env=env, stdout=f, stderr=subprocess.STDOUT)
            commands.append({"module":module,"command":cmd,"exit":proc.returncode})
            (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
            require((proc.returncode == 0) == (expect == 0), "unexpected compile result: " + module)
        for module in MODULES + ["IndependentChallenges"]:
            compile(module)
        (work / "Audit.lean").write_text("import StickyJoinedChallenges\nimport IndependentChallenges\n" + "\n".join("#print axioms " + n for n in names + own_names) + "\n")
        compile("Audit")
        audits = audit(out / "Audit.log", names + own_names)
        negatives = {
            "FalseBatch": "admitted sequential = true",
            "FalseRefresh": "(machineRun true refreshedCase).2.nodes[1]!.current = ⟨20, 7⟩",
            "FalseOverflow": "(machineRun true rootChain).2.trace = #[\"subtree:-1\", \"order:0\", \"normal:0:0\", \"flush\"]",
        }
        for module, claim in negatives.items():
            source = "import IndependentChallenges\nopen IndependentReview StickyAdmission StickyJoined\ntheorem wrong : " + claim + " := by decide +kernel\n"
            (work / (module + ".lean")).write_text(source)
            (out / (module + ".lean")).write_text(source)
            compile(module, 1)
            diagnostic = (out / (module + ".log")).read_text()
            require("is false" in diagnostic or "(kernel) application type mismatch" in diagnostic, "negative did not reach kernel refutation")
            controls.append({"name":module,"result":"kernel rejected false claim"})
        for module, source in {
            "CustomAxiom": "axiom injected : False\ntheorem wrong : False := injected\n#print axioms wrong\n",
            "NativeAxiom": "theorem wrong : (17 : Nat) = 17 := by native_decide\n#print axioms wrong\n",
        }.items():
            (work / (module + ".lean")).write_text(source)
            (out / (module + ".lean")).write_text(source)
            compile(module)
            try:
                audit(out / (module + ".log"), ["wrong"])
            except RuntimeError as e:
                require(str(e).startswith("forbidden axioms:"), "axiom guard failed for wrong reason")
                controls.append({"name":module,"result":str(e)})
            else:
                raise RuntimeError("axiom accepted")
    require(authenticate(root) == auth, "producer drift")
    receipt = {"status":"PASS", "producer_audits":len(names), "independent_audits":len(own_names), "audits":audits,"controls":controls,"lean_toolchain_entries":len(inventory["entries"]),"lean_sha256":sha(lean),"temporary_compiler_products_removed":True,"native_replay":"Not repeated; independent root replay compared separately", "trust":"Pinned Lean executable and bin/lib inventory, kernel, Python and host OS; not a C++ translation proof"}
    (out / "RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k:v for k,v in receipt.items() if k != "audits"}))

if __name__ == "__main__":
    main()
