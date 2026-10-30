import DurationScheduling
open DurationScheduling
example : (equalityStep cssStart ⟨.animation, 1500⟩).applied = (equalityStep cssStart ⟨.animation, 1500⟩).computed := by decide
