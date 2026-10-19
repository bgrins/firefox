set_option maxRecDepth 100000
set_option maxHeartbeats 10000000

namespace Composite

def witnessEnvironment : Environment := ⟨true, true, true, true, false, [], 0⟩
def absentEnvironment : Environment := { witnessEnvironment with target := false, style := false }
def witnessProviders : Providers := {
  computedValues := fun _ frames => frames.map fun f => f.properties.map fun d => (d.property, d.value.map (fun n => (n : Rat)))
  base := fun _ segments => (segments.map Segment.property).eraseDups.filterMap fun property =>
    if segments.any (fun s => s.property = property && (s.fromValue.isNone || s.toValue.isNone || s.fromComposite != .replace || s.toComposite != .replace))
    then some (property, 10) else none
}
def rframe (operation : SpecOperation := .replace) : RawFrame :=
  ⟨some (.percent 0), none, operation, [], some 0⟩
def rproperty (operation : SpecOperation := .replace) : RawFrame :=
  { rframe operation with properties := [⟨0,some 20⟩] }
def initial (env : Environment := witnessEnvironment) : RawState :=
  ⟨[], {frames := [], derived := derive env [], properties := [], base := [], default := .replace, environment := env, events := [], running := [], cumulative := [], computeCalls := 0}⟩
def owner : Ownership := id

theorem admitted_empty : Valid (initial).state := rfl
theorem admitted_missing_singleton :
    (derive absentEnvironment [project owner { rframe with offset := none }]).offsets = [some 1] := by decide +kernel
theorem admitted_missing_three :
    (derive absentEnvironment (List.replicate 3 (project owner { rframe with offset := none }))).offsets = [some 0, some (1/2), some 1] := by decide +kernel
theorem admitted_percentage :
    (derive absentEnvironment [project owner { rframe with offset := some (.percent (1/4)) }]).offsets = [some (1/4)] := by decide +kernel
theorem admitted_unresolved :
    (derive absentEnvironment [project owner { rframe with offset := some (.range .cover (1/4)) }]).offsets = [none] := by decide +kernel
theorem admitted_range :
    (derive {witnessEnvironment with timeline := true, geometry := [(.cover,⟨0,1,1/4,3/4⟩)]}
      [project owner { rframe with offset := some (.range .cover (1/2)) }]).offsets = [some (1/2)] := by decide +kernel

def omitComposite (a b : RawFrame) : Bool := rawFrameEqual owner {a with composite := .replace} {b with composite := .replace}
def omitOffset (a b : RawFrame) : Bool := rawFrameEqual owner {a with offset := none} {b with offset := none}
def omitEasing (a b : RawFrame) : Bool := rawFrameEqual owner {a with easing := none} {b with easing := none}
def omitProperties (a b : RawFrame) : Bool := rawFrameEqual owner {a with properties := []} {b with properties := []}
def autoAsReplace (f : RawFrame) : RawFrame :=
  {f with composite := if f.composite = .auto then .replace else f.composite}

theorem mutant_omit_composite : omitComposite (rframe .replace) (rframe .add) ≠ rawFrameEqual owner (rframe .replace) (rframe .add) := by decide +kernel
theorem mutant_omit_offset : omitOffset rframe {rframe with offset := none} ≠ rawFrameEqual owner rframe {rframe with offset := none} := by decide +kernel
theorem mutant_omit_easing : omitEasing rframe {rframe with easing := some 1} ≠ rawFrameEqual owner rframe {rframe with easing := some 1} := by decide +kernel
theorem mutant_omit_properties : omitProperties rframe rproperty ≠ rawFrameEqual owner rframe rproperty := by decide +kernel
theorem mutant_first_only :
    rawFrameEqual owner rframe rframe ≠ nativeEqual owner [rframe,rframe] [rframe,rframe .add] := by decide +kernel
theorem mutant_last_only :
    rawFrameEqual owner rframe rframe ≠ nativeEqual owner [rframe,rframe] [rframe .add,rframe] := by decide +kernel
theorem mutant_ignore_length : true ≠ nativeEqual owner [] [rframe] := by decide +kernel
theorem mutant_auto_is_replace :
    rawFrameEqual owner (autoAsReplace (rframe .auto)) (autoAsReplace rframe) ≠ rawFrameEqual owner (rframe .auto) rframe := by decide +kernel

def changed : State := (optimizedSetter owner witnessProviders initial [rproperty .add]).state

theorem mutant_drop_store : (initial).state ≠ changed := by decide +kernel
theorem mutant_skip_recompute : { changed with derived := (initial).state.derived } ≠ changed := by decide +kernel
theorem mutant_notify_irrelevant :
    notification {witnessEnvironment with relevant := false} ≠ [.notify] := by decide +kernel
