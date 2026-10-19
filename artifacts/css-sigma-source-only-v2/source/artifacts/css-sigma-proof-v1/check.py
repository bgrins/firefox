import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
ICU_OBJECT = ROOT / "objdir-full.noindex/config/external/icu/common/ucase.o"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, output):
    result = subprocess.run([str(x) for x in command], capture_output=True)
    output.write_bytes(result.stdout + result.stderr)
    return result


def audit_lean(source, output):
    expected = re.findall(r"^#print axioms ([A-Za-z_][A-Za-z_0-9]*)$", source.read_text(), re.M)
    if len(expected) != 16 or len(set(expected)) != 16:
        raise ValueError("missing or duplicated theorem audits")
    if re.search(r"\b(sorry|admit|unsafe)\b|^\s*axiom\s", source.read_text(), re.M):
        raise ValueError("untrusted proof declaration")
    result = run([LEAN, source], output)
    if result.returncode != 0:
        raise ValueError("Lean compilation failed")
    lines = result.stdout.decode().splitlines()
    if result.stderr or len(lines) != len(expected):
        raise ValueError("unexpected Lean diagnostics")
    axioms = {}
    for name, line in zip(expected, lines):
        prefix = f"'SigmaContext.{name}' "
        if line == prefix + "does not depend on any axioms":
            axioms[name] = []
            continue
        match = re.fullmatch(re.escape(prefix) + r"depends on axioms: \[([^\]]*)\]", line)
        if not match:
            raise ValueError("unexpected theorem output")
        used = match[1].split(", ") if match[1] else []
        if any(a not in {"propext", "Quot.sound"} for a in used):
            raise ValueError("unapproved axiom")
        axioms[name] = used
    return axioms


def lean_controls(output):
    source = (BASE / "Sigma.lean").read_text()
    mutations = {
        "cased-before-ignorable": ("if p.ignorable then scan ps else p.cased", "if p.cased then true else if p.ignorable then scan ps else false"),
        "ignore-nothing": ("if p.ignorable then scan ps else p.cased", "p.cased"),
        "drop-predecessor": ("scan before.reverse && !scan after", "!scan after"),
        "invert-successor": ("scan before.reverse && !scan after", "scan before.reverse && scan after"),
        "wrong-backward-direction": ("scan before.reverse && !scan after", "scan before && !scan after"),
        "skip-masked": ("if c.masked then false", "if c.masked then maskedScan cs"),
        "raw-masked-properties": ("if c.masked then barrier else c.properties", "c.properties"),
        "slice-offset": ("full.drop (i + 1)", "full.drop i"),
    }
    rejected = []
    for name, (old, new) in mutations.items():
        if source.count(old) != 1:
            raise ValueError(f"ambiguous mutation {name}")
        path = output / f"mutation-{name}.lean"
        path.write_text(source.replace(old, new))
        result = run([LEAN, path], output / f"mutation-{name}.log")
        if result.returncode == 0 or b"error" not in result.stdout:
            raise ValueError(f"semantic mutation accepted {name}")
        rejected.append(name)
    guards = {
        "missing-audit": source.replace("#print axioms context_slice_correct\n", ""),
        "extra-output": source + "\n#check Nat\n",
        "warning": source + "\nexample : True := by simp [Nat.zero_add]\n",
        "sorry": source.replace("theorem overlap_without_base :", "theorem overlap_without_base :", 1).replace("= false := rfl", "= false := by sorry", 1),
        "axiom": source + "\naxiom forged : False\n",
        "syntax": source + "\nthis is not Lean\n",
    }
    guard_results = []
    for name, text in guards.items():
        path = output / f"guard-{name}.lean"
        path.write_text(text)
        try:
            audit_lean(path, output / f"guard-{name}.log")
        except ValueError as error:
            guard_results.append({"name": name, "reason": str(error)})
        else:
            raise ValueError(f"diagnostic guard accepted {name}")
    return rejected, guard_results


def expected_properties():
    expected = bytearray(0x110000)
    for line in (BASE / "unicode-properties17.txt").read_text().splitlines():
        fields = line.partition("#")[0].split(";")
        if len(fields) < 2 or fields[1].strip() not in {"Cased", "Case_Ignorable"}:
            continue
        bit = 1 if fields[1].strip() == "Cased" else 2
        endpoints = [int(x, 16) for x in fields[0].strip().split("..")]
        for cp in range(endpoints[0], endpoints[-1] + 1):
            expected[cp] |= bit
    return expected


def authenticate(manifest, replacements=None):
    replacements = replacements or {}
    for name, expected in manifest.items():
        path = replacements.get(name, ROOT / name)
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f"source identity mismatch: {name}")


def identity_controls(manifest, output):
    names = ["Sigma.lean", "native-candidate.cpp", "before-nsTextRunTransformations.cpp",
             "bridge.py", "bridge-prefix.cpp", "bridge-suffix.cpp", "icu-probe.cpp",
             "unicode-properties17.txt"]
    rejected = []
    for name in names:
        relative = str((BASE / name).relative_to(ROOT))
        copy = output / ("source-guard-" + name)
        copy.write_bytes((BASE / name).read_bytes() + b"\nchanged\n")
        try:
            authenticate(manifest, {relative: copy})
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("source guard accepted " + name)
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lean-only", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = None
    if not args.development:
        manifest = json.loads((BASE / "SOURCE-v1.json").read_text())
        authenticate(manifest)
    if args.live and digest(ROOT / "layout/generic/nsTextRunTransformations.cpp") != digest(BASE / "native-candidate.cpp"):
        raise ValueError("live native candidate does not match")
    pins = {"lean": digest(LEAN), "Sigma.lean": digest(BASE / "Sigma.lean")}
    axioms = audit_lean(BASE / "Sigma.lean", output / "lean.log")
    mutations, guards = lean_controls(output)
    record = {"lean_audits": axioms, "lean_mutations": mutations, "diagnostic_guards": guards}
    if not args.lean_only:
        import bridge
        record["native"] = bridge.check(output)
    if manifest is not None:
        record["source_identity_controls"] = identity_controls(manifest, output)
        authenticate(manifest)
        record["source_manifest_sha256"] = digest(BASE / "SOURCE-v1.json")
        record["authenticated_inputs"] = manifest
    record["pins"] = pins
    (output / "PROOF-v1.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
