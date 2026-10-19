import CssSemantics.GenericStyle
import CssSemantics.VariablesBase

namespace CssSemantics

structure CustomStyleRule (Selector Token : Type) where
  name : String
  rule : GenericStyleRule Selector (VariableExpr Token)

namespace CustomCascade

variable {Selector Token : Type}

def rulesFor (rules : List (CustomStyleRule Selector Token)) (name : String) :
    List (GenericStyleRule Selector (VariableExpr Token)) :=
  (rules.filter (fun rule => rule.name == name)).map CustomStyleRule.rule

def names (rules : List (CustomStyleRule Selector Token)) : List String :=
  (rules.map CustomStyleRule.name).eraseDups

theorem rulesFor_mem_iff (rules : List (CustomStyleRule Selector Token)) (name : String)
    (rule : GenericStyleRule Selector (VariableExpr Token)) :
    rule ∈ rulesFor rules name ↔
      ∃ named ∈ rules, named.name = name ∧ named.rule = rule := by
  simp [rulesFor, List.mem_map, List.mem_filter, and_assoc]

theorem names_mem_iff (rules : List (CustomStyleRule Selector Token)) (name : String) :
    name ∈ names rules ↔ ∃ rule ∈ rules, rule.name = name := by
  simp [names, List.mem_map]

def cascaded {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String) :
    Option (VariableExpr Token) :=
  GenericStyle.cascaded model (rulesFor rules name) node

def Winner {Node Selector Token : Type} (model : SelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String)
    (selected : CascadeEntry (VariableExpr Token)) : Prop :=
  (∃ rule ∈ rules, rule.name = name ∧ rule.rule.Instance model node selected) ∧
    ∀ rule ∈ rules, rule.name = name → ∀ entry,
      rule.rule.Instance model node entry → entry.Le selected

theorem winner_iff {Node Selector Token : Type} (model : SelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String)
    (selected : CascadeEntry (VariableExpr Token)) :
    Winner model rules node name selected ↔
      GenericStyle.Winner model (rulesFor rules name) node selected := by
  constructor
  · rintro ⟨⟨rule, member, same, applies⟩, maximal⟩
    refine ⟨⟨rule.rule, (rulesFor_mem_iff _ _ _).mpr ⟨rule, member, same, rfl⟩, applies⟩, ?_⟩
    intro candidate member entry applies
    obtain ⟨rule, originalMember, same, rfl⟩ := (rulesFor_mem_iff _ _ _).mp member
    exact maximal rule originalMember same entry applies
  · rintro ⟨⟨candidate, member, applies⟩, maximal⟩
    obtain ⟨rule, originalMember, same, rfl⟩ := (rulesFor_mem_iff _ _ _).mp member
    refine ⟨⟨rule, originalMember, same, applies⟩, ?_⟩
    intro rule member same entry applies
    exact maximal rule.rule ((rulesFor_mem_iff _ _ _).mpr ⟨rule, member, same, rfl⟩) entry applies

theorem cascaded_provenance {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String)
    (selected : VariableExpr Token) (h : cascaded model rules node name = some selected) :
    ∃ entry, Winner model.toSelectorModel rules node name entry ∧ entry.value = selected := by
  have sound := GenericStyle.cascaded_sound model (rulesFor rules name) node
  change GenericStyle.Cascaded _ _ _ (cascaded model rules node name) at sound
  rw [h] at sound
  obtain ⟨entry, winner, value⟩ := sound
  exact ⟨entry, (winner_iff _ _ _ _ _).mpr winner, value⟩

theorem cascaded_supported {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String)
    (selected : VariableExpr Token) (h : cascaded model rules node name = some selected) :
    name ∈ names rules := by
  obtain ⟨entry, ⟨⟨rule, member, same, _⟩, _⟩, _⟩ := cascaded_provenance model rules node name selected h
  exact (names_mem_iff rules name).mpr ⟨rule, member, same⟩

def collect (support : List String) (values : String → Option (VariableExpr Token)) :
    List (String × VariableExpr Token) :=
  support.filterMap fun name => (values name).map fun value => (name, value)

