import RuntimeSupport

open Lean CssNumberLexicalBridge CssDerivation CssDerivation.ParserJson CssDerivation.NumberTransfer

def main (args : List String) : IO Unit := do
  let [documentPath, corpusPath] := args | throw (IO.userError "expected document and corpus paths")
  let json ← IO.ofExcept (Json.parse (← IO.FS.readFile documentPath))
  let some program := readDocument NumberShape json | throw (IO.userError "document rejected")
  for (source, oldError) in ← readCases corpusPath do
    let some bytes := admittedBytes source
      | IO.println (refusalJson source oldError).compress; continue
    let (result, state) := CssParserLowering.run (CssParserLowering.lower program) ⟨scalars bytes, oldError⟩
    let some parts := result | throw (IO.userError "parser failed")
    IO.println (resultJson source oldError (observeParts (scalars bytes) parts state.input) state.error).compress
