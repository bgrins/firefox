import CssSemantics.VariablesRank

namespace CssSemantics.VariableBindings

def lookup (bindings : VariableBindings Token) (name : String) : Option (VariableExpr Token) :=
  bindings.entries.lookup name

theorem lookup_iff (bindings : VariableBindings Token) (name : String)
    (expression : VariableExpr Token) :
    bindings.lookup name = some expression ↔ (name, expression) ∈ bindings.entries := by
  have general : ∀ (entries : List (String × VariableExpr Token)), (entries.map Prod.fst).Nodup →
      (entries.lookup name = some expression ↔ (name, expression) ∈ entries) := by
    intro entries unique
    induction entries with
    | nil => simp
    | cons entry rest ih =>
      rcases entry with ⟨key, value⟩
      simp only [List.map_cons, List.nodup_cons] at unique
      by_cases equal : name = key
      · subst key
        have excluded : (name, expression) ∉ rest := by
          intro member
          exact unique.1 (List.mem_map.mpr ⟨(name, expression), member, rfl⟩)
        simp [excluded, eq_comm]
      · have test : (name == key) = false := by simp [equal]
        simp [List.lookup_cons, test, equal, ih unique.2]
  exact general bindings.entries bindings.unique

theorem lookup_none_iff (bindings : VariableBindings Token) (name : String) :
    bindings.lookup name = none ↔ ∀ expression, (name, expression) ∉ bindings.entries := by
  constructor
  · intro h expression member
    have := (bindings.lookup_iff name expression).mpr member
    simp [h] at this
  · intro h
    cases equal : bindings.lookup name with
    | none => rfl
    | some expression => exact False.elim (h expression ((bindings.lookup_iff _ _).mp equal))

theorem lookup_congr (left right : VariableBindings Token)
    (same : ∀ name expression, (name, expression) ∈ left.entries ↔ (name, expression) ∈ right.entries)
    (name : String) : left.lookup name = right.lookup name := by
  cases h : left.lookup name with
  | none =>
    exact ((right.lookup_none_iff name).mpr
      (fun expression member => (left.lookup_none_iff name).mp h expression ((same _ _).mpr member))).symm
  | some expression =>
    exact ((right.lookup_iff name expression).mpr ((same _ _).mp ((left.lookup_iff _ _).mp h))).symm

def computeWithCompletion (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token)) (name : String) : Option (List Token) :=
  if bindings.cyclicBool name = true then none
  else match bindings.lookup name with
    | none => inherited name
    | some expression => complete name (expression.substitute fun target =>
        if _hdep : bindings.dependsBool name target = true then
          if _hcycle : bindings.cyclicBool target = true then none
          else bindings.computeWithCompletion complete inherited target
        else none)
termination_by bindings.rank name
decreasing_by
  exact bindings.rank_decreases ((bindings.dependsBool_iff _ _).mp _hdep)
    (fun h => _hcycle ((bindings.cyclicBool_iff _).mpr h))

theorem computeWithCompletion_cyclic (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token)) (name : String)
    (cyclic : bindings.Cyclic name) : bindings.computeWithCompletion complete inherited name = none := by
  rw [computeWithCompletion]
  simp [(bindings.cyclicBool_iff name).mpr cyclic]

theorem computeWithCompletion_missing (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token)) (name : String)
    (missing : bindings.lookup name = none) : bindings.computeWithCompletion complete inherited name = inherited name := by
  have notCycle : bindings.cyclicBool name ≠ true := by
    intro cycle
    obtain ⟨expression, member⟩ := bindings.cyclic_declared name
      ((bindings.cyclicBool_iff name).mp cycle)
    exact (bindings.lookup_none_iff name).mp missing expression member
  rw [computeWithCompletion]
  simp [missing, notCycle]

theorem computeWithCompletion_bound (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token)) (name : String)
    (acyclic : ¬bindings.Cyclic name) (bound : bindings.lookup name = some expression) :
    bindings.computeWithCompletion complete inherited name =
      complete name (expression.substitute (bindings.computeWithCompletion complete inherited)) := by
  rw [computeWithCompletion]
  have notCycle : bindings.cyclicBool name ≠ true := fun h => acyclic ((bindings.cyclicBool_iff _).mp h)
  simp only [notCycle, bound]
  apply congrArg (complete name)
  apply expression.substitute_congr
  intro target reference
  have dependency := (bindings.dependsBool_iff name target).mpr
    ⟨expression, (bindings.lookup_iff _ _).mp bound, reference⟩
  simp only [dependency, ↓reduceDIte]
  split
  next cycle => exact (bindings.computeWithCompletion_cyclic complete inherited target ((bindings.cyclicBool_iff _).mp cycle)).symm
  next => rfl

