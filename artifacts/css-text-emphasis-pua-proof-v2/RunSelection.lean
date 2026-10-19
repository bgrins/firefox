import RunGeometry

set_option linter.unusedVariables false

namespace Emphasis.Selection

def midpoint (start limit : Nat) : Nat := start + (limit-start)/2

theorem midpoint_bounds (start limit : Nat) (gap : 1 < limit-start) :
    start < midpoint start limit ∧ midpoint start limit < limit := by
  have small : (limit-start)/2 < limit-start := Nat.div_lt_self (by omega) (by omega)
  have positive : 0 < (limit-start)/2 := Nat.div_pos (by omega) (by omega)
  simp only [midpoint]
  omega

def upperBound (predicate : Nat → Bool) (start limit : Nat) : Nat :=
  if h : 1 < limit-start then
    let mid := midpoint start limit
    if predicate mid then upperBound predicate mid limit else upperBound predicate start mid
  else start
termination_by limit-start
decreasing_by
  all_goals have bounds := midpoint_bounds start limit h
  all_goals omega

theorem upper_bound_valid (predicate : Nat → Bool) (start limit : Nat)
    (ordered : ∀ i j, i ≤ j → predicate j = true → predicate i = true)
    (nonempty : start < limit) (first : predicate start = true) :
    start ≤ upperBound predicate start limit ∧ upperBound predicate start limit < limit ∧
    predicate (upperBound predicate start limit) = true ∧
    (∀ j, upperBound predicate start limit < j → j < limit → predicate j = false) := by
  rw [upperBound]
  split
  next gap =>
    have bounds := midpoint_bounds start limit gap
    dsimp only
    split
    next yes =>
      have ih := upper_bound_valid predicate (midpoint start limit) limit ordered bounds.2 yes
      exact ⟨by omega,ih.2.1,ih.2.2.1,ih.2.2.2⟩
    next no =>
      have ih := upper_bound_valid predicate start (midpoint start limit) ordered bounds.1 first
      refine ⟨ih.1,by omega,ih.2.2.1,?_⟩
      intro j after before
      by_cases h : j < midpoint start limit
      · exact ih.2.2.2 j after h
      · have notTrue : predicate j ≠ true := by
          intro yes
          have bad := ordered (midpoint start limit) j (by omega) yes
          exact no bad
        cases eq : predicate j <;> simp_all
  next gap =>
    exact ⟨by omega,nonempty,first,by intro j after before; omega⟩
termination_by limit-start
decreasing_by
  all_goals have bounds := midpoint_bounds start limit (by omega)
  all_goals omega

def linearLast (predicate : Nat → Bool) : Nat → Nat → Nat
  | 0, start => start
  | fuel+1, start => if predicate (start+1) then linearLast predicate fuel (start+1) else start

theorem linear_last_valid (predicate : Nat → Bool) (fuel start : Nat)
    (ordered : ∀ i j, i ≤ j → predicate j = true → predicate i = true)
    (first : predicate start = true) :
    start ≤ linearLast predicate fuel start ∧ linearLast predicate fuel start ≤ start+fuel ∧
    predicate (linearLast predicate fuel start) = true ∧
    (∀ j, linearLast predicate fuel start < j → j ≤ start+fuel → predicate j = false) := by
  induction fuel generalizing start with
  | zero => simp only [linearLast, Nat.add_zero]; exact ⟨by omega,by omega,first,by intro j a b; omega⟩
  | succ fuel ih =>
    simp only [linearLast]
    split
    next yes =>
      have h := ih (start+1) yes
      exact ⟨by omega,by omega,h.2.2.1,by intro j a b; exact h.2.2.2 j a (by omega)⟩
    next no =>
      refine ⟨by omega,by omega,first,?_⟩
      intro j after before
      have notTrue : predicate j ≠ true := by
        intro yes
        exact no (ordered (start+1) j (by omega) yes)
      cases eq : predicate j <;> simp_all

theorem binary_linear_correspondence (predicate : Nat → Bool) (start limit : Nat)
    (ordered : ∀ i j, i ≤ j → predicate j = true → predicate i = true)
    (nonempty : start < limit) (first : predicate start = true) :
    upperBound predicate start limit = linearLast predicate (limit-start-1) start := by
  have binary := upper_bound_valid predicate start limit ordered nonempty first
  have linear := linear_last_valid predicate (limit-start-1) start ordered first
  by_cases eq : upperBound predicate start limit = linearLast predicate (limit-start-1) start
  · exact eq
  have neq := eq
  by_cases less : upperBound predicate start limit < linearLast predicate (limit-start-1) start
  · have bad := binary.2.2.2 _ less (by omega)
    simp_all
  · have bad := linear.2.2.2 (upperBound predicate start limit) (by omega) (by omega)
    simp_all

structure Interval where
  first : Nat
  pastEnd : Nat
  deriving DecidableEq, Repr

def clip (request run : Interval) : Interval :=
  ⟨max request.first run.first, min request.pastEnd run.pastEnd⟩

