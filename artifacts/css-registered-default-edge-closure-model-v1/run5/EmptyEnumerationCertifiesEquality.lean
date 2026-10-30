import DefaultClosure
open DefaultClosure
example : count ([] : List Bool) (fun _ => false) = count [] (fun _ => true) → (false = true) := by decide
