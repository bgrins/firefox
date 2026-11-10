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
PRIOR = ROOT / "artifacts/css-animation-initial-admission-native-20261110-v1"
REVISION = "b6f9b206df9c22b1ed2f41b1690614ec308a8471"
INPUTS = {
    "SOURCE-ROLES.json": "51a7ac576ad9517a52c484c298e164249aa998624badf1801bd7601a31600f7a",
    "semantic.patch": "0e01a9694afcd90dbc05953616c7e9b065adf992ce19dc3671b5691380b84399",
    "instrumentation.patch": "69de40cff22a7cc156de6128f3fa16addeed936750ec6bf20b37d72c93cb1318",
}
ADDED = ("layout/style/nsAnimationManager.cpp", "dom/animation/KeyframeEffect.cpp")
RUST = (
    "servo/components/style/matching.rs",
    "servo/components/style/traversal.rs",
    "servo/components/style/gecko/wrapper.rs",
)
TRACE = """#include <unistd.h>
#include <atomic>
#include <cstdio>
#include <cstdlib>

static bool TRACE_NAME() {
  if (!std::getenv("MOZ_ROOT_FONT_DRAIN_TRACE")) {
    return false;
  }
  static std::atomic<unsigned> count{0};
  unsigned value = count.load(std::memory_order_relaxed);
  while (value <= 4096 && !count.compare_exchange_weak(
                              value, value + 1, std::memory_order_relaxed)) {
  }
  if (value == 4096) {
    std::fprintf(stderr, "RFDP pid=%ld capped file=%s limit=4096\\n",
                 static_cast<long>(getpid()), __FILE__);
  }
  return value < 4096;
}

"""


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replace(text, old, new):
    require(text.count(old) == 1, "Replacement not unique: " + old)
    return text.replace(old, new)