inductive ComputedWithCompletion (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token)) : String → Option (List Token) → Prop where
  | cyclic : bindings.Cyclic name → ComputedWithCompletion bindings complete inherited name none
  | missing : bindings.lookup name = none → ComputedWithCompletion bindings complete inherited name (inherited name)
  | bound : ¬bindings.Cyclic name → bindings.lookup name = some expression →
      (∀ target, expression.References target → ComputedWithCompletion bindings complete inherited target (environment target)) →
      VariableExpr.Substitutes environment expression value → ComputedWithCompletion bindings complete inherited name (complete name value)

theorem computeWithCompletion_spec (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token)) (name : String) :
    bindings.ComputedWithCompletion complete inherited name (bindings.computeWithCompletion complete inherited name) := by
  by_cases cycle : bindings.Cyclic name
  · rw [bindings.computeWithCompletion_cyclic complete inherited name cycle]
    exact .cyclic cycle
  · cases bound : bindings.lookup name with
    | none => rw [bindings.computeWithCompletion_missing complete inherited name bound]; exact .missing bound
    | some expression =>
      rw [bindings.computeWithCompletion_bound complete inherited name cycle bound]
      apply ComputedWithCompletion.bound (environment := bindings.computeWithCompletion complete inherited) cycle bound
      · intro target reference
        by_cases targetCycle : bindings.Cyclic target
        · rw [bindings.computeWithCompletion_cyclic complete inherited target targetCycle]; exact .cyclic targetCycle
        · exact bindings.computeWithCompletion_spec complete inherited target
      · exact expression.substitute_spec (bindings.computeWithCompletion complete inherited)
termination_by bindings.rank name
decreasing_by
  exact bindings.rank_decreases ⟨expression, (bindings.lookup_iff _ _).mp bound, reference⟩ targetCycle

theorem ComputedWithCompletion.result {bindings : VariableBindings Token}
    {complete : String → Option (List Token) → Option (List Token)}
    {inherited : String → Option (List Token)} (h : bindings.ComputedWithCompletion complete inherited name value) : bindings.computeWithCompletion complete inherited name = value := by
  induction h with
  | cyclic h => exact bindings.computeWithCompletion_cyclic complete inherited _ h
  | missing h => exact bindings.computeWithCompletion_missing complete inherited _ h
  | bound acyclic bound dependencies substituted ih =>
    rw [bindings.computeWithCompletion_bound complete inherited _ acyclic bound]
    exact congrArg (complete _) ((VariableExpr.substitute_congr _ _ _ ih).trans substituted.result)

theorem computeWithCompletion_iff (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token)) (name : String)
    (value : Option (List Token)) :
    bindings.computeWithCompletion complete inherited name = value ↔ bindings.ComputedWithCompletion complete inherited name value := by
  constructor
  · rintro rfl; exact bindings.computeWithCompletion_spec complete inherited name
  · exact ComputedWithCompletion.result

theorem ComputedWithCompletion.unique {bindings : VariableBindings Token}
    {complete : String → Option (List Token) → Option (List Token)}
    {inherited : String → Option (List Token)} (first : bindings.ComputedWithCompletion complete inherited name a) (second : bindings.ComputedWithCompletion complete inherited name b) : a = b :=
  first.result.symm.trans second.result

theorem computedWithCompletion_transfer (left right : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token))
    (same : ∀ name expression, (name, expression) ∈ left.entries ↔ (name, expression) ∈ right.entries)
    (h : left.ComputedWithCompletion complete inherited name value) : right.ComputedWithCompletion complete inherited name value := by
  have edges : ∀ source target, left.Depends source target ↔ right.Depends source target := by
    intro source target
    simp only [Depends, same]
  have cycles : ∀ name, left.Cyclic name ↔ right.Cyclic name := by
    intro name
    rw [← left.cyclicBool_iff, ← right.cyclicBool_iff, left.cycles_congr right edges]
  induction h with
  | cyclic h => exact .cyclic ((cycles _).mp h)
  | missing h => exact .missing ((left.lookup_congr right same _).symm.trans h)
  | bound acyclic bound dependencies substituted ih =>
    exact .bound (fun h => acyclic ((cycles _).mpr h))
      ((left.lookup_congr right same _).symm.trans bound) ih substituted

