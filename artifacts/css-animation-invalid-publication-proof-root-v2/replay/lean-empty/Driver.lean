import PublicationModel
open InvalidPublication
def env (route : Bool) : Environment Nat (List Nat) (List Nat) :=
  ⟨fun _ => route, fun _ => some [20], id, id⟩
def state : State Nat (List Nat) := ⟨fun _ _ => some [20], fun _ => false, false⟩
def main : IO Unit := do
  let mut observations : List Bool := []
  for route in [false, true] do
    let e := env route
    let endpoint : Endpoint Nat (List Nat) := ⟨7, none⟩
    let declarations : List (Entry Nat (List Nat) (List Nat)) := [⟨7, .payload [], true, true⟩]
    let after := run e state (declarations ++ [⟨7, .payload [44], true, true⟩])
    observations := observations ++ [
      decide (selected e after 7 = none),
      decide (referenceObservation (selected e after 7) = .fallback),
      after.seen 7,
      decide (fromDeclaration e (convert e.encode endpoint) = some endpoint),
      decide (selected e (run e state (publication e.encode none)) 7 = some [20]),
      decide (selected e (step e state ⟨7, .initial, true, true⟩) 7 = some [20]),
      decide (selected e (step e state (convert e.encode ⟨7, some []⟩)) 7 = some []),
      decide (after.values (!route) 7 = some [20])]
  IO.println (String.intercalate "|" (observations.map toString))
