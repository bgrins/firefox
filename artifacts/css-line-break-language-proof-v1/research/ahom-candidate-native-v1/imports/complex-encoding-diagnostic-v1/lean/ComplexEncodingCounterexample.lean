import Std

namespace LanguageBreak.ComplexEncoding

structure Outcome where
  position : Nat
  remainingWidths : List Nat
  cache : List Nat
  deriving DecidableEq, Repr

def seek (target : Nat) (tail : List Nat) (consumed position : Nat) : List Nat → Outcome
  | [] => ⟨position,[],[]⟩
  | width::rest =>
    if consumed=target then ⟨position,width::rest,tail.map (·-consumed)⟩
    else seek target tail (consumed+width) (position+width) rest

def next (consumed position : Nat) (widths cache : List Nat) : Option Outcome :=
  match cache with
  | [] => none
  | first::tail => some (seek first tail consumed position widths)

theorem cast_changes_complex_query :
    [0x0e01,0x11700,0x0e01].map (fun value : Nat => value%65536) = [0x0e01,0x1700,0x0e01] := by decide

theorem contracted_cache_is_not_aligned :
    next 1 1 [2,1] [1,2,3] = some ⟨1,[2,1],[1,2]⟩ ∧
    next 0 1 [2,1] [1,2] = some ⟨4,[],[]⟩ := by decide

theorem source_unit_cache_preserves_boundary :
    next 1 1 [2,1] [1,3,4] = some ⟨1,[2,1],[2,3]⟩ ∧
    next 0 1 [2,1] [2,3] = some ⟨3,[1],[1]⟩ ∧
    next 0 3 [1] [1] = some ⟨4,[],[]⟩ := by decide

end LanguageBreak.ComplexEncoding
