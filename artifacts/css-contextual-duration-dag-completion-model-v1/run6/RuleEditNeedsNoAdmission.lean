import Dag
open Dag
example : Covered editedDiamond settled := by
  simp only [Ready, Consistent, Covered]
  decide
