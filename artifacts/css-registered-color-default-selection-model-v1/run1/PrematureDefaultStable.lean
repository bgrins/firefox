import DefaultSelection
open DefaultSelection
example : scheduled false (choose none (.specified .system)) false true = evaluate (choose none (.specified .system)) true := by decide
