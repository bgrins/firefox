import Gap
example : MoveCoverage.refresh
    (fun n => ([0,1,2,3] : List Nat).idxOf n + 1)
    (fun n => ([1,2,0,3] : List Nat).idxOf n + 1)
    (fun n => decide (n = 0)) 1 =
    ([1,2,0,3] : List Nat).idxOf 1 + 1 := by decide
