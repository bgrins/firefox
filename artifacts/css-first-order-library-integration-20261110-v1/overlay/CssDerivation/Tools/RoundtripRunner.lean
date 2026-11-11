import CssDerivation.Codec.Json.Document

open Lean CssDerivation CssDerivation.JsonSchema

def main (args : List String) : IO Unit := do
  let path :: inputs := args | throw (IO.userError "usage: RoundtripRunner.lean fixture.json input ...")
  let text ← IO.FS.readFile path
  let some original := readDocumentText text | throw (IO.userError "document refused")
  let canonical := encodeStmtJson original
  let .ok reparsed := Json.parse canonical.compress | throw (IO.userError "canonical JSON parse failed")
  let some program := checkStmtJson [] [] .scalar reparsed | throw (IO.userError "canonical JSON refused")
  unless TypedCodec.encodeStmt program = TypedCodec.encodeStmt original do
    throw (IO.userError "canonical text roundtrip changed tree")
  for input in inputs do
    let result := FirstOrder.execute program input.toList
    IO.println (Json.mkObj [
      ("input", toJson input), ("value", toJson result.value.toNat),
      ("rest", toJson (String.ofList result.rest)), ("error", toJson result.error)]).compress
