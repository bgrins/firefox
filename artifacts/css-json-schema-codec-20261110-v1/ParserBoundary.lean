import Encoder

open Lean CssDerivation CssDerivation.JsonSchema

def main (args : List String) : IO Unit := do
  for text in args do
    let value : Option Nat := do
      let j ← (Json.parse text).toOption
      let expression ← checkExprJson [] [] .nat j
      some (FirstOrder.eval expression .nil)
    IO.println (toJson value).compress
