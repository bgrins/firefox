import Std

namespace CssSemantics

structure Element where
  namespaceURI : Option String
  localName : String
  id : Option String := none
  classes : List String := []
  deriving DecidableEq, Repr

structure ElementForest (Node : Type) where
  element : Node → Element
  parent : Node → Option Node
  depth : Node → Nat
  parent_depth : ∀ {child ancestor}, parent child = some ancestor →
    depth ancestor < depth child

inductive Ancestor {Node : Type} (forest : ElementForest Node) : Node → Node → Prop
  | direct {ancestor child} : forest.parent child = some ancestor →
      Ancestor forest ancestor child
  | trans {ancestor middle child} : Ancestor forest ancestor middle →
      Ancestor forest middle child → Ancestor forest ancestor child

theorem Ancestor.depth_lt {Node : Type} {forest : ElementForest Node}
    {ancestor child : Node} (h : Ancestor forest ancestor child) :
    forest.depth ancestor < forest.depth child := by
  induction h with
  | direct hp => exact forest.parent_depth hp
  | trans _ _ ih₁ ih₂ => exact Nat.lt_trans ih₁ ih₂

theorem Ancestor.irrefl {Node : Type} {forest : ElementForest Node} (node : Node) :
    ¬ Ancestor forest node node := by
  intro h
  exact Nat.lt_irrefl _ h.depth_lt

end CssSemantics
