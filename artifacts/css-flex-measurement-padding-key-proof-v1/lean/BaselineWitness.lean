import Key
namespace MeasurementPadding

def input (padding : Int) : Input := ⟨⟨100,0⟩,0,1000,1000,⟨0,0,padding,0⟩⟩
def stalePeerPosition (measuredPadding targetAscent peerAscent : Int) : Int :=
  measuredPadding + targetAscent - peerAscent
def sharedBaseline (targetPadding targetAscent peerPosition peerAscent : Int) : Prop :=
  targetPadding + targetAscent = peerPosition + peerAscent

theorem reused_measured_position_aligned_iff_padding_unchanged
    (measured current targetAscent peerAscent : Int) :
    sharedBaseline current targetAscent
      (stalePeerPosition measured targetAscent peerAscent) peerAscent ↔ current = measured := by
  unfold sharedBaseline stalePeerPosition
  omega

theorem fresh_measurement_derives_shared_baseline (padding targetAscent peerAscent : Int) :
    sharedBaseline padding targetAscent (stalePeerPosition padding targetAscent peerAscent) peerAscent := by
  exact (reused_measured_position_aligned_iff_padding_unchanged padding padding targetAscent peerAscent).2 rfl

theorem original_accepts_changed_padding_history :
    oldAccepts (input 50) (input 40) = true ∧
    oldAccepts (input 40) (input 50) = true ∧
    accepts (input 50) (input 40) = false ∧ accepts (input 40) (input 50) = false := by decide +kernel

theorem earlier_baseline_observer_survives_final_geometry_update :
    ¬sharedBaseline 40 15 (stalePeerPosition 50 15 15) 15 ∧
    40 + 15 - (stalePeerPosition 50 15 15 + 15) = -10 ∧
    50 + 15 - (stalePeerPosition 40 15 15 + 15) = 10 := by
  unfold sharedBaseline
  decide +kernel

def omitInlineStart (a b : Input) : Bool := oldAccepts a b &&
  decide (a.borderPadding.inlineEnd = b.borderPadding.inlineEnd ∧
    a.borderPadding.blockStart = b.borderPadding.blockStart ∧ a.borderPadding.blockEnd = b.borderPadding.blockEnd)
def omitInlineEnd (a b : Input) : Bool := oldAccepts a b &&
  decide (a.borderPadding.inlineStart = b.borderPadding.inlineStart ∧
    a.borderPadding.blockStart = b.borderPadding.blockStart ∧ a.borderPadding.blockEnd = b.borderPadding.blockEnd)
def omitBlockStart (a b : Input) : Bool := oldAccepts a b &&
  decide (a.borderPadding.inlineStart = b.borderPadding.inlineStart ∧
    a.borderPadding.inlineEnd = b.borderPadding.inlineEnd ∧ a.borderPadding.blockEnd = b.borderPadding.blockEnd)
def omitBlockEnd (a b : Input) : Bool := oldAccepts a b &&
  decide (a.borderPadding.inlineStart = b.borderPadding.inlineStart ∧
    a.borderPadding.inlineEnd = b.borderPadding.inlineEnd ∧ a.borderPadding.blockStart = b.borderPadding.blockStart)

theorem each_component_omission_is_observably_weaker :
    let a := input 0
    let iStart := {a with borderPadding.inlineStart := 1}
    let iEnd := {a with borderPadding.inlineEnd := 1}
    let bStart := {a with borderPadding.blockStart := 1}
    let bEnd := {a with borderPadding.blockEnd := 1}
    omitInlineStart a iStart = true ∧ accepts a iStart = false ∧
    omitInlineEnd a iEnd = true ∧ accepts a iEnd = false ∧
    omitBlockStart a bStart = true ∧ accepts a bStart = false ∧
    omitBlockEnd a bEnd = true ∧ accepts a bEnd = false := by decide +kernel

theorem key_equality_alone_does_not_constrain_external_baseline_provider :
    accepts (input 40) (input 40) = true ∧
      ¬sharedBaseline 40 16 (stalePeerPosition 40 15 15) 15 := by
  unfold sharedBaseline
  decide +kernel

end MeasurementPadding