theorem computeWithCompletion_congr (left right : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token))
    (inherited : String → Option (List Token))
    (same : ∀ name expression, (name, expression) ∈ left.entries ↔ (name, expression) ∈ right.entries)
    (name : String) : left.computeWithCompletion complete inherited name = right.computeWithCompletion complete inherited name :=
  (computedWithCompletion_transfer left right complete inherited same (left.computeWithCompletion_spec complete inherited name)).result.symm

def computeWithBase (bindings : VariableBindings Token)
    (inherited : String → Option (List Token)) (name : String) : Option (List Token) :=
  bindings.computeWithCompletion (fun _ value => value) inherited name

abbrev ComputedWithBase (bindings : VariableBindings Token)
    (inherited : String → Option (List Token)) : String → Option (List Token) → Prop :=
  bindings.ComputedWithCompletion (fun _ value => value) inherited

theorem computeWithBase_eq_completion (bindings : VariableBindings Token)
    (inherited : String → Option (List Token)) (name : String) :
    bindings.computeWithBase inherited name =
      bindings.computeWithCompletion (fun _ value => value) inherited name := rfl

theorem computeWithBase_cyclic (bindings : VariableBindings Token)
    (inherited : String → Option (List Token)) (name : String)
    (cyclic : bindings.Cyclic name) : bindings.computeWithBase inherited name = none :=
  bindings.computeWithCompletion_cyclic _ inherited name cyclic

theorem computeWithBase_missing (bindings : VariableBindings Token)
    (inherited : String → Option (List Token)) (name : String)
    (missing : bindings.lookup name = none) : bindings.computeWithBase inherited name = inherited name :=
  bindings.computeWithCompletion_missing _ inherited name missing

theorem computeWithBase_bound (bindings : VariableBindings Token)
    (inherited : String → Option (List Token)) (name : String)
    (acyclic : ¬bindings.Cyclic name) (bound : bindings.lookup name = some expression) :
    bindings.computeWithBase inherited name = expression.substitute (bindings.computeWithBase inherited) :=
  bindings.computeWithCompletion_bound _ inherited name acyclic bound

theorem computeWithBase_spec (bindings : VariableBindings Token)
    (inherited : String → Option (List Token)) (name : String) :
    bindings.ComputedWithBase inherited name (bindings.computeWithBase inherited name) :=
  bindings.computeWithCompletion_spec _ inherited name

theorem ComputedWithBase.result {bindings : VariableBindings Token}
    {inherited : String → Option (List Token)} (h : bindings.ComputedWithBase inherited name value) :
    bindings.computeWithBase inherited name = value :=
  ComputedWithCompletion.result h

theorem computeWithBase_iff (bindings : VariableBindings Token)
    (inherited : String → Option (List Token)) (name : String) (value : Option (List Token)) :
    bindings.computeWithBase inherited name = value ↔ bindings.ComputedWithBase inherited name value :=
  bindings.computeWithCompletion_iff _ inherited name value

theorem ComputedWithBase.unique {bindings : VariableBindings Token}
    {inherited : String → Option (List Token)} (first : bindings.ComputedWithBase inherited name a)
    (second : bindings.ComputedWithBase inherited name b) : a = b :=
  ComputedWithCompletion.unique first second

theorem computedWithBase_transfer (left right : VariableBindings Token)
    (inherited : String → Option (List Token))
    (same : ∀ name expression, (name, expression) ∈ left.entries ↔ (name, expression) ∈ right.entries)
    (h : left.ComputedWithBase inherited name value) : right.ComputedWithBase inherited name value :=
  computedWithCompletion_transfer left right _ inherited same h

theorem computeWithBase_congr (left right : VariableBindings Token)
    (inherited : String → Option (List Token))
    (same : ∀ name expression, (name, expression) ∈ left.entries ↔ (name, expression) ∈ right.entries)
    (name : String) : left.computeWithBase inherited name = right.computeWithBase inherited name :=
  computeWithCompletion_congr left right _ inherited same name

theorem computeWithBase_base_congr (bindings : VariableBindings Token)
    (left right : String → Option (List Token)) (same : ∀ name, left name = right name)
    (name : String) : bindings.computeWithBase left name = bindings.computeWithBase right name := by
  have equal : left = right := funext same
  rw [equal]

end CssSemantics.VariableBindings
