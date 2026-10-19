import IdentityDispatch

namespace Emphasis.Ordinary
open Run Dispatch Selection Ligature

inductive Event where
  | provider (event : ProviderEvent)
  | draw (positionTwice : Int)
  deriving DecidableEq, Repr

structure Result where
  coordinate : Int
  draws : List Int
  events : List Event
  identities : List Nat
  deriving DecidableEq, Repr

def nativeShrunk (units : List Ligature.Unit) (range : Interval) : Interval :=
  if range.pastEnd ≤ range.first then range
  else
    let endBoundary := if range.pastEnd = units.length then true
      else ((units[range.pastEnd]?).map ligatureStart).getD false
    let answer := Shrinking.indexShrink range.first ((slice units range.first range.pastEnd).map ligatureStart) endBoundary
    ⟨answer.1,answer.2⟩

def referenceShrunk (units : List Ligature.Unit) (range : Interval) : Interval :=
  if range.pastEnd ≤ range.first then range
  else
    let endBoundary := if range.pastEnd = units.length then true
      else ((units[range.pastEnd]?).map ligatureStart).getD false
    let answer := directShrink range.first ((slice units range.first range.pastEnd).map ligatureStart) endBoundary
    ⟨answer.1,answer.2⟩

theorem shrink_dispatch_refinement (units : List Ligature.Unit) (range : Interval) :
    nativeShrunk units range = referenceShrunk units range := by
  simp [nativeShrunk,referenceShrunk,Shrinking.index_shrink_refinement,shrink_refinement]

def spacingArray (p : Provider) (range : Interval) : Bool × List ProviderEvent :=
  if !p.present || !p.spacingEnabled then (false,[])
  else if p.allocationFailure (range.pastEnd-range.first) then (false,[.allocationFailure])
  else if range.first = range.pastEnd then (false,[.allocation 0])
  else (p.spacingSuccess range.first range.pastEnd,[.allocation (range.pastEnd-range.first),
    .spacing range.first range.pastEnd (p.spacingSuccess range.first range.pastEnd)])

def rawFontInput (direction : Int) (haveSpacing : Bool) (units : List Ligature.Unit) : List RawUnit :=
  units.map fun u =>
    ⟨⟨u.glyph,if haveSpacing then direction*u.before else 0,
       direction*glyphAdvance u.glyph 0,if haveSpacing then direction*u.after else 0⟩,
      clusterStart u⟩

def nativeRun (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) (range : Interval) (coordinate : Int) : Result :=
  let shrunk := nativeShrunk units range
  let adjusted := shrunk != range
  let leading := if adjusted then nativePartial policy p units range.first shrunk.first else (0,[])
  let spacing := spacingArray p shrunk
  let raw := rawFontInput direction spacing.1 (slice units shrunk.first shrunk.pastEnd)
  let drawn := Identity.observedLoop mark (lookAhead raw) (coordinate+direction*leading.1) 0 true false shrunk.first
  let positions := drawn.2.map Prod.fst
  let trailing := if adjusted then nativePartial policy p units shrunk.pastEnd range.pastEnd else (0,[])
  ⟨drawn.1+direction*trailing.1,positions,
    (leading.2++spacing.2).map Event.provider ++ positions.map Event.draw ++
    trailing.2.map Event.provider,drawn.2.map Prod.snd⟩

def referenceRun (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) (range : Interval) (coordinate : Int) : Result :=
  let shrunk := referenceShrunk units range
  let adjusted := shrunk != range
  let leading := if adjusted then referencePartial policy p units range.first shrunk.first else (0,[])
  let spacing := spacingArray p shrunk
  let raw := rawFontInput direction spacing.1 (slice units shrunk.first shrunk.pastEnd)
  let actions := (partitionUnits raw).map Action.cluster
  let origin := coordinate+direction*leading.1
  let positions := directEvents mark origin actions
  let trailing := if adjusted then referencePartial policy p units shrunk.pastEnd range.pastEnd else (0,[])
  ⟨origin+(actions.map actionAdvance).sum+direction*trailing.1,positions,
    (leading.2++spacing.2).map Event.provider ++ positions.map Event.draw ++
    trailing.2.map Event.provider,
    directDraw ((partitionUnits raw).map fun group => group.map fun u => charMay u.glyph) shrunk.first⟩

theorem raw_run_refinement (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) (range : Interval) (coordinate : Int) :
    nativeRun policy p units direction mark range coordinate =
      referenceRun policy p units direction mark range coordinate := by
  simp only [nativeRun,referenceRun,shrink_dispatch_refinement,partial_refinement,Identity.raw_observed_coordinate,
    Identity.raw_observed_positions,Identity.raw_observed_identities,List.map_map]

def nativeRuns (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) : List Interval → Int → Result
  | [], coordinate => ⟨coordinate,[],[],[]⟩
  | range::rest, coordinate =>
    let first := nativeRun policy p units direction mark range coordinate
    let next := nativeRuns policy p units direction mark rest first.coordinate
    ⟨next.coordinate,first.draws++next.draws,first.events++next.events,first.identities++next.identities⟩

def referenceRuns (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) : List Interval → Int → Result
  | [], coordinate => ⟨coordinate,[],[],[]⟩
  | range::rest, coordinate =>
    let first := referenceRun policy p units direction mark range coordinate
    let next := referenceRuns policy p units direction mark rest first.coordinate
    ⟨next.coordinate,first.draws++next.draws,first.events++next.events,first.identities++next.identities⟩

theorem arbitrary_run_dispatch (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) (ranges : List Interval) (coordinate : Int) :
    nativeRuns policy p units direction mark ranges coordinate =
      referenceRuns policy p units direction mark ranges coordinate := by
  induction ranges generalizing coordinate with
  | nil => rfl
  | cons range rest ih => simp only [nativeRuns,referenceRuns,raw_run_refinement,ih]

def nativeOrdinary (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) (runs : List Interval) (request : Interval) (coordinate : Int) : Result :=
  nativeRuns policy p units direction mark (nativeSelection request runs (rawPredicate request runs)) coordinate

def referenceOrdinary (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) (runs : List Interval) (request : Interval) (coordinate : Int) : Result :=
  referenceRuns policy p units direction mark (directSelection request runs (rawPredicate request runs)) coordinate

theorem complete_raw_dispatch (policy : WidthPolicy) (p : Provider) (units : List Ligature.Unit)
    (direction mark : Int) (runs : List Interval) (request : Interval) (coordinate : Int)
    (ordered : OrderedRuns runs)
    (initial : runs = [] ∨ ∃ first, runs[0]? = some first ∧ first.first = 0) :
    nativeOrdinary policy p units direction mark runs request coordinate =
      referenceOrdinary policy p units direction mark runs request coordinate := by
  simp only [nativeOrdinary,referenceOrdinary,raw_selection_refinement request runs ordered initial,
    arbitrary_run_dispatch]

end Emphasis.Ordinary
