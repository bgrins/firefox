import RuntimeSupport

open CssNumberLexicalBridge

def main (args : List String) : IO Unit := do
  let [corpusPath] := args | throw (IO.userError "expected corpus path")
  for (source, oldError) in ← readCases corpusPath do
    let some bytes := admittedBytes source
      | IO.println (refusalJson source oldError).compress; continue
    IO.println (resultJson source oldError (observeNative (NumericLexical.reference bytes)) oldError).compress
