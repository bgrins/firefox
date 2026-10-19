import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time

from corpus import corpus, case_for
from generate_native import generate
from invalid_inputs import run_invalid
from lean_cases import emit
from lean_mutations import emit_mutations
from mutations import MUTATIONS
from native_oracle import encode, oracle
from negative_replay import replay_negative
from arithmetic_replay import replay_arithmetic
from negative_review import review as review_negative_evidence
from numeric_domain import inspect as inspect_numeric_domain
from source_closure import retain
from tamper import run_tamper_controls
from unicode_oracle import UnicodeOracle


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    out = Path(args.output).resolve()
    out.mkdir(parents=True)
    tools = json.loads((root / "TOOLCHAIN.json").read_text())
    for path, expected in [(tools["lean"], tools["lean_sha256"]), (tools["compiler"], tools["compiler_sha256"]), (str(Path(tools["sdk"]) / "SDKSettings.json"), tools["sdk_settings_sha256"])]:
        assert digest(Path(path).read_bytes()) == expected, path
    for row in json.loads((root / "SOURCE-INPUTS.json").read_text()):
        assert digest((root / row["path"]).read_bytes()) == row["sha256"]
    for row in json.loads((root / "ADDITIONAL-SOURCE-INPUTS.json").read_text()):
        assert digest((root / "sources" / row["path"]).read_bytes()) == row["sha256"]
    numeric_types=json.loads((root/"NUMERIC-TYPES.json").read_text())
    for row in numeric_types["inputs"]:
        assert digest((root/row["path"]).read_bytes())==row["sha256"]
    assert "typedef double gfxFloat;" in (root/"numeric-types/gfx/thebes/gfxTypes.h").read_text()
    assert "typedef float Float;" in (root/"numeric-types/gfx/2d/Types.h").read_text()
    assert "using nscoord = int32_t;" in (root/"numeric-types/gfx/src/nsCoord.h").read_text()
    negative_pins=json.loads((root/"NEGATIVE-NATIVE-PINS.json").read_text())
    for key in ["original","candidate"]:
        row=negative_pins[key]
        assert digest((root/row["path"]).read_bytes())==row["sha256"]
    before=(root/negative_pins["original"]["path"]).read_text()
    after=(root/negative_pins["candidate"]["path"]).read_text()
    old="  result.mPartAdvance = partClusterIndex * (ligatureWidth / totalClusterCount);"
    new="  const int64_t advancePerCluster = int64_t(ligatureWidth) / totalClusterCount;\n  result.mPartAdvance = partClusterIndex * advancePerCluster;"
    assert before.count(old)==1
    expected=before.replace(old,new).replace("partClusterCount * (ligatureWidth / totalClusterCount)","partClusterCount * advancePerCluster").replace("totalClusterCount * (ligatureWidth / totalClusterCount)","totalClusterCount * advancePerCluster")
    assert expected==after
    v1 = json.loads((root/"V1-BASE.json").read_text())
    permitted_changes = {"BRIDGE.md", "README.md", "REPORT.md", "RESUME.md", "check.py", "generate_native.py", "lean_cases.py", "native_main.inc", "native_oracle.py", "native_support.inc", "replay.py"}
    preserved = []
    changed = []
    for row in v1["files"]:
        actual = digest((root/row["path"]).read_bytes())
        if row["path"] in permitted_changes:
            changed.append({"path": row["path"], "before": row["sha256"], "after": actual})
        else:
            assert actual == row["sha256"], row["path"]
            preserved.append(row["path"])
    v1_extraction = json.loads((root/"evidence/V1-CANDIDATE-EXTRACTION.json").read_text())
    assert len(v1_extraction) == 55
    (out/"V1-DELTA.json").write_text(json.dumps({"preserved_inputs":preserved,"changed_inputs":changed},indent=2)+"\n")
    compiled = []

    def compile(name, variant="candidate", mutant=None, signed=False, arithmetic_mutant=None):
        cpp, binary = out / (name + ".cpp"), out / name
        extraction = generate(root, cpp, variant, mutant, signed=signed, arithmetic_mutant=arithmetic_mutant)
        (out / (name + ".extraction.json")).write_text(json.dumps(extraction, indent=2) + "\n")
        if name == "candidate":
            for old, current in zip(v1_extraction, extraction[:55]):
                assert all(current[key] == value for key,value in old.items())
            assert len(extraction) == 56 and extraction[-1]["kind"] == "arithmetic-slice"
        result = subprocess.run([tools["compiler"], "-std=c++20", "-O1", "-isysroot", tools["sdk"], str(cpp), "-o", str(binary)], capture_output=True, text=True)
        (out / (name + ".compile.log")).write_text(result.stdout + result.stderr)
        assert result.returncode == 0, name
        compiled.append({"name": name, "variant": variant, "mutant": mutant, "signed_arithmetic": signed, "arithmetic_mutant": arithmetic_mutant, "exit": 0, "source_sha256": digest(cpp.read_bytes()), "extraction_records": len(extraction)})
        return binary

    unicode = UnicodeOracle(root)
    normalization = unicode.validate_normalization(root)
    cases = corpus()
    domains=[inspect_numeric_domain(case,False) for case in cases]
    assert all(row["exact_operation_domain"] for row in domains)
    (out/"NUMERIC-DOMAIN.json").write_text(json.dumps(domains,indent=2)+"\n")
    data = "".join(map(encode, cases))
    expected = [oracle(case, unicode) for case in cases]
    (out / "CORPUS.json").write_text(json.dumps(cases, separators=(",", ":")) + "\n")
    (out / "EXPECTED.json").write_text(json.dumps(expected, separators=(",", ":")) + "\n")
    binary = compile("candidate")
    raw = subprocess.run([str(binary), "unicode"], capture_output=True, check=True).stdout
    names = ["Cn", "Lu", "Ll", "Lt", "Lm", "Lo", "Mn", "Me", "Mc", "Nd", "Nl", "No", "Zs", "Zl", "Zp", "Cc", "Cf", "Co", "Cs", "Pd", "Ps", "Pe", "Pc", "Po", "Sm", "Sc", "Sk", "So", "Pi", "Pf"]
    hb_names = ["Cc", "Cf", "Cn", "Co", "Cs", "Ll", "Lm", "Lo", "Lt", "Lu", "Mc", "Me", "Mn", "Nd", "Nl", "No", "Pc", "Pd", "Pe", "Pf", "Pi", "Po", "Ps", "Sc", "Sk", "Sm", "So", "Zl", "Zp", "Zs"]
    coarse = {"M": 1, "N": 2, "Z": 3, "C": 4, "L": 5, "P": 6, "S": 7}
    assert len(raw) == 4 * 0x110000
    for cp in range(0x110000):
        category = unicode.categories[cp]
        assert names[raw[4 * cp]] == category, cp
        assert hb_names[raw[4 * cp + 1]] == category, cp
        assert raw[4 * cp + 2] == coarse[category[0]], cp
        assert bool(raw[4 * cp + 3]) == unicode.eligible(cp), cp
        assert (category == "Co") == (0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD or 0x100000 <= cp <= 0x10FFFD)
    unicode_receipt = {"codepoints": 0x110000, "scalars": 0x110000 - 2048, "surrogate_controls": 2048, "normalization_rows": normalization, "category_counts": dict(collections.Counter(unicode.categories)), "native_output_sha256": digest(raw), "base_exceptions": sorted(unicode.base_exceptions), "derived_punctuation_exceptions": [cp for cp in range(0x110000) if unicode.categories[cp][0] == "P" and unicode.eligible(cp)]}
    (out / "UNICODE.json").write_text(json.dumps(unicode_receipt, indent=2) + "\n")
    raw = subprocess.run([str(binary), "units"], capture_output=True, check=True).stdout
    assert len(raw) == (256 + 65536 + 0x100000) * 12
    rows = iter(struct.iter_unpack("<III", raw))
    for domain, count in enumerate([256, 65536, 0x100000]):
        for cp in range(count):
            eligible = unicode.eligible(cp + 65536 if domain == 2 else cp)
            first = 0xE07B01C8 if eligible else 0x60410001
            second = (0x870000 | (0 if eligible else 0x400000)) if domain == 2 else 0
            assert next(rows) == (first, second, 1), (domain, cp)
    (out / "LOOPS.json").write_text(json.dumps({"latin1": 256, "units": 65536, "pairs": 0x100000, "rows": 256 + 65536 + 0x100000, "native_output_sha256": digest(raw)}, indent=2) + "\n")

    def run(name, executable, wanted):
        result = subprocess.run([str(executable)], input=data, capture_output=True, text=True)
        (out / (name + ".stdout.jsonl")).write_text(result.stdout)
        (out / (name + ".stderr.txt")).write_text(result.stderr)
        assert result.returncode == 0, name
        actual = [json.loads(line) for line in result.stdout.splitlines()]
        assert len(actual) == len(cases)
        differences = []
        for i, (observed, reference) in enumerate(zip(actual, wanted)):
            keys = [k for k in ["before", "after", "draws", "trace", "draw_units"] if observed[k] != reference[k]]
            if keys:
                differences.append({"case": i, "keys": keys})
        return actual, differences

    _, differences = run("candidate", binary, expected)
    assert not differences
    old = compile("original", "original")
    _, differences = run("original", old, [oracle(case, unicode, True) for case in cases])
    assert not differences
    negative_cases, negative_receipts = replay_negative(root,out,unicode,compile)
    arithmetic_receipts, arithmetic_mutants = replay_arithmetic(out,compile)
    invalid = run_invalid(binary, out / "INVALID.json")
    retained = retain(root, out / "source-callers")
    mutants = []
    for name in MUTATIONS:
        actual, differences = run(name, compile(name, mutant=name), expected)
        assert differences and any(any(key != "trace" for key in d["keys"]) for d in differences), name
        first = next(d["case"] for d in differences if any(key != "trace" for key in d["keys"]))
        mutants.append({"name": name, "compile_exit": 0, "run_exit": 0, "rows": len(cases), "differences": differences, "kernel_witness": "Emphasis.Witness." + name, "complete_dispatch_kernel_witness": "Emphasis.DispatchWitness."+name, "witness": {"input": cases[first], "actual": actual[first], "expected": expected[first]}})
    emit_mutations(mutants,unicode,out/"DispatchMutationWitnesses.lean")
    (out / "MUTATIONS.json").write_text(json.dumps(mutants, indent=2) + "\n")
    (out / "COMPILED.json").write_text(json.dumps(compiled, indent=2) + "\n")
    environment = dict(os.environ)
    environment["LEAN_PATH"] = str(out)
    declarations = []
    for name, namespace in [("Emphasis", "Emphasis"), ("RawWords", "Emphasis.Raw"), ("RunGeometry", "Emphasis.Run"), ("BufferPartition", "Emphasis.Partition"), ("Dispatch", "Emphasis.Dispatch"), ("RunSelection", "Emphasis.Selection"), ("LigatureData", "Emphasis.Ligature"), ("ShrinkDispatch", "Emphasis.Shrinking"), ("IdentityDispatch", "Emphasis.Identity"), ("RunDispatch", "Emphasis.Ordinary"), ("RawBridge", "Emphasis.RawBridge"), ("SignedLigature", "Emphasis.SignedLigature"), ("SignedMutationWitnesses", "Emphasis.SignedWitness"), ("NativeDomain", "Emphasis.NativeDomain"), ("TextInput", "Emphasis.TextInput"), ("MutationWitnesses", "Emphasis.Witness")]:
        source = (root / (name + ".lean")).read_text()
        assert not re.search(r"\b(sorry|axiom|admit|native_decide)\b", source), name
        result = subprocess.run([tools["lean"], "--root", str(root), "-o", str(out / (name + ".olean")), str(root / (name + ".lean"))], capture_output=True, text=True, env=environment)
        (out / (name + ".log")).write_text(result.stdout + result.stderr)
        assert result.returncode == 0 and not result.stdout and not result.stderr, name
        declarations += [namespace + "." + theorem for theorem in re.findall(r"^theorem (\w+)", source, re.M)]
    finite = out / "Finite.lean"
    emit(cases, expected, unicode, finite)
    result = subprocess.run([tools["lean"], "--root", str(out), "-o", str(out / "Finite.olean"), str(finite)], capture_output=True, text=True, env=environment)
    (out / "Finite.log").write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and not result.stdout and not result.stderr
    negative_finite=out/"NegativeFinite.lean"
    result=subprocess.run([tools["lean"],"--root",str(out),"-o",str(out/"NegativeFinite.olean"),str(negative_finite)],capture_output=True,text=True,env=environment)
    (out/"NegativeFinite.log").write_text(result.stdout+result.stderr)
    assert result.returncode==0 and not result.stdout and not result.stderr
    dispatch_witnesses=out/"DispatchMutationWitnesses.lean"
    result=subprocess.run([tools["lean"],"--root",str(out),"-o",str(out/"DispatchMutationWitnesses.olean"),str(dispatch_witnesses)],capture_output=True,text=True,env=environment)
    (out/"DispatchMutationWitnesses.log").write_text(result.stdout+result.stderr)
    assert result.returncode==0 and not result.stdout and not result.stderr
    audit = out / "AxiomAudit.lean"
    all_declarations = declarations + [f"Emphasis.Finite.{kind}{i}" for i in range(len(cases)) for kind in ["flags", "shape", "geometry", "dispatch", "rawSetup", "rawBridge", "inputValid"]] + [f"Emphasis.NegativeFinite.{kind}{i}" for i in range(len(negative_cases)) for kind in ["flags","shape","dispatch","rawSetup","rawBridge","inputValid"]]
    all_declarations += ["Emphasis.DispatchWitness."+name for name in MUTATIONS]
    audit.write_text("import MutationWitnesses\nimport BufferPartition\nimport Finite\nimport NegativeFinite\nimport NativeDomain\nimport TextInput\nimport SignedLigature\nimport SignedMutationWitnesses\nimport DispatchMutationWitnesses\n" + "\n".join("#print axioms " + name for name in all_declarations) + "\n")
    result = subprocess.run([tools["lean"], "--root", str(out), str(audit)], capture_output=True, text=True, env=environment)
    (out / "AXIOMS.txt").write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and "sorryAx" not in result.stdout
    assert all(name in result.stdout for name in all_declarations)
    axiom_sets = re.findall(r"depends on axioms: \[([^\]]*)\]", result.stdout)
    assert all(set(x.strip() for x in group.split(",") if x.strip()) <= {"propext", "Classical.choice", "Quot.sound"} for group in axiom_sets)
    tamper = run_tamper_controls(root, out / "tamper")
    costs = []
    for length in [10, 100, 1000, 10000]:
        c = case_for([0xE000] * length, 1)
        c.update(glyphs=[[0x80010061, []] for _ in range(length)], range=[0, length], runs=[0], spacing=[[0, 0] for _ in range(length)], provider=False, direction=1, vertical=False)
        start = time.monotonic()
        result = subprocess.run([str(binary)], input=encode(c), text=True, capture_output=True, check=True)
        seconds = time.monotonic() - start
        observed = json.loads(result.stdout)
        wanted = oracle(c, unicode)
        assert all(observed[k] == wanted[k] for k in ["before", "after", "draws", "trace", "draw_units"])
        costs.append({"units": length, "draws": len(observed["draws"]), "seconds_including_process_and_serialization": seconds, "output_bytes": len(result.stdout.encode())})
    (out / "COSTS.json").write_text(json.dumps(costs, indent=2) + "\n")
    negative_review = review_negative_evidence(root,out)
    receipt = {"status": "PASS", "unicode_codepoints": 0x110000, "normalization_rows": normalization, "loop_rows": 256 + 65536 + 0x100000, "ordinary_cases_per_variant": len(cases), "native_mutants": len(mutants), "compiled_variants": len(compiled), "source_only_caller_definitions": len(retained), "lean_named_theorems": len(declarations), "lean_finite_theorems": 7 * len(cases) + 6 * len(negative_cases), "lean_dispatch_mutation_theorems": len(MUTATIONS), "lean_axiom_audited_theorems": len(all_declarations), "negative_cases_per_variant": len(negative_cases), "negative_variants": len(negative_receipts), "arithmetic_variants": len(arithmetic_receipts), "arithmetic_mutants": len(arithmetic_mutants), "tamper_controls": len(tamper), "invalid_diagnostics": len(invalid), "cost_rows": len(costs), "negative_review_source_only_definitions": len(negative_review["source_only_closure"])}
    (out / "RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
