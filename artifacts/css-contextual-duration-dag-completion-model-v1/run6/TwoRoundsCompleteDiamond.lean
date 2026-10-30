import Dag
open Dag
example : Ready (run diamond 2 diamondInitial) := by
  simp only [Ready, Consistent, Covered]
  decide
