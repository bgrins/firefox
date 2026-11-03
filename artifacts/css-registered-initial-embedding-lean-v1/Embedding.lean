import Acyclic

namespace RegisteredInitialEmbedding
open CssSemantics AcyclicAttributeMemo

inductive Initial where
  | px : Int → Initial
  | guaranteedInvalid
  deriving DecidableEq, Repr

def Initial.value : Initial → Value
  | .px n => some [.px n]
  | .guaranteedInvalid => none

def Initial.default : Initial → Option Int
  | .px n => some n
  | .guaranteedInvalid => none

def Initial.expression : Initial → VariableExpr Token
  | .px n => AcyclicAttributeMemo.px n
  | .guaranteedInvalid => invalid

inductive Node where
  | declared : VariableExpr Token → Option Initial → Node
  | registeredUnspecified : Initial → Node


def select (declaration : Option (VariableExpr Token)) (registration : Option Initial) : Option Node :=
  match declaration, registration with
  | some expression, registered => some (.declared expression registered)
  | none, some initial => some (.registeredUnspecified initial)
  | none, none => none

def Node.expression : Node → VariableExpr Token
  | .declared expression _ => expression
  | .registeredUnspecified initial => initial.expression

def Node.default : Node → Option Int
  | .declared _ registered => registered.bind Initial.default
  | .registeredUnspecified initial => initial.default

structure Source where
  entries : List (String × Node)
  unique : (entries.map Prod.fst).Nodup

def Source.lookup (source : Source) (name : String) := source.entries.lookup name

def normalize (source : Source) : VariableBindings Token where
  entries := source.entries.map fun entry => (entry.1, entry.2.expression)
  unique := by simpa [List.map_map, Function.comp_def] using source.unique

def defaults (source : Source) (name : String) : Option Int :=
  (source.lookup name).bind Node.default

theorem lookup_normalize (source : Source) (name : String) :
    (normalize source).lookup name = (source.lookup name).map Node.expression := by
  change (source.entries.map (fun entry => (entry.1, entry.2.expression))).lookup name =
    (source.entries.lookup name).map Node.expression
  induction source.entries with
  | nil => rfl
  | cons entry rest ih =>
      rcases entry with ⟨key, value⟩
      by_cases h : name == key <;> simp [List.lookup_cons, h, ih]

theorem selected_initial (initial : Initial) :
    select none (some initial) = some (.registeredUnspecified initial) := rfl

theorem missing_unregistered : select none none = none := rfl

theorem declaration_has_priority (expression : VariableExpr Token) (registration : Option Initial) :
    select (some expression) registration = some (.declared expression registration) := rfl

theorem initial_completion (initial : Initial) (environment : String → Value) :
    complete (fun _ => initial.default) name (initial.expression.substitute environment) =
      initial.value := by
  cases initial <;> simp [Initial.expression, Initial.default, Initial.value, px, invalid,
    VariableExpr.substitute, complete, typedLength]

def evaluate (source : Source) : Nat → String → Value
  | 0, _ => none
  | fuel + 1, name =>
      match source.lookup name with
      | none => none
      | some (.registeredUnspecified initial) => initial.value
      | some (.declared expression _) =>
          complete (defaults source) name (expression.substitute (evaluate source fuel))

def Source.Depends (source : Source) (owner target : String) : Prop :=
  ∃ expression registered, source.lookup owner = some (.declared expression registered) ∧
    expression.References target

theorem normalized_dependencies (source : Source) (owner target : String) :
    (normalize source).Depends owner target ↔ source.Depends owner target := by
  constructor
  · rintro ⟨expression, member, reference⟩
    have lookup := ((normalize source).lookup_iff owner expression).mpr member
    rw [lookup_normalize] at lookup
    cases found : source.lookup owner with
    | none => simp [found] at lookup
    | some node =>
      cases node with
      | declared body registered =>
          simp [found, Node.expression] at lookup
          subst expression
          exact ⟨body, registered, found, reference⟩
      | registeredUnspecified initial =>
          simp [found, Node.expression] at lookup
          subst expression
          cases initial <;> cases reference
  · rintro ⟨expression, registered, found, reference⟩
    refine ⟨expression, ((normalize source).lookup_iff _ _).mp ?_, reference⟩
    simp [lookup_normalize, found, Node.expression]