def instrument(sources):
    output = dict(sources)
    for name in RUST:
        output[name] = replace(
            output[name],
            '        Some("svg") => "svg",',
            """        Some("svg") => "svg",
        Some("provider") => "provider",
        Some("outside") => "outside",
        Some("fallback") => "fallback",""",
        )
    name = ADDED[0]
    text = output[name]
    text = replace(
        text,
        '#include "nsAnimationManager.h"',
        TRACE.replace("TRACE_NAME", "RFDPTraceNamedTimeline")
        + '#include "nsAnimationManager.h"',
    )
    text = replace(
        text,
        "/**\n * Try to update the named timeline associated with this animation.\n",
        """static const char* RFDPTimelineKind(const dom::AnimationTimeline* aTimeline) {
  if (!aTimeline) {
    return "null";
  }
  if (aTimeline->IsUnresolvedTimeline()) {
    return "unresolved";
  }
  if (aTimeline->IsViewTimeline()) {
    return "view";
  }
  if (aTimeline->IsScrollTimeline()) {
    return "scroll";
  }
  return "other";
}

/**
 * Try to update the named timeline associated with this animation.
""",
    )
    text = replace(
        text,
        """  const auto* oldTimeline = aAnimation->GetTimeline();
  if (oldTimeline == newTimeline) {""",
        """  const auto* oldTimeline = aAnimation->GetTimeline();
  const bool rfdpNamed = aTimelineName && aTimelineName->Equals(u"--t", 3);
  if (rfdpNamed && RFDPTraceNamedTimeline()) {
    const char* decision = oldTimeline == newTimeline ? "equal" :
        (aAnimationsWithDeferredUpdate &&
         (!newTimeline || newTimeline->IsUnresolvedTimeline())) ? "defer" : "rebind";
    std::fprintf(stderr,
                 "RFDP pid=%ld timeline-lookup animation=%p target_node=%p document_node=%p name=--t old_timeline=%p new_timeline=%p old_kind=%s new_kind=%s deferred_updates=%d decision=%s\\n",
                 static_cast<long>(getpid()), static_cast<void*>(static_cast<Animation*>(aAnimation)),
                 static_cast<const void*>(static_cast<const nsINode*>(target.mElement)),
                 static_cast<const void*>(static_cast<const nsINode*>(aDocument)),
                 static_cast<const void*>(oldTimeline), static_cast<const void*>(newTimeline.get()),
                 RFDPTimelineKind(oldTimeline), RFDPTimelineKind(newTimeline),
                 int(bool(aAnimationsWithDeferredUpdate)), decision);
  }
  if (oldTimeline == newTimeline) {""",
    )
    text = replace(
        text,
        """    aAnimationsWithDeferredUpdate->Insert(aAnimation);
    return;""",
        """    aAnimationsWithDeferredUpdate->Insert(aAnimation);
    if (rfdpNamed && RFDPTraceNamedTimeline()) {
      std::fprintf(stderr,
                   "RFDP pid=%ld timeline-deferred animation=%p target_node=%p document_node=%p name=--t new_timeline=%p\\n",
                   static_cast<long>(getpid()), static_cast<void*>(static_cast<Animation*>(aAnimation)),
                   static_cast<const void*>(static_cast<const nsINode*>(target.mElement)),
                   static_cast<const void*>(static_cast<const nsINode*>(aDocument)),
                   static_cast<const void*>(newTimeline.get()));
    }
    return;""",
    )
    text = replace(
        text,
        """  aAnimation->SetTimelineNoUpdate(newTimeline, scopedName,
                                  Animation::FromJS::No);""",
        """  if (rfdpNamed && RFDPTraceNamedTimeline()) {
    std::fprintf(stderr,
                 "RFDP pid=%ld timeline-rebind-enter animation=%p target_node=%p document_node=%p name=--t old_timeline=%p new_timeline=%p\\n",
                 static_cast<long>(getpid()), static_cast<void*>(static_cast<Animation*>(aAnimation)),
                 static_cast<const void*>(static_cast<const nsINode*>(target.mElement)),
                 static_cast<const void*>(static_cast<const nsINode*>(aDocument)),
                 static_cast<const void*>(oldTimeline), static_cast<const void*>(newTimeline.get()));
  }
  const bool rfdpChanged = aAnimation->SetTimelineNoUpdate(
      newTimeline, scopedName, Animation::FromJS::No);
  if (rfdpNamed && RFDPTraceNamedTimeline()) {
    std::fprintf(stderr,
                 "RFDP pid=%ld timeline-rebind-return animation=%p target_node=%p document_node=%p name=--t old_timeline=%p new_timeline=%p current_timeline=%p changed=%d\\n",
                 static_cast<long>(getpid()), static_cast<void*>(static_cast<Animation*>(aAnimation)),
                 static_cast<const void*>(static_cast<const nsINode*>(target.mElement)),
                 static_cast<const void*>(static_cast<const nsINode*>(aDocument)),
                 static_cast<const void*>(oldTimeline), static_cast<const void*>(newTimeline.get()),
                 static_cast<const void*>(aAnimation->GetTimeline()), int(rfdpChanged));
  }""",
    )
    output[name] = text
    name = ADDED[1]
    text = output[name]
    text = replace(
        text,
        '#include "mozilla/dom/KeyframeEffect.h"',
        TRACE.replace("TRACE_NAME", "RFDPTraceTimingEligibility")
        + '#include "mozilla/dom/KeyframeEffect.h"',
    )
    text = replace(
        text,
        """    RequestRestyle(restyleType);
  }

  // Detect changes to "in effect" status""",
        """    if (RFDPTraceTimingEligibility()) {
      std::fprintf(stderr,
                   "RFDP pid=%ld timing-eligible effect=%p animation=%p target_node=%p document_node=%p pseudo=%u pseudo_id=%p timing_changed=1 properties=%zu type=%u\\n",
                   static_cast<long>(getpid()), static_cast<void*>(this),
                   static_cast<void*>(mAnimation.get()),
                   static_cast<const void*>(static_cast<const nsINode*>(mTarget.mElement.get())),
                   mTarget.mElement ? static_cast<const void*>(static_cast<const nsINode*>(mTarget.mElement->OwnerDoc())) : nullptr,
                   unsigned(mTarget.mPseudoRequest.mType),
                   static_cast<const void*>(mTarget.mPseudoRequest.mIdentifier.get()),
                   size_t(mProperties.Length()), unsigned(restyleType));
    }
    RequestRestyle(restyleType);
  }

  // Detect changes to "in effect" status""",
    )
    output[name] = text
    return output


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Run with python -I and without -O")
    for name, digest in INPUTS.items():
        require(sha((PRIOR / name).read_bytes()) == digest, "Prior input changed")
    roles = json.loads((PRIOR / "SOURCE-ROLES.json").read_text())
    names = list(roles) + list(ADDED)
    previous = (
        json.loads((HERE / "SOURCE-ROLES.json").read_text())
        if (HERE / "SOURCE-ROLES.json").exists()
        else None
    )
    for name in names:
        for stage in ("base", "semantic", "candidate"):
            path = HERE / stage / name
            if path.exists():
                require(
                    previous is not None
                    and sha(path.read_bytes()) == previous[name][stage],
                    "Existing copy changed",
                )
    logs = []
    with tempfile.TemporaryDirectory(prefix="named-timeline-instrument-") as directory:
        scratch = Path(directory)
        for name in names:
            data = subprocess.run(
                ["git", "-c", "core.fsmonitor=false", "show", REVISION + ":" + name],
                cwd=ROOT,
                capture_output=True,
                check=True,
            ).stdout
            if name in roles:
                require(
                    sha(data) == roles[name]["base"],
                    "Prior base differs at new revision",
                )
            target = scratch / "base" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for source, target, patch in (
            ("base", "semantic", "semantic.patch"),
            ("semantic", "candidate", "instrumentation.patch"),
        ):
            shutil.copytree(scratch / source, scratch / target)
            run = subprocess.run(
                ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(PRIOR / patch)],
                cwd=scratch / target,
                capture_output=True,
                text=True,
                check=True,
            )
            require(
                "offset" not in run.stdout and "fuzz" not in run.stdout,
                "Inexact prior patch",
            )
            logs.append(run.stdout)
        for name, stages in roles.items():
            for stage, digest in stages.items():
                require(
                    sha((scratch / stage / name).read_bytes()) == digest,
                    "Prior reconstruction changed",
                )
        output = instrument({
            name: (scratch / "candidate" / name).read_text() for name in names
        })
        for name, text in output.items():
            (scratch / "candidate" / name).write_text(text)
        contents = {
            stage: {name: (scratch / stage / name).read_bytes() for name in names}
            for stage in ("base", "semantic", "candidate")
        }
    require(not scratch.exists(), "Scratch not removed")
    for stage, files in contents.items():
        for name, data in files.items():
            target = HERE / stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    new_roles = {
        name: {stage: sha(files[name]) for stage, files in contents.items()}
        for name in names
    }
    (HERE / "SOURCE-ROLES.json").write_text(json.dumps(new_roles, indent=2) + "\n")
    for source, target, patch in (
        ("base", "semantic", "semantic.patch"),
        ("base", "candidate", "native.patch"),
        ("semantic", "candidate", "instrumentation.patch"),
    ):
        text = "".join(
            "".join(
                difflib.unified_diff(
                    contents[source][name].decode().splitlines(keepends=True),
                    contents[target][name].decode().splitlines(keepends=True),
                    fromfile="a/" + name,
                    tofile="b/" + name,
                )
            )
            for name in names
        )
        (HERE / patch).write_text(text)
    replay = {
        "base_revision": REVISION,
        "files": {
            name: sha((HERE / name).read_bytes())
            for name in (
                "SOURCE-ROLES.json",
                "semantic.patch",
                "native.patch",
                "instrumentation.patch",
            )
        },
    }
    (HERE / "REPLAY-INPUTS.json").write_text(json.dumps(replay, indent=2) + "\n")
    receipt = {
        "generator_sha256": sha(Path(__file__).read_bytes()),
        "base_revision": REVISION,
        "prior_inputs": INPUTS,
        "prior_patch_logs": logs,
        "source_hashes": len(new_roles) * 3,
        "scratch_removed": True,
        "live_sources_modified": False,
    }
    (HERE / "INSTRUMENTATION.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
