import JsonV2

open Lean

def main (args : List String) : IO UInt32 := do
  if args.length != 2 then
    throw (IO.userError "expected program.json cases.json")
  let grammar ← IO.ofExcept (Json.parse (← IO.FS.readFile args[0]!) >>= CssUnordered.readGrammar)
  let cases ← IO.ofExcept (Json.parse (← IO.FS.readFile args[1]!) >>= Json.getArr?)
  let out ← IO.getStdout
  for case in cases do
    let words ← IO.ofExcept (CssGrammar.readWords case)
    out.putStrLn ((Json.arr #[toJson words, toJson (CssGrammar.accepts grammar words)]).compress)
  return 0
