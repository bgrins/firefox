from pathlib import Path
import difflib, hashlib, json, re, subprocess
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
LIB = ROOT / "artifacts/css-spec-lean"
ORIGIN = ROOT / "artifacts/css-domstring-streaming-20261110-v1"
REV = "0127c4f42c620cdaba4f9b92cca93ca95df2d913"
MAPPING = {
    "PairStream": "CssStreamingPair",
    "PairLaws": "CssStreamingPairLaws",
    "Adapters": "CssStreamingAdapters",
    "AdapterLaws": "CssStreamingAdapterLaws",
    "Pipeline": "CssStreamingPipeline",
    "PipelineLaws": "CssStreamingPipelineLaws",
    "Cases": "CssStreamingExamples",
}
OUT = P / "candidate"
OUT.mkdir(exist_ok=True)
base, candidate = {}, {}
def old(name):
    if name not in base:
        base[name] = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", REV + ":" + name], cwd=LIB).decode()
    return base[name]
def put(name, text):
    candidate[name] = text
names = []
for source, module in MAPPING.items():
    text = (ORIGIN / (source + ".lean")).read_text()
    for a, b in MAPPING.items():
        text = re.sub(r"^import " + a + r"$", "import CssSemantics." + b, text, flags=re.M)
    if source == "Cases":
        text = text.replace("CssStreaming.Cases", "CssSemantics.StreamingExamples")
        text = text.replace("namespace CssSemantics.StreamingExamples\n", "namespace CssSemantics.StreamingExamples\n\nopen Streaming\n")
        text = re.sub(r'  \("([^"\n]+)",', lambda m: '  ("streaming ' + m[1] + '",', text)
        text = text.replace("end CssSemantics.StreamingExamples", "theorem checks_pass : checks.all Prod.snd = true := by decide +kernel\n\nend CssSemantics.StreamingExamples")
        namespace = "CssSemantics.StreamingExamples"
    else:
        text = text.replace("namespace CssStreaming", "namespace CssSemantics.Streaming").replace("end CssStreaming", "end CssSemantics.Streaming")
        namespace = "CssSemantics.Streaming"
    names += [namespace + "." + n for n in re.findall(r"^theorem (\S+)", text, re.M)]
    put("CssSemantics/" + module + ".lean", text)
put("CssSemantics.lean", old("CssSemantics.lean") + "\n" + "".join("import CssSemantics." + m + "\n" for m in MAPPING.values()))
put("tests/Audit.lean", old("tests/Audit.lean") + "\n" + "".join("#print axioms " + n + "\n" for n in names))
put("tests/RunExamples.lean", old("tests/RunExamples.lean") + '\n  for (name, accepted) in StreamingExamples.checks do\n    IO.println s!"PASS {name}: {accepted}"\n')
expected = ["streaming " + n for n in json.loads((ORIGIN / "EXPECTED.json").read_text())]
text = old("check.py")
needle = ']\n\n\ndef check_type_rejection'
assert text.count(needle) == 1
text = text.replace(needle, ''.join('    (' + json.dumps(n) + ', True),\n' for n in expected) + needle)
put("check.py", text)
feature = {
    "id": "finite-domstring-streaming-refinement",
    "status": "checked_fragment",
    "modules": [m + ".lean" for m in MAPPING.values()],
    "specifications": ["webidl-domstring-retrieved20261110", "ecma-domstring-retrieved20261110", "cssom-domstring-retrieved20261110", "syntax3-codepoint-ed-20261110", "infra-codepoint-retrieved20261110"],
    "theorems": names,
    "limits": [
        "Implementation-chosen adjacent-pair carry transducer, proved equivalent to the reviewed whole-input DOMString and CSS preprocessing relations for arbitrary finite partitions, including empty chunks. This is a refinement of existing input coverage, not another CSS specification feature.",
        "The generic Machine.unheld obligation excludes a future pair for immediately emitted input. UTF-16 holds only leading surrogates and CSS holds only CR; composed EOF feeds the first carry through the second stage before flushing the second carry.",
        "Already-acquired Fin 0x10000 code units. Natural-number helpers validate all chunks before streaming; out-of-range units are rejected, direct Fin numerals can wrap, and ECMAScript's string-length bound is not enforced.",
        "Manual mapping to the pinned whole-input contract, not mechanical prose derivation. CSSOMString choice and successful coercion remain caller premises; no CSSOM guards, exceptions, side effects, byte decoding, encodings, BOM policy, re-encoding, tokenizer or Firefox refinement is proved.",
        "Finite-list incremental semantics only: no infinite-stream productivity, allocation, stack, performance or native memory-safety guarantee. Empty chunks preserve carries; complete adapters flush EOF once.",
        "27 transferred laws and one kernel-checked aggregate theorem for 32 ordered observations. Scoped clean dependency closure and global static registration only; historical whole-library and browser gates are not refreshed."
    ]
}
coverage = json.loads(old("coverage.json"))
coverage["features"].append(feature)
# Locate the existing dated integration receipt without depending on its container name.
def add_receipt(value):
    if isinstance(value, dict):
        for child in value.values():
            if add_receipt(child): return True
    elif isinstance(value, list):
        if any(isinstance(x, dict) and x.get("id") == "finite-domstring-codepoint-boundary" and "validation_scope" in x for x in value):
            value.append({"id": feature["id"], "reviewed_on": "2026-11-10", "contract": "research/domstring-streaming.md", "validation_scope": "28 new declarations/32 observations; clean affected dependency closure with existing input-layer controls and global static registrations; no full-library/browser gate refresh"})
            return True
        for child in value:
            if add_receipt(child): return True
    return False
