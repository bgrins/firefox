import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import fixtures
import oracle

BASE = Path(__file__).resolve().parent
TOOLS = json.loads((BASE / "TOOLCHAIN-v1.json").read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(command, log, text=None, cwd=None, env=None, timeout=90):
    result = subprocess.run([str(arg) for arg in command], input=text, capture_output=True,
                            text=True, cwd=cwd, env=env, timeout=timeout)
    log.write_text(result.stdout + result.stderr)
    return result


def identity(path, expected):
    if not path.is_file() or digest(path) != expected:
        raise ValueError("identity mismatch")


def authenticate():
    manifest = json.loads((BASE / "SOURCE-v1.json").read_text())
    for name, expected in manifest.items():
        identity(BASE / name, expected)
    for item in TOOLS.values():
        identity(Path(item["path"]), item["sha256"])
    return manifest


def preservation():
    before = (BASE / "source/tokenizer-before.rs").read_text()
    candidate = (BASE / "source/tokenizer.rs").read_text()
    old = """                b => {
                    parser.consume_known_byte(b);
                    return consume_bad_url(parser, start_pos);
                }"""
    new = """                _ => {
                    return consume_bad_url(parser, start_pos);
                }"""
    if before.count(old) != 1 or candidate != before.replace(old, new):
        raise ValueError("unexpected tokenizer diff")
    a = json.loads((BASE / "source/cargo-checksum-before.json").read_text())
    b = json.loads((BASE / "source/cargo-checksum-candidate.json").read_text())
    if a["files"]["src/tokenizer.rs"] != digest(BASE / "source/tokenizer-before.rs"):
        raise ValueError("original vendor checksum")
    a["files"]["src/tokenizer.rs"] = digest(BASE / "source/tokenizer.rs")
    if a != b:
        raise ValueError("vendor checksum changes")
    lib = (BASE / "source/lib.rs").read_text()
    start = lib.index('#[cfg(not(feature = "fast_match_byte"))]')
    end = lib.index('// Re-exporting phf', start)
    if (BASE / "fallback-macro.rs").read_text() != lib[start:end]:
        raise ValueError("fallback macro extraction changed")
    return before, candidate


def lean_audit(path, log, output=None):
    text = path.read_text()
    names = re.findall(r'^#print axioms (\w+)$', text, re.M)
    if len(names) != 25 or len(set(names)) != 25:
        raise ValueError("missing theorem audit")
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s', text, re.M):
        raise ValueError("untrusted Lean declaration")
    command = [TOOLS["lean"]["path"]]
    if output:
        command += ["-o", output]
    result = execute(command + [path], log)
    if result.returncode or result.stderr:
        raise ValueError("Lean failure or stderr")
    lines = result.stdout.splitlines()
    if len(lines) != len(names):
        raise ValueError("unexpected Lean diagnostics")
    axioms = {}
    for name, line in zip(names, lines):
        prefix = f"'BadUrl.{name}' "
        if line == prefix + "does not depend on any axioms":
            axioms[name] = []
            continue
        match = re.fullmatch(re.escape(prefix) + r'depends on axioms: \[([^\]]*)\]', line)
        if not match or any(a not in {"propext", "Quot.sound", "Classical.choice"} for a in match[1].split(", ")):
            raise ValueError("unapproved Lean axioms")
        axioms[name] = match[1].split(", ")
    return axioms


def dependencies(out):
    rustc = TOOLS["rustc"]["path"]
    smallvec = out / "libsmallvec.rlib"
    result = execute([rustc, "--edition", "2018", "--crate-name", "smallvec", "--crate-type", "rlib", "-D", "warnings",
                      BASE / "source/smallvec/src/lib.rs", "-o", smallvec], out / "smallvec.log")
    if result.returncode or result.stdout or result.stderr:
        raise ValueError("SmallVec compilation diagnostic")
    project = out / "macro-build"
    (project / ".cargo").mkdir(parents=True)
    (project / "src").mkdir()
    (project / "Cargo.toml").write_text('[package]\nname = "bad-url-macro-build"\nversion = "0.1.0"\nedition = "2024"\n[workspace]\n[dependencies]\ncssparser-macros = { path = ' + json.dumps(str(BASE / "source/deps/cssparser-macros")) + ' }\n')
    (project / ".cargo/config.toml").write_text('[source.crates-io]\nreplace-with = "vendored-sources"\n[source.vendored-sources]\ndirectory = ' + json.dumps(str(BASE / "source/deps")) + '\n')
    (project / "src/main.rs").write_text('fn main() {}\n')
    shutil.copyfile(BASE / "macro-Cargo.lock", project / "Cargo.lock")
    env = dict(os.environ)
    env["RUSTC"] = rustc
    env["RUSTFLAGS"] = "-D warnings"
    result = execute([TOOLS["cargo"]["path"], "build", "--offline", "--locked", "--target-dir", project / "target"], out / "macro-build.log", cwd=project, env=env)
    if result.returncode or result.stdout or re.search(r'(^|\n)(warning|error)(:|\[)', result.stderr):
        raise ValueError("macro dependency compilation diagnostic")
    deps = project / "target/debug/deps"
    macros = list(deps.glob("libcssparser_macros-*.dylib"))
    if len(macros) != 1:
        raise ValueError("unexpected macro artifact count")
    return smallvec, deps, macros[0]


def native(source, label, out, deps, data, fast=True, wrapper=None):
    directory = out / label
    directory.mkdir()
    (directory / "tokenizer.rs").write_text(source)
    for name in ["parser.rs", "cow_rc_str.rs", "macros.rs"]:
        shutil.copyfile(BASE / "source" / name, directory / name)
    shutil.copyfile(BASE / "fallback-macro.rs", directory / "fallback-macro.rs")
    (directory / "main.rs").write_text(wrapper if wrapper is not None else (BASE / "capsule-prefix.rs").read_text())
    command = [TOOLS["rustc"]["path"], "--edition", "2024", "-D", "warnings", "-C", "opt-level=1", "-C", "debug-assertions=yes",
               "--extern", "smallvec=" + str(deps[0])]
    if fast:
        command += ["--cfg", 'feature="fast_match_byte"', "--extern", "cssparser_macros=" + str(deps[2]), "-L", "dependency=" + str(deps[1])]
    binary = directory / "capsule"
    result = execute(command + [directory / "main.rs", "-o", binary], directory / "compile.log")
    if result.returncode or result.stdout or result.stderr:
        raise ValueError("native compilation diagnostic")
    result = execute([binary], directory / "run.log", data)
    if result.returncode or result.stderr:
        raise ValueError("native execution diagnostic")
    records = []
    for line in result.stdout.splitlines():
        parts = line.split(" ")
        if len(parts) != 6 or parts[0] not in ["url", "bad-url"]:
            raise ValueError("native output shape")
        kind, payload, suffix, pos, line_number, column = parts
        if not all(re.fullmatch(r'(?:[0-9a-f]{2})*', value) for value in [payload, suffix]):
            raise ValueError("native hex output")
        records.append({"kind": kind, "payload": bytes.fromhex(payload).decode(), "suffix": bytes.fromhex(suffix).decode(),
                        "position": int(pos), "line": int(line_number), "column": int(column)})
    if len(records) != len(data.splitlines()):
        raise ValueError("native output count")
    return records


def lean_export(out, inputs):
    path = out / "Recovery.lean"
    shutil.copyfile(BASE / "Recovery.lean", path)
    axioms = lean_audit(path, out / "lean-audit.log", out / "Recovery.olean")
    env = dict(os.environ)
    env["LEAN_PATH"] = str(out)
    data = "\n".join(text.encode().hex() for text in inputs) + "\n"
    result = execute([TOOLS["lean"]["path"], "--run", BASE / "Export.lean"], out / "lean-export.log", data, env=env)
    if result.returncode or result.stderr or len(result.stdout.splitlines()) != len(inputs):
        raise ValueError("Lean export diagnostics/count")
    for raw, line in zip(inputs, result.stdout.splitlines()):
        filtered = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n").replace("\0", "\ufffd")
        endpoint, _ = oracle.remnants(filtered, 0)
        spec = filtered[endpoint:].encode().hex()
        trimmed = filtered.lstrip(" \t\n")
        if trimmed.startswith(")"):
            handoff = trimmed[1:].encode().hex()
        else:
            endpoint, _ = oracle.remnants(trimmed, 0)
            handoff = trimmed[endpoint:].encode().hex()
        if line.split(" ") != [spec, spec, handoff, handoff]:
            raise ValueError("Lean/reference scanner disagreement")
    return axioms


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("ambiguous mutation")
    return text.replace(old, new)


def controls(before, candidate, out, deps, data, expected, manifest):
    records = []
    bad_start = candidate.index("    fn consume_bad_url")
    bad_finish = candidate.index("\n}\n", bad_start)
    helper = candidate[bad_start:bad_finish]
    skip_line = next(line for line in helper.splitlines() if "Skip an escaped" in line)
    mutations = {
        "premature-handoff": before,
        "skip-escaped-close": candidate[:bad_start] + replace_once(helper, "Some(b')') | Some(b'\\\\')", "Some(b'\\\\')") + candidate[bad_finish:],
        "skip-escaped-backslash": candidate[:bad_start] + replace_once(helper, "Some(b')') | Some(b'\\\\')", "Some(b')')") + candidate[bad_finish:],
        "newline-as-data-escape": candidate[:bad_start] + replace_once(helper, skip_line, skip_line + "\n                    } else if parser.next_byte() == Some(b'\\n') {\n                        parser.consume_char();") + candidate[bad_finish:],
        "bad-url-payload": replace_once(candidate, "let contents = parser.slice_from(start_pos).into();", 'let contents = "".into();'),
        "unicode-column-bookkeeping": candidate[:bad_start] + replace_once(helper, "parser.consume_known_byte(b);", "parser.consume_known_byte(b);\n                    if b & 0xC0 == 0x80 {\n                        parser.state.current_line_start_position = parser.state.current_line_start_position.wrapping_sub(1);\n                    }") + candidate[bad_finish:],
    }
    for name, source in mutations.items():
        actual = native(source, "mutant-" + name, out, deps, data)
        count = sum(a != e for a, e in zip(actual, expected))
        if count == 0:
            raise ValueError("native mutation survived: " + name)
        records.append({"name": name, "compile_exit": 0, "run_exit": 0, "mismatches": count})
    lean = (BASE / "Recovery.lean").read_text()
    lean_mutations = {
        "hex-count": ("skipWhitespace (skipHex 5 cs)", "skipWhitespace (skipHex 4 cs)"),
        "hex-whitespace": ("skipWhitespace (skipHex 5 cs)", "skipHex 5 cs"),
        "newline-classification": ("else if c = '\\n' then .newline", "else if c = '\\n' then .other"),
        "wrong-terminator": ("| c :: cs => if classify c = .close then cs", "| c :: cs => if classify c = .other then cs"),
        "null-normalization": ("| '\\x00' :: cs => '�' :: normalize cs", "| '\\x00' :: cs => '\\x00' :: normalize cs"),
        "handoff": ("else optimized (c :: rest)", "else optimized rest"),
    }
    lean_rejections = []
    for name, (old, new) in lean_mutations.items():
        path = out / ("lean-mutant-" + name + ".lean")
        path.write_text(replace_once(lean, old, new))
        result = execute([TOOLS["lean"]["path"], path], path.with_suffix(".log"))
        if result.returncode == 0 or "error" not in result.stdout:
            raise ValueError("Lean mutation survived: " + name)
        lean_rejections.append(name)
    lean_guards = {"missing-audit": lean.replace("#print axioms raw_suffix_transfer\n", ""),
                   "extra-output": lean + "\n#check Nat\n", "stderr": lean + '\n#eval IO.eprintln "diagnostic"\n',
                   "sorry": lean.replace(":= by decide", ":= by sorry", 1), "axiom": lean + "\naxiom forged : False\n",
                   "syntax": lean + "\ninvalid Lean declaration\n"}
    diagnostics = []
    for name, source in lean_guards.items():
        path = out / ("lean-guard-" + name + ".lean")
        path.write_text(source)
        try:
            lean_audit(path, path.with_suffix(".log"))
        except ValueError:
            diagnostics.append("lean-" + name)
        else:
            raise ValueError("Lean diagnostic accepted")
    wrapper = (BASE / "capsule-prefix.rs").read_text()
    native_guards = {"compile-error": wrapper + "\ncompile_error!(\"guard\");\n",
                     "warning": wrapper + "\n#[must_use]\nfn unused_guard() -> u8 { 0 }\nfn bad_guard() { unused_guard(); }\n",
                     "stderr": wrapper.replace("fn main() {", 'fn main() { eprintln!("guard");'),
                     "extra-output": wrapper.replace("fn main() {", 'fn main() { println!("guard");')}
    for name, source in native_guards.items():
        try:
            native(candidate, "native-guard-" + name, out, deps, data, wrapper=source)
        except ValueError:
            diagnostics.append("native-" + name)
        else:
            raise ValueError("native diagnostic accepted")
    identity_checks = []
    temporary = out / "altered-source"
    for name, expected_hash in manifest.items():
        temporary.write_bytes((BASE / name).read_bytes() + b"\nidentity guard\n")
        try:
            identity(temporary, expected_hash)
        except ValueError:
            identity_checks.append(name)
        else:
            raise ValueError("identity mutation accepted")
    return records, lean_rejections, diagnostics, identity_checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest = authenticate()
    before, candidate = preservation()
    cases = fixtures.fixtures()
    expected = [oracle.first_url(case["input"]) for case in cases]
    data = "\n".join(case["input"].encode().hex() for case in cases) + "\n"
    (out / "fixtures.json").write_text(json.dumps(cases, ensure_ascii=True, indent=2) + "\n")
    (out / "expected.json").write_text(json.dumps(expected, ensure_ascii=True, indent=2) + "\n")
    models = {case["input"] for case in cases}
    for case in cases:
        text = case["input"]
        index = next((i for i in range(4, len(text)) if text[i] in " \t\r\n\f"), None)
        if index is not None:
            models.add(text[index:])
    models.update(["", "\\", ")", "\\\n)", "\\29 ", "\r\n\0é😀)"])
    axioms = lean_export(out, sorted(models))
    deps = dependencies(out)
    original_records = {}
    for fast in [False, True]:
        label = "fast" if fast else "fallback"
        actual = native(candidate, "candidate-" + label, out, deps, data, fast=fast)
        if actual != expected:
            raise ValueError("candidate native/reference mismatch")
        original_records[label] = native(before, "original-" + label, out, deps, data, fast=fast)
    if original_records["fast"] != original_records["fallback"]:
        raise ValueError("original macro feature disagreement")
    old_mismatches = [{"index": i, "family": cases[i]["family"], "changed_fields": [key for key in expected[i] if value[key] != expected[i][key]]}
                      for i, value in enumerate(original_records["fast"]) if value != expected[i]]
    if not old_mismatches:
        raise ValueError("old source lacks counterexamples")
    (out / "original-mismatches.json").write_text(json.dumps(old_mismatches, indent=2) + "\n")
    native_mutations, lean_mutations, diagnostics, identity_checks = controls(before, candidate, out, deps, data, expected, manifest)
    authenticate()
    receipt = {"scope": "Lean scalar suffix theorem plus finite exact-module Rust replay; not universal Rust correctness",
               "source_manifest_sha256": digest(BASE / "SOURCE-v1.json"), "axioms": axioms,
               "native_fixtures": len(cases), "model_fixtures": len(models),
               "candidate_macro_modes": ["fallback", "fast_match_byte"], "candidate_mismatches": 0,
               "original_mismatches": len(old_mismatches), "fixtures_sha256": digest(out / "fixtures.json"),
               "expected_sha256": digest(out / "expected.json"), "original_mismatches_sha256": digest(out / "original-mismatches.json"),
               "native_mutations": native_mutations, "lean_mutations": lean_mutations,
               "diagnostic_guards": diagnostics, "identity_guard_count": len(identity_checks),
               "source_preservation": "whole original/candidate modules and exact two-line change; vendor checksum-only change", "stable_source_pins": True}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(out / "receipt.json"), "sha256": digest(out / "receipt.json")}, indent=2))


if __name__ == "__main__":
    main()
