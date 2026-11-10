import JsonCodec

open Lean CssDerivation CssDerivation.TypedCodec

def main (args : List String) : IO Unit := do
  for text in args do
    let value : Option Nat := do
      let j ← (Json.parse text).toOption
      let data ← (foldJson [] j).atom.expression
      let expression ← checkExpr [] .nat data
      some (FirstOrder.eval expression .nil)
    IO.println (toJson value).compress
