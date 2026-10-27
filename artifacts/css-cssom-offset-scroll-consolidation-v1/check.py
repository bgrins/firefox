import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function(text, signature):
    start = text.index(signature)
    opening = text.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def check():
    for path, expected in json.loads((ROOT / "REFERENCES.json").read_text()).items():
        assert digest(REPO / path) == expected, path
    source = json.loads((ROOT / "SOURCE.json").read_text())
    original_path = ROOT / "original/dom/base/Element.cpp"
    candidate_path = ROOT / "candidate/dom/base/Element.cpp"
    assert digest(original_path) == source["original"]
    assert digest(candidate_path) == source["candidate"]
    original = original_path.read_text()
    candidate = candidate_path.read_text()
    helper = (ROOT / "conversion.inc").read_text()
    assert candidate.count(helper) == 1
    assert candidate.count("AppUnitsToRoundedCSSPixels(") == 7
    for signature in ["nsSize Element::GetScrollSize()", "nsPoint Element::GetScrollOrigin()", "nsRect Element::GetClientAreaRect()"]:
        assert function(original, signature) == function(candidate, signature)
    reverted = candidate.replace(helper, "", 1)
    for dimension in ["width", "height"]:
        reverted = reverted.replace(
            f"AppUnitsToRoundedCSSPixels(GetScrollSize().{dimension})",
            f"nsPresContext::AppUnitsToIntCSSPixels(GetScrollSize().{dimension})")
    new_offset = """  rect = frame->Style()->EffectiveZoom().Unzoom(rect);
  aRect = CSSIntRect(AppUnitsToRoundedCSSPixels(rect.x),
                     AppUnitsToRoundedCSSPixels(rect.y),
                     AppUnitsToRoundedCSSPixels(rect.Width()),
                     AppUnitsToRoundedCSSPixels(rect.Height()));"""
    old_offset = """  aRect = CSSIntRect::FromAppUnitsRounded(
      frame->Style()->EffectiveZoom().Unzoom(rect));"""
    assert reverted.count(new_offset) == 1
    assert reverted.replace(new_offset, old_offset) == original
    patch = "".join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True), fromfile="a/dom/base/Element.cpp", tofile="b/dom/base/Element.cpp"))
    assert (ROOT / "native.patch").read_text() == patch
    old_conversion = (REPO / "artifacts/css-cssom-integer-rounding-repair-v2/conversion.inc").read_text()
    statements = lambda text: [line.strip() for line in text.splitlines() if line.strip().startswith(("constexpr ", "const ", "return "))]
    assert statements(helper) == statements(old_conversion)
    model = ROOT / "Rounding.lean"
    assert model.read_bytes() == (REPO / "artifacts/css-cssom-integer-rounding-model-v1/Rounding.lean").read_bytes()
    assert len(re.findall(r"^theorem ", model.read_text(), re.M)) == 21
    html = (ROOT / "offset-scroll-integer-precision.html").read_text()
    scripts = re.findall(r"<script(?: [^>]*)?>(.*?)</script>", html, re.S)
    old_html = (REPO / "artifacts/css-cssom-integer-rounding-repair-v2/offset-integer-precision.html").read_text()
    old_scripts = re.findall(r"<script(?: [^>]*)?>(.*?)</script>", old_html, re.S)
    assert scripts[:-1] == old_scripts
    assert "offsetWidth" not in scripts[-1] and "offsetHeight" not in scripts[-1]
    assert "getBoundingClientRect" not in scripts[-1]
    javascript = "\n".join(scripts)
    syntax = subprocess.run(["node", "--check"], input=javascript, text=True, capture_output=True)
    assert syntax.returncode == 0, syntax.stderr
    registration = "const names = []; function test(body, name) { names.push(name); }\n" + javascript + "\nprocess.stdout.write(JSON.stringify(names));\n"
    roster_run = subprocess.run(["node", "-"], input=registration, text=True, capture_output=True)
    assert roster_run.returncode == 0, roster_run.stderr
    names = json.loads(roster_run.stdout)
    expected = [f"{axis}-{base}-{extra}-{sign}" for axis in ["x", "y"] for base in [16, 8388600] for extra in [0, 9] for sign in [-1, 1]]
    expected += [f"size-{axis}-{base}-{extra}" for axis in ["x", "y"] for base in [16, 8388600] for extra in [0, 9]]
    expected += [f"{observer}-{base}-{extra}" for observer in ["scrollWidth", "scrollHeight"] for base in [16, 8388600] for extra in [0, 9]]
    assert names == expected and len(set(names)) == 32
    (ROOT / "ROSTER.json").write_text(json.dumps(names, indent=2) + "\n")
    result = {
        "source_reconstruction": True,
        "unchanged_scroll_size_origin_client_functions": True,
        "helper_statements_identical_to_reviewed_lambda": True,
        "proof_byte_identical": True,
        "existing_theorems_reused": 21,
        "new_theorems": 0,
        "original_24_test_bodies_identical": True,
        "registered_test_names": len(names),
        "new_scroll_cases": 8,
        "javascript_syntax_exit": syntax.returncode,
        "registration_only_exit": roster_run.returncode,
        "test_bodies_executed": False,
        "native_compiled": False,
        "browser_executed": False,
    }
    (ROOT / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    check()
