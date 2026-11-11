import NumberDocument
open CssDerivation.ParserJson CssDerivation.NumberTransfer

def main (args : List String) : IO Unit := do
  let p := if args == ["changed"] then changedNumberTree else numberTree
  IO.println ((encodeDocument p).compress)
