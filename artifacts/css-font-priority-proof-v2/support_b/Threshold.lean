import Std

namespace Threshold

def scale : Int := 256
def pivot : Int := 2816
def limit : Int := 23040
def reverseBias : Int := 25600
def italicTag : Int := 25600
def defaultOblique : Int := 3584

structure Interval where
  lo : Int
  hi : Int
deriving Repr, DecidableEq

def ValidPositive (r : Interval) : Prop := 0 < r.lo ∧ r.lo ≤ r.hi ∧ r.hi ≤ limit

def ValidNegative (r : Interval) : Prop := -limit ≤ r.lo ∧ r.lo ≤ r.hi ∧ r.hi < 0

def reflect (r : Interval) : Interval := ⟨-r.hi, -r.lo⟩

def ascendingHit (start : Int) (r : Interval) : Option Int :=
  if r.hi < start then none else some (max start r.lo)

def descendingHit (start : Int) (r : Interval) : Option Int :=
  if start < r.lo then none else some (min start r.hi)

structure Visit where
  phase : Int
  distance : Int
deriving Repr, DecidableEq

def positiveVisit (t : Int) (r : Interval) : Visit :=
  if pivot ≤ t then
    match ascendingHit t r with
    | some angle => ⟨0, angle - t⟩
    | none => ⟨1, t - r.hi⟩
  else
    match descendingHit t r with
    | some angle => ⟨0, t - angle⟩
    | none => ⟨1, r.lo - t⟩

def visitLE (a b : Visit) : Prop :=
  a.phase < b.phase ∨ (a.phase = b.phase ∧ a.distance ≤ b.distance)

def encode (v : Visit) : Int := v.phase * reverseBias + v.distance

def nativeDistance (threshold lo hi target : Int) (italicFallback : Bool) : Int :=
  if target = lo ∨ target = hi then 0
  else if target = 0 then
    if lo = italicTag ∨ hi = italicTag then 179200
    else if lo ≥ 0 then lo
    else if hi ≥ 0 then 0 else 51200 - hi
  else if target = italicTag then
    let aim := if italicFallback then threshold else 0
    let bad := if italicFallback then 0 else 102400
    if lo ≥ aim then bad + lo - aim + 256
    else if hi ≥ aim then bad + 256
    else if hi > 0 then bad + 25600 + (aim - hi)
    else bad + 76800 + (aim - hi)
  else if lo = italicTag ∨ hi = italicTag then 179200
  else if target ≥ threshold then
    if lo ≥ target then lo - target
    else if hi ≥ target then 0
    else if hi > 0 then 25600 + (target - hi)
    else 76800 + (target - hi)
  else if target ≤ -threshold then
    if hi ≤ target then target - hi
    else if lo ≤ target then 0
    else if lo < 0 then 25600 + (lo - target)
    else 76800 + (lo - target)
  else if target ≥ 0 then
    if lo > target then 25600 + (lo - target)
    else if hi ≥ target then 0
    else if hi > 0 then target - hi
    else 76800 + (target - hi)
  else
    if hi < target then 25600 + (target - hi)
    else if lo ≤ target then 0
    else if lo < 0 then lo - target
    else 76800 + (lo - target)

theorem positive_visit_bounds (r : Interval) (t : Int)
    (hr : ValidPositive r) (ht : 0 < t ∧ t ≤ limit) :
    (positiveVisit t r).phase ∈ [0, 1] ∧
    0 ≤ (positiveVisit t r).distance ∧ (positiveVisit t r).distance < reverseBias := by
  rcases r with ⟨lo, hi⟩
  simp only [ValidPositive, limit] at hr ht
  simp only [positiveVisit, ascendingHit, descendingHit, pivot, reverseBias]
  split <;> split <;> simp only [List.mem_cons, List.mem_singleton]
  all_goals repeat first | omega | split | simp_all [Int.max_def, Int.min_def]

theorem encode_order (a b : Visit)
    (ha : a.phase ∈ [0, 1] ∧ 0 ≤ a.distance ∧ a.distance < reverseBias)
    (hb : b.phase ∈ [0, 1] ∧ 0 ≤ b.distance ∧ b.distance < reverseBias) :
    (encode a ≤ encode b) ↔ visitLE a b := by
  simp only [List.mem_cons, List.mem_singleton, reverseBias] at ha hb
  simp only [encode, visitLE, reverseBias]
  omega

theorem positive_agreement (r : Interval) (t : Int)
    (hr : ValidPositive r) (ht : 0 < t ∧ t ≤ limit) :
    nativeDistance pivot r.lo r.hi t true = encode (positiveVisit t r) := by
  rcases r with ⟨lo, hi⟩
  simp only [ValidPositive, limit] at hr ht
  simp only [nativeDistance, positiveVisit, ascendingHit, descendingHit,
    pivot, italicTag, encode, reverseBias, Int.max_def, Int.min_def]
  repeat first | omega | split | simp_all

