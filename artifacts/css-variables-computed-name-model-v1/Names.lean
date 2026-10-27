import CssSemantics.GuardedCompletion

namespace ComputedNames
open CssSemantics
variable {State Token : Type}

structure NameAdapter (Token : Type) where
  parse : List Token → Option String
  accepts : List Token → String → Prop
  exact : ∀ tokens name, parse tokens = some name ↔ accepts tokens name

inductive Expr (Token : Type) where
  | static : VariableExpr Token → Expr Token
  | append : Expr Token → Expr Token → Expr Token
  | reference : Expr Token → Expr Token
  | fallback : Expr Token → Expr Token → Expr Token

def lookupName (parse : List Token → Option String)
    (resolve : State → String → Option (List Token) × State)
    (result : Option (List Token) × State) : Option (List Token) × State :=
  match result.1.bind parse with
  | none => (none, result.2)
  | some name => resolve result.2 name

def evaluate (parse : List Token → Option String)
    (resolve : State → String → Option (List Token) × State)
    (state : State) : Expr Token → Option (List Token) × State
  | .static expression => GuardedExpr.evaluate resolve state expression
  | .append left right =>
      let first := evaluate parse resolve state left
      let second := evaluate parse resolve first.2 right
      (GuardedExpr.combine first.1 second.1, second.2)
  | .reference expression => lookupName parse resolve (evaluate parse resolve state expression)
  | .fallback expression fallback =>
      let primary := lookupName parse resolve (evaluate parse resolve state expression)
      match primary.1 with
      | some value => (some value, primary.2)
      | none => evaluate parse resolve primary.2 fallback

theorem parse_exact (adapter : NameAdapter Token) (tokens : List Token) (name : String) :
    adapter.parse tokens = some name ↔ adapter.accepts tokens name := adapter.exact tokens name

theorem static_semantics (parse : List Token → Option String)
    (resolve : State → String → Option (List Token) × State) (state : State)
    (expression : VariableExpr Token) :
    evaluate parse resolve state (.static expression) = GuardedExpr.evaluate resolve state expression := rfl

theorem name_state (parse : List Token → Option String)
    (resolve : State → String → Option (List Token) × State) (tokens : List Token)
    (state : State) (name : String) (found : parse tokens = some name) :
    lookupName parse resolve (some tokens, state) = resolve state name := by
  simp [lookupName, found]

theorem invalid_name_state (parse : List Token → Option String)
    (resolve : State → String → Option (List Token) × State) (tokens : List Token)
    (state : State) (invalid : parse tokens = none) :
    lookupName parse resolve (some tokens, state) = (none, state) := by
  simp [lookupName, invalid]

theorem fallback_only_after_lookup (parse : List Token → Option String)
    (resolve : State → String → Option (List Token) × State) (state finish : State)
    (expression fallback : Expr Token) (tokens : List Token)
    (primary : lookupName parse resolve (evaluate parse resolve state expression) = (some tokens, finish)) :
    evaluate parse resolve state (.fallback expression fallback) = (some tokens, finish) := by
  simp [evaluate, primary]

theorem fallback_threads_state (parse : List Token → Option String)
    (resolve : State → String → Option (List Token) × State) (state finish : State)
    (expression fallback : Expr Token)
    (primary : lookupName parse resolve (evaluate parse resolve state expression) = (none, finish)) :
    evaluate parse resolve state (.fallback expression fallback) = evaluate parse resolve finish fallback := by
  simp [evaluate, primary]

theorem evaluate_preserves (parse : List Token → Option String)
    (resolve : State → String → Option (List Token) × State)
    (invariant : State → Prop)
    (preserves : ∀ state name, invariant state → invariant (resolve state name).2)
    (expression : Expr Token) (state : State) (h : invariant state) :
    invariant (evaluate parse resolve state expression).2 := by
  have lookup_preserves : ∀ result : Option (List Token) × State,
      invariant result.2 → invariant (lookupName parse resolve result).2 := by
    intro result hr
    unfold lookupName
    split
    · exact hr
    · exact preserves _ _ hr
  induction expression generalizing state with
  | static expression => exact @GuardedExpr.evaluate_preserves State Token resolve invariant preserves expression state h
  | append left right ihLeft ihRight => exact ihRight _ (ihLeft state h)
  | reference expression ih => exact lookup_preserves _ (ih state h)
  | fallback expression fallback ihName ihFallback =>
    have hp := lookup_preserves _ (ihName state h)
    simp only [evaluate]
    split
    · exact hp
    · exact ihFallback _ hp

def remove (entries : List (String × Expr Token)) (name : String) :=
  entries.filter fun entry => decide (entry.1 ≠ name)

theorem remove_length_lt (entries : List (String × Expr Token))
    (found : entries.lookup name = some expression) :
    (remove entries name).length < entries.length := by
  induction entries with
  | nil => simp at found
  | cons entry rest ih =>
    rcases entry with ⟨key, value⟩
    by_cases same : key = name
    · subst key
      simp only [remove, List.filter_cons, ne_eq, not_true_eq_false, decide_false,
        Bool.false_eq_true, ↓reduceIte, List.length_cons]
      exact Nat.lt_succ_of_le (List.length_filter_le _ _)
    · have unequal : (name == key) = false := beq_eq_false_iff_ne.mpr (Ne.symm same)
      simp [List.lookup_cons, unequal] at found
      simpa [remove, same] using Nat.succ_lt_succ (ih found)

