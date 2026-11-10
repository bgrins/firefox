import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUST = [
    "servo/components/style/matching.rs",
    "servo/components/style/traversal.rs",
    "servo/components/style/gecko/wrapper.rs",
]
HELPERS = r"""
fn rfdp_line(mut line: String) {
    use std::io::Write;
    line.push('\n');
    std::io::stderr()
        .lock()
        .write_all(line.as_bytes())
        .expect("RFDP trace write failed");
}

fn rfdp_role<E: TElement>(element: E) -> &'static str {
    match element.id().map(ToString::to_string).as_deref() {
        Some("host") => "host",
        Some("first") => "first",
        Some("second") => "second",
        Some("third") => "third",
        Some("leaf") => "leaf",
        Some("svg") => "svg",
        _ => "-",
    }
}
"""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replace(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def complete_lines(source):
    spans = []
    cursor = 0
    while (start := source.find("eprintln!(", cursor)) != -1:
        opening = start + len("eprintln!")
        depth, quoted, escaped = 0, False, False
        for index in range(opening, len(source)):
            char = source[index]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    break
        else:
            raise RuntimeError("Unclosed eprintln invocation")
        invocation = source[start : index + 1]
        assert "RFDP " in invocation
        spans.append((start, index + 1))
        cursor = index + 1
    for start, end in reversed(spans):
        source = (
            source[:start]
            + "rfdp_line(format!("
            + source[start + len("eprintln!(") : end]
            + ")"
            + source[end:]
        )
    return source + HELPERS, len(spans)


def instrument(inputs):
    output = dict(inputs)
    converted = {}
    for name in RUST:
        output[name], converted[name] = complete_lines(output[name])
    assert list(converted.values()) == [2, 2, 3]

    name = RUST[0]
    text = output[name]
    text = replace(
        text,
        "use crate::dom::{TElement, TNode};",
        "use crate::dom::{TDocument, TElement, TNode};",
    )
    text = replace(
        text,
        "installed node={:#x} style={:p}",
        "installed node={:#x} document_node={:#x} role={} style={:p}",
    )
    text = replace(
        text,
        "std::process::id(), self.as_node().opaque().0, &**new_primary_style,",
        "std::process::id(), self.as_node().opaque().0,\n"
        "                self.as_node().owner_doc().as_node().opaque().0, rfdp_role(*self), &**new_primary_style,",
    )
    text = replace(
        text,
        "        let old_values = &old_styles.primary;\n"
        "        if context.shared.traversal_flags.for_animation_only() && old_values.is_some() {",
        """        let old_values = &old_styles.primary;
        if context.shared.traversal_flags.for_animation_only() && rfdp_trace() {
            rfdp_line(format!(
                "RFDP pid={} animation-management node={:#x} document_node={:#x} role={} flags={:?} old_present={} thread={:?}",
                std::process::id(), self.as_node().opaque().0,
                self.as_node().owner_doc().as_node().opaque().0, rfdp_role(*self),
                context.shared.traversal_flags, old_values.is_some(), std::thread::current().id()
            ));
        }
        if context.shared.traversal_flags.for_animation_only() && old_values.is_some() {""",
    )
    text = replace(
        text,
        "        if !tasks.is_empty() {\n"
        "            let task = crate::context::SequentialTask::update_animations(",
        "        if !tasks.is_empty() {\n"
        "            let rfdp_task_bits = tasks.bits();\n"
        "            let task = crate::context::SequentialTask::update_animations(",
    )
    text = replace(
        text,
        "            context.thread_local.tasks.push(task);",
        """            context.thread_local.tasks.push(task);
            if rfdp_trace() {
                rfdp_line(format!(
                    "RFDP pid={} task-queued node={:#x} document_node={:#x} role={} flags={:?} old_present={} bits={} thread={:?}",
                    std::process::id(), self.as_node().opaque().0,
                    self.as_node().owner_doc().as_node().opaque().0, rfdp_role(*self),
                    context.shared.traversal_flags, old_values.is_some(), rfdp_task_bits,
                    std::thread::current().id()
                ));
            }""",
    )
    output[name] = text

    name = RUST[1]
    text = output[name]
    text = replace(
        text,
        "use crate::dom::{OpaqueNode, TElement, TNode};",
        "use crate::dom::{OpaqueNode, TDocument, TElement, TNode};",
    )
    text = replace(
        text,
        "restyle node={:#x} flags={:?}",
        "restyle node={:#x} document_node={:#x} role={} flags={:?}",
    )
    text = replace(
        text,
        "            element.as_node().opaque().0,\n            flags,",
        "            element.as_node().opaque().0,\n"
        "            element.as_node().owner_doc().as_node().opaque().0,\n"
        "            rfdp_role(element),\n            flags,",
    )
    output[name] = text

    name = RUST[2]
    text = output[name]
    text = replace(
        text,
        "        unsafe {\n            Gecko_UpdateAnimations(",
        """        if rfdp_trace() {
            rfdp_line(format!(
                "RFDP pid={} task-execute node={:#x} document_node={:#x} role={} bits={} thread={:?}",
                std::process::id(), self.as_node().opaque().0,
                self.as_node().owner_doc().as_node().opaque().0, rfdp_role(*self),
                tasks.bits(), std::thread::current().id()
            ));
        }
        unsafe {
            Gecko_UpdateAnimations(""",
    )
    text = replace(
        text,
        """                computed_values_opt,
                tasks.bits(),
            );
        }
    }""",
        """                computed_values_opt,
                tasks.bits(),
            );
        }
        if rfdp_trace() {
            rfdp_line(format!(
                "RFDP pid={} task-return node={:#x} document_node={:#x} role={} bits={} thread={:?}",
                std::process::id(), self.as_node().opaque().0,
                self.as_node().owner_doc().as_node().opaque().0, rfdp_role(*self),
                tasks.bits(), std::thread::current().id()
            ));
        }
    }""",
    )
    output[name] = text

    name = "layout/style/RestyleManager.cpp"
    text = output[name]
    text = replace(
        text,
        "pseudo=%u pseudo_id=%p animation=%d transition=%d\\n",
        "pseudo=%u pseudo_id=%p animation=%d transition=%d smil=%d\\n",
    )
    text = replace(
        text,
        "                 int(aRestyleHint == RestyleHint::RESTYLE_CSS_TRANSITIONS));",
        "                 int(aRestyleHint == RestyleHint::RESTYLE_CSS_TRANSITIONS),\n"
        "                 int(aRestyleHint == RestyleHint::RESTYLE_SMIL));",
    )
    output[name] = text

    name = "layout/style/ServoStyleSet.cpp"
    text = output[name]
    assert '#include "mozilla/ScopeExit.h"' not in text
    text = replace(
        text,
        '#include "mozilla/ServoStyleSet.h"',
        '#include "mozilla/ServoStyleSet.h"\n#include "mozilla/ScopeExit.h"',
    )
    text = replace(
        text,
        "document-enter set=%p document=%p call=%llu flags=%u\\n",
        "document-enter set=%p document=%p document_node=%p call=%llu flags=%u\\n",
    )
    text = replace(
        text,
        "        static_cast<void*>(mDocument), call, unsigned(aFlags));",
        "        static_cast<void*>(mDocument),\n"
        "        static_cast<const void*>(static_cast<const nsINode*>(mDocument)),\n"
        "        call, unsigned(aFlags));",
    )
    text = replace(
        text,
        "void ServoStyleSet::StyleNewSubtree(Element* aRoot) {",
        """void ServoStyleSet::StyleNewSubtree(Element* aRoot) {
  static std::atomic<unsigned long long> calls{0};
  const auto call = calls.fetch_add(1, std::memory_order_relaxed);
  if (RFDPTraceServoStyleSet()) {
    std::fprintf(stderr,
                 "RFDP pid=%ld new-subtree-enter set=%p document_node=%p call=%llu root_node=%p\\n",
                 static_cast<long>(getpid()), static_cast<void*>(this),
                 static_cast<const void*>(static_cast<const nsINode*>(mDocument)),
                 call, static_cast<const void*>(static_cast<const nsINode*>(aRoot)));
  }
  auto rfdpExit = mozilla::MakeScopeExit([&] {
    if (RFDPTraceServoStyleSet()) {
      std::fprintf(stderr,
                   "RFDP pid=%ld new-subtree-exit set=%p document_node=%p call=%llu root_node=%p\\n",
                   static_cast<long>(getpid()), static_cast<void*>(this),
                   static_cast<const void*>(static_cast<const nsINode*>(mDocument)),
                   call, static_cast<const void*>(static_cast<const nsINode*>(aRoot)));
    }
  });""",
    )
    text = replace(
        text,
        "  DebugOnly<bool> postTraversalRequired =\n"
        "      Servo_TraverseSubtree(aRoot, mRawData.get(), &snapshots, flags);",
        """  if (RFDPTraceServoStyleSet()) {
    std::fprintf(stderr,
                 "RFDP pid=%ld new-subtree-pass set=%p document_node=%p call=%llu root_node=%p phase=default flags=%u\\n",
                 static_cast<long>(getpid()), static_cast<void*>(this),
                 static_cast<const void*>(static_cast<const nsINode*>(mDocument)),
                 call, static_cast<const void*>(static_cast<const nsINode*>(aRoot)),
                 unsigned(flags));
  }
  DebugOnly<bool> postTraversalRequired =
      Servo_TraverseSubtree(aRoot, mRawData.get(), &snapshots, flags);""",
    )
    text = replace(
        text,
        "    postTraversalRequired =\n"
        "        Servo_TraverseSubtree(aRoot, mRawData.get(), &snapshots,\n"
        "                              ServoTraversalFlags::AnimationOnly |",
        """    if (RFDPTraceServoStyleSet()) {
      std::fprintf(stderr,
                   "RFDP pid=%ld new-subtree-pass set=%p document_node=%p call=%llu root_node=%p phase=final flags=%u\\n",
                   static_cast<long>(getpid()), static_cast<void*>(this),
                   static_cast<const void*>(static_cast<const nsINode*>(mDocument)),
                   call, static_cast<const void*>(static_cast<const nsINode*>(aRoot)),
                   unsigned(ServoTraversalFlags::AnimationOnly |
                            ServoTraversalFlags::FinalAnimationTraversal));
    }
    postTraversalRequired =
        Servo_TraverseSubtree(aRoot, mRawData.get(), &snapshots,
                              ServoTraversalFlags::AnimationOnly |""",
    )
    output[name] = text
    return output, converted


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Use python3 -I without -O")
    reconstruction = json.loads((HERE / "RECONSTRUCTION.json").read_text())
    prior = ROOT / reconstruction["prior_capsule"]
    prior_roles_bytes = (prior / "SOURCE-ROLES.json").read_bytes()
    assert sha(prior_roles_bytes) == reconstruction["prior_roles_sha256"]
    roles = json.loads(prior_roles_bytes)
    previous = (
        json.loads((HERE / "SOURCE-ROLES.json").read_text())
        if (HERE / "SOURCE-ROLES.json").exists()
        else roles
    )
    for name, role in roles.items():
        for stage in ["base", "semantic"]:
            assert sha((HERE / stage / name).read_bytes()) == role[stage]
        assert sha((HERE / "candidate" / name).read_bytes()) in {
            role["candidate"],
            previous[name]["candidate"],
        }
    with tempfile.TemporaryDirectory(
        prefix="initial-admission-instrument-"
    ) as directory:
        scratch = Path(directory)
        for name in roles:
            target = scratch / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HERE / "semantic" / name, target)
        command = [
            "patch",
            "--batch",
            "--fuzz=0",
            "-p1",
            "-i",
            str(prior / "instrumentation.patch"),
        ]
        result = subprocess.run(
            command, cwd=scratch, capture_output=True, text=True, check=False
        )
        assert result.returncode == 0, result.stdout + result.stderr
        inputs = {}
        for name, role in roles.items():
            data = (scratch / name).read_bytes()
            assert sha(data) == role["candidate"]
            inputs[name] = data.decode()
        outputs, converted = instrument(inputs)
    assert not scratch.exists()
    for name, text in outputs.items():
        (HERE / "candidate" / name).write_text(text)
    new_roles = {
        name: {
            stage: sha((HERE / stage / name).read_bytes())
            for stage in ["base", "semantic", "candidate"]
        }
        for name in roles
    }
    (HERE / "SOURCE-ROLES.json").write_text(json.dumps(new_roles, indent=2) + "\n")
    for stage, patch_name in [
        ("base", "native.patch"),
        ("semantic", "instrumentation.patch"),
    ]:
        patch = "".join(
            "".join(
                difflib.unified_diff(
                    (HERE / stage / name).read_text().splitlines(keepends=True),
                    outputs[name].splitlines(keepends=True),
                    fromfile="a/" + name,
                    tofile="b/" + name,
                )
            )
            for name in roles
        )
        (HERE / patch_name).write_text(patch)
    (HERE / "INSTRUMENTATION.json").write_text(
        json.dumps(
            {
                "generator_sha256": sha(Path(__file__).read_bytes()),
                "input_roles_sha256": sha(prior_roles_bytes),
                "prior_instrumentation_sha256": sha(
                    (prior / "instrumentation.patch").read_bytes()
                ),
                "converted_eprintln_sites": converted,
                "converted_total": sum(converted.values()),
                "reconstruction_patch_output": result.stdout,
                "scratch_removed": True,
                "live_source_changed": False,
            },
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps({
            "converted_sites": sum(converted.values()),
            "candidate_hashes": {
                name: role["candidate"] for name, role in new_roles.items()
            },
        })
    )


if __name__ == "__main__":
    main()
