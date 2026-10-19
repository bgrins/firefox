import URLNativeHex
import URLNativeWhitespace
import URLNativeCharacter
import URLDelegation
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace URLNativeEscape
open URLNativeState
abbrev Byte := CommentScan.Byte

def run (xs : List Byte) (s : State) : State :=
 match xs with
 | [] => s
 | b::_ =>
   match HexPrefix.nativeDigit b with
   | some _ =>
     let h := HexPrefix.run 6 xs 0
     URLNativeWhitespace.consume h.rest (URLNativeHex.run 6 xs 0 s)
   | none =>
     if b.val=0 then advance s 1
     else character s (Escape.width b) (if Escape.width b=4 then 2 else 1)

def Admitted (xs : List Byte) (s : State) : Prop :=
 match xs with
 | [] => True
 | b::_ =>
   match HexPrefix.nativeDigit b with
   | some _ => URLNativeWhitespace.Admitted (HexPrefix.run 6 xs 0).rest
       (URLNativeHex.run 6 xs 0 s)
   | none => True

theorem hex_not_cr (fuel : Nat) (xs : List Byte) (value : Nat) :
 (xs.take (HexPrefix.run fuel xs value).count).getLast? ≠ some 13 := by
 intro h
 obtain ⟨pre,hpre⟩ := List.getLast?_eq_some_iff.mp h
 have hd := URLNativeHex.consumed_digits fuel xs value 13 (by simp [hpre])
 have hn := (URLNativeHex.digit_metadata 13 hd).2
 contradiction

theorem hex_metadata (xs : List Byte) (s : State) (r : CommentObservers.State)
 (block : Nat) (h : Related s r block)
 (ha : URLNativeWhitespace.Admitted (HexPrefix.run 6 xs 0).rest
       (URLNativeHex.run 6 xs 0 s)) :
 Related (URLNativeWhitespace.consume (HexPrefix.run 6 xs 0).rest
       (URLNativeHex.run 6 xs 0 s))
  (CommentObservers.nativeObserve
   (xs.take ((HexPrefix.run 6 xs 0).count+Escape.nativeWhitespace (HexPrefix.run 6 xs 0).rest)) r) block := by
 have hh := URLNativeHex.related 6 xs 0 s r block h
 have hw := URLNativeWhitespace.metadata (HexPrefix.run 6 xs 0).rest _ _ block hh ha
 rw [HexPrefix.exact_remainder] at hw
 rw [← URLDelegation.observe_append _ _ r (Or.inl (hex_not_cr 6 xs 0))] at hw
 rw [StringTrace.take_split _ _ _ (HexPrefix.count_bound 6 xs 0).1] at hw
 simpa only [HexPrefix.exact_remainder] using hw

theorem position (units : List Boundary.Unit) (s : State) :
 (run (Boundary.bytes units) s).position=s.position+(Escape.native (Boundary.bytes units)).count := by
 cases units with
 | nil => simp [Boundary.bytes,run,Escape.native]
 | cons u us =>
   cases hd : HexPrefix.nativeDigit u.first with
   | some d =>
     simp only [Boundary.bytes,List.flatMap_cons,Boundary.Unit.bytes,List.cons_append,run,Escape.native,hd]
     rw [URLNativeWhitespace.position,URLNativeHex.state_exact]
     simp [advance,Nat.add_assoc]
   | none =>
     by_cases hz : u.first.val=0
     · simp [Boundary.bytes,Boundary.Unit.bytes,run,Escape.native,hd,hz,advance]
     · have hw := URLNativeCharacter.byte_length u
       have hl : Escape.width u.first ≤ (u.bytes++Boundary.bytes us).length := by simp only [List.length_append]; omega
       simp only [Boundary.bytes,List.flatMap_cons,Boundary.Unit.bytes,List.cons_append,run,Escape.native,hd,hz,↓reduceIte]
       simp only [character,List.length_take]
       have hl' : Escape.width u.first ≤ (u.first::(u.rest++Boundary.bytes us)).length := hl
       simpa only [Boundary.bytes,Nat.min_eq_left hl'] using congrArg (s.position + ·) (Nat.min_eq_left hl').symm

theorem metadata (units : List Boundary.Unit) (s : State) (r : CommentObservers.State)
 (block : Nat) (h : Related s r block) (ha : Admitted (Boundary.bytes units) s)
 (hn : ∀ b ∈ (Boundary.bytes units).head?, CommentObservers.isNewline b=false) :
 Related (run (Boundary.bytes units) s)
  (CommentObservers.nativeObserve ((Boundary.bytes units).take (Escape.native (Boundary.bytes units)).count) r) block := by
 cases units with
 | nil => simpa [Boundary.bytes,run,Escape.native,CommentObservers.nativeObserve] using h
 | cons u us =>
   cases hd : HexPrefix.nativeDigit u.first with
   | some d =>
     have he := hex_metadata (Boundary.bytes (u::us)) s r block h (by simpa only [Admitted,Boundary.bytes,List.flatMap_cons,Boundary.Unit.bytes,List.cons_append,hd] using ha)
     simpa only [Boundary.bytes,List.flatMap_cons,Boundary.Unit.bytes,List.cons_append,run,Escape.native,hd] using he
   | none =>
     by_cases hz : u.first.val=0
     · have hu : u.first=0 := Fin.ext hz
       have hr := Boundary.unit_ascii_singleton u (by omega)
       have he := advance_related s r block 1 h
       simpa [Boundary.bytes,Boundary.Unit.bytes,run,Escape.native,hd,hz,hr,
         CommentObservers.nativeObserve,hu,CommentObservers.isNewline,
         CommentObservers.ordinary,CommentObservers.nativeWidth,CommentObservers.advance,HexPrefix.nativeDigit] using he
     · have hn' : CommentObservers.isNewline u.first=false := hn u.first (by simp [Boundary.bytes,Boundary.Unit.bytes])
       have he := URLNativeCharacter.metadata u s r block h hn'
       have hw := URLNativeCharacter.byte_length u
       have ht : (u.bytes++Boundary.bytes us).take (Escape.width u.first)=u.bytes := by rw [← hw,List.take_left]
       have hl : Escape.width u.first ≤ (u.bytes++Boundary.bytes us).length := by simp only [List.length_append]; omega
       change Related _ (CommentObservers.nativeObserve
         ((u.bytes++Boundary.bytes us).take (Escape.native (u.bytes++Boundary.bytes us)).count) r) block
       simp only [Boundary.Unit.bytes,List.cons_append,Escape.native,hd,hz,↓reduceIte,List.length_take]
       have hl' : Escape.width u.first ≤ (u.first::(u.rest++Boundary.bytes us)).length := hl
       rw [Nat.min_eq_left hl']
       simp only [Boundary.bytes,List.flatMap_cons,Boundary.Unit.bytes,List.cons_append,run,hd,hz,↓reduceIte]
       change Related (character s (Escape.width u.first) (if Escape.width u.first=4 then 2 else 1))
         (CommentObservers.nativeObserve ((u.bytes++Boundary.bytes us).take (Escape.width u.first)) r) block
       rw [ht]
       simpa only [hw,URLNativeCharacter.units] using he
end URLNativeEscape
