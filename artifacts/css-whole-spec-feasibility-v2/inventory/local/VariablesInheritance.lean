import CssSemantics.GenericVariableEnvironment

namespace CssSemantics.VariableEnvironment

def compute {Node Token : Type} (forest : ElementForest Node)
    (declarations : Node → VariableBindings Token) (node : Node) : String → Option (List Token) :=
  GenericVariableEnvironment.compute .snapshot forest declarations node

def Computed {Node Token : Type} (forest : ElementForest Node)
    (declarations : Node → VariableBindings Token) (node : Node)
    (environment : String → Option (List Token)) : Prop :=
  GenericVariableEnvironment.Computed .snapshot forest declarations node environment

theorem compute_eq_generic {Node Token : Type} (forest : ElementForest Node)
    (declarations : Node → VariableBindings Token) (node : Node) :
    compute forest declarations node =
      GenericVariableEnvironment.compute .snapshot forest declarations node := rfl

theorem compute_iff {Node Token : Type} (forest : ElementForest Node)
    (declarations : Node → VariableBindings Token) (node : Node)
    (environment : String → Option (List Token)) :
    compute forest declarations node = environment ↔ Computed forest declarations node environment :=
  GenericVariableEnvironment.compute_iff .snapshot forest declarations node environment

theorem Computed.unique {Node Token : Type} (forest : ElementForest Node)
    (declarations : Node → VariableBindings Token) (node : Node)
    {a b : String → Option (List Token)} (first : Computed forest declarations node a)
    (second : Computed forest declarations node b) : a = b :=
  GenericVariableEnvironment.Computed.unique .snapshot forest declarations node first second

theorem missing_inherits {Node Token : Type} (forest : ElementForest Node)
    (declarations : Node → VariableBindings Token) (node parent : Node) (name : String)
    (parentEq : forest.parent node = some parent) (missing : (declarations node).lookup name = none) :
    compute forest declarations node name = compute forest declarations parent name := by
  unfold compute
  rw [GenericVariableEnvironment.compute]
  split
  next h => simp [parentEq] at h
  next found h =>
    have equal : found = parent := Option.some.inj (h.symm.trans parentEq)
    subst found
    exact (declarations node).computeWithBase_missing _ name missing

theorem root_missing_invalid {Node Token : Type} (forest : ElementForest Node)
    (declarations : Node → VariableBindings Token) (node : Node) (name : String)
    (root : forest.parent node = none) (missing : (declarations node).lookup name = none) :
    compute forest declarations node name = none := by
  unfold compute
  rw [GenericVariableEnvironment.compute]
  split
  next => exact (declarations node).computeWithBase_missing _ name missing
  next found h => simp [root] at h

theorem cycle_invalid {Node Token : Type} (forest : ElementForest Node)
    (declarations : Node → VariableBindings Token) (node : Node) (name : String)
    (cycle : (declarations node).Cyclic name) :
    compute forest declarations node name = none := by
  unfold compute
  rw [GenericVariableEnvironment.compute]
  exact (declarations node).computeWithBase_cyclic _ name cycle

end CssSemantics.VariableEnvironment
