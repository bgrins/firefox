import WholeAutofill

namespace NameRepeatComputedCache
open SubgridCountTransport SubgridGuardedConsumer SubgridSequencePrefix SubgridWholeAutofill

inductive Entry (Count Group : Type) where
  | repeat (count : Count) (pattern : List Group)
  | ordinary (group : Group)
  | autoFill (pattern : List Group)

structure Specified (Count Group : Type) where
  entries : List (Entry Count Group)
  unusedCache : Nat

def computeEntry (evaluate : Count → Nat) : Entry Count Group → Piece Group
  | .repeat count pattern => .fixed (evaluate count) pattern
  | .ordinary group => .ordinary group
  | .autoFill pattern => .autoFill pattern

def computedEntries (evaluate : Count → Nat) (value : Specified Count Group) : List (Piece Group) :=
  value.entries.map (computeEntry evaluate)

def stored (cap : Nat) (pieces : List (Piece Group)) : Nat :=
  cache cap (weights (prepare 0 pieces))

def rebuild (cap : Nat) (evaluate : Count → Nat) (value : Specified Count Group) :=
  let pieces := computedEntries evaluate value
  (pieces, stored cap pieces)

def specifyEntry : Piece Group → Entry Nat Group
  | .fixed count pattern => .repeat count pattern
  | .ordinary group => .ordinary group
  | .autoFill pattern => .autoFill pattern

def specify (pieces : List (Piece Group)) : Specified Nat Group :=
  ⟨pieces.map specifyEntry, 0⟩

example (cap : Nat) (evaluate : Count → Nat) (value : Specified Count Group) :
    (rebuild cap evaluate value).2 =
      min cap (total (weights (prepare 0 (computedEntries evaluate value)))) := by
  simpa [rebuild, stored, cache] using
    cache_correct cap 0 (weights (prepare 0 (computedEntries evaluate value)))

example (nativeCap : Int) (signedMax cap : Nat) (evaluate : Count → Nat)
    (value : Specified Count Group) (capFits : nativeCap ≤ (signedMax : Int))
    (storageFits : signedMax ≤ cap) :
    (remaining nativeCap (rebuild cap evaluate value).2 : Int) =
      max 0 (nativeCap - (total (weights (prepare 0 (computedEntries evaluate value))) : Int)) := by
  exact (guarded_transport nativeCap signedMax cap capFits storageFits
    (weights (prepare 0 (computedEntries evaluate value)))).1

example (capacity signedMax cap : Nat) (evaluate : Count → Nat)
    (value : Specified Count Group) (capFits : capacity ≤ signedMax)
    (storageFits : signedMax ≤ cap) :
    observed capacity cap (rebuild cap evaluate value).1 =
      (expanded (prepare
        (capacity - total (weights (prepare 0 (computedEntries evaluate value))))
        (computedEntries evaluate value))).take capacity := by
  exact observed_prefix capacity signedMax cap _ capFits storageFits

example (cap : Nat) (evaluate : Count → Nat) (entries : List (Entry Count Group))
    (oldCache newCache : Nat) :
    rebuild cap evaluate ⟨entries, oldCache⟩ = rebuild cap evaluate ⟨entries, newCache⟩ := by
  rfl

example (cap : Nat) (pieces : List (Piece Group)) :
    rebuild cap id (specify pieces) = (pieces, stored cap pieces) := by
  have mapped : (pieces.map specifyEntry).map (computeEntry id) = pieces := by
    induction pieces with
    | nil => rfl
    | cons piece rest ih => cases piece <;> simp [specifyEntry, computeEntry, ih]
  simp [rebuild, computedEntries, specify, mapped]

def supplied : Specified Unit Nat :=
  ⟨[.ordinary 10, .repeat () [20], .autoFill [30], .ordinary 40], 0⟩

def rendered (count : Nat) : List Nat :=
  resolved 5 4294967295 0 (rebuild 4294967295 (fun _ => count) supplied).1

def withStaleCache (count oldStored : Nat) : List Nat :=
  finish 5 0 (boundedSequence 5
    (prepare (remaining 5 oldStored) (computedEntries (fun _ => count) supplied)))

example : [rendered 2, rendered 3, rendered 1, rendered 2] =
    [[10, 20, 20, 30, 40], [10, 20, 20, 20, 40],
     [10, 20, 30, 30, 40], [10, 20, 20, 30, 40]] := by decide +kernel

example : (rebuild 4294967295 (fun _ => 2) supplied).2 = 4 ∧
    (rebuild 4294967295 (fun _ => 3) supplied).2 = 5 ∧
    (rebuild 4294967295 (fun _ => 1) supplied).2 = 3 := by decide +kernel

example : withStaleCache 3 4 = [10, 20, 20, 20, 30] ∧
    rendered 3 = [10, 20, 20, 20, 40] := by decide +kernel

example : withStaleCache 2 0 = [10, 20, 20, 30, 30] ∧
    rendered 2 = [10, 20, 20, 30, 40] := by decide +kernel

example : withStaleCache 1 5 = [10, 20, 40, 0, 0] ∧
    rendered 1 = [10, 20, 30, 30, 40] := by decide +kernel

example : stored 4294967295 ([.ordinary (0 : Nat), .fixed 2 [0], .autoFill [0]] : List (Piece Nat)) = 3 := by decide +kernel

example : stored 4294967295 ([.fixed 2147483647 [1, 2, 3]] : List (Piece Nat)) = 4294967295 ∧
    stored 18446744073709551615 ([.fixed 2147483647 [1, 2, 3]] : List (Piece Nat)) = 6442450941 := by decide +kernel

example : resolved 5 4294967295 0
    (computedEntries id ⟨[.ordinary 10, .repeat 1 [20], .ordinary 40], 0⟩) =
    [10, 20, 40, 0, 0] := by decide +kernel

example : resolved 6 4294967295 0
    (computedEntries id ⟨[.ordinary 10, .repeat 1 [20], .autoFill [30, 31], .ordinary 40], 0⟩) =
    [10, 20, 30, 31, 40, 0] := by decide +kernel

end NameRepeatComputedCache
