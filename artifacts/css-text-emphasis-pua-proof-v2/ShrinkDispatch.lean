import LigatureData

namespace Emphasis.Shrinking
open Run

def forward : Nat → List Bool → Nat
  | index, [] => index
  | index, true::_ => index
  | index, false::rest => forward (index+1) rest

theorem forward_refinement (index : Nat) (cuts : List Bool) :
    forward index cuts = index+leadingSkip cuts := by
  induction cuts generalizing index with
  | nil => simp [forward,leadingSkip]
  | cons b rest ih => cases b <;> simp [forward,leadingSkip,ih,Nat.add_assoc]

def backward : Nat → Nat → List Bool → Nat
  | 0, index, _ => index
  | _, index, [] => index
  | _+1, index, true::_ => index
  | fuel+1, index, false::rest => backward fuel (index-1) rest

theorem backward_refinement (fuel index : Nat) (cuts : List Bool) :
    backward fuel index cuts = index-min fuel (leadingSkip cuts) := by
  induction fuel generalizing index cuts with
  | zero => simp [backward]
  | succ fuel ih =>
    cases cuts with
    | nil => simp [backward,leadingSkip]
    | cons b rest =>
      cases b with
      | true => simp [backward,leadingSkip]
      | false =>
        simp only [backward,ih,leadingSkip]
        omega

def indexShrink (start : Nat) (interior : List Bool) (endBoundary : Bool) : Nat × Nat :=
  let first := forward start interior
  let remaining := interior.drop (first-start)
  let last := backward remaining.length (start+interior.length) (endBoundary::remaining.reverse)
  (first,last)

theorem index_shrink_refinement (start : Nat) (interior : List Bool) (endBoundary : Bool) :
    indexShrink start interior endBoundary = shrink start interior endBoundary := by
  simp only [indexShrink,forward_refinement,Nat.add_sub_cancel_left,backward_refinement,shrink]
  cases endBoundary <;> simp [leadingSkip,trailingSkip]

theorem index_shrink_bounds (start : Nat) (interior : List Bool) (endBoundary : Bool) :
    start ≤ (indexShrink start interior endBoundary).1 ∧
    (indexShrink start interior endBoundary).1 ≤ (indexShrink start interior endBoundary).2 ∧
    (indexShrink start interior endBoundary).2 ≤ start+interior.length := by
  rw [index_shrink_refinement]
  exact shrink_bounds _ _ _

theorem backward_checked_boundary (fuel index : Nat) (cuts : List Bool)
    (indexBound : fuel ≤ index) (length : fuel < cuts.length)
    (nonempty : index-fuel < backward fuel index cuts) :
    cuts[index-backward fuel index cuts]? = some true := by
  induction fuel generalizing index cuts with
  | zero => simp [backward] at nonempty
  | succ fuel ih =>
    cases cuts with
    | nil => simp at length
    | cons boundary rest =>
      cases boundary with
      | true => simp [backward]
      | false =>
        simp only [backward] at nonempty ⊢
        have h := ih (index-1) rest (by omega) (by simp only [List.length_cons] at length; omega) (by omega)
        have bound : backward fuel (index-1) rest ≤ index-1 := by
          rw [backward_refinement]; exact Nat.sub_le _ _
        have offset : index-backward fuel (index-1) rest = (index-1-backward fuel (index-1) rest)+1 := by omega
        rw [offset,List.getElem?_cons_succ]
        exact h

theorem nonempty_start_boundary (start : Nat) (interior : List Bool) (endBoundary : Bool)
    (nonempty : (indexShrink start interior endBoundary).1 < (indexShrink start interior endBoundary).2) :
    (interior.drop ((indexShrink start interior endBoundary).1-start)).head? = some true := by
  have bounds := index_shrink_bounds start interior endBoundary
  have skipBound := leading_bound interior
  have first : (indexShrink start interior endBoundary).1 = start+leadingSkip interior := by
    simp [indexShrink,forward_refinement]
  rw [first,Nat.add_sub_cancel_left]
  rcases leading_remainder interior with empty | boundary
  · have length := congrArg List.length empty
    simp only [List.length_drop,List.length_nil] at length
    omega
  · exact boundary

theorem nonempty_end_boundary (start : Nat) (interior : List Bool) (endBoundary : Bool)
    (nonempty : (indexShrink start interior endBoundary).1 < (indexShrink start interior endBoundary).2) :
    let remaining := interior.drop (leadingSkip interior)
    (endBoundary::remaining.reverse)[start+interior.length-(indexShrink start interior endBoundary).2]? = some true := by
  have skipBound := leading_bound interior
  simp only [indexShrink,forward_refinement,Nat.add_sub_cancel_left] at nonempty ⊢
  apply backward_checked_boundary
  · simp only [List.length_drop]; omega
  · simp
  · simp only [List.length_drop] at nonempty ⊢
    omega

end Emphasis.Shrinking
