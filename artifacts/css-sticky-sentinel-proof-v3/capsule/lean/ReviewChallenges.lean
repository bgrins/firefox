import StickyLifecycle
open MaskedSticky StickyComposition StickyLifecycle
namespace Review
instance (x : Int) : Decidable (Representable x) := by unfold Representable; infer_instance
instance (x : Point) : Decidable (PointSafe x) := by unfold PointSafe; infer_instance
instance (x : Rect) : Decidable (RectSafe x) := by unfold RectSafe; infer_instance

def allAuto : Margin := ⟨autoCode, autoCode, autoCode, autoCode⟩
def stableNode : Node := { hadNormal := true, normal := ⟨7, 11⟩,   current := ⟨9, 13⟩, offsets := some allAuto }
def chainWorld : World := ⟨#[{stableNode with next := some 1},   {stableNode with first := 0, hadNormal := false, current := ⟨19, 23⟩}], #[], false⟩

theorem valid_chain_common_delta :
  let w := ((moveChain ⟨3, 5⟩ 3 (some 0)).run chainWorld).2
  w.nodes[0]!.current = ⟨10, 16⟩ ∧ w.nodes[1]!.current = ⟨22, 28⟩ ∧
  w.exhausted = false := by decide +kernel

theorem missing_property_still_observed :
  ((compute orderedPosition true 0 .current).run ⟨#[{}], #[], false⟩).2.trace =
    #["limits:0:current", "offset:0:0", "normal:0:0", "offset:0:0"] := by decide +kernel

def cyclic : Input := ⟨3, 0, false, [0], #[{stableNode with next := some 0}]⟩
theorem shared_refinement_allows_exhaustion :
  run orderedPosition true cyclic = run referencePosition true cyclic ∧
  (run orderedPosition true cyclic).2.exhausted = true := by
  constructor
  · exact complete_model_projection_refinement cyclic
  · decide +kernel

def hugeNode : Node := {stableNode with normal := ⟨-2147483648, 0⟩,   offsets := some ⟨autoCode, autoCode, autoCode, 0⟩,   ignoreLimits := ⟨⟨0,0,0,0⟩,⟨0,0,0,0⟩⟩}
def huge : Input := ⟨2,0,false,[0],#[hugeNode]⟩
theorem shared_refinement_allows_unsafe_subtraction :
  run orderedPosition true huge = run referencePosition true huge ∧
  (run orderedPosition true huge).1 = some ⟨2147483648,0⟩ ∧
  ¬ Representable 2147483648 := by
  constructor
  · exact complete_model_projection_refinement huge
  · decide +kernel

theorem all_rectangles_and_input_normal_safe :
  RectSafe hugeNode.ignoreLimits.stick ∧ RectSafe hugeNode.ignoreLimits.contain ∧
  PointSafe hugeNode.normal := by decide +kernel

theorem safe_delta_can_overflow_continuation :
  PointSafe (⟨2147483647,0⟩ : Point) ∧ PointSafe (⟨1,0⟩ : Point) ∧
  ¬ PointSafe (plus ⟨2147483647,0⟩ ⟨1,0⟩) := by decide +kernel

theorem explicit_auto_code_alias_breaks_semantics :
  native autoCode (some ⟨encodeInset (some autoCode),encodeInset none⟩) (-10)
    ⟨0,100,-100,100⟩ = -10 ∧
  reference (-10) (semanticBounds (some autoCode) none ⟨0,100,-100,100⟩) = 0 := by
  decide +kernel

theorem active_numeric_sentinel_must_clamp :
  native autoCode (some ⟨autoCode,0⟩) 700000000 sentinelLimits = 536870912 := by
  decide +kernel

def wrongContinuations (project : Projection) (i : Nat) : StateM World Unit := do
  let p ← compute project true i .current
  setPosition i p

theorem wrong_caller_still_substitutes (i : Nat) :
  wrongContinuations orderedPosition i = wrongContinuations referencePosition i := by
  rw [projection_refinement]

theorem wrong_caller_misses_continuation :
  let input : World := ⟨#[{stableNode with next := some 1,       offsets := some ⟨autoCode,autoCode,autoCode,0⟩,       currentLimits := ⟨⟨20,0,0,0⟩,⟨0,0,100,100⟩⟩},     {stableNode with first := 0}], #[], false⟩
  ((continuations orderedPosition true 0).run input).2.nodes[1]!.current = ⟨20,11⟩ ∧
  ((wrongContinuations orderedPosition 0).run input).2.nodes[1]!.current = ⟨9,13⟩ := by
  decide +kernel

end Review
