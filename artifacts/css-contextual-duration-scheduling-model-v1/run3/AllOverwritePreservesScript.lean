import DurationScheduling
open DurationScheduling
example : (overwriteStep scriptStart ⟨.animation, 1500⟩).applied = scriptStart.applied := by decide
