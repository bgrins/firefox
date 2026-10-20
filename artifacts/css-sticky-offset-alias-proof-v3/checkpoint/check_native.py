import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)

def extract(text):
    start = text.index("static nscoord ComputeStickySideOffset(")
    opening = text.index("{", start)
    depth = 0
    for index in range(opening, len(text)):
        depth += (text[index] == "{") - (text[index] == "}")
        if depth == 0:
            return text[start:index + 1]
    raise RuntimeError("Unclosed function")

old = extract((HERE / "source/before.cpp").read_text())
new = extract((HERE / "source/candidate.cpp").read_text())
old_return = "return nsLayoutUtils::ComputeCBDependentValue(aPercentBasis,\n                                                side->AsLengthPercentage());"
new_return = "return std::min(NS_AUTOOFFSET - 1,\n                  nsLayoutUtils::ComputeCBDependentValue(\n                      aPercentBasis, side->AsLengthPercentage()));"
if old.count(old_return) != 1 or new.count(new_return) != 1:
    raise RuntimeError("Unexpected source")
expected = old.replace(old_return, "// Reserve NS_AUTOOFFSET for actual auto insets.\n  " + new_return)
if expected != new:
    raise RuntimeError("Source differs outside the accepted producer change")

coord = (HERE / "source/nsCoord.h").read_text()
constants = (HERE / "source/LayoutConstants.h").read_text()
for spelling in ["using nscoord = int32_t;", "inline constexpr nscoord nscoord_MAX = (1 << 30) - 1;", "inline constexpr nscoord nscoord_MIN = -nscoord_MAX;"]:
    if spelling not in coord:
        raise RuntimeError("Coordinate declaration changed")
if "inline constexpr nscoord NS_AUTOOFFSET = NS_UNCONSTRAINEDSIZE;" not in constants or "inline constexpr nscoord NS_UNCONSTRAINEDSIZE = nscoord_MAX;" not in constants:
    raise RuntimeError("Sentinel declaration changed")

auto = 1073741823
values = [-1073741823, -100, -1, 0, 1, 100, auto - 2, auto - 1, auto]
cases = [{"side": side, "auto": is_auto, "resolved": value, "basis": basis}
         for side, is_auto, value, basis in itertools.product(range(4), [False, True], values, [0, 60, 6000])]
text_input = "".join(f"{c['side']} {int(c['auto'])} {c['resolved']} {c['basis']}\n" for c in cases)

def oracle(case, repaired):
    if case["auto"]:
        return [auto, case["side"], 1, 0, -1]
    value = case["resolved"]
    if repaired and value == auto:
        value -= 1
    return [value, case["side"], 1, 1, case["basis"]]

