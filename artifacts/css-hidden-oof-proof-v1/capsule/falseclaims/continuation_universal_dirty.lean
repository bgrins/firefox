import OOF
example : Subtree.eligible (OOF.execute .beforeInput true true true OOF.erasingProvider OOF.centered OOF.clean).tree = true := by decide
