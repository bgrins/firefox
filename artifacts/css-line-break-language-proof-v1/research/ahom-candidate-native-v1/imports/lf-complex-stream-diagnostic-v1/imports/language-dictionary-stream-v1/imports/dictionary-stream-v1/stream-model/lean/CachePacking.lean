import SegmentCache

namespace LanguageBreak

structure PackedBreaks where
  stored : List BreakKind
  zeros : Nat
  deriving DecidableEq, Repr

def PackedBreaks.decode (packed : PackedBreaks) : List BreakKind :=
  packed.stored ++ List.replicate packed.zeros .none

def packBreaks : List BreakKind → PackedBreaks
  | [] => ⟨[],0⟩
  | value::rest =>
    let tail := packBreaks rest
    if tail.stored = [] ∧ value = .none then ⟨[],tail.zeros+1⟩
    else ⟨value::tail.stored,tail.zeros⟩

theorem packing_preserves (values : List BreakKind) : (packBreaks values).decode = values := by
  induction values with
  | nil => rfl
  | cons value rest ih =>
    simp only [packBreaks]
    split
    next empty =>
      rcases empty with ⟨stored,rfl⟩
      have tail : List.replicate (packBreaks rest).zeros BreakKind.none = rest := by
        simpa [PackedBreaks.decode,stored] using ih
      simp [PackedBreaks.decode,List.replicate_succ,tail]
    next nonempty =>
      simpa [PackedBreaks.decode] using congrArg (List.cons value) ih

theorem packing_length (values : List BreakKind) :
    (packBreaks values).stored.length + (packBreaks values).zeros = values.length := by
  have same := congrArg List.length (packing_preserves values)
  simpa [PackedBreaks.decode] using same

theorem stored_stored_in_range (values : List BreakKind) :
    (packBreaks values).stored.length ≤ values.length := by
  have same := packing_length values
  omega

theorem copy_and_fill_exact (values : List BreakKind) :
    (packBreaks values).stored ++
      List.replicate (values.length - (packBreaks values).stored.length) .none = values := by
  have count : values.length - (packBreaks values).stored.length = (packBreaks values).zeros := by
    have same := packing_length values
    omega
  rw [count]
  exact packing_preserves values

end LanguageBreak
