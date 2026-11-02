import Selection

namespace PreparationStability
open SelectedDeclaration

def visited (eligible : S → D → Bool) (evaluate : S → D → Evaluation S V E)
    (state : S) : List D → List (S × D)
  | [] => []
  | d :: rest =>
      (state, d) :: if eligible state d then
        match (evaluate state d).next with
        | .rollback next => visited eligible evaluate next rest
        | _ => []
      else visited eligible evaluate state rest

def agreesAt (eligible eligible' : S → D → Bool)
    (evaluate evaluate' : S → D → Evaluation S V E) (point : S × D) : Prop :=
  eligible' point.1 point.2 = eligible point.1 point.2 ∧
    (eligible point.1 point.2 = true → evaluate' point.1 point.2 = evaluate point.1 point.2)

theorem scan_eq_of_reached_agreement
    (eligible eligible' : S → D → Bool)
    (evaluate evaluate' : S → D → Evaluation S V E)
    (state : S) (decls : List D)
    (stable : ∀ point ∈ visited eligible evaluate state decls,
      agreesAt eligible eligible' evaluate evaluate' point) :
    scan eligible' evaluate' state decls = scan eligible evaluate state decls := by
  induction decls generalizing state with
  | nil => rfl
  | cons d rest ih =>
      obtain ⟨sameEligible, sameEvaluation⟩ := stable (state, d) (by simp [visited])
      by_cases yes : eligible state d = true
      · have same := sameEvaluation yes
        cases step : (evaluate state d).next with
        | terminal value => simp [scan, sameEligible, yes, same, step]
        | blocked => simp [scan, sameEligible, yes, same, step]
        | rollback next =>
            have tail : ∀ point ∈ visited eligible evaluate next rest,
                agreesAt eligible eligible' evaluate evaluate' point := by
              intro point member
              exact stable point (by simp [visited, yes, step, member])
            simpa [scan, sameEligible, yes, same, step] using
              congrArg (prepend d (evaluate state d).reads) (ih next tail)
      · have no : eligible state d = false := Bool.eq_false_iff.mpr yes
        have tail : ∀ point ∈ visited eligible evaluate state rest,
            agreesAt eligible eligible' evaluate evaluate' point := by
          intro point member
          exact stable point (by simp [visited, no, member])
        simpa [scan, sameEligible, no] using ih state tail

def beforeEligibility (_ : Unit) (d : Nat) : Bool := d != 0
def afterEligibility (_ : Unit) (_ : Nat) : Bool := true

def literal (_ : Unit) (d : Nat) : Evaluation Unit Nat Nat :=
  ⟨.terminal (some d), [d]⟩

theorem retained_entries_can_stay_eligible_while_selection_changes :
    (∀ d ∈ (scan beforeEligibility literal () [0, 1]).evaluated,
      afterEligibility () d = true) ∧
    scan beforeEligibility literal () [0, 1] = ⟨.terminal (some 1), [1], [1]⟩ ∧
    scan afterEligibility literal () [0, 1] = ⟨.terminal (some 0), [0], [0]⟩ := by decide

def beforeAdjustment (_ : Unit) (d : Nat) : Evaluation Unit Nat Nat :=
  if d = 0 then ⟨.rollback (), [10]⟩ else literal () d

def afterAdjustment (_ : Unit) (d : Nat) : Evaluation Unit Nat Nat :=
  if d = 0 then ⟨.terminal (some 0), [10]⟩ else literal () d

theorem unchanged_eligibility_does_not_freeze_adjustment :
    scan afterEligibility beforeAdjustment () [0, 1] =
      ⟨.terminal (some 1), [0, 1], [10, 1]⟩ ∧
    scan afterEligibility afterAdjustment () [0, 1] =
      ⟨.terminal (some 0), [0], [10]⟩ := by decide

def unrelatedDrift (_ : Unit) (d : Nat) : Evaluation Unit Nat Nat :=
  if d = 0 then literal () d else ⟨.blocked, [99]⟩

theorem unvisited_evaluator_may_change (tail : List Nat) :
    scan afterEligibility unrelatedDrift () (0 :: tail) =
      scan afterEligibility literal () (0 :: tail) := by
  apply scan_eq_of_reached_agreement afterEligibility afterEligibility literal unrelatedDrift
  intro point member
  have only : point = ((), 0) := by simpa [visited, afterEligibility, literal] using member
  subst point
  simp [agreesAt, unrelatedDrift]

end PreparationStability
