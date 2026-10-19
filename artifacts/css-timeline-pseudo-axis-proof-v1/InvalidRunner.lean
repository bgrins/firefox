import Runner
open Lean

def main (args : List String) : IO Unit := do
  let input ← IO.FS.readFile args[0]!
  let stdout ← IO.getStdout
  for line in input.splitOn "\n" do
    if line.isEmpty then continue
    let parsed ← IO.ofExcept (Json.parse line)
    let c : Scenario ← IO.ofExcept (fromJson? parsed)
    for w in c.worlds do
      if Timeline.Typed.rolesValid w then throw (IO.userError s!"accepted invalid typed role {c.id}")
    stdout.putStrLn s!"rejected {c.id}"
