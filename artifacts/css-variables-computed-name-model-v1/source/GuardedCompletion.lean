import CssSemantics.GuardedExpr
import CssSemantics.GuardedState
import CssSemantics.VariablesBase
import CssSemantics.GuardedSupport

namespace CssSemantics
namespace GuardedCompletion

open GuardedSolver


def resolve (complete : String → Option (List Token) → Option (List Token)) (base : String → Option (List Token))
    (remaining : List (String × VariableExpr Token)) (active marked : List String)
    (name : String) : Option (List Token) × List String :=
  if name ∈ active then (none, GuardedState.markCycle active marked name)
  else match _found : remaining.lookup name with
    | none => (base name, marked)
    | some expression =>
        let result := GuardedExpr.evaluate
          (fun marks target => resolve complete base (remove remaining name) (name :: active) marks target)
          marked expression
        (if name ∈ result.2 then none else complete name result.1, GuardedState.pop name result.2)
termination_by remaining.length
  decreasing_by exact remove_length_lt remaining _found

mutual
inductive Resolves (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token)) (base : String → Option (List Token)) :
    List String → List String → String → Option (List Token) → List String → Prop where
  | repeated : name ∈ active → Resolves bindings complete base active marked name none
      (GuardedState.markCycle active marked name)
  | missing : name ∉ active → bindings.lookup name = none →
      Resolves bindings complete base active marked name (base name) marked
  | bound : name ∉ active → bindings.lookup name = some expression →
      Evaluates bindings complete base (name :: active) marked expression value finish →
      Resolves bindings complete base active marked name
        (if name ∈ finish then none else complete name value) (GuardedState.pop name finish)
inductive Evaluates (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token)) (base : String → Option (List Token)) :
    List String → List String → VariableExpr Token → Option (List Token) → List String → Prop where
  | literal : Evaluates bindings complete base active marked (.literal tokens) (some tokens) marked
  | append : Evaluates bindings complete base active start left first middle →
      Evaluates bindings complete base active middle right second finish →
      Evaluates bindings complete base active start (.append left right) (GuardedExpr.combine first second) finish
  | reference : Resolves bindings complete base active start name value finish →
      Evaluates bindings complete base active start (.reference name) value finish
  | fallbackValue : Resolves bindings complete base active start name (some tokens) finish →
      Evaluates bindings complete base active start (.fallback name expression) (some tokens) finish
  | fallback : Resolves bindings complete base active start name none middle →
      Evaluates bindings complete base active middle expression value finish →
      Evaluates bindings complete base active start (.fallback name expression) value finish
end

variable {Token : Type}
variable {complete : String → Option (List Token) → Option (List Token)}
variable {bindings : VariableBindings Token} {base : String → Option (List Token)}

theorem evaluates_iff_generic (expression : VariableExpr Token) (active start : List String)
    (value : Option (List Token)) (finish : List String) :
    Evaluates bindings complete base active start expression value finish ↔
      GuardedExpr.Evaluates (Resolves bindings complete base active) start expression value finish := by
  induction expression generalizing start value finish with
  | literal tokens =>
    constructor <;> intro h <;> cases h <;> exact .literal
  | append left right ihLeft ihRight =>
    constructor
    · intro h
      cases h with
      | append first second => exact .append ((ihLeft _ _ _).mp first) ((ihRight _ _ _).mp second)
    · intro h
      cases h with
      | append first second => exact .append ((ihLeft _ _ _).mpr first) ((ihRight _ _ _).mpr second)
  | reference name =>
    constructor <;> intro h <;> cases h with
    | reference h => exact .reference h
  | fallback name expression ih =>
    constructor
    · intro h
      cases h with
      | fallbackValue h => exact .fallbackValue h
      | fallback h next => exact .fallback h ((ih _ _ _).mp next)
    · intro h
      cases h with
      | fallbackValue h => exact .fallbackValue h
      | fallback h next => exact .fallback h ((ih _ _ _).mpr next)


theorem resolve_iff (remaining : List (String × VariableExpr Token))
    (active : List String)
    (agreement : ∀ name, name ∉ active → remaining.lookup name = bindings.lookup name)
    (marked : List String) (name : String) (value : Option (List Token)) (finish : List String) :
    resolve complete base remaining active marked name = (value, finish) ↔
      Resolves bindings complete base active marked name value finish := by
  rw [resolve]
  by_cases repeated : name ∈ active
  · simp only [repeated, ↓reduceIte]
    constructor
    · intro h; cases h; exact .repeated repeated
    · intro h
      cases h with
      | repeated => rfl
      | missing absent _ => exact False.elim (absent repeated)
      | bound absent _ _ => exact False.elim (absent repeated)
  · simp only [repeated, ↓reduceIte]
    cases found : remaining.lookup name with
    | none =>
      simp only
      have absent : bindings.lookup name = none := (agreement name repeated).symm.trans found
      constructor
      · intro h; cases h; exact .missing repeated absent
      · intro h
        cases h with
        | repeated member => exact False.elim (repeated member)
        | missing => rfl
        | bound _ lookup _ => simp [absent] at lookup
    | some expression =>
      simp only
      have declared : bindings.lookup name = some expression := (agreement name repeated).symm.trans found
      have smallerAgreement : ∀ target, target ∉ name :: active →
          (remove remaining name).lookup target = bindings.lookup target := by
        intro target outside
        have different : target ≠ name := fun equal => outside (List.mem_cons.mpr (Or.inl equal))
        exact (remove_lookup_other remaining different).trans
          (agreement target (fun h => outside (List.mem_cons_of_mem _ h)))
      have inner : ∀ marks target result final,
          resolve complete base (remove remaining name) (name :: active) marks target = (result, final) ↔
            Resolves bindings complete base (name :: active) marks target result final :=
        fun marks target result final => resolve_iff (remove remaining name) (name :: active)
          smallerAgreement marks target result final
      have body : ∀ result final,
          GuardedExpr.evaluate (fun marks target => resolve complete base (remove remaining name)
            (name :: active) marks target) marked expression = (result, final) ↔
          Evaluates bindings complete base (name :: active) marked expression result final :=
        fun result final => (GuardedExpr.evaluate_iff inner expression marked result final).trans
          (evaluates_iff_generic expression (name :: active) marked result final).symm
      constructor
      · intro h
        generalize outcome : GuardedExpr.evaluate
          (fun marks target => resolve complete base (remove remaining name) (name :: active) marks target)
          marked expression = result at h ⊢
        rcases result with ⟨tokens, marks⟩
        cases h
        exact .bound repeated declared ((body tokens marks).mp outcome)
      · intro h
        cases h with
        | repeated member => exact False.elim (repeated member)
        | missing _ lookup => simp [declared] at lookup
        | bound _ lookup evaluation =>
          have same := Option.some.inj (declared.symm.trans lookup)
          subst same
          rw [(body _ _).mpr evaluation]
