import FlexMBP.FreeSpace

namespace FlexMBP

theorem compensated_acquired (magnitude : Int) (count : Nat)
    (hm : 0 ≤ magnitude) (hm32 : Fits32 magnitude) (hn : count ≤ maxCount) :
    Acquired id (List.replicate count (-magnitude)) := by
  refine ⟨by simpa using hn, ?_⟩
  intro item hi
  have he : item = -magnitude := (List.mem_replicate.mp hi).2
  subst item
  simp [Fits32, min32, max32] at *
  omega

theorem compensated_budget (magnitude inner : Int) (count : Nat)
    (hm : 0 ≤ magnitude) (hm32 : Fits32 magnitude)
    (hc : 0 ≤ inner) (hc32 : Fits32 inner) (hn : count ≤ maxCount) :
    0 ≤ inner + magnitude * (count : Int) ∧
      inner + magnitude * (count : Int) ≤ max64 := by
  have hnInt : (count : Int) ≤ 4294967295 := by
    simp [maxCount] at hn
    omega
  have hmInt : magnitude ≤ 2147483647 := by simpa [max32] using hm32.2
  have hcInt : inner ≤ 2147483647 := by simpa [max32] using hc32.2
  have prodCount := Int.mul_le_mul_of_nonneg_left hnInt hm
  have prodMagnitude := Int.mul_le_mul_of_nonneg_right hmInt (show (0 : Int) ≤ 4294967295 by decide)
  have prodNonneg := Int.mul_nonneg hm (Int.natCast_nonneg count)
  simp [max64]
  omega

theorem compensated_downstream (magnitude inner : Int) (count : Nat)
    (hm : 0 ≤ magnitude) (hm32 : Fits32 magnitude)
    (hc : 0 ≤ inner) (hc32 : Fits32 inner) (hn : count ≤ maxCount) :
    DownstreamFits id (fun _ => magnitude) inner 0 (List.replicate count (-magnitude)) := by
  have ha := compensated_acquired magnitude count hm hm32 hn
  have sumRange := prefix_range id (List.replicate count (-magnitude)) ha count (by simp)
  have budget := compensated_budget magnitude inner count hm hm32 hc hc32 hn
  refine ⟨hc32, by decide, fun _ _ => hm32, ?_, ?_⟩
  · simpa using sumRange
  · intro k hk
    have hkn : k ≤ count := by simpa using hk
    have hki : (k : Int) ≤ count := by omega
    have hmul := Int.mul_le_mul_of_nonneg_left hki hm
    have hnonneg := Int.mul_nonneg hm (Int.natCast_nonneg k)
    simp only [sum_replicate, Int.add_zero, sum_constant,
      List.length_take, List.length_replicate, Nat.min_eq_left hkn, Int.neg_mul]
    unfold Fits64
    constructor
    · have hl : min64 ≤ 0 := by decide
      omega
    · omega

theorem compensated_case (magnitude inner : Int) (count : Nat)
    (hm : 0 ≤ magnitude) (hm32 : Fits32 magnitude)
    (hc : 0 ≤ inner) (hc32 : Fits32 inner) (hn : count ≤ maxCount) :
    CompensatedCase magnitude inner count := by
  have ha := compensated_acquired magnitude count hm hm32 hn
  have hd := compensated_downstream magnitude inner count hm hm32 hc hc32 hn
  refine ⟨ha, hd, ?_, ?_⟩
  · simpa [sum_replicate] using wide_exact id (List.replicate count (-magnitude)) ha
  · simpa [sum_replicate, sum_constant, Int.neg_mul] using
      free_space_exact id (fun _ => magnitude) inner 0 (List.replicate count (-magnitude)) ha hd

theorem compensated_family_target : CompensatedFamilyTarget := by
  intro magnitude inner count hm hm32 hc hc32 hn
  exact compensated_case magnitude inner count hm hm32 hc hc32 hn

theorem boundary_coverage_target : BoundaryCoverageTarget := by
  refine ⟨?_, ?_, ?_⟩
  · apply compensated_case 60000 60000 35792 <;> decide
  · apply compensated_case 6000000 60000 358 <;> decide
  · apply compensated_case 600000000 60000 4 <;> decide

end FlexMBP
