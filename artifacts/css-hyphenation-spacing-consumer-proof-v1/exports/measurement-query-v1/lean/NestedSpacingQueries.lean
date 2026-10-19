import MeasurementQueryTrace
import SpacingAssociation

namespace NestedSpacingQueries

structure Range where
  first : Nat
  finish : Nat
  deriving DecidableEq, Repr

def adjusted (enabled : Bool) (range : Range) : List Range :=
  if enabled && range.first < range.finish then [range] else []

def ligature (enabled : Bool) (part whole : Range) : List Range :=
  if part.first < part.finish && enabled then
    (if part.first == whole.first then [⟨part.first,part.first+1⟩] else []) ++
    (if part.finish == whole.finish then [⟨part.finish-1,part.finish⟩] else [])
  else []

def array (enabled allocated : Bool) (spacingRange : Range) : List Range :=
  if allocated then adjusted enabled spacingRange else []

def partialMetrics (enabled allocated : Bool) (part whole : Range) : List Range :=
  if part.first < part.finish then ligature enabled part whole ++ array enabled allocated part else []

structure GlyphRun where
  input : Range
  shrunk : Range
  adjusted : Bool
  leftWhole : Range
  rightWhole : Range
  leftAllocated : Bool
  middleAllocated : Bool
  rightAllocated : Bool
  deriving DecidableEq, Repr

def metricRun (enabled : Bool) (run : GlyphRun) : List Range :=
  (if run.adjusted then
    partialMetrics enabled run.leftAllocated ⟨run.input.first,run.shrunk.first⟩ run.leftWhole else []) ++
  array enabled run.middleAllocated run.shrunk ++
  (if run.adjusted then
    partialMetrics enabled run.rightAllocated ⟨run.shrunk.finish,run.input.finish⟩ run.rightWhole else [])

def metrics (enabled : Bool) (runs : List GlyphRun) : List Range := runs.flatMap (metricRun enabled)

def advance (enabled leftFirst allocated : Bool) (run : GlyphRun) : List Range :=
  let left := ligature enabled ⟨run.input.first,run.shrunk.first⟩ run.leftWhole
  let right := ligature enabled ⟨run.shrunk.finish,run.input.finish⟩ run.rightWhole
  (if run.adjusted then (if leftFirst then left ++ right else right ++ left) else []) ++
    array enabled allocated run.shrunk

structure Expansion where
  enabled : Bool
  whole : Range → Range
  finalRuns : Range → List GlyphRun

def expand (source : Expansion) : MeasurementQueryTrace.Event → List Range
  | .spacing first finish => [⟨first,finish⟩]
  | .ligature first finish => ligature source.enabled ⟨first,finish⟩ (source.whole ⟨first,finish⟩)
  | .measure first finish => metrics source.enabled (source.finalRuns ⟨first,finish⟩)

def complete (source : Expansion) (events : List MeasurementQueryTrace.Event) : List Range :=
  events.flatMap (expand source)

theorem empty_adjusted (enabled : Bool) (first : Nat) : adjusted enabled ⟨first,first⟩ = [] := by simp [adjusted]

theorem empty_ligature (enabled : Bool) (first : Nat) (whole : Range) :
    ligature enabled ⟨first,first⟩ whole = [] := by simp [ligature]

theorem failed_array_has_no_query (enabled : Bool) (range : Range) : array enabled false range = [] := rfl

theorem ligature_query_count (enabled : Bool) (part whole : Range) :
    (ligature enabled part whole).length ≤ 2 := by
  unfold ligature
  split
  · simp only [List.length_append]
    split <;> split <;> simp
  · simp

theorem singleton_ligature_keeps_duplicate (index : Nat) :
    ligature true ⟨index,index+1⟩ ⟨index,index+1⟩ = [⟨index,index+1⟩,⟨index,index+1⟩] := by
  simp [ligature]

theorem metric_runs_in_source_order (enabled : Bool) (left right : List GlyphRun) :
    metrics enabled (left ++ right) = metrics enabled left ++ metrics enabled right := by
  simp [metrics]

theorem expansion_in_source_order (source : Expansion) (left right : List MeasurementQueryTrace.Event) :
    complete source (left ++ right) = complete source left ++ complete source right := by simp [complete]

def execute (environment : SpacingAssociation.Environment Value)
    (input : Range → HyphenSpacingPhases.Input Value) (session : PropertySession.Session Value)
    (ranges : List Range) := SpacingAssociation.history environment session (ranges.map input)

theorem complete_history_associated (environment : SpacingAssociation.Environment Value)
    (input : Range → HyphenSpacingPhases.Input Value) (session : PropertySession.Session Value)
    (source : Expansion) (events : List MeasurementQueryTrace.Event)
    (ready : PropertySession.Associated session) :
    PropertySession.Associated (execute environment input session (complete source events)).1 :=
  SpacingAssociation.history_preserves_association _ _ _ ready

theorem exact_answer_multiplicity (environment : SpacingAssociation.Environment Value)
    (input : Range → HyphenSpacingPhases.Input Value) (session : PropertySession.Session Value)
    (ranges : List Range) : (execute environment input session ranges).2.length = ranges.length := by
  simpa [execute] using SpacingAssociation.history_answer_count environment session (ranges.map input)

end NestedSpacingQueries
