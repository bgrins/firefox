import Std

namespace FlexWideProjection

def min32 : Int := -2147483648
def max32 : Int := 2147483647
def clip (lo hi value : Int) : Int := max lo (min hi value)
def stored (value : Int) : Int := clip min32 max32 value
def magnitude (value : Int) : Int := max (-value) value

theorem clamp_commutes (lo hi raw : Int)
    (bounds : min32 ≤ lo ∧ lo ≤ hi ∧ hi ≤ max32) :
    clip lo hi (stored raw) = clip lo hi raw := by
  simp only [clip, stored, min32, max32] at *
  omega

theorem corrected_violation (lo hi raw : Int)
    (bounds : min32 ≤ lo ∧ lo ≤ hi ∧ hi ≤ max32) :
    (stored raw - raw) + (clip lo hi (stored raw) - stored raw) =
      clip lo hi raw - raw := by
  have := clamp_commutes lo hi raw bounds
  omega

theorem minimum_flag (lo raw : Int) (bound : min32 ≤ lo) :
    (raw < min32 ∨ stored raw < lo) ↔ raw < lo := by
  simp only [stored, clip, min32, max32] at *
  omega

theorem maximum_flag (hi raw : Int) (bound : hi ≤ max32) :
    (max32 < raw ∨ hi < stored raw) ↔ hi < raw := by
  simp only [stored, clip, min32, max32] at *
  omega

theorem exclusive_flags (lo hi raw : Int)
    (bounds : min32 ≤ lo ∧ lo ≤ hi ∧ hi ≤ max32) :
    ¬((raw < min32 ∨ stored raw < lo) ∧
      (max32 < raw ∨ hi < stored raw)) := by
  rw [minimum_flag lo raw bounds.1, maximum_flag hi raw bounds.2.2]
  omega

theorem correction_bound (base delta : Int)
    (bounds : min32 ≤ base ∧ base ≤ max32) :
    magnitude (stored (base + delta) - (base + delta)) ≤ magnitude delta := by
  simp only [magnitude, stored, clip, min32, max32] at *
  omega

structure Item where
  base : Int
  delta : Int
  minimum : Int
  maximum : Int

def Valid (item : Item) : Prop :=
  min32 ≤ item.base ∧ item.base ≤ max32 ∧ min32 ≤ item.minimum ∧
    item.minimum ≤ item.maximum ∧ item.maximum ≤ max32

def correction (item : Item) : Int :=
  stored (item.base + item.delta) - (item.base + item.delta)

def adjustment (item : Item) : Int :=
  clip item.minimum item.maximum (stored (item.base + item.delta)) -
    stored (item.base + item.delta)

def exactViolation (item : Item) : Int :=
  clip item.minimum item.maximum (item.base + item.delta) - (item.base + item.delta)

def sum (f : Item → Int) : List Item → Int
  | [] => 0
  | item :: rest => f item + sum f rest

theorem aggregate_identity (items : List Item) (valid : ∀ i ∈ items, Valid i) :
    sum correction items + sum adjustment items = sum exactViolation items := by
  induction items with
  | nil => rfl
  | cons item rest ih =>
    have bounds := valid item (by simp)
    have head := corrected_violation item.minimum item.maximum
      (item.base + item.delta) bounds.2.2
    have tail := ih (by intro i h; exact valid i (by simp [h]))
    simp only [sum, correction, adjustment, exactViolation] at *
    omega

theorem correction_budget (items : List Item) (valid : ∀ i ∈ items, Valid i) :
    magnitude (sum correction items) ≤ sum (fun i => magnitude i.delta) items := by
  induction items with
  | nil => decide
  | cons item rest ih =>
    have bounds := valid item (by simp)
    have head := correction_bound item.base item.delta ⟨bounds.1, bounds.2.1⟩
    have tail := ih (by intro i h; exact valid i (by simp [h]))
    simp only [sum, correction, magnitude] at *
    omega

theorem adjustment_budget (items : List Item) (valid : ∀ i ∈ items, Valid i) :
    magnitude (sum adjustment items) ≤ (items.length : Int) * 4294967295 := by
  induction items with
  | nil => decide
  | cons item rest ih =>
    have bounds := valid item (by simp)
    have tail := ih (by intro i h; exact valid i (by simp [h]))
    simp only [Valid, min32, max32] at bounds
    simp only [sum, adjustment, stored, clip, min32, max32, magnitude,
      List.length_cons, Int.natCast_add, Int.natCast_one] at *
    omega

theorem combined_prefix_fits64 (correctionPrefix clampPrefix : List Item)
    (cv : ∀ i ∈ correctionPrefix, Valid i)
    (av : ∀ i ∈ clampPrefix, Valid i)
    (budget : sum (fun i => magnitude i.delta) correctionPrefix ≤ 4611686018427387904)
    (count : clampPrefix.length ≤ 134217727) :
    -9223372036854775808 ≤ sum correction correctionPrefix + sum adjustment clampPrefix ∧
    sum correction correctionPrefix + sum adjustment clampPrefix ≤ 9223372036854775807 := by
  have hc := correction_budget correctionPrefix cv
  have ha := adjustment_budget clampPrefix av
  simp only [magnitude] at hc ha
  omega

theorem saturation_changes_sign :
    sum exactViolation [⟨0, -3100000000, 0, 0⟩, ⟨0, 1500000000, 0, 0⟩,
      ⟨0, 1500000000, 0, 0⟩] = 100000000 ∧
    sum adjustment [⟨0, -3100000000, 0, 0⟩, ⟨0, 1500000000, 0, 0⟩,
      ⟨0, 1500000000, 0, 0⟩] = -852516352 := by
  decide

end FlexWideProjection
