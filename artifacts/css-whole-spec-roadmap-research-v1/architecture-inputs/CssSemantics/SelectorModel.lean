import CssSemantics.ContextSyntax

namespace CssSemantics

structure SelectorModel (Node Selector : Type) where
  forest : ElementForest Node
  Matches : Selector → Node → Prop
  specificity : Selector → Specificity

structure ExecutableSelectorModel (Node Selector : Type) extends SelectorModel Node Selector where
  matchesBool : Selector → Node → Bool
  matchesBool_iff : ∀ selector node, matchesBool selector node = true ↔ Matches selector node

def SelectorModel.combined {Node : Type} (forest : OrderedForest Node) :
    SelectorModel Node CombinedSyntax where
  forest := forest.toElementForest
  Matches := CombinedSyntax.Matches forest
  specificity := CombinedSyntax.specificity

def ExecutableSelectorModel.combined {Node : Type} [DecidableEq Node] (forest : FiniteForest Node) :
    ExecutableSelectorModel Node CombinedSyntax where
  toSelectorModel := SelectorModel.combined forest.toOrderedForest
  matchesBool := CombinedSyntax.matchesBool forest
  matchesBool_iff := CombinedSyntax.matchesBool_iff forest

def SelectorModel.contextual {Node : Type} (context : ContentContext Node) (profile : EmptyProfile) :
    SelectorModel Node ContextSyntax where
  forest := context.toElementForest
  Matches := ContextSyntax.Matches context profile
  specificity := ContextSyntax.specificity

def ExecutableSelectorModel.contextual {Node : Type} [DecidableEq Node]
    (context : ContentContext Node) (profile : EmptyProfile) :
    ExecutableSelectorModel Node ContextSyntax where
  toSelectorModel := SelectorModel.contextual context profile
  matchesBool := ContextSyntax.matchesBool context profile
  matchesBool_iff := ContextSyntax.matchesBool_iff context profile

theorem SelectorModel.combined_matches {Node : Type} (forest : OrderedForest Node)
    (selector : CombinedSyntax) (node : Node) :
    (combined forest).Matches selector node ↔ selector.Matches forest node := Iff.rfl

theorem SelectorModel.contextual_matches {Node : Type} (context : ContentContext Node)
    (profile : EmptyProfile) (selector : ContextSyntax) (node : Node) :
    (contextual context profile).Matches selector node ↔ selector.Matches context profile node := Iff.rfl

end CssSemantics
