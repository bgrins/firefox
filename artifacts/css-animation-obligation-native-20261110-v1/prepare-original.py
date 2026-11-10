import difflib
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "artifacts/css-root-font-drain-stall-instrumentation-v1"
PATHS = [
    "servo/ports/geckolib/glue.rs",
    "servo/components/style/gecko/traversal.rs",
    "layout/style/ServoStyleSet.cpp",
    "dom/animation/EffectCompositor.cpp",
    "layout/style/RestyleManager.cpp",
    "servo/components/style/gecko/wrapper.rs",
    "servo/components/style/matching.rs",
    "servo/components/style/traversal.rs",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edit(path, before, after):
    source = path.read_text()
    assert source.count(before) == 1, (path, before)
    path.write_text(source.replace(before, after))


def patch(directory, path):
    result = subprocess.run(
        ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(path)],
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def main():
    for stage in ["base", "semantic", "candidate"]:
        assert not (HERE / stage).exists()
    for path in PATHS:
        target = HERE / "base" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, target)
    shutil.copytree(HERE / "base", HERE / "semantic")
    producer = (
        ROOT / "artifacts/css-root-font-producer-local-certified-path-v1/native.patch"
    )
    applied = [patch(HERE / "semantic", producer)]
    style_set = "layout/style/ServoStyleSet.cpp"
    assert (
        sha(HERE / "base" / style_set)
        == "9c44b15945c9eba8d82f16d4980e76cc4ad1d9ffd330bb14cc3a2d131dc4caf5"
    )
    assert (
        sha(ARCHIVE / "base" / style_set)
        == "7036f51285117abf685a9e272bf91f88dd8f1ccd761fc7b3b39b4b1c0152f604"
    )
    shutil.copy2(ARCHIVE / "base" / style_set, HERE / "semantic" / style_set)
    shutil.copytree(HERE / "semantic", HERE / "candidate")
    saved = (ARCHIVE / "native.patch").read_text()
    chunks = re.split(r"(?=^--- a/)", saved, flags=re.M)
    selected = [
        chunk
        for chunk in chunks
        if any(
            chunk.startswith("--- a/" + path + "\n")
            for path in [
                "dom/animation/EffectCompositor.cpp",
                style_set,
                "servo/components/style/traversal.rs",
            ]
        )
    ]
    assert len(selected) == 3
    (HERE / "reused-trace.patch").write_text("".join(selected))
    applied.append(patch(HERE / "candidate", HERE / "reused-trace.patch"))

    root = HERE / "candidate"
    effect = (root / "dom/animation/EffectCompositor.cpp").read_text()
    start = effect.index("#include <unistd.h>")
    end = effect.index('\n#include "EffectCompositor.h"', start)
    helper = effect[start:end].replace(
        "RFDPTraceEffectCompositor", "RFDPTraceRestyleManager"
    )
    manager = root / "layout/style/RestyleManager.cpp"
    text = manager.read_text()
    boundary = text.index("*/") + 2
    manager.write_text(text[:boundary] + "\n\n" + helper + text[boundary:])
    before = (
        "  Element* elementToRestyle = aElement->GetPseudoElement(aPseudoRequest);\n"
    )
    after = (
        before
        + """  if (RFDPTraceRestyleManager()) {
    std::fprintf(stderr,
                 "RFDP pid=%ld hint-map target_node=%p normalized_node=%p "
                 "pseudo=%u pseudo_id=%p animation=%d transition=%d\\n",
                 static_cast<long>(getpid()),
                 static_cast<const void*>(static_cast<const nsINode*>(aElement)),
                 static_cast<const void*>(static_cast<const nsINode*>(elementToRestyle)),
                 unsigned(aPseudoRequest.mType),
                 static_cast<const void*>(aPseudoRequest.mIdentifier.get()),
                 int(aRestyleHint == RestyleHint::RESTYLE_CSS_ANIMATIONS),
                 int(aRestyleHint == RestyleHint::RESTYLE_CSS_TRANSITIONS));
  }
"""
    )
    edit(manager, before, after)

    old_matching = (
        ARCHIVE / "candidate/servo/components/style/matching.rs"
    ).read_text()
    rust_helper = old_matching[old_matching.index("\nfn rfdp_trace() -> bool {") :]
    wrapper = root / "servo/components/style/gecko/wrapper.rs"
    before = """        let Some(mut data) = self.mutate_data() else {
            debug!("(Element not styled, discarding hints)");
"""
    after = """        let Some(mut data) = self.mutate_data() else {
            if rfdp_trace() {
                eprintln!("RFDP pid={} hint-discard node={:#x} hint={:?} reason=no-data",
                    std::process::id(), self.as_node().opaque().0, restyle_hint);
            }
            debug!("(Element not styled, discarding hints)");
"""
    edit(wrapper, before, after)
    before = "        data.hint.insert(restyle_hint);\n        data.damage |= damage;"
    after = (
        before
        + """
        if rfdp_trace() {
            eprintln!("RFDP pid={} hint-posted node={:#x} hint={:?} merged={:?}",
                std::process::id(), self.as_node().opaque().0, restyle_hint, data.hint);
        }"""
    )
    edit(wrapper, before, after)
    wrapper.write_text(wrapper.read_text() + rust_helper)

    matching = root / "servo/components/style/matching.rs"
    edit(
        matching,
        'use crate::dom::TElement;\n#[cfg(feature = "servo")]\nuse crate::dom::TNode;',
        "use crate::dom::{TElement, TNode};",
    )
    before = "        let new_primary_style = data.styles.primary.as_ref().unwrap();\n"
    after = (
        before
        + """
        if rfdp_trace() {
            eprintln!("RFDP pid={} installed node={:#x} style={:p} flags={:?} initial={} font_px={} thread={:?}",
                std::process::id(), self.as_node().opaque().0, &**new_primary_style,
                context.shared.traversal_flags, old_styles.primary.is_none(),
                new_primary_style.get_font().slow_clone_font_size().computed_size().px(),
                std::thread::current().id());
        }
"""
    )
    edit(matching, before, after)
    matching.write_text(matching.read_text() + rust_helper)

    roles = {
        path: {
            stage: sha(HERE / stage / path)
            for stage in ["base", "semantic", "candidate"]
        }
        for path in PATHS
    }
    for origin, name in [
        ("base", "native.patch"),
        ("semantic", "instrumentation.patch"),
    ]:
        parts = []
        for path in PATHS:
            parts.extend(
                difflib.unified_diff(
                    (HERE / origin / path).read_text().splitlines(True),
                    (root / path).read_text().splitlines(True),
                    fromfile="a/" + path,
                    tofile="b/" + path,
                )
            )
        (HERE / name).write_text("".join(parts))
    (HERE / "SOURCE-ROLES.json").write_text(json.dumps(roles, indent=2) + "\n")
    (HERE / "PREPARATION.json").write_text(
        json.dumps({"patch_output": applied, "live_source_modified": False}, indent=2)
        + "\n"
    )
    print(json.dumps(roles, indent=2))


if __name__ == "__main__":
    main()
