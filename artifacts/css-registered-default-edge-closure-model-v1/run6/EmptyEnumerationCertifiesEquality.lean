import DefaultClosure
open DefaultClosure
example : count ([] : List Bool) (fun _ => false) = count ([] : List Bool) (fun _ => true) → (false = true) := by decide
