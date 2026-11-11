import JsonInput

open Lean CssGrammar

def main (args : List String) : IO UInt32 := do
  if args.length != 2 then
    throw (IO.userError "expected program.json cases.json")
  let input ← IO.FS.readFile args[0]!
  let grammar ← IO.ofExcept (Json.parse input >>= readGrammar)
  let cases ← IO.ofExcept (Json.parse (← IO.FS.readFile args[1]!) >>= Json.getArr?)
  let out ← IO.getStdout
  for case in cases do
    let words ← IO.ofExcept (readWords case)
    out.putStrLn ((Json.arr #[toJson words, toJson (accepts grammar words)]).compress)
  return 0
