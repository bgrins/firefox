import RecordedFilter

open HyphenScalarFilter HyphenRecordedFilter

def classify (kind : Nat) : Category :=
  if kind == 6 then .mn else if kind == 15 then .control
  else if kind == 16 then .format else if kind == 18 then .surrogate
  else if [19,20,21,22,23,28,29].contains kind then .punctuation else .other

def expect (value : Option α) (message : String) : Except String α :=
  match value with
  | some a => .ok a
  | none => .error message

def process (line : String) : Except String String := do
  let fields := (line.trimAscii.toString.splitOn " ").filter (fun s => !s.isEmpty)
  let identity ← expect fields.head? "empty input"
  let values ← fields.tail.mapM (fun s => expect s.toNat? s!"invalid number {s}")
  let minimum := values[0]?.getD 0
  let pre := values[1]?.getD 0
  let after := values[2]?.getD 0
  let n := values[3]?.getD 0
  let units := (values.drop 4).take n
  let mask := (values.drop (4+n)).take n
  let old := (values.drop (4+2*n)).take n
  let cpCount := values[4+3*n]?.getD 0
  let cats := values.drop (5+3*n)
  if values.length != 5+3*n+2*cpCount then throw "wrong field count"
  let category := fun cp => classify (((List.range cpCount).find?
    (fun i => cats[2*i]?.getD 0 == cp)).map
      (fun i => cats[2*i+1]?.getD 0) |>.getD 0)
  let provider := fun i => mask[i]?.getD 0 != 0
  let original := fun i => old[i]?.getD 0
  let native := nativeFilter category units minimum pre after provider original
  let reference := writes (referenceCandidates category units minimum pre after provider original)
    (fun _ => 2) original
  let positions := List.range n
  let result := positions.map native
  if result != positions.map reference then throw "native/reference discrepancy"
  pure (identity ++ " " ++ String.join (result.map toString))

partial def loop (input output : IO.FS.Stream) : IO Unit := do
  let line ← input.getLine
  if line.isEmpty then return
  match process line with
  | .error message => throw (IO.userError message)
  | .ok value => output.putStrLn value
  loop input output

def main : IO Unit := do
  loop (← IO.getStdin) (← IO.getStdout)
