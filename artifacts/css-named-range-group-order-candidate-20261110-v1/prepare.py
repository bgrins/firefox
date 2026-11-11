import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent / "css-named-range-group-order-review-20261110-v1"
NATIVE = "servo/ports/geckolib/glue.rs"
EXISTING = "testing/web-platform/tests/scroll-animations/css/merge-timeline-offset-keyframes.html"
NEW = "testing/web-platform/tests/scroll-animations/css/named-range-group-earliest-order.html"


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def main():
    pinned = json.loads((REVIEW / "SOURCES.json").read_text())
    sources = {name: (REVIEW / "source" / name).read_text() for name in [NATIVE, EXISTING]}
    for name, data in sources.items():
        assert hashlib.sha256(data.encode()).hexdigest() == pinned["files"][name]
        path = HERE / "source" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)
    native = once(sources[NATIVE],
        "    let mut grouped_keyframes_indexes = HashSet::new();\n    for step in animation.steps_with_range_name.iter().rev() {",
        "    let mut grouped_keyframes_indexes = HashSet::new();\n"
        "    let mut keyframe_source_positions = Vec::new();\n"
        "    for (source_position, step) in animation.steps_with_range_name.iter().enumerate().rev() {")
    native = once(native,
        "    // After appending the missing initial and final keyframes, we start to append the Keyframes\n"
        "    // with timeline range names. We create the Keyframes in a temporary array because we need to\n"
        "    // reverse it later.\n",
        "    // Keep range group indices stable until property deduplication is complete.\n")
    native = once(native,
        "        if matched_idx != keyframes_with_range_names.len() {\n"
        "            grouped_keyframes_indexes.insert(matched_idx);\n        }",
        "        if matched_idx != keyframes_with_range_names.len() {\n"
        "            grouped_keyframes_indexes.insert(matched_idx);\n"
        "            keyframe_source_positions[matched_idx] = source_position;\n"
        "        } else {\n            keyframe_source_positions.push(source_position);\n        }")
    native = once(native,
        "    // Reverse the keyframes order because we reversed them in the loop above.\n"
        "    keyframes.extend(&mut keyframes_with_range_names.drain(..).rev());",
        "    // Reorder only after the saved group indices have been consumed.\n"
        "    debug_assert_eq!(\n        keyframes_with_range_names.len(),\n"
        "        keyframe_source_positions.len()\n    );\n"
        "    let mut ordered_keyframes: Vec<_> = keyframes_with_range_names\n"
        "        .drain(..)\n        .zip(keyframe_source_positions)\n        .collect();\n"
        "    ordered_keyframes.sort_unstable_by_key(|(_, position)| *position);\n"
        "    keyframes.extend(ordered_keyframes.into_iter().map(|(keyframe, _)| keyframe));")
    old_frames = '''        {
          offset: { rangeName: "contain", offset: CSS.percent(0) },
          easing: "linear", composite: "auto", opacity: "0.8",
          computedOffset: 1/3
        },
        {
          offset: { rangeName: "entry", offset: CSS.percent(100) },
          easing: "linear", composite: "auto", opacity: "0.5",
          computedOffset : 1/3
        }'''
    new_frames = '''        {
          offset: { rangeName: "entry", offset: CSS.percent(100) },
          easing: "linear", composite: "auto", opacity: "0.5",
          computedOffset : 1/3
        },
        {
          offset: { rangeName: "contain", offset: CSS.percent(0) },
          easing: "linear", composite: "auto", opacity: "0.8",
          computedOffset: 1/3
        }'''
    existing = once(sources[EXISTING], old_frames, new_frames)
    proposal = (REVIEW / "proposal/named-range-group-earliest-order.html").read_text()
    probe = once(proposal, "</style>", '''  @keyframes repeated-groups {
    cover 50% { opacity: .2; animation-timing-function: linear; }
    cover 50% { margin-left: 10px; animation-timing-function: ease-in; }
    cover 50% { padding-left: 20px; animation-timing-function: ease-out; }
    cover 50% { margin-left: 30px; animation-timing-function: ease-in; }
    cover 50% { opacity: .7; animation-timing-function: linear; }
  }
</style>''')
    probe = once(probe, "for (const [name, margin] of [\n  ['unique-groups', '10px'],\n  ['repeated-group', '30px'],",
        "for (const [name, margin, opacity] of [\n  ['unique-groups', '10px', '0.2'],\n"
        "  ['repeated-group', '30px', '0.2'],\n  ['repeated-groups', '30px', '0.7'],")
    probe = once(probe, "assert_equals(frames[0].opacity, '0.2');", "assert_equals(frames[0].opacity, opacity);")
    candidates = {NATIVE: native, EXISTING: existing, NEW: probe}
    for name, data in candidates.items():
        path = HERE / "candidate" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)
    (HERE / "SOURCES.json").write_text(json.dumps({"revision": pinned["revision"],
        "files": {name: pinned["files"][name] for name in sources},
        "prior_probe_sha256": hashlib.sha256(proposal.encode()).hexdigest()}, indent=2) + "\n")
    write_patch()


def write_patch():
    patch = []
    hashes = {}
    for name in [NATIVE, EXISTING, NEW]:
        before = (HERE / "source" / name).read_text() if name != NEW else ""
        after = (HERE / "candidate" / name).read_text()
        patch.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                         fromfile="a/" + name if before else "/dev/null", tofile="b/" + name))
        hashes[name] = hashlib.sha256(after.encode()).hexdigest()
    (HERE / "range-order.patch").write_text("".join(patch))
    (HERE / "CANDIDATE.json").write_text(json.dumps(hashes, indent=2) + "\n")


if __name__ == "__main__":
    main()
