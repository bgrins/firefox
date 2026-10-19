import Bridge
open Tab

def parse (line : String) : Except String Input := do
  let values ← (line.splitOn " ").mapM fun s => match s.toInt? with | some n => Except.ok n | none => Except.error s!"invalid integer {s}"
  let get := fun (i : Nat) => values[i]?.getD 0
  let tokens := (values.drop 13).map fun n => if n == -1 then Token.tab else Token.glyph n.toNat
  if values.length != (get 2).toNat + 13 then throw "row length"
  if get 5 != 0 || get 9 != 0 || get 11 != 0 then throw "outside Lean bridge domain"
  return { id := (get 0).toNat, mode := (get 1).toNat, tokens := tokens,
           begin := (get 3).toNat, ending := (get 4).toNat, width := get 6,
           minimum := get 7, initial := get 8, split := get 12 }

def main (args : List String) : IO Unit := do
  let input ← IO.getStdin
  let output ← IO.getStdout
  for line in (← input.readToEnd).splitOn "\n" do
    if !line.isEmpty then
      match parse line with
      | .error e => throw (IO.userError e)
      | .ok c => output.putStrLn (encode (args == ["candidate"]) c)
