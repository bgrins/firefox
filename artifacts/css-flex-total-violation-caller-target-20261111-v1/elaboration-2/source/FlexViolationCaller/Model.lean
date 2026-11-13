import FlexViolation.Target

namespace FlexViolationCaller

structure Fields where
  identity : Nat
  base : Int
  minimum : Int
  maximum : Int
  growZero : Bool
  shrinkZero : Bool
  deriving DecidableEq, Repr

structure ItemState where
  fields : Fields
  current : Int
  frozen : Bool
  minFlag : Bool
  maxFlag : Bool
  deriving DecidableEq, Repr

def asItem (item : ItemState) : FlexViolation.Item :=
  ⟨item.fields.identity, item.current, item.fields.minimum, item.fields.maximum⟩

def FieldsValid (fields : Fields) : Prop :=
  FlexViolation.Fits32 fields.base ∧ 0 ≤ fields.minimum ∧
  fields.minimum ≤ fields.maximum ∧ fields.maximum ≤ FlexViolation.max32

structure Seed where
  fields : Fields
  retainedFrozen : Option (Int × Bool × Bool) := none
  deriving DecidableEq, Repr

def SeedValid (seed : Seed) : Prop :=
  FieldsValid seed.fields ∧ match seed.retainedFrozen with
  | none => True
  | some (size, minFlag, maxFlag) =>
    seed.fields.minimum ≤ size ∧ size ≤ seed.fields.maximum ∧
    ¬(minFlag = true ∧ maxFlag = true)

def SeedsValid (seeds : List Seed) : Prop :=
  seeds.length ≤ FlexViolation.maxCount ∧ ∀ seed ∈ seeds, SeedValid seed

def seedItem (seed : Seed) : ItemState :=
  match seed.retainedFrozen with
  | some (size, minFlag, maxFlag) => ⟨seed.fields, size, true, minFlag, maxFlag⟩
  | none =>
    ⟨seed.fields, FlexViolation.clamped
      ⟨seed.fields.identity, seed.fields.base, seed.fields.minimum, seed.fields.maximum⟩,
      false, false, false⟩

structure Line where
  items : List ItemState
  frozenCount : Nat
  deriving DecidableEq, Repr

def appendItem (line : Line) (item : ItemState) : Line :=
  ⟨line.items ++ [item], line.frozenCount + if item.frozen then 1 else 0⟩

def initialLine (seeds : List Seed) : Line :=
  seeds.foldl (fun line seed => appendItem line (seedItem seed)) ⟨[], 0⟩

def active (items : List ItemState) : List ItemState := items.filter (! ·.frozen)
def remaining (line : Line) : Nat := (active line.items).length
def countedFrozen (items : List ItemState) : Nat := (items.filter (·.frozen)).length

def CountAgrees (line : Line) : Prop := line.frozenCount = countedFrozen line.items
def Fresh (items : List ItemState) : Prop :=
  ∀ item ∈ items, item.frozen = false → item.minFlag = false ∧ item.maxFlag = false

def LineValid (line : Line) : Prop :=
  CountAgrees line ∧ Fresh line.items ∧
  ∀ item ∈ line.items, FieldsValid item.fields ∧
    item.fields.minimum ≤ item.current ∧ item.current ≤ item.fields.maximum ∧
    ¬(item.minFlag = true ∧ item.maxFlag = true)

def freeze (item : ItemState) : ItemState :=
  { item with frozen := true, minFlag := false, maxFlag := false }

def earlyItem (grow : Bool) (item : ItemState) : ItemState :=
  if item.frozen then item
  else if (if grow then item.fields.growZero else item.fields.shrinkZero) ||
      (if grow then decide (item.fields.base > item.current)
       else decide (item.fields.base < item.current)) then
    { freeze item with
      minFlag := decide (item.fields.base < item.current)
      maxFlag := decide (item.fields.base > item.current) }
  else item

structure Walk where
  items : List ItemState
  left : Nat
  newlyFrozen : Nat := 0
  violation : Int := 0
  fallback : Bool := false
  deriving DecidableEq, Repr

def earlyWalk (grow : Bool) : Nat → List ItemState → Walk
  | left, [] => ⟨[], left⟩
  | 0, items => ⟨items, 0⟩
  | left + 1, item :: rest =>
    if item.frozen then
      let tail := earlyWalk grow (left + 1) rest
      { tail with items := item :: tail.items }
    else
      let updated := earlyItem grow item
      let tail := earlyWalk grow left rest
      { tail with
        items := updated :: tail.items
        newlyFrozen := tail.newlyFrozen + (if updated.frozen then 1 else 0) }

def early (grow : Bool) (line : Line) : Line :=
  let result := earlyWalk grow (line.items.length - line.frozenCount) line.items
  ⟨result.items, line.frozenCount + result.newlyFrozen⟩

def resetBase (items : List ItemState) : List ItemState :=
  items.map fun item => if item.frozen then item else { item with current := item.fields.base }

def suppliedItems (items : List ItemState) (values : List Int) : List ItemState :=
  (items.zip values).map fun (item, value) =>
    if item.frozen then item else { item with current := value }

