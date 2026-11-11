import NumberDocument
open Lean CssDerivation CssDerivation.ParserIR CssDerivation.ParserJson CssDerivation.NumberTransfer

def sources : List String :=
  ["0", "-0", "+12x", "00123!", ".5;", "-.5", "1.20", "1.", "1e2x", "1E-2!",
   "1e+", "1.ee2", "1ee2", "1e-0", "123456789012345678901234567890.125e-7!",
   "1e999999999999999999999999999999!", String.ofList (List.replicate 128 '9') ++ "e-140!",
   "", "e2", "+.", "١2"]

def row (source : String) (oldError : Bool) (result : Option Exact × State) : Json :=
  let common := [("source", .str source), ("error_before", .bool oldError),
    ("rest", .str (String.ofList result.2.input)), ("error_after", .bool result.2.error)]
  match result.1 with
  | none => Json.mkObj (common ++ [("matched", .bool false)])
  | some value => Json.mkObj (common ++ [("matched", .bool true),
      ("significand", .str (toString value.significand)), ("scale", .str (toString value.scale)),
      ("type", .str (if value.isNumber then "number" else "integer")),
      ("sign", value.sign.map (fun c => .str (String.singleton c)) |>.getD .null)])

def main (args : List String) : IO Unit := do
  let [path] := args | throw (IO.userError "expected one parser document path")
  let text ← IO.FS.readFile path
  let .ok json := Json.parse text | throw (IO.userError "invalid JSON text")
  let some parser := readDocument NumberShape json | throw (IO.userError "rejected parser document")
  for source in sources do
    for oldError in [false, true] do
      IO.println ((row source oldError (projectRun parser ⟨source.toList, oldError⟩)).compress)
