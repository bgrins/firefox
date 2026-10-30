import Dag
open Dag
example : Covered branchEdit (firstDependencyOnly branchEdit branchAdmission) := by
  simp only [Ready, Consistent, Covered]
  decide
