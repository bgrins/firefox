import CssDerivation.Codec.Document.Profile

open Lean CssDerivation CssDerivation.DocumentSchema

def main (args : List String) : IO Unit := do
  let profile :: path :: inputs := args | throw (IO.userError "usage: Runner.lean profile file input ...")
  let signatures ← match profile with
    | "escape" => pure escapeSignatures
    | "next" => pure [⟨"next", .nat, .scalar⟩]
    | "empty" => pure []
    | "fold" => pure [⟨"sum", .nat, .nat⟩]
    | _ => throw (IO.userError "profile refused")
  let text ← IO.FS.readFile path
  let some document := (Json.parse text).toOption | throw (IO.userError "JSON refused")
  let some program := readDocumentWith signatures .scalar document | throw (IO.userError "document refused")
  for input in inputs do
    let result := FirstOrder.execute program input.toList
    IO.println (Json.mkObj [("input", toJson input), ("value", toJson result.value.toNat),
      ("rest", toJson (String.ofList result.rest)), ("error", toJson result.error)]).compress