prefix = r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <utility>
using nscoord = int32_t;
inline constexpr nscoord nscoord_MAX = (1 << 30) - 1;
inline constexpr nscoord NS_AUTOOFFSET = nscoord_MAX;
enum Side { eSideTop, eSideRight, eSideBottom, eSideLeft };
enum class StylePositionProperty { Sticky };
struct AnchorPosOffsetResolutionParams {
  static AnchorPosOffsetResolutionParams UseCBFrameSize(std::pair<void*, StylePositionProperty> input) {
    assert(input.first == nullptr && input.second == StylePositionProperty::Sticky);
    return {};
  }
};
int queriedSide, queries, resolves;
nscoord seenBasis;
struct LengthPercentage { nscoord resolved; };
struct Inset {
  bool automatic;
  LengthPercentage value;
  bool IsAuto() const { return automatic; }
  const LengthPercentage& AsLengthPercentage() const { assert(!automatic); return value; }
};
struct nsStylePosition {
  Inset insets[4];
  const Inset* GetAnchorResolvedInset(Side side, AnchorPosOffsetResolutionParams) const {
    queriedSide = side;
    ++queries;
    return &insets[side];
  }
};
struct nsLayoutUtils {
  static nscoord ComputeCBDependentValue(nscoord basis, const LengthPercentage& value) {
    ++resolves;
    seenBasis = basis;
    return value.resolved;
  }
};
'''
suffix = r'''
int main() {
  int side, automatic;
  nscoord value, basis;
  while (std::cin >> side >> automatic >> value >> basis) {
    assert(side >= 0 && side < 4 && (automatic == 0 || automatic == 1));
    nsStylePosition position;
    for (int i = 0; i < 4; ++i) position.insets[i] = {false, {7 + i}};
    position.insets[side] = {automatic != 0, {value}};
    queriedSide = -1; queries = resolves = 0; seenBasis = -1;
    nscoord result = ComputeStickySideOffset(static_cast<Side>(side), position, basis);
    std::cout << result << ' ' << queriedSide << ' ' << queries << ' ' << resolves << ' ' << seenBasis << '\n';
  }
}
'''
variants = {
    "before": old,
    "candidate": new,
    "auto_reserved_too": new.replace("return NS_AUTOOFFSET;", "return NS_AUTOOFFSET - 1;"),
    "maximum_instead_of_minimum": new.replace("std::min(", "std::max("),
    "reserve_two_units": new.replace("NS_AUTOOFFSET - 1", "NS_AUTOOFFSET - 2"),
    "negative_values_lost": new.replace(new_return, "return std::max(nscoord(0), " + new_return.removeprefix("return ").removesuffix(";") + ");"),
    "wrong_side": new.replace("      aSide, AnchorPosOffsetResolutionParams", "      static_cast<Side>((aSide + 1) % 4), AnchorPosOffsetResolutionParams"),
}
for name, source in variants.items():
    if name not in ["before", "candidate"] and source == new:
        raise RuntimeError("Mutation did not alter source")
compiler = Path(subprocess.check_output(["xcrun", "--find", "clang++"], text=True).strip())
sdk = subprocess.check_output(["xcrun", "--show-sdk-path"], text=True).strip()
version = subprocess.check_output([str(compiler), "--version"], text=True)
compiler_sha = hashlib.sha256(compiler.read_bytes()).hexdigest()
results = {}
with tempfile.TemporaryDirectory(prefix="sticky-offset-native-") as temporary:
    work = Path(temporary)
    for mode, flags in [("debug", ["-O0"]), ("optimized", ["-O2"])]:
        for name, source in variants.items():
            if mode == "debug" and name not in ["before", "candidate"]:
                continue
            identity = mode + "-" + name
            cpp = work / (identity + ".cpp")
            cpp.write_text(prefix + source + suffix)
            executable = work / identity
            command = [str(compiler), "-isysroot", sdk, "-std=c++17", "-fsanitize=undefined", "-fno-sanitize-recover=all", *flags, str(cpp), "-o", str(executable)]
            compile_result = subprocess.run(command, text=True, capture_output=True)
            (args.output / (identity + "-compile.log")).write_text(compile_result.stdout + compile_result.stderr)
            if compile_result.returncode:
                raise RuntimeError("Compilation failure is not a semantic mutant result: " + identity)
            execution = subprocess.run([str(executable)], input=text_input, text=True, capture_output=True)
            (args.output / (identity + ".txt")).write_text(execution.stdout)
            (args.output / (identity + "-stderr.log")).write_text(execution.stderr)
            if execution.returncode or execution.stderr:
                raise RuntimeError("Native execution failed: " + identity)
            rows = [list(map(int, line.split())) for line in execution.stdout.splitlines()]
            if len(rows) != len(cases) or any(len(row) != 5 for row in rows):
                raise RuntimeError("Native result roster mismatch")
            expected_rows = [oracle(case, name != "before") for case in cases]
            differences = [i for i, (row, expected_row) in enumerate(zip(rows, expected_rows)) if row != expected_row]
            if name in ["before", "candidate"] and differences:
                raise RuntimeError("Source/oracle disagreement: " + identity)
            if name not in ["before", "candidate"] and not differences:
                raise RuntimeError("Surviving semantic mutant: " + identity)
            results[identity] = {"command": command, "compile_exit": 0, "execution_exit": 0,
                "cases": len(cases), "differences": differences,
                "source_sha256": hashlib.sha256(cpp.read_bytes()).hexdigest(),
                "stdout_sha256": hashlib.sha256(execution.stdout.encode()).hexdigest()}
if hashlib.sha256(compiler.read_bytes()).hexdigest() != compiler_sha:
    raise RuntimeError("Compiler changed during calibration")
(args.output / "CASES.json").write_text(json.dumps(cases, indent=2) + "\n")
(args.output / "RESULT.json").write_text(json.dumps({
    "status": "SOURCE_CALIBRATION_CHECKPOINT_ONLY",
    "compiler": str(compiler), "compiler_version": version, "compiler_sha256": compiler_sha, "sdk": sdk,
    "variants": results, "temporary_products_removed": True,
    "admissions": ["Anchor resolution and style selection are providers.",
        "Numeric resolution is represented by its already-resolved bounded nscoord result; floating-point/Rust calc evaluation is not proved here.",
        "C++ compiler, standard min/max, facade fidelity and native caller lifetime are trusted.",
        "Downstream geometry and scrolling require their own arithmetic and provider conditions."],
}, indent=2) + "\n")
print(json.dumps({"status": "SOURCE_CALIBRATION_CHECKPOINT_ONLY", "cases_per_variant": len(cases), "variants": len(results)}))