theorem collect_keys (support : List String) (values : String → Option (VariableExpr Token)) :
    (collect support values).map Prod.fst = support.filter (fun name => (values name).isSome) := by
  induction support with
  | nil => rfl
  | cons name rest ih =>
    simp only [collect] at ih ⊢
    cases h : values name <;> simp [h, ih]

theorem collect_mem_iff (support : List String) (values : String → Option (VariableExpr Token))
    (name : String) (value : VariableExpr Token) :
    (name, value) ∈ collect support values ↔ name ∈ support ∧ values name = some value := by
  simp [collect, List.mem_filterMap, Option.map_eq_some_iff]

theorem distinct_support (support : List String) : support.eraseDups.Nodup := by
  cases support with
  | nil => simp
  | cons name rest =>
    rw [List.eraseDups_cons, List.nodup_cons]
    constructor
    · simp
    · exact distinct_support (rest.filter fun other => !other == name)
termination_by support.length
decreasing_by exact Nat.lt_succ_of_le (List.length_filter_le _ _)

def bindings {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) : VariableBindings Token where
  entries := collect (names rules) (cascaded model rules node)
  unique := by
    rw [collect_keys]
    exact List.Nodup.sublist (List.filter_sublist) (distinct_support _)

theorem entry_mem_iff {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String)
    (expression : VariableExpr Token) :
    (name, expression) ∈ (bindings model rules node).entries ↔
      cascaded model rules node name = some expression := by
  change (name, expression) ∈ collect _ _ ↔ _
  rw [collect_mem_iff]
  exact ⟨And.right, fun h => ⟨cascaded_supported model rules node name expression h, h⟩⟩

theorem lookup_eq_cascaded {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String) :
    (bindings model rules node).lookup name = cascaded model rules node name := by
  cases h : cascaded model rules node name with
  | none =>
    apply ((bindings model rules node).lookup_none_iff name).mpr
    intro expression member
    have present := (entry_mem_iff model rules node name expression).mp member
    simp [h] at present
  | some expression =>
    exact ((bindings model rules node).lookup_iff name expression).mpr
      ((entry_mem_iff model rules node name expression).mpr h)

theorem lookup_provenance {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String)
    (expression : VariableExpr Token) (h : (bindings model rules node).lookup name = some expression) :
    ∃ entry, Winner model.toSelectorModel rules node name entry ∧ entry.value = expression := by
  rw [lookup_eq_cascaded] at h
  exact cascaded_provenance model rules node name expression h

theorem lookup_none_iff {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (name : String) :
    (bindings model rules node).lookup name = none ↔
      ∀ rule ∈ rules, rule.name = name → ∀ entry,
        ¬rule.rule.Instance model.toSelectorModel node entry := by
  rw [lookup_eq_cascaded]
  constructor
  · intro absent rule member same entry applies
    have sound := GenericStyle.cascaded_sound model (rulesFor rules name) node
    change GenericStyle.Cascaded _ _ _ (cascaded model rules node name) at sound
    rw [absent] at sound
    exact sound rule.rule ((rulesFor_mem_iff _ _ _).mpr ⟨rule, member, same, rfl⟩) entry applies
  · intro absent
    cases selected : cascaded model rules node name with
    | none => rfl
    | some expression =>
      obtain ⟨entry, ⟨⟨rule, member, same, applies⟩, _⟩, _⟩ :=
        cascaded_provenance model rules node name expression selected
      exact False.elim (absent rule member same entry applies)

theorem dependency_iff {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (CustomStyleRule Selector Token)) (node : Node) (source target : String) :
    (bindings model rules node).Depends source target ↔
      ∃ expression, cascaded model rules node source = some expression ∧ expression.References target := by
  simp only [VariableBindings.Depends, entry_mem_iff]

theorem lookup_congr {Node Selector Token : Type} (model : ExecutableSelectorModel Node Selector)
    (left right : List (CustomStyleRule Selector Token)) (node : Node)
    (same : ∀ name, cascaded model left node name = cascaded model right node name) (name : String) :
    (bindings model left node).lookup name = (bindings model right node).lookup name := by
  rw [lookup_eq_cascaded, lookup_eq_cascaded, same]

end CustomCascade
end CssSemantics
