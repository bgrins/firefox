import TaintValue
namespace EndpointTaint
open TaintShortcut
abbrev Endpoint (P : Type) := Option (Option (Value P))
def tainted : Endpoint P → Bool
  | some (some v) => v.attr
  | _ => false
structure Segment (P C : Type) where
  core : C
  fromValue : Endpoint P
  toValue : Endpoint P
structure Property (K P C : Type) where
  key : K
  custom : Bool
  segments : List (Segment P C)
def pairs (cmp : A → B → Bool) : List A → List B → Bool
  | [], [] => true
  | a :: as, b :: bs => cmp a b && pairs cmp as bs
  | _, _ => false
def endpointSame (cmp : P → P → Bool) : Endpoint P → Endpoint P → Bool
  | none, none => true
  | some a, some b => payloadSame cmp a b
  | _, _ => false
def segmentSame (payload : P → P → Bool) (core : C → C → Bool)
    (a b : Segment P C) : Bool :=
  core a.core b.core && endpointSame payload a.fromValue b.fromValue &&
    endpointSame payload a.toValue b.toValue
def propertySame (key : K → K → Bool) (payload : P → P → Bool) (core : C → C → Bool)
    (a b : Property K P C) : Bool :=
  key a.key b.key && (a.custom == b.custom) && pairs (segmentSame payload core) a.segments b.segments
def ordinarySame (key : K → K → Bool) (payload : P → P → Bool) (core : C → C → Bool) :=
  pairs (propertySame key payload core)
def endpointBits (s : Segment P C) : Bool × Bool := (tainted s.fromValue, tainted s.toValue)
def segmentMeta (a b : Segment P C) : Bool :=
  (tainted a.toValue == tainted b.toValue)
def propertyMeta (a b : Property K P C) : Bool :=
  if b.custom then pairs segmentMeta a.segments b.segments else true
def metadataScan (a b : List (Property K P C)) : Bool := pairs propertyMeta a b
def propertyObservation (p : Property K P C) : Option (List (Bool × Bool)) :=
  if p.custom then some (p.segments.map endpointBits) else none
def observation (ps : List (Property K P C)) := ps.map propertyObservation
def changed (ordinary : Bool) (a b : List (Property K P C)) : Bool :=
  if ordinary then !metadataScan a b else true
def retain (ordinary : Bool) (a b : List (Property K P C)) :=
  if changed ordinary a b then b else a
end EndpointTaint
