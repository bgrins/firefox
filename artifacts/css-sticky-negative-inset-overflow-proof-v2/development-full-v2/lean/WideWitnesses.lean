import WideProviders
namespace WideWitnesses
open StickyNumeric StickyGeometry WideCallers StickyAbsolute

def clampFrame : Frame :=
  ⟨⟨⟨⟨0,6000⟩,⟨0,6000⟩,⟨0,12000⟩,0,0,6000,0,0,0,⟨some 0,some 0⟩⟩,
      ⟨⟨12000,600⟩,⟨12000,600⟩,⟨0,60000⟩,12000,12000,6000,0,0,0,
       ⟨some (-1073741823),some (-1073734823)⟩⟩,
      true,.horizontal,false,.mixed⟩,true⟩

theorem original_clamp_path_rejected :
    CoreSafe clampFrame false ∧
    WideGeometry.LegacyStorageSafe true true (-1073741823) 1073740223 ∧
    Admitted (WideNormalization.oldEndExpression 6000 600 (-1073741823) (-1073734823)) ∧
    ¬ AbsoluteSafe clampFrame := by decide +kernel

theorem actual_clamp_inputs :
    stickBox (selected clampFrame .x false) (selected clampFrame .y false) = clampStick ∧
    containRect clampFrame = clampContain ∧
    Empty (intersect (edges clampStick (fromRect clampContain) 0 12000).2
      (edges clampStick (fromRect clampContain) 0 12000).1) := by decide +kernel

def wideFrame : Frame :=
  {clampFrame with axes := {clampFrame.axes with
    x := {clampFrame.axes.x with insets := ⟨none,none⟩},
    y := {clampFrame.axes.y with insets := ⟨some (-1073741823),some (-1073741823)⟩}}}

theorem repaired_full_callers_admitted :
    PositionSafe wideFrame false ∧ PositionSafe wideFrame true ∧ TranslationSafe wideFrame ∧
    AbsoluteSafe wideFrame ∧ WideAxisRanges.Safe wideFrame .x ∧ WideAxisRanges.Safe wideFrame .y ∧
    WideAxisRanges.DebugSafe wideFrame .x ∧ WideAxisRanges.DebugSafe wideFrame .y := by decide +kernel

theorem normalization_sign_mutant_witness :
    WidenedInsets.referenceEnd 100 200 20 10 = -120 ∧
    10 + (200 - (100 - 20 - 10)) ≠ WidenedInsets.referenceEnd 100 200 20 10 := by decide +kernel

theorem omitted_intersection_mutant_witness :
    rangeReference ⟨0,0,10,10⟩ ⟨20,0,100,100⟩ 0 50 ≠
      edges ⟨0,0,10,10⟩ (fromRect ⟨20,0,100,100⟩) 0 50 := by decide +kernel

theorem omitted_clamp_mutant_witness :
    finish ⟨5,2,8,6⟩ ⟨0,0,3,10⟩ ≠ intersect ⟨5,2,8,6⟩ ⟨0,0,3,10⟩ := by decide +kernel

theorem position_direction_mutant_witness :
    positionReference 100 ⟨120,500,0,600⟩ true false = 120 ∧
    min 100 (min 120 600) ≠ positionReference 100 ⟨120,500,0,600⟩ true false := by decide +kernel
end WideWitnesses