theorem negative_reflection_valid (r : Interval) (hr : ValidNegative r) :
    ValidPositive (reflect r) := by
  simp only [ValidNegative, ValidPositive, reflect, limit] at *
  omega

theorem negative_agreement (r : Interval) (t : Int)
    (hr : ValidNegative r) (ht : -limit ≤ t ∧ t < 0) :
    nativeDistance pivot r.lo r.hi t true = encode (positiveVisit (-t) (reflect r)) := by
  rcases r with ⟨lo, hi⟩
  simp only [ValidNegative, limit] at hr ht
  simp only [nativeDistance, positiveVisit, ascendingHit, descendingHit,
    reflect, pivot, italicTag, encode, reverseBias, Int.max_def, Int.min_def]
  repeat first | omega | split | simp_all

theorem same_sign_symmetry (r : Interval) (t : Int)
    (hr : ValidPositive r) (ht : 0 < t ∧ t ≤ limit) :
    nativeDistance pivot (-r.hi) (-r.lo) (-t) true =
      nativeDistance pivot r.lo r.hi t true := by
  have hn : ValidNegative (reflect r) := by
    simp only [ValidPositive, ValidNegative, reflect, limit] at *
    omega
  have ht' : -limit ≤ -t ∧ -t < 0 := by omega
  rw [positive_agreement r t hr ht]
  simpa [reflect] using negative_agreement (reflect r) (-t) hn ht'

theorem positive_order_agreement (a b : Interval) (t : Int)
    (ha : ValidPositive a) (hb : ValidPositive b) (ht : 0 < t ∧ t ≤ limit) :
    (nativeDistance pivot a.lo a.hi t true ≤ nativeDistance pivot b.lo b.hi t true) ↔
      visitLE (positiveVisit t a) (positiveVisit t b) := by
  rw [positive_agreement a t ha ht, positive_agreement b t hb ht]
  exact encode_order _ _ (positive_visit_bounds a t ha ht) (positive_visit_bounds b t hb ht)

def selectedByVisit (faces : List Interval) (t : Int) (r : Interval) : Prop :=
  r ∈ faces ∧ ∀ s ∈ faces, visitLE (positiveVisit t r) (positiveVisit t s)

def selectedByNative (faces : List Interval) (t : Int) (r : Interval) : Prop :=
  r ∈ faces ∧ ∀ s ∈ faces,
    nativeDistance pivot r.lo r.hi t true ≤ nativeDistance pivot s.lo s.hi t true

theorem all_minimizers_agree (faces : List Interval) (t : Int) (r : Interval)
    (valid : ∀ s ∈ faces, ValidPositive s) (ht : 0 < t ∧ t ≤ limit) :
    selectedByNative faces t r ↔ selectedByVisit faces t r := by
  constructor
  · rintro ⟨member, best⟩
    exact ⟨member, fun s hs => (positive_order_agreement r s t (valid r member) (valid s hs) ht).mp (best s hs)⟩
  · rintro ⟨member, best⟩
    exact ⟨member, fun s hs => (positive_order_agreement r s t (valid r member) (valid s hs) ht).mpr (best s hs)⟩

def italicVisit (r : Interval) : Visit :=
  match ascendingHit pivot r with
  | some angle => ⟨0, angle - pivot⟩
  | none => ⟨1, pivot - r.hi⟩

def encodeItalic (v : Visit) : Int :=
  if v.phase = 0 then v.distance + 256 else reverseBias + v.distance

theorem italic_positive_agreement (r : Interval) (hr : ValidPositive r) :
    nativeDistance pivot r.lo r.hi italicTag true = encodeItalic (italicVisit r) := by
  rcases r with ⟨lo, hi⟩
  simp only [ValidPositive, limit] at hr
  simp only [nativeDistance, italicTag, pivot, italicVisit, ascendingHit,
    encodeItalic, reverseBias, Int.max_def]
  repeat first | omega | split | simp_all

theorem exact_italic_preferred (r : Interval) (hr : ValidPositive r) :
    nativeDistance pivot italicTag italicTag italicTag true <
      nativeDistance pivot r.lo r.hi italicTag true := by
  rcases r with ⟨lo, hi⟩
  simp only [ValidPositive, limit] at hr
  simp only [nativeDistance, italicTag, pivot]
  repeat first | omega | split | simp_all

theorem oblique_only_unchanged (lo hi : Int) :
    nativeDistance 2816 lo hi italicTag false = nativeDistance 3584 lo hi italicTag false := by
  simp [nativeDistance, italicTag]

theorem normal_unchanged (lo hi : Int) (fallback : Bool) :
    nativeDistance 2816 lo hi 0 fallback = nativeDistance 3584 lo hi 0 fallback := by
  simp [nativeDistance]

theorem threshold_partition (t : Int) :
    (pivot ≤ t ∨ t ≤ -pivot) ∨ (-pivot < t ∧ t < pivot) := by omega

