import FlexMBP.Model

namespace FlexMBP

def PrefixTarget : Prop :=
  ∀ (α : Type) (mbp : α → Int) items,
    Acquired mbp items → ∀ n ≤ items.length,
      min32 * (n : Int) ≤ sum mbp (items.take n) ∧
      sum mbp (items.take n) ≤ max32 * (n : Int) ∧
      Fits64 (sum mbp (items.take n))

def AccumulatorTarget : Prop :=
  ∀ (α : Type) (mbp : α → Int) items,
    Acquired mbp items →
      wideFold mbp items = some (sum mbp items) ∧
      accumulate mbp items = some (items, sum mbp items)

def OldCompatibilityTarget : Prop :=
  ∀ (α : Type) (mbp : α → Int) items total,
    Acquired mbp items → oldFold mbp items = some total →
      wideFold mbp items = some total

def FreeSpaceTarget : Prop :=
  ∀ (α : Type) (mbp usedMain : α → Int) inner gaps items,
    Acquired mbp items → DownstreamFits mbp usedMain inner gaps items →
      freeSpace mbp usedMain inner gaps items =
        some (inner - (sum mbp items + gaps) - sum usedMain items)

def BoundaryTarget : Prop :=
  FirstRejectedBoundary 60000 35791 ∧
  FirstRejectedBoundary 6000000 357 ∧
  FirstRejectedBoundary 600000000 3

def WitnessTarget : Prop :=
  wideFold id ([] : List Int) = some 0 ∧
  wideFold id ([2147483647, 2147483647] : List Int) = some 4294967294 ∧
  wideFold id ([-2147483648, -2147483648] : List Int) = some (-4294967296) ∧
  wideFold id ([2147483647, -2147483648, 1] : List Int) = some 0 ∧
  accumulate Prod.snd ([(1, -60000), (2, -60000)] : List (Nat × Int)) =
    some ([(1, -60000), (2, -60000)], -120000) ∧
  freeSpace id (fun _ => 60000) 60000 0 ([-60000, -60000] : List Int) =
    some 60000

def CompensatedCase (magnitude inner : Int) (count : Nat) : Prop :=
  let items := List.replicate count (-magnitude)
  Acquired id items ∧
  DownstreamFits id (fun _ => magnitude) inner 0 items ∧
  wideFold id items = some (-magnitude * (count : Int)) ∧
  freeSpace id (fun _ => magnitude) inner 0 items = some inner

def CompensatedFamilyTarget : Prop :=
  ∀ magnitude inner count,
    0 ≤ magnitude → Fits32 magnitude → 0 ≤ inner → Fits32 inner →
    count ≤ maxCount → CompensatedCase magnitude inner count

def BoundaryCoverageTarget : Prop :=
  CompensatedCase 60000 60000 35792 ∧
  CompensatedCase 6000000 60000 358 ∧
  CompensatedCase 600000000 60000 4

def JointWitnessTarget : Prop :=
  (Acquired id ([2147483647, -2147483648, 1] : List Int) ∧
    wideFold id ([2147483647, -2147483648, 1] : List Int) = some 0) ∧
  (Acquired id ([-2147483648, -2147483648] : List Int) ∧
    wideFold id ([-2147483648, -2147483648] : List Int) = some (-4294967296)) ∧
  CompensatedCase 60000 60000 2

def UniversalTarget : Prop :=
  PrefixTarget ∧ AccumulatorTarget ∧ OldCompatibilityTarget ∧
  FreeSpaceTarget ∧ BoundaryTarget ∧ WitnessTarget ∧
  CompensatedFamilyTarget ∧ BoundaryCoverageTarget ∧ JointWitnessTarget

end FlexMBP
