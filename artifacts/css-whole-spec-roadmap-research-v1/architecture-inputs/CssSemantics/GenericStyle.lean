import CssSemantics.SelectorModel
import CssSemantics.Cascade
import CssSemantics.Defaulting

namespace CssSemantics

def GenericSelectorList.weights {Node Selector : Type} (model : ExecutableSelectorModel Node Selector)
    (selectors : List Selector) (node : Node) : List Specificity :=
  (selectors.filter (fun selector => model.matchesBool selector node)).map model.specificity

def GenericSelectorList.matchingSpecificity {Node Selector : Type} (model : ExecutableSelectorModel Node Selector)
    (selectors : List Selector) (node : Node) : Option Specificity :=
  match weights model selectors node with
  | [] => none
  | first :: rest => some (Specificity.maximum (first :: rest))

theorem GenericSelectorList.weight_mem_iff {Node Selector : Type} (model : ExecutableSelectorModel Node Selector)
    (selectors : List Selector) (node : Node) (weight : Specificity) :
    weight ∈ weights model selectors node ↔
      ∃ selector ∈ selectors, model.Matches selector node ∧ (model.specificity selector) = weight := by
  simp [weights, model.matchesBool_iff, and_assoc]

theorem GenericSelectorList.none_iff {Node Selector : Type} (model : ExecutableSelectorModel Node Selector)
    (selectors : List Selector) (node : Node) :
    matchingSpecificity model selectors node = none ↔
      ∀ selector ∈ selectors, ¬ model.Matches selector node := by
  have empty_iff : matchingSpecificity model selectors node = none ↔
      weights model selectors node = [] := by
    unfold matchingSpecificity
    cases weights model selectors node <;> simp
  rw [empty_iff]
  simp [weights, List.filter_eq_nil_iff,
    model.matchesBool_iff]

theorem GenericSelectorList.selected_member {Node Selector : Type} (model : ExecutableSelectorModel Node Selector)
    (selectors : List Selector) (node : Node) (weight : Specificity)
    (h : matchingSpecificity model selectors node = some weight) :
    ∃ selector ∈ selectors, model.Matches selector node ∧ (model.specificity selector) = weight := by
  apply (weight_mem_iff model selectors node weight).mp
  unfold matchingSpecificity at h
  cases he : weights model selectors node with
  | nil => simp [he] at h
  | cons first rest =>
      simp only [he, Option.some.injEq] at h
      rw [← h]
      exact Specificity.maximum_mem (by simp)

theorem GenericSelectorList.selected_upper_bound {Node Selector : Type} (model : ExecutableSelectorModel Node Selector)
    (selectors : List Selector) (node : Node) (weight : Specificity)
    (h : matchingSpecificity model selectors node = some weight)
    (selector : Selector) (hmem : selector ∈ selectors) (hm : model.Matches selector node) :
    (model.specificity selector).Le weight := by
  have hw := (weight_mem_iff model selectors node (model.specificity selector)).mpr ⟨selector, hmem, hm, rfl⟩
  unfold matchingSpecificity at h
  cases he : weights model selectors node with
  | nil => simp [he] at h
  | cons first rest =>
      simp only [he, Option.some.injEq] at h
      rw [← h]
      exact Specificity.le_maximum (he ▸ hw)


def GenericSelectorList.SelectedWeight {Node Selector : Type} (model : SelectorModel Node Selector)
    (selectors : List Selector) (node : Node) (weight : Specificity) : Prop :=
  (∃ selector ∈ selectors, model.Matches selector node ∧ (model.specificity selector) = weight) ∧
  ∀ selector ∈ selectors, model.Matches selector node → (model.specificity selector).Le weight

