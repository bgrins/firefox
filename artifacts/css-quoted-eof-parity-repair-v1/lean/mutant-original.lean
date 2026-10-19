import ParityRepair
open TerminalString ParityRepair
example : consume (slashes 1 ++ [.quote]) = consume (repaired 2) := by decide
