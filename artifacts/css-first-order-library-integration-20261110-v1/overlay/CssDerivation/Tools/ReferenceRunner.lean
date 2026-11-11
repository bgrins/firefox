import CssDerivation.Examples.EscapeDocument

open Lean CssDerivation CssDerivation.JsonSchema

def main (args : List String) : IO Unit := do
  let path :: inputs := args | throw (IO.userError "usage: ReferenceRunner.lean fixture.json input ...")
  let text ← IO.FS.readFile path
  let some program := readDocumentText text | throw (IO.userError "document refused")
  unless TypedCodec.encodeStmt program = TypedCodec.encodeStmt FirstOrder.escapeTree do
    throw (IO.userError "parsed tree differs from proved fixture")
  for input in inputs do
    let result := FirstOrder.execute program input.toList
    IO.println (Json.mkObj [
      ("input", toJson input), ("value", toJson result.value.toNat),
      ("rest", toJson (String.ofList result.rest)), ("error", toJson result.error)]).compress
