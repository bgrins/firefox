import CssSemantics.VariablesGraph

namespace CssSemantics.VariableBindings

theorem countP_lt_of_witness {Node : Type} (nodes : List Node) (small large : Node → Bool)
    (subset : ∀ x ∈ nodes, small x = true → large x = true)
    (witness : ∃ x ∈ nodes, small x = false ∧ large x = true) :
    nodes.countP small < nodes.countP large := by
  induction nodes with
  | nil => simp at witness
  | cons head rest ih =>
    have subrest : ∀ x ∈ rest, small x = true → large x = true :=
      fun x hx => subset x (List.mem_cons_of_mem head hx)
    have le := List.countP_mono_left subrest
    rcases witness with ⟨x, member, hs, hl⟩
    rcases List.mem_cons.mp member with rfl | member
    · simp [hs, hl]; omega
    · have lt := ih subrest ⟨x, member, hs, hl⟩
      have subhead := subset head List.mem_cons_self
      cases hsmall : small head <;> cases hlarge : large head <;>
        simp_all <;> omega

def rankSupport (bindings : VariableBindings Token) : List String := bindings.names.eraseDups

def rank (bindings : VariableBindings Token) (name : String) : Nat :=
  bindings.rankSupport.countP (bindings.graph.reachesBool name)

theorem rank_le_support (bindings : VariableBindings Token) (name : String) :
    bindings.rank name ≤ bindings.rankSupport.length := List.countP_le_length

theorem rank_lt_of_reaches (bindings : VariableBindings Token)
    (path : FiniteGraph.Reach bindings.Depends owner target)
    (acyclic : ¬bindings.Cyclic target) : bindings.rank target < bindings.rank owner := by
  apply countP_lt_of_witness
  · intro x _ reachable
    apply (bindings.graph.reachesBool_iff _ _).mpr
    exact .trans path ((bindings.graph.reachesBool_iff _ _).mp reachable)
  · refine ⟨target, ?_, ?_, ?_⟩
    · simpa [rankSupport] using path.target_mem bindings.dependency_supported
    · cases h : bindings.graph.reachesBool target target with
      | false => rfl
      | true => exact False.elim (acyclic ((bindings.graph.reachesBool_iff _ _).mp h))
    · exact (bindings.graph.reachesBool_iff _ _).mpr path

theorem rank_decreases (bindings : VariableBindings Token)
    (edge : bindings.Depends owner target) (acyclic : ¬bindings.Cyclic target) :
    bindings.rank target < bindings.rank owner :=
  bindings.rank_lt_of_reaches (.edge edge) acyclic

end CssSemantics.VariableBindings