theorem mutant_suppress_notify : changed.events.filter (· != .notify) ≠ changed.events := by decide +kernel
theorem mutant_skip_update :
    (afterChanged witnessProviders {initial.state with environment := {witnessEnvironment with style := false}}
      [project owner (rproperty .add)]).events ≠ changed.events := by decide +kernel
theorem mutant_suppress_restyle : changed.events.filter (· != .restyle) ≠ changed.events := by decide +kernel
theorem mutant_suppress_effect_updated : changed.events.filter (· != .effectUpdated) ≠ changed.events := by decide +kernel

def baseChangedProviders : Providers := {witnessProviders with base := fun env segments => ((witnessProviders.base env segments).map (fun (property,value) => (property,value+1)))}

theorem mutant_suppress_base_restyle :
    (rebuild baseChangedProviders {changed with events := []}).events.filter (· != .restyle) ≠ (rebuild baseChangedProviders {changed with events := []}).events := by decide +kernel

def autoFrames := [project owner (rproperty .auto)]
theorem mutant_collapse_endpoint_auto :
    buildConsumer witnessProviders witnessEnvironment autoFrames (derive witnessEnvironment autoFrames) .replace ≠
    buildConsumer witnessProviders witnessEnvironment autoFrames (derive witnessEnvironment autoFrames) .add := by decide +kernel

def twoFrames := [project owner (rproperty .replace),project owner {rproperty .add with offset := some (.percent 1)}]
def twoSegments := buildConsumer witnessProviders witnessEnvironment twoFrames (derive witnessEnvironment twoFrames) .replace

theorem mutant_drop_endpoint_composite :
    twoSegments.map (fun s => {s with toComposite := .replace}) ≠ twoSegments := by decide +kernel

def autoState := (optimizedSetter owner witnessProviders initial [rproperty .auto]).state
theorem mutant_suppress_default_rebuild :
    {autoState with default := .add, events := autoState.events ++ notification witnessEnvironment} ≠
      defaultSetter witnessProviders autoState .add := by decide +kernel

def rangeEnvironment : Environment := {witnessEnvironment with timeline := true, geometry := [(.cover,⟨0,1,0,1⟩)]}
def rangeState := (optimizedSetter owner witnessProviders (initial rangeEnvironment)
  [{rproperty .add with offset := some (.range .cover (1/2))}]).state
def changedRangeEnvironment : Environment := {rangeEnvironment with geometry := [(.cover,⟨0,1,0,2⟩)]}
theorem mutant_suppress_range_rebuild :
    {rangeState with environment := changedRangeEnvironment, derived := derive changedRangeEnvironment rangeState.frames} ≠
      contextRefresh witnessProviders rangeState ⟨true,changedRangeEnvironment.geometry⟩ := by decide +kernel

theorem unchanged_derived_field_control :
    nativeEqual owner [rframe] [{rframe with ignoredComputed := some 999}] = true := by decide +kernel

theorem distinct_allocation_control :
    rawDeclarationEqual (fun _ => 20) ⟨0,some 1⟩ ⟨0,some 2⟩ = true := by decide +kernel


def versionProviders : Providers := {
  computedValues := fun version frames => frames.map fun f => f.properties.map fun d =>
    (d.property,d.value.map (fun n => (n : Rat) * (version + 1)))
  base := fun version segments => (witnessProviders.base version segments).map fun (property,value) => (property,value + version * 20)
}
def cacheStart := (optimizedSetter owner versionProviders initial [rproperty .add]).state
def staleCache := invalidateStyle cacheStart 1 true true
def restoredCache := styleRefresh versionProviders staleCache 1

theorem initial_cache_certificate : Invariant versionProviders initial.state := by
  constructor <;> simp [initial,propertiesAt,baseAt]

theorem current_cache_nonvacuous : cacheStart.pending = false ∧ CacheFresh versionProviders cacheStart := by
  unfold CacheFresh
  decide +kernel

theorem invalidation_really_stale : staleCache.pending = true ∧
    staleCache.properties ≠ consumerAt versionProviders (inputs staleCache) ∧
    staleCache.base ≠ versionProviders.base staleCache.environment.styleVersion staleCache.properties := by
  decide +kernel

theorem stale_cache_certificate : Invariant versionProviders staleCache :=
  invalidate_invariant versionProviders _
    (changed_invariant versionProviders initial.state initial_cache_certificate _) 1 true true

theorem equal_setter_preserves_pending_cache :
    (optimizedSetter owner versionProviders ⟨[rproperty .add],staleCache⟩ [rproperty .add]).state = staleCache := by
  decide +kernel

theorem delivered_update_restores : restoredCache.pending = false ∧
    CacheFresh versionProviders restoredCache ∧ restoredCache.properties ≠ staleCache.properties ∧
    restoredCache.base ≠ staleCache.base := by
  unfold CacheFresh
  decide +kernel