def Source.Cyclic (source : Source) (name : String) : Prop :=
  FiniteGraph.Reach source.Depends name name

theorem normalization_preserves_acyclicity (source : Source)
    (acyclic : ∀ name, ¬source.Cyclic name) : ∀ name, ¬(normalize source).Cyclic name := by
  intro name cyclic
  have transfer : ∀ left right, FiniteGraph.Reach (normalize source).Depends left right →
      FiniteGraph.Reach source.Depends left right := by
    intro left right path
    induction path with
    | edge h => exact .edge ((normalized_dependencies source _ _).mp h)
    | trans _ _ first second => exact .trans first second
  exact acyclic name (transfer name name cyclic)

theorem registered_initial_has_no_dependencies (source : Source) (name target : String)
    (found : source.lookup name = some (.registeredUnspecified initial)) :
    ¬(normalize source).Depends name target := by
  rw [normalized_dependencies]
  rintro ⟨expression, registration, other, _⟩
  simp [found] at other

theorem evaluate_normalization (source : Source)
    (acyclic : ∀ name, ¬(normalize source).Cyclic name) (fuel : Nat) (name : String)
    (enough : (normalize source).rank name < fuel) :
    evaluate source fuel name = semantic (normalize source) (defaults source) name := by
  change evaluate source fuel name =
    (normalize source).computeWithCompletion (complete (defaults source)) (fun _ => none) name
  induction fuel generalizing name with
  | zero => omega
  | succ fuel ih =>
    cases found : source.lookup name with
    | none =>
        have missing : (normalize source).lookup name = none := by simp [lookup_normalize, found]
        rw [VariableBindings.computeWithCompletion_missing _ _ _ _ missing]
        simp [evaluate, found]
    | some node =>
      have bound : (normalize source).lookup name = some node.expression := by
        simp [lookup_normalize, found]
      rw [VariableBindings.computeWithCompletion_bound _ _ _ _ (acyclic name) bound]
      cases node with
      | registeredUnspecified initial =>
          simp only [evaluate, found, Node.expression]
          cases initial <;> simp [defaults, found, Node.default, Initial.expression,
            Initial.default, Initial.value, px, invalid, VariableExpr.substitute, complete, typedLength]
      | declared expression registration =>
          simp only [evaluate, found, Node.expression]
          apply congrArg (complete (defaults source) name)
          apply expression.substitute_congr
          intro target reference
          have edge : (normalize source).Depends name target :=
            (normalized_dependencies source name target).mpr ⟨expression, registration, found, reference⟩
          have smaller := (normalize source).rank_decreases edge (acyclic target)
          exact ih target (by omega)

theorem memo_agrees_with_source (source : Source)
    (acyclic : ∀ name, ¬(normalize source).Cyclic name) (fuel : Nat) (name : String)
    (enough : (normalize source).rank name < fuel) :
    (resolveMemo (normalize source) (defaults source) fuel name (fun _ => none)).1 =
      evaluate source fuel name := by
  rw [evaluate_normalization source acyclic fuel name enough]
  exact (resolveMemo_correct _ _ acyclic fuel name enough _ (empty_sound _)).1

theorem roots_compute_source (source : Source)
    (acyclic : ∀ name, ¬(normalize source).Cyclic name) (fuel : Nat)
    (enough : ∀ name, (normalize source).rank name < fuel) (roots : List String)
    (member : name ∈ roots) :
    runRoots (normalize source) (defaults source) fuel roots (fun _ => none) name =
      some (evaluate source fuel name) := by
  rw [evaluate_normalization source acyclic fuel name (enough name)]
  exact (runRoots_correct _ _ acyclic fuel enough roots _ (empty_sound _)).2.2 name member