termination_by remaining.length
  decreasing_by exact remove_length_lt remaining found

theorem resolve_marks (remaining : List (String × VariableExpr Token))
    (active marked : List String) (name : String)
    (contained : ∀ mark, mark ∈ marked → mark ∈ active) :
    (∀ mark, mark ∈ (resolve complete base remaining active marked name).2 → mark ∈ active) ∧
    (∀ mark, mark ∈ marked → mark ∈ (resolve complete base remaining active marked name).2) := by
  rw [resolve]
  by_cases repeated : name ∈ active
  · simp only [repeated, ↓reduceIte]
    exact ⟨GuardedState.markCycle_subset active marked name contained,
      GuardedState.markCycle_preserves active marked name⟩
  · simp only [repeated, ↓reduceIte]
    cases found : remaining.lookup name with
    | none => exact ⟨contained, fun _ h => h⟩
    | some expression =>
      let invariant := fun marks : List String =>
        (∀ mark, mark ∈ marks → mark ∈ name :: active) ∧
        (∀ mark, mark ∈ marked → mark ∈ marks)
      have preservation : ∀ marks target, invariant marks →
          invariant (resolve complete base (remove remaining name) (name :: active) marks target).2 := by
        intro marks target h
        have next := resolve_marks (remove remaining name) (name :: active) marks target h.1
        exact ⟨next.1, fun mark old => next.2 mark (h.2 mark old)⟩
      have initial : invariant marked :=
        ⟨fun mark h => List.mem_cons_of_mem _ (contained mark h), fun _ h => h⟩
      have final := GuardedExpr.evaluate_preserves invariant preservation expression marked initial
      constructor
      · exact GuardedState.pop_subset_tail name active _ final.1
      · intro mark old
        apply (GuardedState.mem_pop name mark _).mpr
        refine ⟨final.2 mark old, ?_⟩
        intro equal
        exact repeated (equal ▸ contained mark old)
termination_by remaining.length
  decreasing_by exact remove_length_lt remaining found

def compute (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token)) (base : String → Option (List Token))
    (name : String) : Option (List Token) :=
  (resolve complete base bindings.entries [] [] name).1

theorem resolve_fresh_marks (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token)) (base : String → Option (List Token)) (name : String) :
    (resolve complete base bindings.entries [] [] name).2 = [] := by
  have contained := (resolve_marks (complete := complete) (base := base) bindings.entries [] [] name
    (fun _ h => h)).1
  cases h : (resolve complete base bindings.entries [] [] name).2 with
  | nil => rfl
  | cons head rest =>
    have impossible := contained head (by rw [h]; exact List.mem_cons_self)
    exact False.elim (List.not_mem_nil impossible)

theorem compute_iff (bindings : VariableBindings Token)
    (complete : String → Option (List Token) → Option (List Token)) (base : String → Option (List Token)) (name : String) (value : Option (List Token)) :
    compute bindings complete base name = value ↔ Resolves bindings complete base [] [] name value [] := by
  have pair : resolve complete base bindings.entries [] [] name = (compute bindings complete base name, []) := by
    exact Prod.ext rfl (resolve_fresh_marks bindings complete base name)
  constructor
  · intro h
    apply (resolve_iff bindings.entries [] (fun _ _ => rfl) [] name value []).mp
    simpa [h] using pair
  · intro h
    have result := (resolve_iff bindings.entries [] (fun _ _ => rfl) [] name value []).mpr h
    exact congrArg Prod.fst result

theorem Resolves.unique (left : Resolves bindings complete base active marked name a first)
    (right : Resolves bindings complete base active marked name b second) :
    (a, first) = (b, second) := by
  have lhs := (resolve_iff bindings.entries active (fun _ _ => rfl) marked name a first).mpr left
  have rhs := (resolve_iff bindings.entries active (fun _ _ => rfl) marked name b second).mpr right
  exact lhs.symm.trans rhs

theorem Evaluates.unique (left : Evaluates bindings complete base active marked expression a first)
    (right : Evaluates bindings complete base active marked expression b second) :
    (a, first) = (b, second) := by
  have lhs := (evaluates_iff_generic expression active marked a first).mp left
  have rhs := (evaluates_iff_generic expression active marked b second).mp right
  exact GuardedExpr.Evaluates.unique (resolve := fun marks name =>
    resolve complete base bindings.entries active marks name)
    (fun marks name value finish =>
      (resolve_iff bindings.entries active (fun _ _ => rfl) marks name value finish).mpr) lhs rhs

end GuardedCompletion
end CssSemantics
