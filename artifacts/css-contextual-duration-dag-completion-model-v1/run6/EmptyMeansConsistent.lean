import Dag
open Dag
example : Consistent diamond discarded := by
  simp only [Ready, Consistent, Covered]
  decide