theorem root_order_preserves_initial_embedding (source : Source)
    (acyclic : ∀ name, ¬(normalize source).Cyclic name) (fuel : Nat)
    (enough : ∀ name, (normalize source).rank name < fuel) (left right : List String)
    (same : left.Perm right) (member : name ∈ left) :
    runRoots (normalize source) (defaults source) fuel left (fun _ => none) name =
      runRoots (normalize source) (defaults source) fuel right (fun _ => none) name :=
  root_order_independent _ _ acyclic fuel enough left right same name member

def control : Source where
  entries := [(property "a", .declared (attrFallback "x" (px 7)) (some (.px 8))),
              (property "b", .declared (attrFallback "x" (px 3)) (some (.px 8))),
              (attributeName "x", .declared (varRef "c") none),
              (property "c", .registeredUnspecified (.px 11)),
              (property "invalid", .registeredUnspecified .guaranteedInvalid),
              (property "invalid-consumer", .declared (varFallback "invalid" (px 23)) none),
              (property "missing-consumer", .declared (varFallback "missing" (px 29)) none),
              (property "empty", .declared (.literal []) (some (.px 31))),
              (property "override", .declared (px 41) (some (.px 11)))]
  unique := by decide

def budget := (normalize control).rankSupport.length + 1
def observed (roots : List String) :=
  runRoots (normalize control) (defaults control) budget roots (fun _ => none)

theorem control_acyclic (name : String) : ¬(normalize control).Cyclic name := by
  intro cyclic
  obtain ⟨expression, member⟩ := (normalize control).cyclic_declared name cyclic
  have names : name ∈ (normalize control).entries.map Prod.fst :=
    List.mem_map.mpr ⟨(name, expression), member, rfl⟩
  have alternatives : name = property "a" ∨ name = property "b" ∨ name = attributeName "x" ∨
      name = property "c" ∨ name = property "invalid" ∨ name = property "invalid-consumer" ∨
      name = property "missing-consumer" ∨ name = property "empty" ∨ name = property "override" := by
    simpa [normalize, control] using names
  have yes := ((normalize control).cyclicBool_iff name).mpr cyclic
  rcases alternatives with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> contradiction

theorem no_declaration_initial_is_primary :
    observed [property "a", property "c"] (property "a") = some (some [.px 11]) := by decide

theorem no_declaration_orders_agree :
    observed [property "a", property "c"] (property "a") =
      observed [property "c", property "a"] (property "a") := by
  apply root_order_preserves_initial_embedding control control_acyclic budget
    (finite_rank_budget (normalize control))
  · exact List.Perm.swap _ _ _
  · simp

theorem registered_invalid_is_present_but_invalid :
    (control.lookup (property "invalid")).isSome = true ∧
      evaluate control budget (property "invalid") = none ∧
      evaluate control budget (property "invalid-consumer") = some [.px 23] := by decide

theorem missing_unregistered_is_absent :
    (control.lookup (property "missing")).isSome = false ∧
      evaluate control budget (property "missing") = none ∧
      evaluate control budget (property "missing-consumer") = some [.px 29] := by decide

theorem declared_empty_and_initial_are_distinct :
    evaluate control budget (property "empty") = some [.px 31] ∧
      evaluate control budget (property "override") = some [.px 41] := by decide

theorem browser_control_values :
    evaluate control budget (property "a") = some [.px 11] ∧
    evaluate control budget (property "b") = some [.px 11] ∧
    (attrFallback "x" (px 9)).substitute (evaluate control budget) = some [.px 11] := by decide

def omittedInitialGraph : VariableBindings Token where
  entries := [(property "a", attrFallback "x" (px 7)), (attributeName "x", varRef "c")]
  unique := by decide

def oldDefaultsOnly :=
  (resolveMemo omittedInitialGraph (defaults control) 4 (property "a") (fun _ => none)).1

theorem default_map_alone_is_insufficient :
    defaults control (property "c") = some 11 ∧ oldDefaultsOnly = some [.px 7] ∧
    evaluate control budget (property "a") = some [.px 11] := by decide

end RegisteredInitialEmbedding
