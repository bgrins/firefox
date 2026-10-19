import Retention
namespace EndpointTaint

def eqNat (a b : Nat) := a == b
def endValue (bit : Bool) : Endpoint Nat := some (some ⟨7,bit⟩)
def prop (custom fromBit toBit : Bool) : Property Nat Nat Nat :=
  ⟨1,custom,[⟨0,endValue fromBit,endValue toBit⟩]⟩
def clean : List (Property Nat Nat Nat) := [prop true false false]
def fromTainted : List (Property Nat Nat Nat) := [prop true true false]
def toTainted : List (Property Nat Nat Nat) := [prop true false true]
def same := ordinarySame eqNat eqNat eqNat

theorem equal_payload_from_change : same clean fromTainted = true ∧
    changed (same clean fromTainted) clean fromTainted = true := by decide

theorem equal_payload_to_change : same clean toTainted = true ∧
    changed (same clean toTainted) clean toTainted = true := by decide

theorem both_reverse_directions :
    changed (same fromTainted clean) fromTainted clean = true ∧
    changed (same toTainted clean) toTainted clean = true := by decide

theorem noncustom_ignored :
    let a := [prop false false false]
    let b := [prop false true true]
    same a b = true ∧ changed (same a b) a b = false := by decide

theorem different_shape_uses_original_decision : same clean [] = false ∧
    changed (same clean []) clean [] = true := by decide

theorem changed_payload_uses_original_decision :
    let b : List (Property Nat Nat Nat) := [⟨1,true,[⟨0,some (some ⟨8,false⟩),endValue false⟩]⟩]
    same clean b = false ∧ changed (same clean b) clean b = true := by decide

theorem null_and_invalid_distinguished :
    tainted (none : Endpoint Nat) = false ∧ tainted (some none : Endpoint Nat) = false ∧
    endpointSame eqNat none (some none) = false := by decide

theorem both_endpoint_history :
    observation (run eqNat eqNat eqNat clean [fromTainted,toTainted,clean]) = observation clean ∧
    observation (run eqNat eqNat eqNat clean [fromTainted,toTainted]) = observation toTainted := by decide
end EndpointTaint
