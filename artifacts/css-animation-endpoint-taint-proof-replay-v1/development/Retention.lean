import Shape
namespace EndpointTaint

theorem segment_metadata_iff (a b : Segment P C) :
    segmentMeta a b = true ↔ endpointBits a = endpointBits b := by
  simp [segmentMeta,endpointBits,Prod.ext_iff]

theorem segments_metadata_iff (as bs : List (Segment P C)) (shape : as.length = bs.length) :
    pairs segmentMeta as bs = true ↔ as.map endpointBits = bs.map endpointBits := by
  induction as generalizing bs with
  | nil => cases bs <;> simp_all [pairs]
  | cons a as ih =>
    cases bs with
    | nil => simp at shape
    | cons b bs =>
      have tail : as.length = bs.length := by simpa using shape
      simp only [pairs,Bool.and_eq_true,List.map_cons,List.cons.injEq]
      rw [segment_metadata_iff,ih bs tail]

theorem property_metadata_iff (a b : Property K P C) (kind : a.custom = b.custom)
    (shape : a.segments.length = b.segments.length) :
    propertyMeta a b = true ↔ propertyObservation a = propertyObservation b := by
  cases h : b.custom
  · simp [propertyMeta,propertyObservation,kind,h]
  · simp [propertyMeta,propertyObservation,kind,h,segments_metadata_iff a.segments b.segments shape]

theorem metadata_scan_iff (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (as bs : List (Property K P C))
    (h : ordinarySame key payload core as bs = true) :
    metadataScan as bs = true ↔ observation as = observation bs := by
  induction as generalizing bs with
  | nil => cases bs <;> simp_all [ordinarySame,pairs,metadataScan,observation]
  | cons a as ih =>
    cases bs with
    | nil => simp [ordinarySame,pairs] at h
    | cons b bs =>
      have pieces : propertySame key payload core a b = true ∧ ordinarySame key payload core as bs = true := by
        simpa only [ordinarySame,pairs,Bool.and_eq_true] using h
      have ready := property_ready key payload core a b pieces.1
      change (propertyMeta a b && metadataScan as bs) = true ↔
        propertyObservation a :: observation as = propertyObservation b :: observation bs
      simp only [Bool.and_eq_true,List.cons.injEq]
      rw [property_metadata_iff a b ready.1 ready.2.2,ih bs pieces.2]

theorem original_changes_preserved (as bs : List (Property K P C)) :
    changed false as bs = true := rfl

theorem new_change_exact (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (as bs : List (Property K P C)) :
    changed (ordinarySame key payload core as bs) as bs = true ↔
      ordinarySame key payload core as bs = false ∨ observation as ≠ observation bs := by
  cases h : ordinarySame key payload core as bs with
  | false => simp [changed]
  | true =>
    have eq := metadata_scan_iff key payload core as bs h
    simp only [changed,↓reduceIte,Bool.not_eq_true',Bool.true_eq_false,false_or]
    cases hm : metadataScan as bs <;> simp_all

theorem retained_metadata (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (as bs : List (Property K P C)) :
    observation (retain (ordinarySame key payload core as bs) as bs) = observation bs := by
  unfold retain
  split
  · rfl
  · have nochange : changed (ordinarySame key payload core as bs) as bs ≠ true := by assumption
    apply Classical.byContradiction
    intro mismatch
    exact nochange ((new_change_exact key payload core as bs).mpr (Or.inr mismatch))

def run (key : K → K → Bool) (payload : P → P → Bool) (core : C → C → Bool) :
    List (Property K P C) → List (List (Property K P C)) → List (Property K P C)
  | state, [] => state
  | state, next :: rest => run key payload core (retain (ordinarySame key payload core state next) state next) rest

def reference : List (Property K P C) → List (List (Property K P C)) → List (Property K P C)
  | state, [] => state
  | _, next :: rest => reference next rest

theorem history_metadata (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (history : List (List (Property K P C)))
    (initial other : List (Property K P C)) (same : observation initial = observation other) :
    observation (run key payload core initial history) = observation (reference other history) := by
  induction history generalizing initial other with
  | nil => exact same
  | cons next rest ih =>
    exact ih _ next (retained_metadata key payload core initial next)

theorem every_prefix_metadata (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (history : List (List (Property K P C)))
    (initial : List (Property K P C)) (n : Nat) :
    observation (run key payload core initial (history.take n)) = observation (reference initial (history.take n)) :=
  history_metadata key payload core _ initial initial rfl
theorem decision_delta_exact (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (as bs : List (Property K P C)) :
    changed (ordinarySame key payload core as bs) as bs ≠ !ordinarySame key payload core as bs ↔
      ordinarySame key payload core as bs = true ∧ observation as ≠ observation bs := by
  cases h : ordinarySame key payload core as bs with
  | false => simp [changed]
  | true =>
    have eq := metadata_scan_iff key payload core as bs h
    cases hm : metadataScan as bs <;> simp_all [changed]

end EndpointTaint
