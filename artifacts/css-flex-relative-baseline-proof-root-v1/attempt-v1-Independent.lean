import RelativeBaseline
namespace RelativeBaselineRoot
open FlexRelativeBaseline

theorem block_projection_suffices (last : Bool) (mode : Mode)
    (container : Point) (frame : Frame)
    (h : logicalB mode container frame.size (readNormal frame).point =
      logicalB mode container frame.size frame.expectedNormal) :
    correctedDistance last mode container frame =
      referenceDistance last mode container frame := by
  simp only [correctedDistance, referenceDistance, baselineDistance, h]

def endpoint : Frame := visualShift ⟨0, 20⟩ exampleFrame
def stale : Frame :=
  { exampleFrame with identity := 99, normalProperty := some ⟨0, 100⟩ }

theorem unselected_stale_property_does_not_leak :
    native false false .horizontal ⟨160, 80⟩ unset [endpoint, stale, endpoint] = 39 ∧
    native true false .horizontal ⟨160, 80⟩ unset [endpoint, stale, endpoint] = 41 ∧
    propertyReads false false unset [endpoint, stale, endpoint] = [(0, true)] ∧
    propertyReads true false unset [endpoint, stale, endpoint] = [(0, true)] := by
  decide +kernel

theorem established_ascent_ignores_stale_selected_property :
    native false false .horizontal ⟨160, 80⟩ 23 [stale] = 23 ∧
    native true false .horizontal ⟨160, 80⟩ 23 [stale] = 23 ∧
    propertyReads false false 23 [stale] = [] := by decide +kernel

theorem inline_only_property_error_does_not_change_horizontal_baseline :
    ¬ PropertyReady { exampleFrame with actual := ⟨90, 0⟩ } ∧
    correctedDistance false .horizontal ⟨160, 80⟩
      { exampleFrame with actual := ⟨90, 0⟩ } =
      referenceDistance false .horizontal ⟨160, 80⟩ exampleFrame := by
  unfold PropertyReady
  decide +kernel

theorem raw_order_reversal_changes_the_selected_endpoint :
    native false false .horizontal ⟨160, 80⟩ unset
      [endpoint, { endpoint with firstAscent := 17 }] = 39 ∧
    native false true .horizontal ⟨160, 80⟩ unset
      [endpoint, { endpoint with firstAscent := 17 }] = 17 := by decide +kernel

theorem vertical_rl_error_changes_sign_before_group_conversion :
    originalDistance false .verticalRL ⟨160, 80⟩
      (visualShift ⟨20, 0⟩ exampleFrame) = 139 ∧
    correctedDistance false .verticalRL ⟨160, 80⟩
      (visualShift ⟨20, 0⟩ exampleFrame) = 159 ∧
    originalDistance true .verticalRL ⟨160, 80⟩
      (visualShift ⟨20, 0⟩ exampleFrame) = 21 ∧
    correctedDistance true .verticalRL ⟨160, 80⟩
      (visualShift ⟨20, 0⟩ exampleFrame) = 1 := by decide +kernel

def sentinelFrame : Frame :=
  { exampleFrame with actual := ⟨0, 0⟩, expectedNormal := ⟨0, 0⟩,
    size := ⟨1073741823, 50⟩, firstAscent := 0 }

theorem ready_nonnegative_geometry_can_produce_unset :
    PropertyReady sentinelFrame ∧
    correctedDistance false .verticalRL ⟨0, 80⟩ sentinelFrame = unset := by
  unfold PropertyReady sentinelFrame exampleFrame
  decide +kernel

theorem stale_executed_property_still_needs_a_provider_contract :
    native false false .horizontal ⟨160, 80⟩ unset [stale] = 139 ∧
    reference false false .horizontal ⟨160, 80⟩ unset [stale] = 39 := by
  decide +kernel

#print axioms block_projection_suffices
#print axioms unselected_stale_property_does_not_leak
#print axioms established_ascent_ignores_stale_selected_property
#print axioms inline_only_property_error_does_not_change_horizontal_baseline
#print axioms raw_order_reversal_changes_the_selected_endpoint
#print axioms vertical_rl_error_changes_sign_before_group_conversion
#print axioms ready_nonnegative_geometry_can_produce_unset
#print axioms stale_executed_property_still_needs_a_provider_contract
end RelativeBaselineRoot
