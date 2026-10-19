import CssSemantics.Selectors

namespace CssSemantics

def NamespaceConstraint.matchesBool (constraint : NamespaceConstraint)
    (namespaceURI : Option String) : Bool :=
  match constraint with
  | .any => true
  | .exact expected => namespaceURI == expected

theorem NamespaceConstraint.matchesBool_iff (constraint : NamespaceConstraint)
    (namespaceURI : Option String) :
    constraint.matchesBool namespaceURI = true ↔ constraint.Matches namespaceURI := by
  cases constraint <;> simp [matchesBool, Matches]

def Compound.matchesBool (compound : Compound) (element : Element) : Bool :=
  compound.namespaceConstraint.matchesBool element.namespaceURI &&
  (match compound.localName with
   | none => true
   | some name => element.localName == name) &&
  compound.ids.all (fun id => element.id == some id) &&
  compound.classes.all (fun cls => element.classes.contains cls)

theorem Compound.matchesBool_iff (compound : Compound) (element : Element) :
    compound.matchesBool element = true ↔ compound.Matches element := by
  cases h : compound.localName <;>
    simp [matchesBool, Matches, h, NamespaceConstraint.matchesBool_iff, and_assoc]

theorem Ancestor.parent_step {Node : Type} {forest : ElementForest Node}
    {ancestor node : Node} (h : Ancestor forest ancestor node) :
    ∃ parent, forest.parent node = some parent ∧
      (ancestor = parent ∨ Ancestor forest ancestor parent) := by
  induction h with
  | direct hp => exact ⟨_, hp, Or.inl rfl⟩
  | trans hab _ _ ih =>
      obtain ⟨parent, hp, heq | ha⟩ := ih
      · subst parent
        exact ⟨_, hp, Or.inr hab⟩
      · exact ⟨parent, hp, Or.inr (.trans hab ha)⟩

def anyAncestor {Node : Type} (forest : ElementForest Node) (predicate : Node → Bool)
    (node : Node) : Bool :=
  match _h : forest.parent node with
  | none => false
  | some parent => predicate parent || anyAncestor forest predicate parent
termination_by forest.depth node
decreasing_by exact forest.parent_depth _h

theorem anyAncestor_iff {Node : Type} (forest : ElementForest Node)
    (predicate : Node → Bool) (node : Node) :
    anyAncestor forest predicate node = true ↔
      ∃ ancestor, Ancestor forest ancestor node ∧ predicate ancestor = true := by
  rw [anyAncestor]
  split
  next hp =>
    simp only [Bool.false_eq_true, false_iff]
    rintro ⟨ancestor, ha, _⟩
    obtain ⟨parent, hparent, _⟩ := ha.parent_step
    simp [hp] at hparent
  next parent hp =>
    rw [Bool.or_eq_true, anyAncestor_iff forest predicate parent]
    constructor
    · rintro (hm | ⟨ancestor, ha, hm⟩)
      · exact ⟨parent, .direct hp, hm⟩
      · exact ⟨ancestor, .trans ha (.direct hp), hm⟩
    · rintro ⟨ancestor, ha, hm⟩
      obtain ⟨otherParent, hparent, heq | hancestor⟩ := ha.parent_step
      · have he : otherParent = parent := Option.some.inj (hparent.symm.trans hp)
        exact Or.inl (by simpa only [heq, he] using hm)
      · have he : otherParent = parent := Option.some.inj (hparent.symm.trans hp)
        exact Or.inr ⟨ancestor, he ▸ hancestor, hm⟩
termination_by forest.depth node
decreasing_by
  apply forest.parent_depth
  assumption

def Selector.matchesBool {Node : Type} (forest : ElementForest Node) :
    Selector → Node → Bool
  | .compound c, node => c.matchesBool (forest.element node)
  | .child left c, node => c.matchesBool (forest.element node) &&
      match forest.parent node with
      | none => false
      | some parent => left.matchesBool forest parent
  | .descendant left c, node => c.matchesBool (forest.element node) &&
      anyAncestor forest (left.matchesBool forest) node

theorem Selector.matchesBool_iff {Node : Type} (forest : ElementForest Node)
    (selector : Selector) (node : Node) :
    selector.matchesBool forest node = true ↔ selector.Matches forest node := by
  induction selector generalizing node with
  | compound c => exact Compound.matchesBool_iff c (forest.element node)
  | child left subject ih =>
      cases h : forest.parent node <;>
        simp [matchesBool, Matches, h, Compound.matchesBool_iff, ih]
  | descendant left subject ih =>
      simp [matchesBool, Matches, Compound.matchesBool_iff, anyAncestor_iff, ih]

theorem Selector.matchesBool_ancestor_compounds {Node : Type}
    {forest : ElementForest Node} {selector : Selector} {node : Node}
    (h : selector.matchesBool forest node = true) :
    ∀ compound ∈ selector.ancestorCompounds,
      ∃ ancestor, Ancestor forest ancestor node ∧ compound.Matches (forest.element ancestor) := by
  exact matches_ancestor_compounds ((matchesBool_iff forest selector node).mp h)

end CssSemantics
