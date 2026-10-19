import ClosureRepair
open TerminalString ClosureRepair
example : (consume (raw 1)).closed = true := by decide
