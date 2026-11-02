import Resumption
open SelectedDeclaration PreparationStability SelectedResumption
example : (resumedScan Nat.mul rollbackEligible rollbackPlan 0 [0, 1, 2, 3]).reads = ["size", "scale"] := by decide
