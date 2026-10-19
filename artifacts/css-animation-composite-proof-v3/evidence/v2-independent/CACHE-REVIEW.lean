
namespace Composite
namespace IndependentV2

def staleRaw : RawState := ⟨[rproperty .add],staleCache⟩
def equalInput : Action := .success [rproperty .add]
def skip := nativeStep owner versionProviders staleRaw equalInput
theorem v2_admits_stale_equal_skip : Admitted owner staleRaw equalInput := by
  unfold Admitted equalInput
  intro equal
  unfold OffsetsFresh
  decide +kernel
theorem v2_skip_preserves_stale_caches : skip.state = staleCache := by decide +kernel
theorem v2_admitted_skip_not_current : ¬ CacheFresh versionProviders skip.state := by
  unfold CacheFresh
  decide +kernel
theorem v2_skip_honestly_pending : skip.state.pending = true := by decide +kernel

def sequence : List Action := [.success [rproperty .add],.invalidate 1 true true,.success [rproperty .add]]
theorem v2_sequence_admitted : AdmittedSequence owner versionProviders initial sequence := by
  simp only [sequence, AdmittedSequence, Admitted]
  decide +kernel
theorem v2_sequence_invariant : Invariant versionProviders (nativeRun owner versionProviders initial sequence).state :=
 finite_sequence_invariant owner versionProviders initial initial_cache_certificate sequence
theorem v2_sequence_refines : (nativeRun owner versionProviders initial sequence).state =
 referenceRun owner versionProviders initial.state sequence :=
 finite_sequence_refinement owner versionProviders initial (by rfl) sequence v2_sequence_admitted
theorem v2_sequence_still_not_current :
 ¬ CacheFresh versionProviders (nativeRun owner versionProviders initial sequence).state := by
 unfold CacheFresh
 decide +kernel

theorem geometry_cannot_smuggle_style (env : Environment) (geometry : GeometryInputs) :
 (geometryEnvironment env geometry).styleVersion = env.styleVersion ∧
 (geometryEnvironment env geometry).target = env.target ∧
 (geometryEnvironment env geometry).style = env.style := by exact ⟨rfl,rfl,rfl⟩

theorem delivered_equal_skip_current (owner : Ownership) (p : Providers) (s : RawState)
 (invariant : Invariant p s.state) (ready : s.state.pending = false)
 (input : List RawFrame) (equal : nativeEqual owner input s.raw = true) :
 Fresh p (optimizedSetter owner p s input).state := by
 rw [unchanged_skips_all_effects owner p s input equal]
 exact invariant.current ready

theorem v2_actual_style_delivery_restores : Fresh versionProviders restoredCache ∧ restoredCache.pending = false := by
 unfold Fresh OffsetsFresh CacheFresh
 decide +kernel

def missingTimeline := contextRefresh witnessProviders rangeState ⟨false,[]⟩
theorem v2_missing_dispatch_remains_pending : missingTimeline.pending = true ∧ ¬ OffsetsFresh missingTimeline := by
 unfold OffsetsFresh
 decide +kernel
theorem v2_style_alone_does_not_repair_offsets :
 (styleRefresh witnessProviders missingTimeline 0).pending = true ∧
 ¬ OffsetsFresh (styleRefresh witnessProviders missingTimeline 0) := by
 unfold OffsetsFresh
 decide +kernel
end IndependentV2
end Composite