theorem absent_target_preserves_old_base :
    (styleRefresh versionProviders (invalidateStyle cacheStart 1 false false) 1).base = cacheStart.base ∧
    (styleRefresh versionProviders (invalidateStyle cacheStart 1 false false) 1).properties = [] := by decide +kernel

def nullFrames := [project owner {rframe .add with properties := [⟨0,none⟩]}]
def nullSegments := buildConsumer witnessProviders witnessEnvironment nullFrames (derive witnessEnvironment nullFrames) .replace

theorem existing_null_retained : ((nullSegments.head?).map Segment.fromValue) = some none ∧
    ((nullSegments.head?).map Segment.fromComposite) = some .add := by decide +kernel

theorem synthesized_missing_distinct : ((nullSegments.head?).map Segment.toValue) = some none ∧
    ((nullSegments.head?).map Segment.toComposite) = some .replace := by decide +kernel

theorem null_is_not_base_value : nullSegments ≠
    buildConsumer witnessProviders witnessEnvironment
      [project owner {rproperty .add with properties := [⟨0,some 10⟩]}]
      (derive witnessEnvironment nullFrames) .replace := by decide +kernel


def pendingDiagnostic : List Action := [.success [rproperty .add],.invalidate 1 true true,.success [rproperty .add]]

theorem pending_diagnostic_not_admitted :
    ¬ AdmittedSequence owner versionProviders initial pendingDiagnostic := by
  simp only [pendingDiagnostic,AdmittedSequence,Admitted]
  decide +kernel

theorem pending_diagnostic_history_preserved :
    Invariant versionProviders (nativeRun owner versionProviders initial pendingDiagnostic).state :=
  finite_sequence_invariant owner versionProviders initial initial_cache_certificate pendingDiagnostic

theorem pending_diagnostic_really_stale :
    ¬ CacheFresh versionProviders (nativeRun owner versionProviders initial pendingDiagnostic).state := by
  unfold CacheFresh
  decide +kernel

def readySequence : List Action := [.success [rproperty .add],.success [rproperty .add],.failure,
  .defaultValue .accumulate,.success [rproperty .add],.invalidate 1 true true,.style 1,
  .success [rproperty .add]]

theorem ready_sequence_admitted : AdmittedSequence owner versionProviders initial readySequence := by
  simp only [readySequence,AdmittedSequence,Admitted]
  decide +kernel

theorem ready_sequence_refines : (nativeRun owner versionProviders initial readySequence).state =
    referenceRun owner versionProviders initial.state readySequence :=
  finite_sequence_refinement owner versionProviders initial (by rfl) initial_cache_certificate readySequence ready_sequence_admitted

theorem ready_sequence_final_current : Fresh versionProviders (nativeRun owner versionProviders initial readySequence).state := by
  unfold Fresh OffsetsFresh CacheFresh
  decide +kernel

def absentDelivery : List Action := [.success [rproperty .add],.style 0,.success [rproperty .add],
  .invalidate 1 true true,.style 1,.success [rproperty .add]]

theorem absent_target_style_delivery_admitted :
    AdmittedSequence owner versionProviders (initial absentEnvironment) absentDelivery := by
  simp only [absentDelivery,AdmittedSequence,Admitted]
  decide +kernel

def rangeRaw := [{rproperty .add with offset := some (.range .cover (1/2))}]
def offsetStyleDelivery : List Action := [.success rangeRaw,.invalidate 1 true false,
  .context ⟨true,[(.cover,⟨0,1,0,2⟩)]⟩,.style 1,.success rangeRaw]

theorem offset_then_style_delivery_admitted :
    AdmittedSequence owner versionProviders (initial rangeEnvironment) offsetStyleDelivery := by
  simp only [offsetStyleDelivery,AdmittedSequence,Admitted]
  decide +kernel

theorem offset_only_waits_for_style :
    (nativeRun owner versionProviders (initial rangeEnvironment)
      [.success rangeRaw,.invalidate 1 true false,.context ⟨true,[(.cover,⟨0,1,0,2⟩)]⟩]).state.pending = true := by decide +kernel

def missingRange := contextRefresh versionProviders
  (optimizedSetter owner versionProviders (initial rangeEnvironment) rangeRaw).state ⟨false,[]⟩

theorem style_before_offsets_not_ready :
    (styleRefresh versionProviders missingRange 1).pending = true ∧
    ¬ Admitted owner ⟨rangeRaw,styleRefresh versionProviders missingRange 1⟩ (.success rangeRaw) := by
  unfold Admitted
  decide +kernel

theorem fresh_but_undelivered_not_admitted :
    CacheFresh witnessProviders (invalidateStyle changed 1 true true) ∧
    ¬ Admitted owner ⟨[rproperty .add],invalidateStyle changed 1 true true⟩ (.success [rproperty .add]) := by
  unfold CacheFresh Admitted
  decide +kernel

end Composite
