import Projection

namespace FlexWideProjection

def Envelope (free error delta : Int) : Prop :=
  min free 0 - error ≤ delta ∧ delta ≤ max free 0 + error

def Distribution (error : Int) : Int → List Item → Prop
  | _, [] => True
  | free, item :: rest =>
    Envelope free error item.delta ∧ Distribution error (free - item.delta) rest

theorem step_budget (free error delta : Int)
    (nonnegative : 0 ≤ error)
    (envelope : Envelope free error delta) :
    magnitude delta + magnitude (free - delta) ≤ magnitude free + 2 * error := by
  simp only [Envelope, magnitude] at *
  omega

theorem distribution_budget (error free : Int) (items : List Item)
    (nonnegative : 0 ≤ error)
    (distribution : Distribution error free items) :
    sum (fun i => magnitude i.delta) items + magnitude (free - sum Item.delta items) ≤
      magnitude free + 2 * (items.length : Int) * error := by
  induction items generalizing free with
  | nil => simp [sum]
  | cons item rest ih =>
    have step := step_budget free error item.delta nonnegative distribution.1
    have tail := ih (free - item.delta) distribution.2
    simp only [sum, List.length_cons, Int.natCast_add, Int.natCast_one,
      Int.mul_add, Int.add_mul, Int.mul_one, magnitude] at *
    omega

theorem native_sized_budget (free : Int) (items : List Item)
    (distribution : Distribution 1048576 free items)
    (available : magnitude free ≤ 576460752303423488)
    (count : items.length ≤ 134217727) :
    sum (fun i => magnitude i.delta) items ≤ 1152921504606846976 := by
  have budget := distribution_budget 1048576 free items (by decide) distribution
  simp only [magnitude] at *
  omega

theorem distribution_prefix_fits64 (free : Int) (items clamps : List Item)
    (distribution : Distribution 1048576 free items)
    (available : magnitude free ≤ 576460752303423488)
    (count : items.length ≤ 134217727)
    (clampCount : clamps.length ≤ 134217727)
    (valid : ∀ i ∈ items, Valid i) (clampValid : ∀ i ∈ clamps, Valid i) :
    -9223372036854775808 ≤ sum correction items + sum adjustment clamps ∧
    sum correction items + sum adjustment clamps ≤ 9223372036854775807 := by
  have budget := native_sized_budget free items distribution available count
  exact combined_prefix_fits64 items clamps valid clampValid (by omega) clampCount

theorem rounding_overshoot_is_admitted :
    Distribution 1 127 [⟨0, 128, 0, 100⟩] ∧
    127 - sum Item.delta [⟨0, 128, 0, 100⟩] = -1 := by
  simp only [Distribution, Envelope, sum]
  decide

end FlexWideProjection