assert add_receipt(coverage)
put("coverage.json", json.dumps(coverage, indent=2, ensure_ascii=False) + "\n")
text = old("README.md")
anchor = "## Resolved baseline groups\n"
assert text.count(anchor) == 1
put("README.md", text.replace(anchor, "## Chunked DOMString input\n\n`Streaming.pipeline` preserves surrogate and CR carries across finite chunks,\nincluding empty chunks, and is proved equivalent to whole-input DOMString\ndecoding and CSS preprocessing. The [streaming contract](research/domstring-streaming.md)\nseparates this algorithmic refinement from prose translation, byte decoding,\nCSSOM behavior and native performance claims.\n\n" + anchor))
text = old("research/coverage-map.md")
anchor = "## What the evidence establishes\n"
assert text.count(anchor) == 1
text = text.replace(anchor, "## Finite streaming refinement (2026-11-10)\n\nThe [chunked input refinement](domstring-streaming.md) preserves UTF-16 and CR\ncarries and proves composition with the existing whole-input relations. It adds\n28 audited declarations and 32 ordered observations; it does not count another\nCSS feature or refresh historical whole-library/browser evidence.\n\n" + anchor)
anchor = "| DOMString code-unit input |"
assert text.count(anchor) == 1
text = text.replace(anchor, "| Chunked DOMString input | Arbitrary finite partitions, both pending carries, explicit EOF and exact whole-input correspondence | No new native/browser evidence | CSSOM conversion, byte decoding, infinite streams, allocation and stack/performance bounds |\n" + anchor)
put("research/coverage-map.md", text)
put("research/domstring-streaming.md", (P / "CONTRACT.md").read_text())
patch = []
for name, text in candidate.items():
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    patch += difflib.unified_diff(base.get(name, "").splitlines(True), text.splitlines(True), fromfile="a/" + name if name in base else "/dev/null", tofile="b/" + name)
(P / "library.patch").write_text(''.join(patch))
hash_text = lambda text: hashlib.sha256(text.encode()).hexdigest()
record = {"base_revision": REV, "origin_firefox_commit": "d34a26d38d78", "origin_capsule": str(ORIGIN.relative_to(ROOT)), "module_mapping": MAPPING, "new_theorems": names, "new_examples": expected, "files": {name: {"base_sha256": hash_text(base[name]) if name in base else None, "candidate_sha256": hash_text(text)} for name, text in candidate.items()}, "patch_sha256": hash_text(''.join(patch))}
(P / "SOURCES.json").write_text(json.dumps(record, indent=2) + "\n")
print(f"Prepared {len(candidate)} files, {len(names)} declarations, {len(expected)} observations")
