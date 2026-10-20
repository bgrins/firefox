import UntilAfter
set_option autoImplicit false
namespace AfterChallenges
open PublicCache

def names : List (List Byte) := [[118,97,114]]
def initial : State := PublicHistory.begin names (constructor ⟨none,none⟩)
def initialRef : PublicHistory.Reference := PublicHistory.initialReference initial

def misleading (p : Nat) : Lexeme := ⟨.function [118,97,114], ⟨p+1,none⟩⟩
theorem delimiter_provider_law_is_needed :
    seen (UntilAfter.takeNative 1 misleading names 59 initial).mode = false ∧
    (UntilAfter.takeReference 1 misleading initialRef).observations.any (relevant names) = true := by
  decide +kernel

def ordinary (p : Nat) : Lexeme := ⟨.other,⟨p+1,none⟩⟩
theorem boundary_ownership_premise_is_needed :
    (UntilAfter.finishNative [59] ordinary names [] initial).cursor.position = 1 ∧
    (UntilAfter.finishReference [59] ordinary [] [] initialRef).cursor.position = 0 := by
  decide +kernel

def pending : State := {initial with cursor := ⟨0,some .parenthesis⟩}
theorem pending_cleanup_premise_is_needed :
    (UntilAfter.takeNative 1 ordinary names 59 pending).cursor.pending = some .parenthesis ∧
    (UntilAfter.takeReference 1 ordinary (PublicHistory.initialReference pending)).cursor.pending = none := by
  decide +kernel

def wide (p : Nat) : Lexeme := ⟨.other,⟨p+2,none⟩⟩
theorem arbitrary_nonascii_mask_is_not_native :
    ¬ UntilAfter.requested 195 ∧
    (UntilAfter.finishNative [195,169] wide names [] initial).cursor.position = 1 ∧
    (UntilAfter.finishReference [195,169] wide [] [195] initialRef).cursor.position = 2 := by
  unfold UntilAfter.requested
  decide +kernel

def provider (family : ByteLex.Family) (xs : List Byte) : Nat :=
  match family with
  | .whitespace => (xs.takeWhile URLScan.nativeWhitespace).length
  | .punctuation => if [33,44,59].contains (xs.head?.getD 0) then 1 else 0
  | _ => 0

def run (bytes outer extra : List Byte) (stop : Bool) (count : Nat) :
    Bool × Nat × Option Block × Bool :=
  let result := UntilAfter.native bytes (ByteLex.read provider bytes) names extra stop
    (fun stops => .callback (List.replicate count (.next stops)) (fun _ => false))
    ⟨initial,outer,0,75⟩
  (result.1,result.2.core.cursor.position,result.2.core.cursor.pending,seen result.2.core.mode)

theorem semicolon_consumes_one_byte : run [59, 116, 97, 105, 108] [] [59] false 0 = (false,1,none,false) := by
  decide +kernel

theorem overlap_belongs_to_outer : run [59, 116, 97, 105, 108] [59] [59] false 0 = (false,0,none,false) := by
  decide +kernel

theorem outer_close_is_unread : run [125, 116, 97, 105, 108] [125] [59] false 0 = (false,0,none,false) := by
  decide +kernel

theorem stop_keeps_pending_function : run [98, 97, 100, 40, 118, 97, 114, 40, 45, 45, 120, 41, 41, 59, 116, 97, 105, 108] [] [59] true 1 = (false,4,some .parenthesis,false) := by
  decide +kernel

theorem consume_recovers_function : run [98, 97, 100, 40, 118, 97, 114, 40, 45, 45, 120, 41, 41, 59, 116, 97, 105, 108] [] [59] false 1 = (false,14,none,true) := by
  decide +kernel

theorem curly_ignores_mismatched_close : run [123, 118, 97, 114, 40, 45, 45, 120, 41, 93, 125, 116, 97, 105, 108] [] [123] false 0 = (false,11,none,true) := by
  decide +kernel

theorem unterminated_curly_reaches_eof : run [123, 118, 97, 114, 40, 45, 45, 120, 41] [] [123] false 0 = (false,9,none,true) := by
  decide +kernel

end AfterChallenges
