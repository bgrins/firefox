import ClosureRepair
open TerminalString ClosureRepair
example : consume (raw 0 ++ [.quote] ++ [.other 1]) = consume (repaired 0 ++ [.other 1]) := by decide
