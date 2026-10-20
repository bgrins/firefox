import Lean
import StickyAdmission

open Lean StickyLifecycle StickyComposition StickyIndexed StickyMachineLifecycle StickyUpdate StickyJoined StickyAdmission

structure RawNode where
  first : Nat
  next : Int
  parent : Int
  hadNormal : Bool
  sticky : Bool
  hasContainer : Bool
  normal : Array Int
  current : Array Int
  fallback : Array Int
  offsets : Option (Array Int)
  recomputed : Option (Array Int)
  current_limits : Array (Array Int)
  ignore : Array (Array Int)
  deriving FromJson

structure RawInput where
  action : Nat
  target : Nat
  reflow : Bool
  primaries : List Nat
  frames : Array RawNode
  deriving FromJson

def decodePoint (a : Array Int) : Except String Point := do
  if a.size != 2 then throw "point size"
  return ⟨a[0]!, a[1]!⟩

def decodeRect (a : Array Int) : Except String Rect := do
  if a.size != 4 then throw "rect size"
  return ⟨a[0]!, a[1]!, a[2]!, a[3]!⟩

def decodeMargin (a : Option (Array Int)) : Except String (Option Margin) := do
  match a with
  | none => return none
  | some v =>
    if v.size != 4 then throw "margin size"
    return some ⟨v[0]!, v[1]!, v[2]!, v[3]!⟩

def decodeGeometry (a : Array (Array Int)) : Except String Geometry := do
  if a.size != 2 then throw "geometry size"
  return ⟨← decodeRect a[0]!, ← decodeRect a[1]!⟩

def decodeNode (root : Nat) (n : RawNode) : Except String Node := do
  if n.next < -1 || n.parent < -2 then throw "negative index"
  return {
    first := n.first
    next := if n.next < 0 then none else some n.next.toNat
    parent := if n.parent == -2 then some root
      else if n.parent < 0 then none else some n.parent.toNat
    hadNormal := n.hadNormal
    sticky := n.sticky
    hasContainer := n.hasContainer
    normal := ← decodePoint n.normal
    current := ← decodePoint n.current
    fallback := ← decodePoint n.fallback
    offsets := ← decodeMargin n.offsets
    recomputed := ← decodeMargin n.recomputed
    currentLimits := ← decodeGeometry n.current_limits
    ignoreLimits := ← decodeGeometry n.ignore
  }

def decodeInput (r : RawInput) : Except String Input := do
  if r.action > 6 then throw "action"
  return {
    action := r.action
    target := r.target
    reflow := r.reflow
    primaries := r.primaries
    nodes := ← r.frames.mapM (decodeNode r.frames.size)
  }

def pointJson (p : Point) : Json := toJson #[p.x, p.y]

def outputJson (result : Option Point × World) : Json :=
  Json.mkObj [
    ("value", result.1.map pointJson |>.getD Json.null),
    ("frames", Json.arr (result.2.nodes.map fun n => pointJson n.current)),
    ("trace", toJson result.2.trace)
  ]

def checked {α} (result : Except String α) : IO α :=
  match result with
  | .ok value => pure value
  | .error message => throw (IO.userError message)

def main : IO Unit := do
  let json ← checked (Json.parse (← (← IO.getStdin).readToEnd))
  let cases ← checked json.getArr?
  let stdout ← IO.getStdout
  for idx in [:cases.size] do
    let raw : RawInput ← checked (fromJson? cases[idx]!)
    let input ← checked (decodeInput raw)
    let machine := machineRun true input
    let mathematical := run orderedPosition true input
    let independent := independentObservation input
    let row := Json.mkObj [
      ("id", toJson idx), ("admitted", toJson (admitted input)),
      ("exhausted", toJson machine.2.exhausted),
      ("machine", outputJson machine),
      ("mathematical", outputJson mathematical),
      ("independent_value", independent.1.map pointJson |>.getD Json.null),
      ("independent_frames", Json.arr (independent.2.map fun n => pointJson n.current))]
    stdout.putStrLn row.compress
