namespace AttributeEligibility

inductive Slot (V : Type) where
  | absent
  | invalid
  | pending (value : V)
  | ready (value : V)
  deriving DecidableEq

def eligible (parse : C → S → V → Option O) (context : C) (descriptor : S)
    (slot : Slot V) : Bool :=
  match slot with
  | .ready value => (parse context descriptor value).isSome
  | _ => false

def fallbackEdges (parse : C → S → V → Option O) (context : C) (descriptor : S)
    (slot : Slot V) (fallback : List E) : List E :=
  if eligible parse context descriptor slot then [] else fallback

def originalReadyOnly (slot : Slot V) : Bool :=
  match slot with | .ready _ => true | _ => false

theorem absent_uses_fallback (parse : C → S → V → Option O) (context descriptor)
    (fallback : List E) :
    fallbackEdges parse context descriptor .absent fallback = fallback := rfl

theorem invalid_uses_fallback (parse : C → S → V → Option O) (context descriptor)
    (fallback : List E) :
    fallbackEdges parse context descriptor .invalid fallback = fallback := rfl

theorem pending_uses_fallback (parse : C → S → V → Option O) (context descriptor value)
    (fallback : List E) :
    fallbackEdges parse context descriptor (.pending value) fallback = fallback := rfl

theorem ready_success_has_no_fallback_edges (parse : C → S → V → Option O)
    (context descriptor value output) (fallback : List E)
    (h : parse context descriptor value = some output) :
    fallbackEdges parse context descriptor (.ready value) fallback = [] := by
  simp [fallbackEdges, eligible, h]

theorem ready_failure_uses_fallback (parse : C → S → V → Option O)
    (context descriptor value) (fallback : List E)
    (h : parse context descriptor value = none) :
    fallbackEdges parse context descriptor (.ready value) fallback = fallback := by
  simp [fallbackEdges, eligible, h]

theorem successful_primary_ignores_any_fallback (parse : C → S → V → Option O)
    (context descriptor value output) (a b : List E)
    (h : parse context descriptor value = some output) :
    fallbackEdges parse context descriptor (.ready value) a =
    fallbackEdges parse context descriptor (.ready value) b := by
  simp [fallbackEdges, eligible, h]

theorem parser_result_correspondence (p q : C → S → V → Option O)
    (context descriptor) (slot : Slot V) (fallback : List E)
    (h : ∀ v, p context descriptor v = q context descriptor v) :
    fallbackEdges p context descriptor slot fallback =
    fallbackEdges q context descriptor slot fallback := by
  cases slot <;> simp only [fallbackEdges, eligible, h] <;> rfl

theorem ready_only_misses_rejection (parse : C → S → V → Option O)
    (context descriptor value) (h : parse context descriptor value = none) :
    originalReadyOnly (.ready value) = true ∧
    eligible parse context descriptor (.ready value) = false := by
  simp [originalReadyOnly, eligible, h]

theorem same_cached_value_different_occurrence_decisions
    (parse : C → S → V → Option O) (context first second value output)
    (accepted : parse context first value = some output)
    (rejected : parse context second value = none) :
    eligible parse context first (.ready value) = true ∧
    eligible parse context second (.ready value) = false := by
  simp [eligible, accepted, rejected]

theorem no_value_only_boolean_classifier
    (parse : C → S → V → Option O) (context first second value output)
    (accepted : parse context first value = some output)
    (rejected : parse context second value = none) :
    ¬ ∃ classify : V → Bool,
      classify value = eligible parse context first (.ready value) ∧
      classify value = eligible parse context second (.ready value) := by
  simp [eligible, accepted, rejected]

theorem preload_preserving_current_slot_preserves_decision
    (parse : C → S → V → Option O) (context descriptor key)
    (before after : K → Slot V) (h : before key = after key) (fallback : List E) :
    fallbackEdges parse context descriptor (before key) fallback =
    fallbackEdges parse context descriptor (after key) fallback := by
  rw [h]

inductive Syntax where | any | length deriving DecidableEq
inductive Value where | badIdent | length deriving DecidableEq

def exampleParser (_ : Unit) (descriptor : Syntax) (value : Value) : Option Unit :=
  match descriptor, value with
  | .length, .badIdent => none
  | _, _ => some ()

theorem ready_bad_ident_counterexample :
    originalReadyOnly (.ready Value.badIdent) = true ∧
    fallbackEdges exampleParser () .length (.ready .badIdent) [37] = [37] := by decide

theorem same_key_two_syntax_counterexample :
    fallbackEdges exampleParser () .any (.ready .badIdent) [37] = [] ∧
    fallbackEdges exampleParser () .length (.ready .badIdent) [37] = [37] := by decide

inductive Property where | fontSize | lineHeight deriving DecidableEq
inductive Node where | fontUnits | lineHeightUnits deriving DecidableEq

def recordedUnder : Property → List Node
  | .fontSize => [.fontUnits]
  | .lineHeight => [.lineHeightUnits, .fontUnits]

theorem font_node_has_two_source_properties :
    Node.fontUnits ∈ recordedUnder .fontSize ∧
    Node.fontUnits ∈ recordedUnder .lineHeight := by
  simp [recordedUnder]

theorem node_cannot_reconstruct_both_property_ids :
    ¬ ∃ decode : Node → Property,
      decode .fontUnits = .fontSize ∧ decode .fontUnits = .lineHeight := by
  intro ⟨decode, hfont, hline⟩
  rw [hfont] at hline
  cases hline

end AttributeEligibility
