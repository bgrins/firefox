import BaseModel
open EndpointTaint BaseMetadata

def clean (n : Nat) : Endpoint Nat := some (some ⟨n, false⟩)
def dirty (n : Nat) : Endpoint Nat := some (some ⟨n, true⟩)
def old (v : Endpoint Nat) : Lookup Nat Nat := fun k => if k = 7 then v else none
def detector := changed (fun a b : Nat => a == b) (fun k : Nat => k == 7)
def sample (before after : Endpoint Nat) (force : Bool := false) : Endpoint Nat :=
  (tick (requestsRestyle false true (detector (old before) [(7, after)])) force
    after ⟨before, before⟩).sampled

def checks : List Bool := [
  detector (old (clean 0)) [(7, dirty 0)],
  detector (old (dirty 0)) [(7, clean 0)],
  tainted (sample (clean 0) (dirty 0)),
  !tainted (sample (dirty 0) (clean 0)),
  detector (old (clean 0)) [(7, clean 1)],
  !changed (fun a b : Nat => a == b) (fun _ => false) (old (clean 0)) [(7, dirty 0)],
  tainted (sample (clean 0) (dirty 0) true),
  !detector (old (dirty 0)) [],
  !detector (fun _ => none) [(7, none)],
  detector (fun _ => none) [(7, some none)]]

def main : IO Unit := IO.println (String.intercalate "|" (checks.map toString))