def resolve (parse : List Token → Option String)
    (complete : String → Option (List Token) → Option (List Token))
    (base : String → Option (List Token)) (remaining : List (String × Expr Token))
    (active marked : List String) (name : String) : Option (List Token) × List String :=
  if name ∈ active then (none, GuardedState.markCycle active marked name)
  else match _found : remaining.lookup name with
    | none => (base name, marked)
    | some expression =>
      let result := evaluate parse
        (fun marks target => resolve parse complete base (remove remaining name)
          (name :: active) marks target) marked expression
      (if name ∈ result.2 then none else complete name result.1, GuardedState.pop name result.2)
termination_by remaining.length
  decreasing_by exact remove_length_lt remaining _found

def embed (entries : List (String × VariableExpr Token)) : List (String × Expr Token) :=
  entries.map fun (name, expression) => (name, .static expression)

theorem embed_lookup (entries : List (String × VariableExpr Token)) (name : String) :
    (embed entries).lookup name = (entries.lookup name).map Expr.static := by
  induction entries with
  | nil => rfl
  | cons entry rest ih =>
    rcases entry with ⟨key, value⟩
    simp only [embed, List.map_cons, List.lookup_cons]
    split <;> simp_all [embed]

theorem embed_remove (entries : List (String × VariableExpr Token)) (name : String) :
    remove (embed entries) name = embed (GuardedSolver.remove entries name) := by
  induction entries with
  | nil => rfl
  | cons entry rest ih =>
    rcases entry with ⟨key, value⟩
    by_cases h : key = name <;> simp_all [remove, embed, GuardedSolver.remove]

theorem embedded_resolve (parse : List Token → Option String)
    (complete : String → Option (List Token) → Option (List Token))
    (base : String → Option (List Token)) (entries : List (String × VariableExpr Token))
    (active marked : List String) (name : String) :
    resolve parse complete base (embed entries) active marked name =
      GuardedCompletion.resolve complete base entries active marked name := by
  rw [resolve, GuardedCompletion.resolve]
  by_cases repeated : name ∈ active
  · simp [repeated]
  · simp only [repeated, ↓reduceIte]
    have lookup := embed_lookup entries name
    generalize hlookup : (embed entries).lookup name = result
    rw [hlookup] at lookup
    rw [lookup]
    cases found : entries.lookup name with
    | none => rfl
    | some expression =>
      simp only [Option.map_some, evaluate, embed_remove]
      have callbacks : (fun marks target => resolve parse complete base
          (embed (GuardedSolver.remove entries name)) (name :: active) marks target) =
          (fun marks target => GuardedCompletion.resolve complete base
          (GuardedSolver.remove entries name) (name :: active) marks target) := by
        funext marks target
        exact embedded_resolve parse complete base (GuardedSolver.remove entries name)
          (name :: active) marks target
      rw [callbacks]
termination_by entries.length
  decreasing_by exact GuardedSolver.remove_length_lt entries found

theorem resolve_marks (parse : List Token → Option String)
    (complete : String → Option (List Token) → Option (List Token))
    (base : String → Option (List Token)) (remaining : List (String × Expr Token))
    (active marked : List String) (name : String)
    (contained : ∀ mark, mark ∈ marked → mark ∈ active) :
    (∀ mark, mark ∈ (resolve parse complete base remaining active marked name).2 → mark ∈ active) ∧
    (∀ mark, mark ∈ marked → mark ∈ (resolve parse complete base remaining active marked name).2) := by
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
          invariant (resolve parse complete base (remove remaining name) (name :: active) marks target).2 := by
        intro marks target h
        have next := resolve_marks parse complete base (remove remaining name) (name :: active) marks target h.1
        exact ⟨next.1, fun mark old => next.2 mark (h.2 mark old)⟩
      have initial : invariant marked :=
        ⟨fun mark h => List.mem_cons_of_mem _ (contained mark h), fun _ h => h⟩
      have final := evaluate_preserves parse _ invariant preservation expression marked initial
      constructor
      · exact GuardedState.pop_subset_tail name active _ final.1
      · intro mark old
        apply (GuardedState.mem_pop name mark _).mpr
        refine ⟨final.2 mark old, ?_⟩
        intro equal
        exact repeated (equal ▸ contained mark old)
termination_by remaining.length
  decreasing_by exact remove_length_lt remaining found

theorem fresh_marks (parse : List Token → Option String)
    (complete : String → Option (List Token) → Option (List Token))
    (base : String → Option (List Token)) (entries : List (String × Expr Token))
    (name : String) : (resolve parse complete base entries [] [] name).2 = [] := by
  have contained := (resolve_marks parse complete base entries [] [] name (fun _ h => h)).1
  cases h : (resolve parse complete base entries [] [] name).2 with
  | nil => rfl
  | cons head rest =>
    have impossible := contained head (by rw [h]; exact List.mem_cons_self)
    exact False.elim (List.not_mem_nil impossible)

end ComputedNames
