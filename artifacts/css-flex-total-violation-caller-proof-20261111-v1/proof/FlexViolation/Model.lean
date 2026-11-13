import Std

namespace FlexViolation

def min32 : Int := -(2 ^ 31)
def max32 : Int := 2 ^ 31 - 1
def min64 : Int := -(2 ^ 63)
def max64 : Int := 2 ^ 63 - 1
def maxCount : Nat := 2 ^ 31 - 1

def Fits32 (value : Int) : Prop := min32 ≤ value ∧ value ≤ max32
def Fits64 (value : Int) : Prop := min64 ≤ value ∧ value ≤ max64

structure Item where
  identity : Nat
  before : Int
  minimum : Int
  maximum : Int
  deriving DecidableEq, Repr

def ValidItem (item : Item) : Prop :=
  Fits32 item.before ∧ 0 ≤ item.minimum ∧
  item.minimum ≤ item.maximum ∧ item.maximum ≤ max32

def Acquired (items : List Item) : Prop :=
  items.length ≤ maxCount ∧ ∀ item ∈ items, ValidItem item

def clamped (item : Item) : Int :=
  if item.before < item.minimum then item.minimum
  else if item.maximum < item.before then item.maximum
  else item.before

def adjustment (item : Item) : Int := clamped item - item.before
def total (items : List Item) : Int := (items.map adjustment).sum

def checkedFold (lower upper : Int) : Int → List Item → Option Int
  | acc, [] => some acc
  | acc, item :: rest =>
    let contribution := adjustment item
    let next := acc + contribution
    if lower ≤ contribution ∧ contribution ≤ upper ∧ lower ≤ next ∧ next ≤ upper then
      checkedFold lower upper next rest
    else none

def oldFold (items : List Item) : Option Int := checkedFold min32 max32 0 items
def wideFold (items : List Item) : Option Int := checkedFold min64 max64 0 items

inductive FreezeKind where
  | all | minimum | maximum
  deriving DecidableEq, Repr

def kind (value : Int) : FreezeKind :=
  if value = 0 then .all else if 0 < value then .minimum else .maximum

def selected (choice : FreezeKind) (item : Item) : Bool :=
  match choice with
  | .all => true
  | .minimum => item.before < item.minimum
  | .maximum => ¬ (item.before < item.minimum) ∧ item.maximum < item.before

def frozen (items : List Item) : List Item := items.filter (selected (kind (total items)))

def specSelected (value : Int) (item : Item) : Bool :=
  if value = 0 then true
  else if 0 < value then 0 < adjustment item
  else adjustment item < 0

def wrap32 (value : Int) : Int := (value - min32) % (2 ^ 32) + min32

def positiveWitness : List Item :=
  [{ identity := 0, before := 59999, minimum := 0, maximum := max32 },
   { identity := 1, before := 0, minimum := 600000000, maximum := 600000000 },
   { identity := 2, before := 0, minimum := 600000000, maximum := 600000000 },
   { identity := 3, before := 0, minimum := 600000000, maximum := 600000000 },
   { identity := 4, before := 0, minimum := 600000000, maximum := 600000000 }]

def subtractionWitness : List Item :=
  [{ identity := 0, before := max32, minimum := 0, maximum := 0 },
   { identity := 1, before := 1, minimum := 0, maximum := 0 },
   { identity := 2, before := min32, minimum := max32, maximum := max32 }]

end FlexViolation
