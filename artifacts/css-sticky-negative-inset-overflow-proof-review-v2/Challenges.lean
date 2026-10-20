import WideWitnesses

namespace IndependentNegative
open StickyNumeric StickyGeometry StickyWritingMode WideCallers StickyAbsolute

theorem near_end_real_order :
    WideNormalization.machineEndNear 100 200 20 10 = -110 ∧
    WideNormalization.machineEnd 100 200 20 10 = -120 ∧
    WideNormalization.machineEndNear 100 200 20 10 =
      WideNormalization.machineEnd 100 200 10 20 := by decide +kernel

theorem narrowed_result_need_not_be_coordinate :
    WideNormalization.Safe true ⟨some (coordMax-1), some 0⟩ 0 coordMax true ∧
    InMachine (WidenedInsets.nativeEnd 0 coordMax (coordMax-1) 0) ∧
    ¬ InCoordinate (WidenedInsets.nativeEnd 0 coordMax (coordMax-1) 0) := by
  unfold InCoordinate
  decide +kernel

theorem storage_size_is_not_provider_bound :
    InMachine 2147483647 ∧
    ¬ WideNormalization.Safe true ⟨some coordMax,some 0⟩ 0 2147483647 true := by decide +kernel

def crossAxis : Frame :=
  {WideWitnesses.wideFrame with axes := {WideWitnesses.wideFrame.axes with
    x := {WideWitnesses.wideFrame.axes.x with insets := ⟨some 0,none⟩},
    y := {WideWitnesses.wideFrame.axes.y with framePosition := machineMax, border := ⟨machineMin,600⟩}}}

theorem inactive_component_cannot_be_ignored :
    WideGeometry.Safe crossAxis.axes.x true true true ∧
    WideAxisRanges.entered crossAxis .x = true ∧
    ¬ WideAxisRanges.Safe crossAxis .x ∧ ¬ PositionSafe crossAxis false := by decide +kernel

def noHorizontal : Frame :=
  {crossAxis with axes := {crossAxis.axes with x := {crossAxis.axes.x with insets := ⟨none,none⟩}}}

theorem actual_early_return_avoids_other_core :
    ¬ CoreSafe noHorizontal true ∧ WideAxisRanges.Safe noHorizontal .x ∧
    WideAxisRanges.caller noHorizontal .x = ⟨none,none⟩ := by decide +kernel

theorem missing_offsets_skip_raw_geometry :
    CoreSafe {crossAxis with axes := {crossAxis.axes with hasOffsets := false}} false ∧
    WideAxisRanges.Safe {crossAxis with axes := {crossAxis.axes with hasOffsets := false}} .y := by decide +kernel

theorem direct_wide_edges_do_not_require_width :
    AbsoluteSafe WideWitnesses.wideFrame ∧
    ¬ InMachine ((selected WideWitnesses.wideFrame .y false).stickFar -
      (selected WideWitnesses.wideFrame .y false).stickNear) := by decide +kernel

theorem clamp_branch_reintroduces_width_obligation :
    CoreSafe WideWitnesses.clampFrame false ∧
    ¬ AbsoluteSafe WideWitnesses.clampFrame ∧
    WideGeometry.LegacyStorageSafe true true (-1073741823) 1073740223 := by decide +kernel

def containFrame : Frame :=
  {WideWitnesses.wideFrame with axes := {WideWitnesses.wideFrame.axes with
    y := {WideWitnesses.wideFrame.axes.y with containing := ⟨25,60000⟩, margin := ⟨11995,620⟩}}}

theorem actual_containment_record :
    CoreSafe containFrame false ∧
    machineContainRect containFrame = ⟨0,30,6000,59380⟩ ∧
    machineContainRect containFrame = containRect containFrame := by decide +kernel

theorem zero_width_does_not_mean_cross_reset :
    intersect ⟨3,2,8,6⟩ ⟨0,0,3,10⟩ = ⟨3,2,3,6⟩ ∧
    intersect ⟨4,2,8,6⟩ ⟨0,0,3,10⟩ = ⟨4,2,4,2⟩ := by decide +kernel

theorem checked_conversion_is_not_saturating_conversion :
    fromRect ⟨machineMax,7,1,8⟩ = zero ∧ RectInputs ⟨machineMax,7,1,8⟩ := by decide +kernel

def actualMachineTranslation (f : Frame) : Int × Int :=
  (signed32 (machinePosition f .x true - f.axes.x.normal),
   signed32 (machinePosition f .y true - f.axes.y.normal))

theorem full_machine_translation_join (f : Frame) (h : TranslationSafe f)
    (hx : 0 ≤ f.axes.x.border.size) (hy : 0 ≤ f.axes.y.border.size) :
    actualMachineTranslation f =
      (referencePosition f .x true-f.axes.x.normal,
       referencePosition f .y true-f.axes.y.normal) := by
  have bx := admitted_result_bound _ h.2.1
  have by_ := admitted_result_bound _ h.2.2
  simp only [translation,evaluate,WideCallers.position,position_expression,
    selected_refines f .x true hx,selected_refines f .y true hy] at bx by_
  unfold actualMachineTranslation
  rw [complete_position f .x true h.1 hx,complete_position f .y true h.1 hy]
  exact Prod.ext (signed32_exact _ bx) (signed32_exact _ by_)

end IndependentNegative
