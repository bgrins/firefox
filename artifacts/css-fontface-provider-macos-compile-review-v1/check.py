#!/usr/bin/env python3
"""Authenticate retained source before source-only structural checks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
manifest = json.loads((ROOT / "MANIFEST.json").read_text())
for rel, digest in manifest["files"].items():
    path = ROOT / rel
    assert path.is_file() and sha(path.read_bytes()) == digest, rel

def source(rel):
    return (ROOT / "source" / rel).read_text()

def candidate(rel):
    return (ROOT / "candidate" / rel).read_text()

identity = json.loads((ROOT / "SOURCE-IDENTITY.json").read_text())
assert len(identity["native_comparisons"]) == 16
for row in identity["native_comparisons"]:
    rel = row["file"]
    assert sha((ROOT / "source" / rel).read_bytes()) == row["original_live_sha256"]
    assert sha((ROOT / "candidate" / rel).read_bytes()) == row["candidate_sha256"]
    assert row["live_matches_frozen_original"]

checks = [
    (source("mfbt/AlreadyAddRefed.h"), "already_AddRefed(already_AddRefed<U>&& aOther)"),
    (source("gfx/thebes/gfxFontEntry.h"), "friend class gfxUserFontEntry;"),
    (source("gfx/thebes/gfxFontEntry.h"), "mutable mozilla::RWLock mLock;"),
    (source("gfx/thebes/CoreTextFontList.cpp"), "CFRetain(mFontRef);"),
    (candidate("gfx/thebes/CoreTextFontList.cpp"), "CTFontEntry::CloneUserFontEntry("),
    (candidate("gfx/thebes/gfxUserFontSet.cpp"), "platform->SetSkrifaFont(font);"),
    (source("gfx/thebes/FontData.h"), "uint32_t Length() const"),
    (source("xpcom/ds/nsTArray.h"), "self_type Clone() const"),
    (source("dom/workers/WorkerRunnable.h"), "virtual bool MainThreadRun() = 0;"),
    (candidate("layout/style/FontFaceSetImpl.cpp"), "task->Dispatch(GetCurrentThreadWorkerPrivate(), Canceling, aRv);"),
    (candidate("layout/style/FontFaceImpl.cpp"), "SetUserFontEntry(entry, false);"),
    (source("layout/style/FontFaceImpl.cpp"), "[self = RefPtr{impl}, status] { self->SetStatus(status); }"),
    (source("layout/style/FontFaceImpl.h"), "return HasRule() ? mRule : mDescriptors;"),
    (source("servo/components/style/properties/properties.mako.rs"), "self.${descriptor.ident} = value;"),
]
for text, needle in checks:
    assert needle in text, needle
ctor = source("layout/style/FontFace.cpp")
assert ctor.index("obj->mImpl->SetDescriptors(aFamily, aDescriptors)") < ctor.index("obj->mImpl->InitializeSourceURL(") < ctor.index("obj->mImpl->InitializeSourceBuffer(")
parser = source("servo/components/style/properties/properties.mako.rs")
start = parser.index("pub fn set(&mut self, id: DescriptorId")
setter = parser[start:parser.index("/// Removes a descriptor", start)]
assert setter.index("input.parse_entirely") < setter.index(")?);") < setter.index("self.${descriptor.ident} = value;")
print(json.dumps({"authenticated_inputs": len(manifest["files"]), "original_candidate_pairs": 16, "structural_checks": len(checks) + 2, "compiler_run": False, "status": "PASS_SOURCE_ONLY"}, indent=2))
