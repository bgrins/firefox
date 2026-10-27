import Std

namespace CssSemantics

namespace FiniteGraph

inductive Reach {Node : Type} (edge : Node → Node → Prop) : Node → Node → Prop
  | edge {x y} : edge x y → Reach edge x y
  | trans {x y z} : Reach edge x y → Reach edge y z → Reach edge x z

def pivot {Node : Type} (relation : Node → Node → Bool) (middle : Node)
    (left right : Node) : Bool :=
  relation left right || (relation left middle && relation middle right)

def closure {Node : Type} (relation : Node → Node → Bool) : List Node → Node → Node → Bool
  | [] => relation
  | middle :: rest => pivot (closure relation rest) middle

def TransAt {Node : Type} (relation : Node → Node → Bool) (middle : Node) : Prop :=
  ∀ left right, relation left middle = true → relation middle right = true →
    relation left right = true

theorem pivot_contains {Node : Type} (relation : Node → Node → Bool)
    (middle left right : Node) (h : relation left right = true) :
    pivot relation middle left right = true := by
  simp [pivot, h]

theorem pivot_transAt {Node : Type} (relation : Node → Node → Bool) (middle : Node) :
    TransAt (pivot relation middle) middle := by
  intro left right hl hr
  simp only [pivot, Bool.or_eq_true, Bool.and_eq_true] at *
  exact Or.inr ⟨hl.elim id And.left, hr.elim id And.right⟩

theorem pivot_preserves_transAt {Node : Type} (relation : Node → Node → Bool)
    (middle prior : Node) (h : TransAt relation prior) :
    TransAt (pivot relation middle) prior := by
  intro left right hl hr
  simp only [pivot, Bool.or_eq_true, Bool.and_eq_true] at *
  rcases hl with hl | ⟨hl, hm⟩
  · rcases hr with hr | ⟨hp, hr⟩
    · exact Or.inl (h left right hl hr)
    · exact Or.inr ⟨h left middle hl hp, hr⟩
  · rcases hr with hr | ⟨_, hr⟩
    · exact Or.inr ⟨hl, h middle right hm hr⟩
    · exact Or.inr ⟨hl, hr⟩

theorem closure_contains {Node : Type} (relation : Node → Node → Bool)
    (nodes : List Node) (left right : Node) (h : relation left right = true) :
    closure relation nodes left right = true := by
  induction nodes with
  | nil => exact h
  | cons middle rest ih => exact pivot_contains _ _ _ _ ih

theorem closure_transAt {Node : Type} (relation : Node → Node → Bool)
    (nodes : List Node) (middle : Node) (h : middle ∈ nodes) :
    TransAt (closure relation nodes) middle := by
  induction nodes with
  | nil => simp at h
  | cons head rest ih =>
      rcases List.mem_cons.mp h with rfl | h
      · exact pivot_transAt _ _
      · exact pivot_preserves_transAt _ _ _ (ih h)

theorem closure_sound {Node : Type} (edge : Node → Node → Prop)
    (relation : Node → Node → Bool) (correct : ∀ x y, relation x y = true ↔ edge x y)
    (nodes : List Node) (left right : Node) :
    closure relation nodes left right = true → Reach edge left right := by
  induction nodes generalizing left right with
  | nil => intro h; exact .edge ((correct _ _).mp h)
  | cons middle rest ih =>
      simp only [closure, pivot, Bool.or_eq_true, Bool.and_eq_true]
      rintro (h | ⟨hl, hr⟩)
      · exact ih _ _ h
      · exact .trans (ih _ _ hl) (ih _ _ hr)

theorem Reach.target_mem {Node : Type} {edge : Node → Node → Prop} {nodes : List Node}
    (supported : ∀ x y, edge x y → y ∈ nodes) {left right : Node}
    (h : Reach edge left right) : right ∈ nodes := by
  induction h with
  | edge h => exact supported _ _ h
  | trans _ _ _ ih => exact ih

theorem closure_complete {Node : Type} (edge : Node → Node → Prop)
    (relation : Node → Node → Bool) (correct : ∀ x y, relation x y = true ↔ edge x y)
    (nodes : List Node) (supported : ∀ x y, edge x y → y ∈ nodes)
    (left right : Node) :
    Reach edge left right → closure relation nodes left right = true := by
  intro h
  induction h with
  | edge h => exact closure_contains _ _ _ _ ((correct _ _).mpr h)
  | trans hl _ ihl ihr =>
      exact closure_transAt relation nodes _ (hl.target_mem supported) _ _ ihl ihr

end FiniteGraph

structure FiniteGraph (Node : Type) where
  nodes : List Node
  Edge : Node → Node → Prop
  edgeBool : Node → Node → Bool
  edgeBool_iff : ∀ x y, edgeBool x y = true ↔ Edge x y
  edge_targets_mem : ∀ x y, Edge x y → y ∈ nodes

namespace FiniteGraph

def reachesBool {Node : Type} (graph : FiniteGraph Node) (left right : Node) : Bool :=
  closure graph.edgeBool graph.nodes left right

theorem reachesBool_iff {Node : Type} (graph : FiniteGraph Node) (left right : Node) :
    graph.reachesBool left right = true ↔ Reach graph.Edge left right :=
  ⟨closure_sound _ _ graph.edgeBool_iff _ _ _,
    closure_complete _ _ graph.edgeBool_iff _ graph.edge_targets_mem _ _⟩

def Cyclic {Node : Type} (graph : FiniteGraph Node) (node : Node) : Prop :=
  Reach graph.Edge node node

def cyclicBool {Node : Type} (graph : FiniteGraph Node) (node : Node) : Bool :=
  graph.reachesBool node node

theorem cyclicBool_iff {Node : Type} (graph : FiniteGraph Node) (node : Node) :
    graph.cyclicBool node = true ↔ graph.Cyclic node :=
  graph.reachesBool_iff node node

end FiniteGraph

end CssSemantics
