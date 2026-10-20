import StickyChallenges
namespace IndependentReview
open StickyAxis StickyGeometry StickyNumeric StickyMachineGeometry

theorem nearest_projection (n sl sh cl ch x : Int)
    (hnl : cl ≤ n) (hnh : n ≤ ch)
    (hx : max sl cl ≤ x ∧ x ≤ min sh ch) :
    Int.natAbs (StickyPosition.native n sl sh cl ch - n) ≤ Int.natAbs (x-n) := by
  simp only [StickyPosition.native]
  omega

theorem negative_end_preserves_start :
    nativeNormalize ⟨some (-30),some (-10)⟩ 50 100 false = ⟨-40,-10⟩ := by decide +kernel

theorem inactive_oversized_does_not_fit :
    nativeNormalize ⟨none,none⟩ 0 100 true = ⟨0,0⟩ := by decide +kernel

theorem finite_sentinel_both_sides :
    StickyPosition.native (-700000000) sentinelLow sentinelHigh sentinelLow sentinelHigh = sentinelLow ∧
    StickyPosition.native 700000000 sentinelLow sentinelHigh sentinelLow sentinelHigh = sentinelHigh := by decide +kernel

def overwritten : Raw :=
  ⟨⟨0,0⟩,⟨0,0⟩,⟨0,100⟩,0,0,100,0,1700000000,0,⟨some 0,some 0⟩⟩

theorem overwritten_temporary_must_be_bounded :
    ¬ ArithmeticSafe (construct overwritten true false) ∧
    fieldsValue (construct overwritten true false) = ⟨-1700000000,-1699999900,0,100⟩ := by decide +kernel

theorem all_masks_machine_safe :
    ArithmeticSafe (construct (exampleRaw none none) false false) ∧
    ArithmeticSafe (construct (exampleRaw none (some 20)) false false) ∧
    ArithmeticSafe (construct (exampleRaw (some 20) none) true true) ∧
    ArithmeticSafe (construct (exampleRaw (some 20) (some 20)) true true) := by decide +kernel

theorem upright_vs_sideways :
    StickyWritingMode.referenceEnd .verticalLr true .upright .y = .bottom ∧
    StickyWritingMode.referenceEnd .sidewaysLr true .upright .y = .bottom ∧
    StickyWritingMode.referenceEnd .sidewaysLr false .upright .y = .top := by decide +kernel

theorem native_infeasible_priority :
    StickyPosition.native 12 30 10 0 40 = 10 ∧
    StickyPosition.native 100 0 200 0 10 = 100 := by decide +kernel

theorem negative_translation_continuations :
    (StickyContinuations.nativeDispatch (-10)
      [⟨1,40,some 20,⟨40,5⟩,⟨40,5⟩⟩,⟨2,60,none,⟨60,5⟩,⟨60,5⟩⟩]).1.map StickyContinuations.Frame.current = [-10,30] := by decide +kernel

theorem near_range_threshold :
    StickyRanges.earliest 10 0 20 10 30 = 10 ∧
    StickyRanges.latest 10 0 20 10 30 = 40 := by decide +kernel

theorem far_range_threshold :
    StickyRanges.earliest 0 0 20 10 30 = -20 ∧
    StickyRanges.latest 0 0 20 10 30 = 0 := by decide +kernel

theorem alias_excluded :
    decodeInset (encodeInset (some coordMax)) = none ∧
    ¬ InsetAdmitted (some coordMax) := by
  simp [decodeInset,encodeInset,InsetAdmitted]

theorem endpoint_requires_additional_bound :
    StickyRanges.latest machineMax 0 0 0 1 = machineMax+1 ∧
    ¬ InMachine (StickyRanges.latest machineMax 0 0 0 1) := by
  unfold InMachine machineMin machineMax
  decide +kernel

end IndependentReview
