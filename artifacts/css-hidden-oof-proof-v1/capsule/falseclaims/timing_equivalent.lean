import OOF
example : OOF.resizeFlag (OOF.prepare .beforeInput true OOF.clean) true = OOF.resizeFlag (OOF.prepare .afterInput true OOF.clean) true := by decide