theorem GenericSelectorList.some_iff {Node Selector : Type} (model : ExecutableSelectorModel Node Selector)
    (selectors : List Selector) (node : Node) (weight : Specificity) :
    matchingSpecificity model selectors node = some weight ↔
      SelectedWeight model.toSelectorModel selectors node weight := by
  constructor
  · intro h
    exact ⟨selected_member model selectors node weight h,
      fun selector hs hm => selected_upper_bound model selectors node weight h selector hs hm⟩
  · rintro ⟨⟨selector, hs, hm, hw⟩, hu⟩
    cases he : matchingSpecificity model selectors node with
    | none => exact False.elim (((none_iff model selectors node).mp he) selector hs hm)
    | some other =>
        have ⟨otherSelector, ho, hom, how⟩ := selected_member model selectors node other he
        have left := selected_upper_bound model selectors node other he selector hs hm
        have right := hu otherSelector ho hom
        rw [hw] at left
        rw [how] at right
        have equal := Specificity.le_antisymm left right
        simp [equal]

structure StyleDeclaration (Value : Type) where
  value : Value
  origin : CascadeOrigin := .author
  important : Bool := false
  layer : Option Nat := none
  sourceOrder : Nat := 0
  deriving DecidableEq, Repr

def StyleDeclaration.entry (declaration : StyleDeclaration Value) (weight : Specificity) : CascadeEntry Value :=
  { value := declaration.value, origin := declaration.origin, important := declaration.important,
    layer := declaration.layer, specificity := weight, sourceOrder := declaration.sourceOrder }

structure GenericStyleRule (Selector Value : Type) where
  selectors : List Selector
  declaration : StyleDeclaration Value
  deriving DecidableEq, Repr

def GenericStyleRule.Instance {Node Selector Value : Type} (model : SelectorModel Node Selector)
    (rule : GenericStyleRule Selector Value) (node : Node) (entry : CascadeEntry Value) : Prop :=
  ∃ weight, GenericSelectorList.SelectedWeight model rule.selectors node weight ∧
    entry = rule.declaration.entry weight

def GenericStyleRule.instantiate {Node Selector Value : Type} (model : ExecutableSelectorModel Node Selector)
    (rule : GenericStyleRule Selector Value) (node : Node) : Option (CascadeEntry Value) :=
  (GenericSelectorList.matchingSpecificity model rule.selectors node).map fun weight =>
    rule.declaration.entry weight

theorem GenericStyleRule.instantiate_iff {Node Selector Value : Type}
    (model : ExecutableSelectorModel Node Selector) (rule : GenericStyleRule Selector Value) (node : Node) (entry : CascadeEntry Value) :
    rule.instantiate model node = some entry ↔ rule.Instance model.toSelectorModel node entry := by
  simp only [instantiate, Option.map_eq_some_iff, Instance, GenericSelectorList.some_iff]
  constructor
  · rintro ⟨weight, hw, he⟩
    exact ⟨weight, hw, he.symm⟩
  · rintro ⟨weight, hw, he⟩
    exact ⟨weight, hw, he.symm⟩

def GenericStyle.candidates {Node Selector Value : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (GenericStyleRule Selector Value)) (node : Node) : List (CascadeEntry Value) :=
  rules.filterMap (fun rule => rule.instantiate model node)

theorem GenericStyle.candidate_mem_iff {Node Selector Value : Type}
    (model : ExecutableSelectorModel Node Selector) (rules : List (GenericStyleRule Selector Value)) (node : Node)
    (entry : CascadeEntry Value) :
    entry ∈ candidates model rules node ↔
      ∃ rule ∈ rules, rule.Instance model.toSelectorModel node entry := by
  simp [candidates, List.mem_filterMap, GenericStyleRule.instantiate_iff]

def GenericStyle.Winner {Node Selector Value : Type} (model : SelectorModel Node Selector)
    (rules : List (GenericStyleRule Selector Value)) (node : Node) (selected : CascadeEntry Value) : Prop :=
  (∃ rule ∈ rules, rule.Instance model node selected) ∧
  ∀ rule ∈ rules, ∀ entry, rule.Instance model node entry → entry.Le selected

def GenericStyle.winner {Node Selector Value : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (GenericStyleRule Selector Value)) (node : Node) : Option (CascadeEntry Value) :=
  Cascade.winner (candidates model rules node)

