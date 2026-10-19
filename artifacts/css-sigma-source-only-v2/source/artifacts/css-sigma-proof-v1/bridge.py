import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OBJECT = ROOT / "objdir-full.noindex/config/external/icu/common/ucase.o"
NATIVE = ROOT / "layout/generic/nsTextRunTransformations.cpp"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(source):
    pattern = r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\w+|[^\s]'
    return [t for t in re.findall(pattern, source, re.S) if not t.startswith(("//", "/*"))]


def block(source, marker):
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 0
    for i in range(opening, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    raise ValueError("unterminated source block")


def replace_once(sequence, old, new):
    indexes = [i for i in range(len(sequence) - len(old) + 1) if sequence[i:i + len(old)] == old]
    if len(indexes) != 1:
        raise ValueError(f"source anchor count: {len(indexes)} for {old[:8]}")
    i = indexes[0]
    return sequence[:i] + new + sequence[i + len(old):]


def preserve(before, candidate):
    helper = block(candidate, "static bool IsFinalSigma(")
    candidate = candidate.replace(helper, "", 1)
    candidate = candidate.replace('#include "mozilla/intl/String.h"', "", 1)
    expected = tokens(before)
    expected = replace_once(expected, tokens("uint32_t sigmaIndex = uint32_t(-1);"), [])
    pending = block(before, "if (sigmaIndex != uint32_t(-1))")
    expected = replace_once(expected, tokens(pending), [])
    old_sigma = block(before, "if (ch == GREEK_CAPITAL_LETTER_SIGMA)")
    new_sigma = block(candidate, "if (ch == GREEK_CAPITAL_LETTER_SIGMA)")
    allowed = """if (ch == GREEK_CAPITAL_LETTER_SIGMA) {
      ch = IsFinalSigma(aTextRun ? aTextRun->mString : aString,
                        aTextRun ? aOffsetInTextRun : i, aTextRun)
               ? GREEK_SMALL_LETTER_FINAL_SIGMA : GREEK_SMALL_LETTER_SIGMA;
      prevIsLetter = true;
      break;
    }"""
    if tokens(new_sigma) != tokens(allowed):
        raise ValueError("unexpected sigma callsite or state change")
    expected = replace_once(expected, tokens(old_sigma), tokens(new_sigma))
    assignment = tokens("sigmaIndex = uint32_t(-1);")
    count = 0
    while True:
        matches = [i for i in range(len(expected) - len(assignment) + 1)
                   if expected[i:i + len(assignment)] == assignment]
        if not matches:
            break
        i = matches[0]
        expected[i:i + len(assignment)] = []
        count += 1
    if count != 7:
        raise ValueError(f"unexpected sigma assignment removal count {count}")
    if expected != tokens(candidate):
        raise ValueError("non-sigma native code changed")
    return helper, new_sigma


def compile_bridge(output, helper, callsite, name):
    call = re.search(r"ch\s*=\s*(IsFinalSigma\(.*?);", callsite, re.S)
    if call is None:
        raise ValueError("missing call expression")
    wrapper = ("\nstatic uint32_t bridgeCall(const nsAString& aString, uint32_t i, "
               "const nsTransformedTextRun* aTextRun, uint32_t aOffsetInTextRun) {\n"
               "return " + call[1] + ";\n}\n")
    source = output / (name + ".cpp")
    source.write_text((BASE / "bridge-prefix.cpp").read_text() + "\n" + helper + wrapper +
                      (BASE / "bridge-suffix.cpp").read_text())
    binary = output / name
    command = ["clang++", "-std=c++17", "-O2", "-I", str(ROOT / "objdir-full.noindex/dist/include"),
               "-Wl,-dead_strip", str(source), str(OBJECT), "-o", str(binary)]
    run = subprocess.run(command, capture_output=True)
    (output / (name + "-compile.log")).write_bytes(run.stdout + run.stderr)
    if run.returncode != 0 or run.stdout or run.stderr:
        raise ValueError("bridge compile failed or emitted diagnostics")
    return binary


def native_controls(output, helper, callsite, properties, before, candidate):
    changes = {
        "ignore-backward-mask": ("if (masked) {\n      return false;", "if (false) {\n      return false;"),
        "ignore-forward-mask": ("if (masked) {\n      return true;", "if (false) {\n      return true;"),
        "ignore-high-unit-mask": ("masked |= isMasked(--index);", "--index;"),
        "ignore-low-unit-mask": ("masked |= isMasked(++index);", "++index;"),
        "dont-skip-ignorable": ("mozilla::intl::String::IsCaseIgnorable(ch)", "false"),
        "ascii-only-cased": ("mozilla::intl::String::IsCased(ch)", "(ch == 0x41)"),
        "inverted-successor": ("return !mozilla::intl::String::IsCased(ch);", "return mozilla::intl::String::IsCased(ch);"),
    }
    results = []
    for name, (old, new) in changes.items():
        count = helper.count(old)
        expected_count = 2 if name in {"dont-skip-ignorable", "ascii-only-cased"} else 1
        if count != expected_count:
            raise ValueError(f"ambiguous native mutation {name}")
        binary = compile_bridge(output, helper.replace(old, new), callsite, "mutation-" + name)
        result = subprocess.run([binary, properties], capture_output=True)
        (output / ("mutation-" + name + ".log")).write_bytes(result.stdout + result.stderr)
        if result.returncode != 1 or b"Mismatch" not in result.stderr:
            raise ValueError(f"native mutation was not semantically rejected: {name}")
        results.append({"name": name, "exit": result.returncode})
    guards = {
        "lost-irish-state": ("prevIsLetter = true;", "prevIsLetter = false;"),
        "wrong-context-string": ("aTextRun ? aTextRun->mString : aString", "aString"),
        "wrong-context-offset": ("aTextRun ? aOffsetInTextRun : i", "i"),
        "wrong-sigma-output": ("? GREEK_SMALL_LETTER_FINAL_SIGMA", "? GREEK_SMALL_LETTER_SIGMA"),
        "lost-locale-state": ("bool seenSoftDotted = false;", "bool seenSoftDotted = true;"),
    }
    rejected = []
    for name, (old, new) in guards.items():
        if old not in candidate:
            raise ValueError(f"missing source-control anchor {name}")
        modified = candidate.replace(old, new, 1)
        try:
            preserve(before, modified)
        except ValueError as error:
            rejected.append({"name": name, "reason": str(error)})
        else:
            raise ValueError(f"source preservation accepted {name}")
    return results, rejected


def check(output):
    from check import expected_properties
    before = (BASE / "before-nsTextRunTransformations.cpp").read_text()
    candidate_path = BASE / "native-candidate.cpp"
    candidate = candidate_path.read_text()
    helper, callsite = preserve(before, candidate)
    sources = [OBJECT, candidate_path, BASE / "before-nsTextRunTransformations.cpp",
               BASE / "bridge-prefix.cpp", BASE / "bridge-suffix.cpp", BASE / "bridge.py",
               BASE / "icu-probe.cpp", BASE / "unicode-properties17.txt",
               ROOT / "mfbt/Utf16.h", ROOT / "intl/components/src/String.h",
               ROOT / "intl/icu/source/common/uprops.cpp",
               ROOT / "intl/icu/source/common/ucase.cpp",
               ROOT / "objdir-full.noindex/dist/include/unicode/uchar.h"]
    pins = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    probe = output / "icu-probe"
    command = ["clang++", "-std=c++17", "-O2", "-I", str(ROOT / "objdir-full.noindex/dist/include"),
               "-Wl,-dead_strip", str(BASE / "icu-probe.cpp"), str(OBJECT), "-o", str(probe)]
    compile_run = subprocess.run(command, capture_output=True)
    (output / "icu-compile.log").write_bytes(compile_run.stdout + compile_run.stderr)
    if compile_run.returncode != 0 or compile_run.stdout or compile_run.stderr:
        raise ValueError("ICU probe compile failed or emitted diagnostics")
    property_run = subprocess.run([probe], capture_output=True)
    if property_run.returncode != 0 or property_run.stderr or property_run.stdout != expected_properties():
        raise ValueError("compiled ICU properties differ from Unicode 17")
    properties = output / "properties.bin"
    properties.write_bytes(property_run.stdout)
    binary = compile_bridge(output, helper, callsite, "bridge")
    run = subprocess.run([binary, properties], capture_output=True)
    (output / "bridge.log").write_bytes(run.stdout + run.stderr)
    if run.returncode != 0 or run.stderr:
        raise ValueError("native helper disagrees with scalar reference")
    counts = json.loads(run.stdout)
    mutations, source_controls = native_controls(output, helper, callsite, properties, before, candidate)
    if pins != {str(p.relative_to(ROOT)): sha(p) for p in sources}:
        raise ValueError("input changed during replay")
    return {"scope": "exact C++ helper and call expression; transparent string/style adapters; built ICU case backend; finite UTF16 checks, not full Gecko proof",
            "icu_codepoints": len(property_run.stdout), "checks": counts,
            "preserved_non_sigma_native_tokens": True,
            "native_mutations": mutations, "preservation_controls": source_controls,
            "pins": pins}
