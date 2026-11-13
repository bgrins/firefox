import Std

namespace FlexMBP

def min32 : Int := -(2 ^ 31)
def max32 : Int := 2 ^ 31 - 1
def min64 : Int := -(2 ^ 63)
def max64 : Int := 2 ^ 63 - 1
def maxCount : Nat := 2 ^ 32 - 1

def Fits32 (n : Int) : Prop := min32 ≤ n ∧ n ≤ max32
def Fits64 (n : Int) : Prop := min64 ≤ n ∧ n ≤ max64

def sum {α : Type} (mbp : α → Int) (items : List α) : Int :=
  (items.map mbp).sum

def Acquired {α : Type} (mbp : α → Int) (items : List α) : Prop :=
  items.length ≤ maxCount ∧ ∀ item ∈ items, Fits32 (mbp item)

def checkedAdd (lower upper total contribution : Int) : Option Int :=
  let next := total + contribution
  if lower ≤ next ∧ next ≤ upper then some next else none

def fold {α : Type} (mbp : α → Int) (lower upper : Int) :
    Int → List α → Option Int
  | total, [] => some total
  | total, item :: items =>
    match checkedAdd lower upper total (mbp item) with
    | none => none
    | some next => fold mbp lower upper next items

def oldFold {α : Type} (mbp : α → Int) (items : List α) : Option Int :=
  fold mbp min32 max32 0 items

def wideFold {α : Type} (mbp : α → Int) (items : List α) : Option Int :=
  fold mbp min64 max64 0 items

def accumulate {α : Type} (mbp : α → Int) (items : List α) :
    Option (List α × Int) :=
  (wideFold mbp items).map (fun total => (items, total))

def checkedSub64 (left right : Int) : Option Int :=
  let next := left - right
  if min64 ≤ next ∧ next ≤ max64 then some next else none

def subtractUsed {α : Type} (usedMain : α → Int) : Int → List α → Option Int
  | available, [] => some available
  | available, item :: items =>
    match checkedSub64 available (usedMain item) with
    | none => none
    | some next => subtractUsed usedMain next items

def DownstreamFits {α : Type} (mbp usedMain : α → Int)
    (inner gaps : Int) (items : List α) : Prop :=
  Fits32 inner ∧ Fits32 gaps ∧
  (∀ item ∈ items, Fits32 (usedMain item)) ∧
  Fits64 (sum mbp items + gaps) ∧
  ∀ n ≤ items.length,
    Fits64 (inner - (sum mbp items + gaps) - sum usedMain (items.take n))

def freeSpace {α : Type} (mbp usedMain : α → Int)
    (inner gaps : Int) (items : List α) : Option Int := do
  let total ← wideFold mbp items
  let occupied ← checkedAdd min64 max64 total gaps
  let available ← checkedSub64 inner occupied
  subtractUsed usedMain available items

def FirstRejectedBoundary (magnitude : Int) (lastSafe : Nat) : Prop :=
  (∀ n ≤ lastSafe,
    oldFold id (List.replicate n (-magnitude)) = some (-magnitude * (n : Int))) ∧
  oldFold id (List.replicate (lastSafe + 1) (-magnitude)) = none

end FlexMBP
