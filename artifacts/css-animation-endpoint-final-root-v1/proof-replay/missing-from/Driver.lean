import Model
open EndpointTaint

def endpoint (bit : Bool) : Endpoint Nat := some (some ⟨7,bit⟩)
def property (custom fromBit toBit : Bool) : Property Nat Nat Nat :=
  ⟨1,custom,[⟨0,endpoint fromBit,endpoint toBit⟩]⟩
def main : IO Unit := do
  let eq := fun a b : Nat => a == b
  let same := ordinarySame eq eq eq
  let a := [property true false false]
  let fromArray := [property true true false]
  let toArray := [property true false true]
  let nc := [property false false false]
  let ncNew := [property false true true]
  let observations := [decide (observation (retain (same a fromArray) a fromArray) = observation fromArray),
    decide (observation (retain (same a toArray) a toArray) = observation toArray),
    decide (observation (retain (same fromArray a) fromArray a) = observation a),
    decide (observation (retain (same toArray a) toArray a) = observation a),
    decide (changed (same a []) a [] = true),
    decide (changed (same nc ncNew) nc ncNew = false),
    decide (endpointSame eq none (some none) = false),
    decide (changed (same a a) a a = false)]
  IO.println (String.intercalate "|" (observations.map toString))