def continues (request run : Interval) : Bool :=
  run.first < request.pastEnd && request.first ≤ run.pastEnd

def nextRuns (request : Interval) : List Interval → List Interval
  | [] => []
  | run::rest =>
    if request.pastEnd ≤ run.first then []
    else if run.pastEnd < request.first then []
    else clip request run :: nextRuns request rest

def referenceNext (request : Interval) (runs : List Interval) : List Interval :=
  (runs.takeWhile (continues request)).map (clip request)

theorem next_runs_refinement (request : Interval) (runs : List Interval) :
    nextRuns request runs = referenceNext request runs := by
  induction runs with
  | nil => rfl
  | cons run rest ih =>
    simp only [nextRuns, referenceNext, List.takeWhile_cons]
    by_cases first : request.pastEnd ≤ run.first
    · simp [first, continues, show ¬ run.first < request.pastEnd by omega]
    · by_cases last : run.pastEnd < request.first
      · simp [first,last,continues,show ¬ request.first ≤ run.pastEnd by omega]
      · simp [first,last,continues,show run.first < request.pastEnd by omega,
          show request.first ≤ run.pastEnd by omega, ih, referenceNext]

def selectedRuns (request : Interval) (runs : List Interval) (index : Nat) : List Interval :=
  match runs.drop index with
  | [] => []
  | first::rest => clip request first :: nextRuns request rest

def referenceRuns (request : Interval) (runs : List Interval) (index : Nat) : List Interval :=
  match runs.drop index with
  | [] => []
  | first::rest => clip request first :: referenceNext request rest

theorem selected_runs_refinement (request : Interval) (runs : List Interval) (index : Nat) :
    selectedRuns request runs index = referenceRuns request runs index := by
  unfold selectedRuns referenceRuns
  cases runs.drop index <;> simp [next_runs_refinement]

def nativeSelection (request : Interval) (runs : List Interval) (predicate : Nat → Bool) : List Interval :=
  if runs.length ≤ 1 then selectedRuns request runs 0
  else if request.first = (runs.getLast?.map Interval.pastEnd).getD 0 then
    selectedRuns request runs (runs.length-1)
  else selectedRuns request runs (upperBound predicate 0 runs.length)

def directSelection (request : Interval) (runs : List Interval) (predicate : Nat → Bool) : List Interval :=
  if runs.length ≤ 1 then referenceRuns request runs 0
  else if request.first = (runs.getLast?.map Interval.pastEnd).getD 0 then
    referenceRuns request runs (runs.length-1)
  else referenceRuns request runs (linearLast predicate (runs.length-1) 0)

theorem font_run_selection_refinement (request : Interval) (runs : List Interval)
    (predicate : Nat → Bool)
    (ordered : ∀ i j, i ≤ j → predicate j = true → predicate i = true)
    (first : predicate 0 = true) :
    nativeSelection request runs predicate = directSelection request runs predicate := by
  unfold nativeSelection directSelection
  split
  · exact selected_runs_refinement _ _ _
  next length =>
    split
    · exact selected_runs_refinement _ _ _
    · rw [binary_linear_correspondence predicate 0 runs.length ordered (by omega) first]
      simp only [Nat.sub_zero]
      exact selected_runs_refinement _ _ _

def rawPredicate (request : Interval) (runs : List Interval) (index : Nat) : Bool :=
  match runs[index]? with
  | none => false
  | some run => run.first ≤ request.first

def OrderedRuns (runs : List Interval) : Prop :=
  ∀ (i j : Nat) (a b : Interval), i ≤ j → runs[i]? = some a → runs[j]? = some b → a.first ≤ b.first

theorem raw_predicate_ordered (request : Interval) (runs : List Interval)
    (ordered : OrderedRuns runs) :
    ∀ i j, i ≤ j → rawPredicate request runs j = true → rawPredicate request runs i = true := by
  intro i j ij yes
  unfold rawPredicate at yes ⊢
  cases hj : runs[j]? with
  | none => simp [hj] at yes
  | some b =>
    have jbound : j < runs.length := by
      exact List.getElem?_eq_some_iff.mp hj |>.1
    have ibound : i < runs.length := by omega
    have hi : runs[i]? = some runs[i] := List.getElem?_eq_getElem ibound
    rw [hi]
    have le := ordered i j runs[i] b ij hi hj
    have y : b.first ≤ request.first := by simpa [hj] using yes
    simpa using (show runs[i].first ≤ request.first by omega)

theorem raw_selection_refinement (request : Interval) (runs : List Interval)
    (ordered : OrderedRuns runs)
    (initial : runs = [] ∨ ∃ first, runs[0]? = some first ∧ first.first = 0) :
    nativeSelection request runs (rawPredicate request runs) =
      directSelection request runs (rawPredicate request runs) := by
  rcases initial with empty | ⟨first,head,zero⟩
  · subst runs; rfl
  · apply font_run_selection_refinement _ _ _ (raw_predicate_ordered _ _ ordered)
    simp [rawPredicate,head,zero]

end Emphasis.Selection