theorem default_is_fourteen : defaultOblique = (14 : Int) * scale := by decide

theorem default_distinct_from_pivot : defaultOblique ≠ pivot := by decide

theorem positive_containment (r : Interval) (t : Int)
    (hr : ValidPositive r) (ht : 0 < t ∧ t ≤ limit)
    (inside : r.lo ≤ t ∧ t ≤ r.hi) :
    nativeDistance pivot r.lo r.hi t true = 0 := by
  rw [positive_agreement r t hr ht]
  simp only [positiveVisit, ascendingHit, descendingHit, encode, Int.max_def, Int.min_def]
  repeat first | omega | split | simp_all

theorem positive_endpoints (r : Interval) (hr : ValidPositive r) :
    nativeDistance pivot r.lo r.hi r.lo true = 0 ∧
    nativeDistance pivot r.lo r.hi r.hi true = 0 := by
  simp [nativeDistance]

theorem negative_order_agreement (a b : Interval) (t : Int)
    (ha : ValidNegative a) (hb : ValidNegative b) (ht : -limit ≤ t ∧ t < 0) :
    (nativeDistance pivot a.lo a.hi t true ≤ nativeDistance pivot b.lo b.hi t true) ↔
      visitLE (positiveVisit (-t) (reflect a)) (positiveVisit (-t) (reflect b)) := by
  rw [negative_agreement a t ha ht, negative_agreement b t hb ht]
  have ht' : 0 < -t ∧ -t ≤ limit := by omega
  exact encode_order _ _
    (positive_visit_bounds _ _ (negative_reflection_valid a ha) ht')
    (positive_visit_bounds _ _ (negative_reflection_valid b hb) ht')

theorem negative_minimizers_agree (faces : List Interval) (t : Int) (r : Interval)
    (valid : ∀ s ∈ faces, ValidNegative s) (ht : -limit ≤ t ∧ t < 0) :
    selectedByNative faces t r ↔
      (r ∈ faces ∧ ∀ s ∈ faces,
        visitLE (positiveVisit (-t) (reflect r)) (positiveVisit (-t) (reflect s))) := by
  constructor
  · rintro ⟨member, best⟩
    exact ⟨member, fun s hs => (negative_order_agreement r s t (valid r member) (valid s hs) ht).mp (best s hs)⟩
  · rintro ⟨member, best⟩
    exact ⟨member, fun s hs => (negative_order_agreement r s t (valid r member) (valid s hs) ht).mpr (best s hs)⟩

theorem italic_order_agreement (a b : Interval)
    (ha : ValidPositive a) (hb : ValidPositive b) :
    (nativeDistance pivot a.lo a.hi italicTag true ≤ nativeDistance pivot b.lo b.hi italicTag true) ↔
      visitLE (italicVisit a) (italicVisit b) := by
  rw [italic_positive_agreement a ha, italic_positive_agreement b hb]
  rcases a with ⟨al, ah⟩
  rcases b with ⟨bl, bh⟩
  simp only [ValidPositive, limit] at ha hb
  by_cases hA : ah < 2816 <;> by_cases hB : bh < 2816
  all_goals simp only [italicVisit, ascendingHit, pivot, hA, hB, ↓reduceIte, encodeItalic, visitLE, reverseBias, Int.max_def]
  all_goals repeat first | omega | split | simp_all

theorem italic_minimizers_agree (faces : List Interval) (r : Interval)
    (valid : ∀ s ∈ faces, ValidPositive s) :
    selectedByNative faces italicTag r ↔
      (r ∈ faces ∧ ∀ s ∈ faces, visitLE (italicVisit r) (italicVisit s)) := by
  constructor
  · rintro ⟨member, best⟩
    exact ⟨member, fun s hs => (italic_order_agreement r s (valid r member) (valid s hs)).mp (best s hs)⟩
  · rintro ⟨member, best⟩
    exact ⟨member, fun s hs => (italic_order_agreement r s (valid r member) (valid s hs)).mpr (best s hs)⟩

theorem inclusive_positive_pivot :
    visitLE (positiveVisit pivot ⟨3072,3072⟩) (positiveVisit pivot ⟨2560,2560⟩) := by
  simp [visitLE, positiveVisit, pivot, ascendingHit]

theorem inclusive_negative_pivot :
    nativeDistance pivot (-3072) (-3072) (-pivot) true <
      nativeDistance pivot (-2560) (-2560) (-pivot) true := by decide


theorem positive_native_bound (r : Interval) (t : Int)
    (hr : ValidPositive r) (ht : 0 < t ∧ t ≤ limit) :
    0 ≤ nativeDistance pivot r.lo r.hi t true ∧
      nativeDistance pivot r.lo r.hi t true < 51200 := by
  rw [positive_agreement r t hr ht]
  have bounds := positive_visit_bounds r t hr ht
  simp only [List.mem_cons, List.not_mem_nil, or_false, reverseBias] at bounds
  simp only [encode, reverseBias]
  omega

end Threshold
