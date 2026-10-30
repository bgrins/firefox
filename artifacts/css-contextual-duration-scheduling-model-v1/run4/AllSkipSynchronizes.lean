import DurationScheduling
open DurationScheduling
example : (skipStep cssStart ⟨.animation, 1500⟩).applied = (skipStep cssStart ⟨.animation, 1500⟩).computed := by decide
