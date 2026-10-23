import Subtree
open Subtree
example : let w : World := ⟨false, [], [], [leaf], []⟩;
    ((markPrincipal w).externalOutOfFlow.head?).any eligible = true := by decide
