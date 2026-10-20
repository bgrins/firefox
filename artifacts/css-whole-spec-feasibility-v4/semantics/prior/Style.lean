import CssSemantics.GenericStyle

namespace CssSemantics

def CombinedList.weights {Node : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (selectors : List CombinedSyntax) (node : Node) : List Specificity :=
  GenericSelectorList.weights (ExecutableSelectorModel.combined forest) selectors node

def CombinedList.matchingSpecificity {Node : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (selectors : List CombinedSyntax) (node : Node) : Option Specificity :=
  GenericSelectorList.matchingSpecificity (ExecutableSelectorModel.combined forest) selectors node

theorem CombinedList.weight_mem_iff {Node : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (selectors : List CombinedSyntax) (node : Node) (weight : Specificity) :
    weight ∈ weights forest selectors node ↔
      ∃ selector ∈ selectors, selector.Matches forest.toOrderedForest node ∧ selector.specificity = weight := by
  exact GenericSelectorList.weight_mem_iff (ExecutableSelectorModel.combined forest) selectors node weight

theorem CombinedList.none_iff {Node : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (selectors : List CombinedSyntax) (node : Node) :
    matchingSpecificity forest selectors node = none ↔
      ∀ selector ∈ selectors, ¬ selector.Matches forest.toOrderedForest node := by
  exact GenericSelectorList.none_iff (ExecutableSelectorModel.combined forest) selectors node

theorem CombinedList.selected_member {Node : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (selectors : List CombinedSyntax) (node : Node) (weight : Specificity)
    (h : matchingSpecificity forest selectors node = some weight) :
    ∃ selector ∈ selectors, selector.Matches forest.toOrderedForest node ∧ selector.specificity = weight := by
  exact GenericSelectorList.selected_member (ExecutableSelectorModel.combined forest) selectors node weight h

theorem CombinedList.selected_upper_bound {Node : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (selectors : List CombinedSyntax) (node : Node) (weight : Specificity)
    (h : matchingSpecificity forest selectors node = some weight)
    (selector : CombinedSyntax) (hmem : selector ∈ selectors) (hm : selector.Matches forest.toOrderedForest node) :
    selector.specificity.Le weight := by
  exact GenericSelectorList.selected_upper_bound (ExecutableSelectorModel.combined forest) selectors node weight h selector hmem hm

def CombinedList.SelectedWeight {Node : Type} (forest : OrderedForest Node)
    (selectors : List CombinedSyntax) (node : Node) (weight : Specificity) : Prop :=
  GenericSelectorList.SelectedWeight (SelectorModel.combined forest) selectors node weight

theorem CombinedList.some_iff {Node : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (selectors : List CombinedSyntax) (node : Node) (weight : Specificity) :
    matchingSpecificity forest selectors node = some weight ↔
      SelectedWeight forest.toOrderedForest selectors node weight := by
  exact GenericSelectorList.some_iff (ExecutableSelectorModel.combined forest) selectors node weight

abbrev StyleRule (Value : Type) := GenericStyleRule CombinedSyntax Value

abbrev StyleRule.mk {Value : Type} (selectors : List CombinedSyntax)
    (declaration : StyleDeclaration Value) : StyleRule Value :=
  GenericStyleRule.mk selectors declaration

def StyleRule.Instance {Node Value : Type} (forest : OrderedForest Node)
    (rule : StyleRule Value) (node : Node) (entry : CascadeEntry Value) : Prop :=
  GenericStyleRule.Instance (SelectorModel.combined forest) rule node entry

def StyleRule.instantiate {Node Value : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (rule : StyleRule Value) (node : Node) : Option (CascadeEntry Value) :=
  GenericStyleRule.instantiate (ExecutableSelectorModel.combined forest) rule node

theorem StyleRule.instantiate_iff {Node Value : Type} [DecidableEq Node]
    (forest : FiniteForest Node) (rule : StyleRule Value) (node : Node) (entry : CascadeEntry Value) :
    rule.instantiate forest node = some entry ↔ rule.Instance forest.toOrderedForest node entry := by
  exact GenericStyleRule.instantiate_iff (ExecutableSelectorModel.combined forest) rule node entry

def Style.candidates {Node Value : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (rules : List (StyleRule Value)) (node : Node) : List (CascadeEntry Value) :=
  GenericStyle.candidates (ExecutableSelectorModel.combined forest) rules node

theorem Style.candidate_mem_iff {Node Value : Type} [DecidableEq Node]
    (forest : FiniteForest Node) (rules : List (StyleRule Value)) (node : Node)
    (entry : CascadeEntry Value) :
    entry ∈ candidates forest rules node ↔
      ∃ rule ∈ rules, rule.Instance forest.toOrderedForest node entry := by
  exact GenericStyle.candidate_mem_iff (ExecutableSelectorModel.combined forest) rules node entry

def Style.Winner {Node Value : Type} (forest : OrderedForest Node)
    (rules : List (StyleRule Value)) (node : Node) (selected : CascadeEntry Value) : Prop :=
  GenericStyle.Winner (SelectorModel.combined forest) rules node selected

def Style.winner {Node Value : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (rules : List (StyleRule Value)) (node : Node) : Option (CascadeEntry Value) :=
  GenericStyle.winner (ExecutableSelectorModel.combined forest) rules node

theorem Style.winner_sound {Node Value : Type} [DecidableEq Node]
    (forest : FiniteForest Node) (rules : List (StyleRule Value)) (node : Node)
    (selected : CascadeEntry Value) (h : winner forest rules node = some selected) :
    Winner forest.toOrderedForest rules node selected := by
  exact GenericStyle.winner_sound (ExecutableSelectorModel.combined forest) rules node selected h

def Style.Cascaded {Node Value : Type} (forest : OrderedForest Node)
    (rules : List (StyleRule Value)) (node : Node) : Option Value → Prop :=
  GenericStyle.Cascaded (SelectorModel.combined forest) rules node

def Style.cascaded {Node Value : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (rules : List (StyleRule Value)) (node : Node) : Option Value :=
  GenericStyle.cascaded (ExecutableSelectorModel.combined forest) rules node

theorem Style.cascaded_sound {Node Value : Type} [DecidableEq Node]
    (forest : FiniteForest Node) (rules : List (StyleRule Value)) (node : Node) :
    Cascaded forest.toOrderedForest rules node (cascaded forest rules node) := by
  exact GenericStyle.cascaded_sound (ExecutableSelectorModel.combined forest) rules node

def Style.compute {Node Value : Type} [DecidableEq Node] (forest : FiniteForest Node)
    (profile : PropertyProfile Value) (rules : List (StyleRule (CascadedValue Value)))
    (node : Node) : Value :=
  computeProperty forest.toElementForest profile (cascaded forest rules) node

def Style.Computed {Node Value : Type} (forest : OrderedForest Node)
    (profile : PropertyProfile Value) (rules : List (StyleRule (CascadedValue Value)))
    (node : Node) (value : Value) : Prop :=
  GenericStyle.Computed (SelectorModel.combined forest) profile rules node value

theorem Style.compute_eq_generic {Node Value : Type} [DecidableEq Node]
    (forest : FiniteForest Node) (profile : PropertyProfile Value)
    (rules : List (StyleRule (CascadedValue Value))) (node : Node) :
    compute forest profile rules node =
      GenericStyle.compute (ExecutableSelectorModel.combined forest) profile rules node := rfl

theorem Style.compute_sound {Node Value : Type} [DecidableEq Node]
    (forest : FiniteForest Node) (profile : PropertyProfile Value)
    (rules : List (StyleRule (CascadedValue Value))) (node : Node) :
    Computed forest.toOrderedForest profile rules node (compute forest profile rules node) := by
  exact GenericStyle.compute_sound (ExecutableSelectorModel.combined forest) profile rules node

end CssSemantics
