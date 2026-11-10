import Lean

def main : IO Unit := do
  for text in ["0", "-0", "1", "1.0", "1e0", "1e1", "10e-1", "1.0e1", "-1", "true", "01"] do
    let value := (Lean.Json.parse text).bind Lean.Json.getNat?
    IO.println s!"{text}: {repr value}"
  for text in ["{\"schema\":0,\"schema\":1}", "{\"schema\":1,\"schema\":0}"] do
    let value := (Lean.Json.parse text).bind fun j => (j.getObjVal? "schema").bind Lean.Json.getNat?
    IO.println s!"{text}: {repr value}"
