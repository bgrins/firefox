import SkipRunObservation

namespace HyphenSkipRunTraversal

open HyphenSkipRanges HyphenSkipRunObservation

structure Run where
  original : Nat
  transformed : Nat
  length : Nat
  skipped : Bool
  deriving DecidableEq, Repr

def contribution (r : Run) : List Nat :=
  if r.skipped then [] else List.range' r.transformed r.length

def traverse (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) : List Run :=
  if _active : offset < count ∧ 0 < remaining then
    let observation := observe ranges count offset
    let length := min observation.length remaining
    let rest := if observation.skipped then remaining else remaining-length
    ⟨offset,lookupOriginal ranges offset,length,observation.skipped⟩ ::
      traverse ranges count valid (offset+length) rest
  else []
termination_by count-offset
decreasing_by
  have positive := positive_bounded ranges count offset valid _active.1
  omega

theorem initialized_coordinates (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) (offset remaining : Nat)
    (bounded : offset ≤ count)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count) :
    (traverse ranges count valid offset remaining).flatMap contribution =
      List.range' (lookupOriginal ranges offset) remaining := by
  rw [traverse]
  split
  next active =>
    dsimp only
    have extent := positive_bounded ranges count offset valid active.1
    have amount : min (observe ranges count offset).length remaining ≤
        (observe ranges count offset).length := Nat.min_le_left _ _
    have delta := observed_coordinate_delta ranges count offset
      (min (observe ranges count offset).length remaining) valid active.1 amount
    have nextBound : offset+min (observe ranges count offset).length remaining ≤ count := by omega
    cases kind : (observe ranges count offset).skipped with
    | true =>
      simp only [kind,↓reduceIte] at delta ⊢
      have nextAvailable : lookupOriginal ranges (offset+min (observe ranges count offset).length remaining)+remaining ≤
          lookupOriginal ranges count := by omega
      rw [List.flatMap_cons]
      simp only [contribution,↓reduceIte,List.nil_append]
      rw [initialized_coordinates ranges count valid _ _ nextBound nextAvailable,delta]
      simp
    | false =>
      simp only [kind,Bool.false_eq_true,↓reduceIte] at delta ⊢
      have nextAvailable : lookupOriginal ranges (offset+min (observe ranges count offset).length remaining)+
          (remaining-min (observe ranges count offset).length remaining) ≤ lookupOriginal ranges count := by omega
      rw [List.flatMap_cons]
      simp only [contribution,Bool.false_eq_true,↓reduceIte]
      rw [initialized_coordinates ranges count valid _ _ nextBound nextAvailable,delta,List.range'_append_1]
      congr 1
      omega
  next inactive =>
    have zero : remaining = 0 := by
      by_cases endReached : offset = count
      · subst offset; omega
      · omega
    simp [zero]
termination_by count-offset
decreasing_by all_goals omega

theorem source_reads_bounded (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) (offset remaining : Nat) :
    ∀ run ∈ traverse ranges count valid offset remaining,
      0 < run.length ∧ run.original+run.length ≤ count ∧
        run.original+run.length-1 < count := by
  rw [traverse]
  split
  next active =>
    dsimp only
    intro run member
    rcases List.mem_cons.mp member with same | later
    · subst run
      dsimp only
      have extent := positive_bounded ranges count offset valid active.1
      omega
    · exact source_reads_bounded ranges count valid _ _ run later
  next inactive => simp
termination_by count-offset
decreasing_by
  all_goals
    have extent := positive_bounded ranges count offset valid (by omega)
    omega

theorem split_fixture_valid : WellFormed [⟨0,5,0⟩] 6 :=
  ⟨by change 5 ≤ 6; omega,rfl,True.intro⟩

theorem skipped_span_is_split :
    (traverse [⟨0,5,0⟩] 6 split_fixture_valid 0 1).map Run.length = [1,1,1,1,1,1] := by simp [traverse,observe,Range.finish,Range.nextDelta,lookupOriginal,contribution]

theorem split_span_initializes_once :
    (traverse [⟨0,5,0⟩] 6 split_fixture_valid 0 1).flatMap contribution = [0] := by simp [traverse,observe,Range.finish,Range.nextDelta,lookupOriginal,contribution]

end HyphenSkipRunTraversal
