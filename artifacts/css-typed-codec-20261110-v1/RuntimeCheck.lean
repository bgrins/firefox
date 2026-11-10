import Fixture

open Lean CssDerivation CssDerivation.TypedCodec

def main (args : List String) : IO Unit := do
  let path :: inputs := args | throw (IO.userError "usage: RuntimeCheck.lean fixture.json input ...")
  let text ← IO.FS.readFile path
  let some program := decodeText text | throw (IO.userError "document refused")
  unless encodeStmt program = encodeStmt FirstOrder.escapeTree do
    throw (IO.userError "parsed tree differs from proved fixture")
  for input in inputs do
    let result := FirstOrder.execute program input.toList
    let row := Lean.Json.mkObj [
      ("input", toJson input), ("value", toJson result.value.toNat),
      ("rest", toJson (String.ofList result.rest)), ("error", toJson result.error)]
    IO.println row.compress
