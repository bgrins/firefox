import URLNativeState
import CommentCodepoints
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace URLNativeCharacter
open URLNativeState
abbrev Byte := CommentScan.Byte

def units (u : Boundary.Unit) : Nat := if Escape.width u.first=4 then 2 else 1

theorem byte_length (u : Boundary.Unit) : u.bytes.length=Escape.width u.first := by
 simpa [Boundary.Unit.bytes,Nat.add_comm] using u.lengthWidth

theorem units_le_bytes (u : Boundary.Unit) : units u≤u.bytes.length := by
 have widths : ∀ b : Byte, (if Escape.width b=4 then 2 else 1)≤Escape.width b := by decide
 rw [byte_length]
 exact widths u.first

theorem observed (u : Boundary.Unit) (r : CommentObservers.State)
 (hn : CommentObservers.isNewline u.first=false) :
 CommentObservers.nativeObserve u.bytes r=
 ⟨r.offset+u.bytes.length,r.line,r.column+units u⟩ := by
 rw [CommentObservers.native_reference]
 unfold CommentObservers.referenceObserve
 rw [CommentCodepoints.unit_observer]
 unfold CommentCodepoints.unitStep
 split
 · rename_i ha
   have rest := Boundary.unit_ascii_singleton u ha
   have facts : ∀ b : Byte, b.val<128 → CommentObservers.isNewline b=false →
    b≠13 ∧ b≠10 ∧ b≠12 ∧ CommentObservers.referenceWidth b=1 ∧ Escape.width b=1 := by decide
   obtain ⟨h13,h10,h12,hw,hu⟩ := facts u.first ha hn
   simp [CommentObservers.referenceStep,h13,h10,h12,hw,units,hu,Boundary.Unit.bytes,rest]
 · rfl

theorem metadata (u : Boundary.Unit) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (hn : CommentObservers.isNewline u.first=false) :
 Related (character s u.bytes.length (units u))
  (CommentObservers.nativeObserve u.bytes r) block := by
 rw [observed u r hn]
 exact character_related s r block _ _ h (units_le_bytes u)
end URLNativeCharacter