theorem GenericStyle.winner_sound {Node Selector Value : Type}
    (model : ExecutableSelectorModel Node Selector) (rules : List (GenericStyleRule Selector Value)) (node : Node)
    (selected : CascadeEntry Value) (h : winner model rules node = some selected) :
    Winner model.toSelectorModel rules node selected := by
  obtain ⟨hm, hu⟩ := Cascade.winner_spec (candidates model rules node) selected h
  exact ⟨(candidate_mem_iff model rules node selected).mp hm,
    fun rule hr entry hi => hu entry ((candidate_mem_iff model rules node entry).mpr ⟨rule, hr, hi⟩)⟩

def GenericStyle.Cascaded {Node Selector Value : Type} (model : SelectorModel Node Selector)
    (rules : List (GenericStyleRule Selector Value)) (node : Node) : Option Value → Prop
  | none => ∀ rule ∈ rules, ∀ entry, ¬ rule.Instance model node entry
  | some value => ∃ entry, Winner model rules node entry ∧ entry.value = value

def GenericStyle.cascaded {Node Selector Value : Type} (model : ExecutableSelectorModel Node Selector)
    (rules : List (GenericStyleRule Selector Value)) (node : Node) : Option Value :=
  (winner model rules node).map CascadeEntry.value

theorem GenericStyle.cascaded_sound {Node Selector Value : Type}
    (model : ExecutableSelectorModel Node Selector) (rules : List (GenericStyleRule Selector Value)) (node : Node) :
    Cascaded model.toSelectorModel rules node (cascaded model rules node) := by
  unfold cascaded
  cases h : winner model rules node with
  | none =>
      simp only [Option.map_none, Cascaded]
      intro rule hr entry hi
      have hc := (candidate_mem_iff model rules node entry).mpr ⟨rule, hr, hi⟩
      have he := (Cascade.winner_none_iff (candidates model rules node)).mp h
      simp [he] at hc
  | some entry =>
      exact ⟨entry, winner_sound model rules node entry h, rfl⟩

def GenericStyle.compute {Node Selector Value : Type} (model : ExecutableSelectorModel Node Selector)
    (profile : PropertyProfile Value) (rules : List (GenericStyleRule Selector (CascadedValue Value)))
    (node : Node) : Value :=
  computeProperty model.forest profile (cascaded model rules) node

def GenericStyle.Computed {Node Selector Value : Type} (model : SelectorModel Node Selector)
    (profile : PropertyProfile Value) (rules : List (GenericStyleRule Selector (CascadedValue Value)))
    (node : Node) (value : Value) : Prop :=
  match _h : model.forest.parent node with
  | none => ∃ cascaded, Cascaded model rules node cascaded ∧ Resolves profile none cascaded value
  | some parent => ∃ inherited cascaded,
      Computed model profile rules parent inherited ∧ Cascaded model rules node cascaded ∧
      Resolves profile (some inherited) cascaded value
termination_by model.forest.depth node
decreasing_by exact model.forest.parent_depth _h

theorem GenericStyle.compute_sound {Node Selector Value : Type}
    (model : ExecutableSelectorModel Node Selector) (profile : PropertyProfile Value)
    (rules : List (GenericStyleRule Selector (CascadedValue Value))) (node : Node) :
    Computed model.toSelectorModel profile rules node (compute model profile rules node) := by
  rw [Computed]
  unfold compute
  rw [computeProperty]
  split
  next hp =>
    rw [hp]
    exact ⟨cascaded model rules node, cascaded_sound model rules node,
      (resolve_eq_iff profile _ _ _).mp rfl⟩
  next parent hp =>
    rw [hp]
    exact ⟨compute model profile rules parent, cascaded model rules node,
      compute_sound model profile rules parent, cascaded_sound model rules node,
      (resolve_eq_iff profile _ _ _).mp rfl⟩
termination_by model.forest.depth node
decreasing_by exact model.forest.parent_depth (by assumption)

end CssSemantics
