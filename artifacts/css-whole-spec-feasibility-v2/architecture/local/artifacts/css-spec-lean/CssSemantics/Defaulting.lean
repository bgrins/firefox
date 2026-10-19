import CssSemantics.Dom

namespace CssSemantics

structure PropertyProfile (Value : Type) where
  inherited : Bool
  initial : Value

inductive CascadedValue (Value : Type) where
  | literal (value : Value)
  | initial
  | inherit
  | unset
  deriving DecidableEq, Repr

def InheritedValue (profile : PropertyProfile Value) (parent : Option Value) (value : Value) : Prop :=
  (∃ parentValue, parent = some parentValue ∧ value = parentValue) ∨
    (parent = none ∧ value = profile.initial)

def DefaultValue (profile : PropertyProfile Value) (parent : Option Value) (value : Value) : Prop :=
  (profile.inherited = true ∧ InheritedValue profile parent value) ∨
    (profile.inherited = false ∧ value = profile.initial)

def Resolves (profile : PropertyProfile Value) (parent : Option Value) :
    Option (CascadedValue Value) → Value → Prop
  | some (.literal expected), value => value = expected
  | some .initial, value => value = profile.initial
  | some .inherit, value => InheritedValue profile parent value
  | none, value | some .unset, value => DefaultValue profile parent value

def resolve (profile : PropertyProfile Value) (parent : Option Value)
    (cascaded : Option (CascadedValue Value)) : Value :=
  let inherited := parent.getD profile.initial
  let defaulted := if profile.inherited then inherited else profile.initial
  match cascaded with
  | some (.literal value) => value
  | some .initial => profile.initial
  | some .inherit => inherited
  | none | some .unset => defaulted

theorem resolve_eq_iff (profile : PropertyProfile Value) (parent : Option Value)
    (cascaded : Option (CascadedValue Value)) (value : Value) :
    resolve profile parent cascaded = value ↔ Resolves profile parent cascaded value := by
  cases cascaded with
  | none => cases h : profile.inherited <;> cases parent <;>
      simp [resolve, Resolves, DefaultValue, InheritedValue, h, eq_comm]
  | some cascaded => cases cascaded <;> cases h : profile.inherited <;> cases parent <;>
      simp [resolve, Resolves, DefaultValue, InheritedValue, h, eq_comm]

theorem Resolves.unique (profile : PropertyProfile Value) (parent : Option Value)
    (cascaded : Option (CascadedValue Value)) {left right : Value}
    (hl : Resolves profile parent cascaded left) (hr : Resolves profile parent cascaded right) :
    left = right :=
  ((resolve_eq_iff profile parent cascaded left).mpr hl).symm.trans
    ((resolve_eq_iff profile parent cascaded right).mpr hr)

def computeProperty {Node Value : Type} (forest : ElementForest Node)
    (profile : PropertyProfile Value) (cascaded : Node → Option (CascadedValue Value))
    (node : Node) : Value :=
  match _h : forest.parent node with
  | none => resolve profile none (cascaded node)
  | some parent => resolve profile (some (computeProperty forest profile cascaded parent)) (cascaded node)
termination_by forest.depth node
decreasing_by exact forest.parent_depth _h

def ComputedProperty {Node Value : Type} (forest : ElementForest Node)
    (profile : PropertyProfile Value) (cascaded : Node → Option (CascadedValue Value))
    (node : Node) (value : Value) : Prop :=
  match _h : forest.parent node with
  | none => Resolves profile none (cascaded node) value
  | some parent => ∃ inherited,
      ComputedProperty forest profile cascaded parent inherited ∧
      Resolves profile (some inherited) (cascaded node) value
termination_by forest.depth node
decreasing_by exact forest.parent_depth _h

theorem computeProperty_eq_iff {Node Value : Type} (forest : ElementForest Node)
    (profile : PropertyProfile Value) (cascaded : Node → Option (CascadedValue Value))
    (node : Node) (value : Value) :
    computeProperty forest profile cascaded node = value ↔
      ComputedProperty forest profile cascaded node value := by
  rw [computeProperty, ComputedProperty]
  split
  next => exact resolve_eq_iff profile none (cascaded node) value
  next parent hp =>
    constructor
    · intro h
      exact ⟨computeProperty forest profile cascaded parent,
        (computeProperty_eq_iff forest profile cascaded parent _).mp rfl,
        (resolve_eq_iff profile _ _ _).mp h⟩
    · rintro ⟨inherited, hi, hr⟩
      have he := (computeProperty_eq_iff forest profile cascaded parent inherited).mpr hi
      rw [he]
      exact (resolve_eq_iff profile _ _ _).mpr hr
termination_by forest.depth node
decreasing_by all_goals exact forest.parent_depth (by assumption)

theorem ComputedProperty.unique {Node Value : Type} (forest : ElementForest Node)
    (profile : PropertyProfile Value) (cascaded : Node → Option (CascadedValue Value))
    (node : Node) {left right : Value}
    (hl : ComputedProperty forest profile cascaded node left)
    (hr : ComputedProperty forest profile cascaded node right) : left = right :=
  ((computeProperty_eq_iff forest profile cascaded node left).mpr hl).symm.trans
    ((computeProperty_eq_iff forest profile cascaded node right).mpr hr)

end CssSemantics
