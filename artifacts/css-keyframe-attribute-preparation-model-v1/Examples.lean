import Preparation
open KeyframeAttributePreparation
namespace PreparationExamples

def plain : Key := ⟨none, "n"⟩
def qualified : Key := ⟨some "urn:other", "n"⟩
def provider : Provider Nat := fun key =>
  if key = plain then some 2 else if key = qualified then some 7 else none
def resolver (context : Nat) (_ : Key) (raw : Nat) : Option Nat := some (raw + context)
def parser (n : Nat) : Option Nat := some n
def fallback : Value Nat := ⟨1, false⟩
def cache : Cache Nat := prepare provider resolver 10 [plain, qualified]
def request : Request Nat Nat := ⟨plain, parser, fallback⟩
def frame (context : Nat) : Frame Nat Nat Nat Nat :=
  ⟨provider, context, [plain, qualified], [request]⟩
def aliasCache : Cache Nat := fun key => cache ⟨none, key.localName⟩
def stale : Value Nat := evaluate provider cache parser plain fallback

example : evaluate provider cache parser plain fallback = ⟨12, true⟩ := by decide +kernel
example : evaluate (fun _ => (none : Option Nat)) cache parser plain fallback = fallback := by decide +kernel
example : evaluate provider (fun _ => none) parser plain fallback = fallback := by decide +kernel
example : evaluate provider cache parser qualified fallback = ⟨17, true⟩ := by decide +kernel
example : evaluate provider aliasCache parser qualified fallback = ⟨12, true⟩ := by decide +kernel
example : runHistory resolver [frame 10, frame 20, frame 0, frame 10] =
    [[⟨12, true⟩], [⟨22, true⟩], [⟨2, true⟩], [⟨12, true⟩]] := by decide +kernel
example : [stale] ≠ runFrame resolver (frame 20) := by decide +kernel
example : evaluate provider cache (fun n => some (2 * n)) plain fallback = ⟨24, true⟩ := by decide +kernel
example : evaluate provider cache (fun _ => none) plain (⟨3, true⟩ : Value Nat) =
    ⟨3, true⟩ := by decide +kernel
end PreparationExamples
