import Witnesses
open Fragmentation
example :
    emergencyGuard regionInput [] = true ∧ emergencyGuard regionInput [atA 1] = false ∧
    RegionCandidateAdmitted regionInput [] ∧ RegionCandidateAdmitted regionInput [atA 1] := by decide
