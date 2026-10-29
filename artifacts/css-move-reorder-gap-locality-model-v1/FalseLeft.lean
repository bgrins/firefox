import Gap
example : MoveCoverage.refresh
    (fun n => ([0,1,2,3] : List Nat).idxOf n + 1)
    (fun n => ([2,0,1,3] : List Nat).idxOf n + 1)
    (fun n => decide (n = 2 ∨ (0 < ([0,1,2,3] : List Nat).idxOf n ∧
      ([0,1,2,3] : List Nat).idxOf n < 2))) 0 =
    ([2,0,1,3] : List Nat).idxOf 0 + 1 := by decide
