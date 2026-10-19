import CssSemantics.Variables
import CssSemantics.FiniteGraph

namespace CssSemantics

structure VariableBindings (Token : Type) where
  entries : List (String × VariableExpr Token)
  unique : (entries.map Prod.fst).Nodup

namespace VariableBindings

def Depends (bindings : VariableBindings Token) (source target : String) : Prop :=
  ∃ expression, (source, expression) ∈ bindings.entries ∧ expression.References target

def dependsBool (bindings : VariableBindings Token) (source target : String) : Bool :=
  bindings.entries.any fun entry => decide (entry.1 = source ∧ target ∈ entry.2.references)

theorem dependsBool_iff (bindings : VariableBindings Token) (source target : String) :
    bindings.dependsBool source target = true ↔ bindings.Depends source target := by
  simp only [dependsBool, List.any_eq_true, decide_eq_true_eq, Depends]
  constructor
  · rintro ⟨⟨name, expression⟩, member, rfl, reference⟩
    exact ⟨expression, member, (expression.references_iff target).mp reference⟩
  · rintro ⟨expression, member, reference⟩
    exact ⟨(source, expression), member, rfl, (expression.references_iff target).mpr reference⟩

def names (bindings : VariableBindings Token) : List String :=
  bindings.entries.flatMap fun entry => entry.2.references

theorem dependency_supported (bindings : VariableBindings Token) (source target : String)
    (h : bindings.Depends source target) : target ∈ bindings.names := by
  rcases h with ⟨expression, member, reference⟩
  exact List.mem_flatMap.mpr ⟨(source, expression), member, (expression.references_iff target).mpr reference⟩

def graph (bindings : VariableBindings Token) : FiniteGraph String where
  nodes := bindings.names
  Edge := bindings.Depends
  edgeBool := bindings.dependsBool
  edgeBool_iff := bindings.dependsBool_iff
  edge_targets_mem := bindings.dependency_supported

def Cyclic (bindings : VariableBindings Token) (name : String) : Prop :=
  FiniteGraph.Reach bindings.Depends name name

def cyclicBool (bindings : VariableBindings Token) (name : String) : Bool :=
  bindings.graph.cyclicBool name

theorem cyclicBool_iff (bindings : VariableBindings Token) (name : String) :
    bindings.cyclicBool name = true ↔ bindings.Cyclic name :=
  bindings.graph.cyclicBool_iff name

theorem direct_cycle (bindings : VariableBindings Token) (name : String)
    (h : bindings.Depends name name) : bindings.Cyclic name := .edge h

theorem fallback_self_cycle (bindings : VariableBindings Token)
    (member : (name, VariableExpr.fallback target expression) ∈ bindings.entries)
    (reference : expression.References name) : bindings.Cyclic name :=
  bindings.direct_cycle name ⟨_, member, .fallback reference⟩

theorem cyclic_declared (bindings : VariableBindings Token) (name : String)
    (h : bindings.Cyclic name) : ∃ expression, (name, expression) ∈ bindings.entries := by
  have first : ∀ {left right}, FiniteGraph.Reach bindings.Depends left right →
      ∃ expression, (left, expression) ∈ bindings.entries := by
    intro left right path
    induction path with
    | edge edge => exact ⟨edge.choose, edge.choose_spec.1⟩
    | trans _ _ ih _ => exact ih
  exact first h

theorem cycles_congr (left right : VariableBindings Token)
    (same : ∀ source target, left.Depends source target ↔ right.Depends source target)
    (name : String) : left.cyclicBool name = right.cyclicBool name := by
  have transfer : ∀ (a b : VariableBindings Token),
      (∀ x y, a.Depends x y → b.Depends x y) →
      ∀ x y, FiniteGraph.Reach a.Depends x y → FiniteGraph.Reach b.Depends x y := by
    intro a b agree x y path
    induction path with
    | edge h => exact .edge (agree _ _ h)
    | trans _ _ first second => exact .trans first second
  apply Bool.eq_iff_iff.mpr
  rw [left.cyclicBool_iff, right.cyclicBool_iff]
  exact ⟨transfer left right (fun x y => (same x y).mp) name name,
    transfer right left (fun x y => (same x y).mpr) name name⟩

end VariableBindings
end CssSemantics
