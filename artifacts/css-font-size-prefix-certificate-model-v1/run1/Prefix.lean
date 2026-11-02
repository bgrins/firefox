import Stability

namespace SizePrefix
open SelectedDeclaration PreparationStability

structure Declaration (S V E : Type) where
  needsBase : Bool
  otherFlags : Bool
  dynamic : Bool
  staticEvaluation : Evaluation S V E

def eligible (base : Bool) (allows : S → Declaration S V E → Bool)
    (state : S) (d : Declaration S V E) : Bool :=
  d.otherFlags && (!d.needsBase || base) && allows state d

def evaluate (dynamicEvaluation : S → Declaration S V E → Evaluation S V E)
    (state : S) (d : Declaration S V E) : Evaluation S V E :=
  if d.dynamic then dynamicEvaluation state d else d.staticEvaluation

def certificate (base : Bool) (allows : S → Declaration S V E → Bool)
    (state : S) : List (Declaration S V E) → Bool
  | [] => true
  | d :: rest =>
      if d.needsBase then false else
      if eligible base allows state d then
        if d.dynamic then false else
        match d.staticEvaluation.next with
        | .rollback next => certificate base allows next rest
        | _ => true
      else certificate base allows state rest

theorem ungated_eligibility (before : Bool) (allows : S → Declaration S V E → Bool)
    (state : S) (d : Declaration S V E) (ungated : d.needsBase = false) :
    eligible true allows state d = eligible before allows state d := by
  simp [eligible, ungated]

theorem certificate_implies_reached_agreement
    (before : Bool) (allows : S → Declaration S V E → Bool)
    (oldDynamic newDynamic : S → Declaration S V E → Evaluation S V E)
    (state : S) (decls : List (Declaration S V E))
    (accepted : certificate before allows state decls = true) :
    ∀ point ∈ visited (eligible before allows) (evaluate oldDynamic) state decls,
      agreesAt (eligible before allows) (eligible true allows)
        (evaluate oldDynamic) (evaluate newDynamic) point := by
  induction decls generalizing state with
  | nil => simp [visited]
  | cons d rest ih =>
      have ungated : d.needsBase = false := by
        cases h : d.needsBase <;> simp_all [certificate]
      have sameEligible := ungated_eligibility before allows state d ungated
      by_cases yes : eligible before allows state d = true
      · have static : d.dynamic = false := by
          cases h : d.dynamic <;> simp_all [certificate]
        have sameEvaluation : evaluate newDynamic state d = evaluate oldDynamic state d := by
          simp [evaluate, static]
        intro point member
        cases outcome : d.staticEvaluation.next with
        | rollback next =>
            have tailAccepted : certificate before allows next rest = true := by
              simpa [certificate, ungated, yes, static, outcome] using accepted
            have members : point = (state, d) ∨
                point ∈ visited (eligible before allows) (evaluate oldDynamic) next rest := by
              simpa [visited, yes, evaluate, static, outcome] using member
            rcases members with head | tail
            · subst point; exact ⟨sameEligible, fun _ => sameEvaluation⟩
            · exact ih next tailAccepted point tail
        | terminal value =>
            have head : point = (state, d) := by
              simpa [visited, yes, evaluate, static, outcome] using member
            subst point; exact ⟨sameEligible, fun _ => sameEvaluation⟩
        | blocked =>
            have head : point = (state, d) := by
              simpa [visited, yes, evaluate, static, outcome] using member
            subst point; exact ⟨sameEligible, fun _ => sameEvaluation⟩
      · have no : eligible before allows state d = false := Bool.eq_false_iff.mpr yes
        have tailAccepted : certificate before allows state rest = true := by
          simpa [certificate, ungated, no] using accepted
        intro point member
        have members : point = (state, d) ∨
            point ∈ visited (eligible before allows) (evaluate oldDynamic) state rest := by
          simpa [visited, no] using member
        rcases members with head | tail
        · subst point; exact ⟨sameEligible, by simp [no]⟩
        · exact ih state tailAccepted point tail

theorem checked_prefix_preserves_selection_and_reads
    (before : Bool) (allows : S → Declaration S V E → Bool)
    (oldDynamic newDynamic : S → Declaration S V E → Evaluation S V E)
    (state : S) (decls : List (Declaration S V E))
    (accepted : certificate before allows state decls = true) :
    scan (eligible true allows) (evaluate newDynamic) state decls =
      scan (eligible before allows) (evaluate oldDynamic) state decls := by
  apply scan_eq_of_reached_agreement
  exact certificate_implies_reached_agreement before allows oldDynamic newDynamic state decls accepted

def winner (n : Nat) (gate : Bool := false) (dynamic : Bool := false) : Declaration Nat Nat Nat :=
  ⟨gate, true, dynamic, ⟨.terminal (some n), [n]⟩⟩
def rollback : Declaration Nat Nat Nat := ⟨false, true, false, ⟨.rollback 1, [7]⟩⟩
def allow (s : Nat) (d : Declaration Nat Nat Nat) : Bool :=
  !(s == 1 && d.staticEvaluation.reads == [8])
def oldDynamic (_ : Nat) (_ : Declaration Nat Nat Nat) : Evaluation Nat Nat Nat :=
  ⟨.terminal (some 90), [90]⟩
def newDynamic (_ : Nat) (_ : Declaration Nat Nat Nat) : Evaluation Nat Nat Nat :=
  ⟨.terminal (some 91), [91]⟩

theorem skipped_higher_gate_rejected :
    certificate false allow 0 [winner 8 true, winner 20] = false := by decide

theorem lower_unreached_gate_allowed :
    certificate false allow 0 [winner 20, winner 8 true] = true := by decide

theorem rollback_prefix_preserves_exact_reads :
    certificate false allow 0 [rollback, winner 8, winner 20, winner 99 true] = true ∧
    (scan (eligible false allow) (evaluate oldDynamic) 0
      [rollback, winner 8, winner 20, winner 99 true]).reads = [7, 20] := by decide

theorem dynamic_eligible_rejected :
    certificate false allow 0 [winner 20 false true] = false := by decide

theorem dynamic_rollback_skipped_allowed :
    certificate false allow 0 [rollback, winner 8 false true, winner 20] = true := by decide

theorem unchecked_higher_gate_changes_selection :
    (scan (eligible false allow) (evaluate oldDynamic) 0 [winner 8 true, winner 20]).reads = [20] ∧
    (scan (eligible true allow) (evaluate newDynamic) 0 [winner 8 true, winner 20]).reads = [8] := by decide

end SizePrefix
