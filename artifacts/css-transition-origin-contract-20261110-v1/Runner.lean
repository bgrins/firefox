import Cases

def main : IO UInt32 := do
  for (name, result) in TransitionOrigin.Cases.observations do
    IO.println s!"{name}\t{if result then "pass" else "FAIL"}"
  return if TransitionOrigin.Cases.observations.all Prod.snd then 0 else 1