def ProviderValid (line : Line) (values : List Int) : Prop :=
  values.length = line.items.length ∧
  ∀ pair ∈ line.items.zip values, pair.1.frozen = false → FlexViolation.Fits32 pair.2

def prepare (line : Line) (values : List Int) : Option Line :=
  if values.length = line.items.length then
    some ⟨suppliedItems (resetBase line.items) values, line.frozenCount⟩
  else none

def clampItem (item : ItemState) : ItemState × Int :=
  if item.current < item.fields.minimum then
    ({ item with current := item.fields.minimum, minFlag := true }, item.fields.minimum - item.current)
  else if item.fields.maximum < item.current then
    ({ item with current := item.fields.maximum, maxFlag := true }, item.fields.maximum - item.current)
  else (item, 0)

def clampWalk : Nat → Int → List ItemState → Walk
  | left, acc, [] => ⟨[], left, 0, acc, false⟩
  | 0, acc, items => ⟨items, 0, 0, acc, false⟩
  | left + 1, acc, item :: rest =>
    if item.frozen then
      let tail := clampWalk (left + 1) acc rest
      { tail with items := item :: tail.items }
    else
      let (updated, delta) := clampItem item
      let tail := clampWalk left (acc + delta) rest
      { tail with items := updated :: tail.items }

def flagSelected (choice : FlexViolation.FreezeKind) (item : ItemState) : Bool :=
  match choice with
  | .all => true
  | .minimum => item.minFlag
  | .maximum => item.maxFlag

def freezeWalk (choice : FlexViolation.FreezeKind) (finalIteration : Bool) :
    Nat → List ItemState → Walk
  | left, [] => ⟨[], left⟩
  | 0, items => ⟨items, 0⟩
  | left + 1, item :: rest =>
    if item.frozen then
      let tail := freezeWalk choice finalIteration (left + 1) rest
      { tail with items := item :: tail.items }
    else
      let selected := flagSelected choice item
      let updated := if selected then
          { freeze item with
            minFlag := item.minFlag
            maxFlag := (!item.minFlag && item.maxFlag) }
        else if finalIteration then freeze item
        else { item with minFlag := false, maxFlag := false }
      let tail := freezeWalk choice finalIteration left rest
      { tail with
        items := updated :: tail.items
        newlyFrozen := tail.newlyFrozen + (if updated.frozen then 1 else 0)
        fallback := tail.fallback || (!selected && finalIteration) }

structure Pass where
  prepared : Line
  clamped : Walk
  helper : Walk
  after : Line
  deriving DecidableEq, Repr

def runPass (iteration : Nat) (line : Line) (values : List Int) : Option Pass := do
  let prepared ← prepare line values
  let left := line.items.length - line.frozenCount
  let clamped := clampWalk left 0 prepared.items
  let helper := freezeWalk (FlexViolation.kind clamped.violation)
    (iteration + 1 == line.items.length) left clamped.items
  return ⟨prepared, clamped, helper, ⟨helper.items, line.frozenCount + helper.newlyFrozen⟩⟩

structure LoopState where
  line : Line
  iteration : Nat
  finished : Bool
  deriving DecidableEq, Repr

def start (seeds : List Seed) (grow wantsInfo : Bool) : LoopState :=
  let line := early grow (initialLine seeds)
  ⟨line, 0, line.items.isEmpty || (line.frozenCount == line.items.length && !wantsInfo)⟩

def advance (state : LoopState) (pass : Pass) : LoopState :=
  let next := state.iteration + 1
  ⟨pass.after, next,
    pass.after.frozenCount == pass.after.items.length || decide (pass.after.items.length ≤ next)⟩

inductive History (seeds : List Seed) (grow wantsInfo : Bool) : LoopState → Prop
  | initial : History seeds grow wantsInfo (start seeds grow wantsInfo)
  | step {state : LoopState} {values : List Int} {pass : Pass} :
      History seeds grow wantsInfo state →
      state.finished = false → state.iteration < seeds.length →
      ProviderValid state.line values → runPass state.iteration state.line values = some pass →
      History seeds grow wantsInfo (advance state pass)

def Aligned (relation : ItemState → ItemState → Prop) : List ItemState → List ItemState → Prop
  | [], [] => True
  | a :: xs, b :: ys => relation a b ∧ Aligned relation xs ys
  | _, _ => False

def FrozenPreserved (before after : List ItemState) : Prop :=
  Aligned (fun a b => a.fields = b.fields ∧ (a.frozen = true → b = a)) before after

def ClampedFrom (before after : List ItemState) : Prop :=
  Aligned (fun a b => if a.frozen then b = a else
    b.fields = a.fields ∧ b.frozen = false ∧ b.current = FlexViolation.clamped (asItem a) ∧
    b.minFlag = decide (a.current < a.fields.minimum) ∧
    b.maxFlag = decide (a.fields.maximum < a.current)) before after

def newlySelected (before after : List ItemState) : List FlexViolation.Item :=
  ((before.zip after).filter fun (a,b) => !a.frozen && b.frozen).map (fun pair => asItem pair.1)

end FlexViolationCaller
