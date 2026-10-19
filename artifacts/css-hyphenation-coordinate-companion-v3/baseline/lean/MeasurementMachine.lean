import MeasurementSelection

namespace HyphenMeasurementMachine

open HyphenMeasurementClassification HyphenMeasurementSelection HyphenMeasurementRescanProgress

inductive Hyphens where
  | none | manual | auto
  deriving DecidableEq, Repr

structure Configuration (α : Type) where
  start : Nat
  requestedLength : Nat
  runLength : Nat
  width : α
  lineBreakBefore : Bool
  suppressAll : Bool
  suppressInitial : Bool
  canWordWrap : Bool
  canWhitespaceWrap : Bool
  breakSpaces : Bool
  trimming : Bool
  spacingEnabled : Bool
  hyphenBreaksEnabled : Bool
  hyphens : Hyphens
  ligatureStart : Nat
  ligatureEnd : Nat
  initialPriority : Priority
  incomingLast : Nat
  repairedCoordinates : Bool := false

def Configuration.finish (config : Configuration α) : Nat :=
  config.start+min config.requestedLength (config.runLength-config.start)

structure Providers (α μ : Type) where
  arithmetic : Arithmetic α
  glyphKind : Nat → Nat
  clusterStart : Nat → Bool
  isSpace : Nat → Bool
  isTab : Nat → Bool
  isNewline : Nat → Bool
  glyphAdvance : Nat → α
  partialAdvance : Nat → α
  spacing : Nat → Nat → List (α × α)
  hyphenation : Nat → Nat → List Kind
  allocation : Nat → Nat → Nat → Bool
  hyphenWidth : α
  measure : Nat → Nat → μ

structure Machine (α : Type) where
  cursor : Cursor
  selection : HyphenMeasurementSelection.State α
  classification : HyphenMeasurementClassification.State
  spacing : List (α × α)
  haveHyphenation : Bool
  allocations : Nat

def separators (providers : Providers α μ) (index : Nat) : Bool :=
  providers.isSpace index || providers.isTab index || providers.isNewline index

def initialMachine (config : Configuration α) (providers : Providers α μ) : Machine α := Id.run do
  let cursor := HyphenMeasurementRescanProgress.initial config.start config.finish
  let haveHyphenation := !config.suppressAll &&
    (config.hyphens == .auto || (config.hyphens == .manual && config.hyphenBreaksEnabled))
  let mut result : Machine α := ⟨cursor,HyphenMeasurementSelection.initial providers.arithmetic config.initialPriority,
    ⟨⟨config.start,false,false,false⟩,[]⟩,
    if config.spacingEnabled then providers.spacing cursor.bufferStart cursor.bufferEnd else [],haveHyphenation,0⟩
  if haveHyphenation then
    result := {result with allocations := 1}
    if providers.allocation 0 0 (cursor.bufferEnd-cursor.bufferStart) then
      result := {result with classification.buffer := providers.hyphenation cursor.bufferStart cursor.bufferEnd}
      if config.hyphens == .auto then
        result := {result with classification := range config.start cursor.bufferStart cursor.bufferEnd config.runLength (separators providers) result.classification}
    else result := {result with haveHyphenation := false}
  return result

structure Refilled (α : Type) where
  payload : Machine α
  rewind : Bool

def fetch (config : Configuration α) (providers : Providers α μ) (machine : Machine α) : Refilled α := Id.run do
  let first := machine.cursor.position
  let finish := min config.finish (first+100)
  let oldLength := machine.classification.buffer.length
  let mut result := machine
  let mut rewind := false
  if config.spacingEnabled then
    result := {result with spacing := providers.spacing first finish}
  if result.haveHyphenation then
    result := {result with allocations := result.allocations+1}
    if providers.allocation machine.allocations oldLength (finish-first) then
      result := {result with classification.buffer := result.classification.buffer ++ providers.hyphenation first finish}
      if config.hyphens == .auto then
        result := {result with classification := range config.start first finish config.runLength (separators providers) result.classification}
        rewind := if config.repairedCoordinates then machine.classification.word.boundary < config.start+oldLength
          else machine.classification.word.boundary < oldLength
    else result := {result with haveHyphenation := false}
  return ⟨result,rewind⟩

def refreshed (config : Configuration α) (machine : Machine α) (fetched : Refilled α) : Machine α :=
  {fetched.payload with cursor := refill config.finish machine.cursor machine.classification.word.boundary fetched.rewind}

def charAdvance (config : Configuration α) (providers : Providers α μ) (machine : Machine α) : α :=
  let index := machine.cursor.position
  if config.ligatureStart ≤ index ∧ index < config.ligatureEnd then
    let width := providers.glyphAdvance index
    if config.spacingEnabled then
      let spacing := machine.spacing[index-machine.cursor.bufferStart]?.getD
        (providers.arithmetic.zero,providers.arithmetic.zero)
      providers.arithmetic.add width (providers.arithmetic.add spacing.1 spacing.2)
    else width
  else providers.partialAdvance index

def consider (config : Configuration α) (providers : Providers α μ) (machine : Machine α) : Machine α :=
  let index := machine.cursor.position
  let input : BreakInputs := ⟨config.suppressAll,config.suppressInitial,config.lineBreakBefore,
    config.canWordWrap,config.canWhitespaceWrap,config.breakSpaces,machine.haveHyphenation,
    providers.glyphKind index,providers.clusterStart index,separators providers (index-1),
    machine.classification.buffer[index-config.start]?.getD .none⟩
  let op := opportunity config.start index machine.selection.priority input
  let measured := atBreak providers.arithmetic config.width providers.hyphenWidth index op machine.selection
  let selection := if measured.aborted || index < machine.cursor.rescanLimit then measured
    else accumulate providers.arithmetic (charAdvance config providers machine) config.trimming (providers.isSpace index) measured
  {machine with selection := selection}

def advanced (machine : Machine α) : Machine α :=
  {machine with cursor := advance machine.cursor}

theorem considered_cursor (config : Configuration α) (providers : Providers α μ) (machine : Machine α) :
    (consider config providers machine).cursor = machine.cursor := rfl

theorem advance_budget_nonstrict (finish : Nat) (cursor : Cursor) :
    budget finish (advance cursor) ≤ budget finish cursor := by
  dsimp [budget,advance]
  omega

def loop (config : Configuration α) (providers : Providers α μ) (machine : Machine α) : Machine α :=
  if _active : machine.cursor.position < config.finish then
    if _exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position then
      let fetched := fetch config providers machine
      let next := refreshed config machine fetched
      if fetched.rewind then loop config providers next
      else
        let measured := consider config providers next
        if measured.selection.aborted then measured else loop config providers (advanced measured)
    else
      let measured := consider config providers machine
      if measured.selection.aborted then measured else loop config providers (advanced measured)
  else machine
termination_by budget config.finish machine.cursor
decreasing_by
  · exact refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ _active _exhausted
  · exact Nat.lt_of_le_of_lt (advance_budget_nonstrict config.finish _)
      (refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ _active _exhausted)
  · exact advance_budget_decreases config.finish machine.cursor _active

def run (config : Configuration α) (providers : Providers α μ) : Result α μ :=
  let result := loop config providers (initialMachine config providers)
  finalize providers.arithmetic config.width config.start (config.finish-config.start) config.incomingLast providers.measure result.selection

theorem initial_cursor (config : Configuration α) (providers : Providers α μ) :
    (initialMachine config providers).cursor = HyphenMeasurementRescanProgress.initial config.start config.finish := by
  simp only [initialMachine,Id.run,Pure.pure]
  repeat first | rfl | split

theorem initial_selection (config : Configuration α) (providers : Providers α μ) :
    (initialMachine config providers).selection = HyphenMeasurementSelection.initial providers.arithmetic config.initialPriority := by
  simp only [initialMachine,Id.run,Pure.pure]
  repeat first | rfl | split

theorem fetch_selection (config : Configuration α) (providers : Providers α μ) (machine : Machine α) :
    (fetch config providers machine).payload.selection = machine.selection := by
  simp only [fetch,Id.run,Pure.pure]
  repeat first | rfl | split

theorem consider_selection (config : Configuration α) (providers : Providers α μ) (machine : Machine α) :
    (consider config providers machine).selection =
      iteration providers.arithmetic config.width providers.hyphenWidth (charAdvance config providers machine)
        machine.cursor.position machine.cursor.rescanLimit
        (opportunity config.start machine.cursor.position machine.selection.priority
          ⟨config.suppressAll,config.suppressInitial,config.lineBreakBefore,config.canWordWrap,
            config.canWhitespaceWrap,config.breakSpaces,machine.haveHyphenation,providers.glyphKind machine.cursor.position,
            providers.clusterStart machine.cursor.position,separators providers (machine.cursor.position-1),
            machine.classification.buffer[machine.cursor.position-config.start]?.getD .none⟩)
        config.trimming (providers.isSpace machine.cursor.position) machine.selection := rfl

theorem whole_machine_metric_request (config : Configuration α) (providers : Providers α μ) :
    (run config providers).metrics = providers.measure config.start (config.start+(run config providers).fit) :=
  final_metric_range providers.arithmetic config.width config.start (config.finish-config.start)
    config.incomingLast providers.measure _

theorem initial_boundary_bounds (config : Configuration α) (providers : Providers α μ) :
    config.start ≤ (initialMachine config providers).classification.word.boundary ∧
      (initialMachine config providers).classification.word.boundary ≤
        (initialMachine config providers).cursor.bufferEnd := by
  rw [initial_cursor]
  have finishBound : config.start ≤ config.finish := by simp [Configuration.finish]
  have bufferBound : config.start ≤ (HyphenMeasurementRescanProgress.initial config.start config.finish).bufferEnd := by
    dsimp [HyphenMeasurementRescanProgress.initial];omega
  have classified : ∀ buffer : List Kind,
      config.start ≤ (range config.start config.start
        (HyphenMeasurementRescanProgress.initial config.start config.finish).bufferEnd config.runLength
        (separators providers) ⟨⟨config.start,false,false,false⟩,buffer⟩).word.boundary ∧
      (range config.start config.start (HyphenMeasurementRescanProgress.initial config.start config.finish).bufferEnd
        config.runLength (separators providers) ⟨⟨config.start,false,false,false⟩,buffer⟩).word.boundary ≤
        (HyphenMeasurementRescanProgress.initial config.start config.finish).bufferEnd := by
    intro buffer
    apply complete_range_bounds
    · exact ⟨Nat.le_refl _,bufferBound⟩
    · exact Nat.le_refl _
  simp only [initialMachine,Id.run,Pure.pure]
  repeat first | exact classified _ | (solve | constructor <;> assumption) | split | (solve | simp_all)

theorem fetch_boundary_bounds (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (oldBounds : config.start ≤ machine.classification.word.boundary ∧
      machine.classification.word.boundary ≤ machine.cursor.position)
    (active : machine.cursor.position < config.finish) :
    config.start ≤ (fetch config providers machine).payload.classification.word.boundary ∧
      (fetch config providers machine).payload.classification.word.boundary ≤ min config.finish (machine.cursor.position+100) := by
  have low : config.start ≤ machine.cursor.position := by omega
  have high : machine.cursor.position ≤ min config.finish (machine.cursor.position+100) := by omega
  have preserved : config.start ≤ machine.classification.word.boundary ∧
      machine.classification.word.boundary ≤ min config.finish (machine.cursor.position+100) := by omega
  have classified : ∀ buffer : List Kind,
      config.start ≤ (range config.start machine.cursor.position (min config.finish (machine.cursor.position+100))
        config.runLength (separators providers) {machine.classification with buffer := buffer}).word.boundary ∧
      (range config.start machine.cursor.position (min config.finish (machine.cursor.position+100))
        config.runLength (separators providers) {machine.classification with buffer := buffer}).word.boundary ≤
          min config.finish (machine.cursor.position+100) := by
    intro buffer
    exact complete_range_bounds config.start machine.cursor.position _ config.runLength (separators providers)
      _ preserved low
  simp only [fetch,Id.run,Pure.pure]
  repeat first | exact preserved | exact classified _ | split

def LoopReady (config : Configuration α) (machine : Machine α) : Prop :=
  HyphenMeasurementRescanProgress.Ready config.start config.finish machine.cursor ∧
  (config.start ≤ machine.classification.word.boundary ∧ machine.classification.word.boundary ≤ machine.cursor.bufferEnd) ∧
  HyphenMeasurementSelection.Bounded config.start config.finish machine.selection

theorem initial_loop_ready (config : Configuration α) (providers : Providers α μ) :
    LoopReady config (initialMachine config providers) := by
  refine ⟨?_,initial_boundary_bounds config providers,?_⟩
  · rw [initial_cursor]
    exact initial_ready config.start config.finish (by simp [Configuration.finish])
  · rw [initial_selection]
    exact initial_bounded providers.arithmetic config.initialPriority _ _

theorem refreshed_loop_ready (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (ready : LoopReady config machine) (active : machine.cursor.position < config.finish)
    (exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position) :
    LoopReady config (refreshed config machine (fetch config providers machine)) := by
  have oldBounds : config.start ≤ machine.classification.word.boundary ∧
      machine.classification.word.boundary ≤ machine.cursor.position := by
    have old := ready.2.1;omega
  refine ⟨?_,?_,?_⟩
  · exact refill_ready config.start config.finish machine.classification.word.boundary machine.cursor _ ready.1 active oldBounds
  · exact fetch_boundary_bounds config providers machine oldBounds active
  · change Bounded _ _ (fetch config providers machine).payload.selection
    rw [fetch_selection]
    exact ready.2.2

theorem considered_loop_ready (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (ready : LoopReady config machine) (active : machine.cursor.position < config.finish) :
    LoopReady config (consider config providers machine) := by
  refine ⟨ready.1,ready.2.1,?_⟩
  rw [consider_selection]
  exact iteration_bounded providers.arithmetic config.width providers.hyphenWidth
    (charAdvance config providers machine) machine.cursor.position machine.cursor.rescanLimit
    config.start config.finish _ config.trimming (providers.isSpace machine.cursor.position) machine.selection
      ready.2.2 ⟨ready.1.1,active⟩

theorem advanced_loop_ready (config : Configuration α) (machine : Machine α)
    (ready : LoopReady config machine) (active : machine.cursor.position < config.finish) :
    LoopReady config (advanced machine) :=
  ⟨advance_ready config.start config.finish machine.cursor ready.1 active,ready.2⟩

theorem refreshed_active (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (ready : LoopReady config machine) (active : machine.cursor.position < config.finish)
    (exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position) :
    (refreshed config machine (fetch config providers machine)).cursor.position < config.finish := by
  have old := ready.2.1
  have bound := exhausted_refill_covers_position config.finish machine.classification.word.boundary
    machine.cursor (fetch config providers machine).rewind active (by omega)
  have newReady := refreshed_loop_ready config providers machine ready active exhausted
  have finishBound := newReady.1.2.2.2.2.1
  change (refreshed config machine (fetch config providers machine)).cursor.position <
    (refreshed config machine (fetch config providers machine)).cursor.bufferEnd at bound
  omega

theorem loop_ready (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (ready : LoopReady config machine) : LoopReady config (loop config providers machine) := by
  rw [loop]
  split
  next active =>
    split
    next exhausted =>
      dsimp only
      have nextReady := refreshed_loop_ready config providers machine ready active exhausted
      have nextActive := refreshed_active config providers machine ready active exhausted
      split
      · exact loop_ready config providers _ nextReady
      · have considered := considered_loop_ready config providers _ nextReady nextActive
        split
        · exact considered
        · exact loop_ready config providers _ (advanced_loop_ready config _ considered nextActive)
    next buffered =>
      dsimp only
      have considered := considered_loop_ready config providers machine ready active
      split
      · exact considered
      · exact loop_ready config providers _ (advanced_loop_ready config _ considered active)
  next finished => exact ready
termination_by budget config.finish machine.cursor
decreasing_by
  all_goals first
    | exact advance_budget_decreases config.finish machine.cursor (by assumption)
    | exact refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ (by assumption) (by assumption)
    | exact Nat.lt_of_le_of_lt (advance_budget_nonstrict config.finish _)
        (refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ (by assumption) (by assumption))

theorem whole_machine_fit_bound (config : Configuration α) (providers : Providers α μ) :
    (run config providers).fit ≤ min config.requestedLength (config.runLength-config.start) := by
  have admitted := loop_ready config providers _ (initial_loop_ready config providers)
  have fitted := final_fit_bounded providers.arithmetic config.width config.start
    (config.finish-config.start) config.incomingLast providers.measure
    (loop config providers (initialMachine config providers)).selection
  have sum : config.start+(config.finish-config.start) = config.finish := by
    simp [Configuration.finish]
  rw [sum] at fitted
  have result := fitted admitted.2.2
  simpa [run,Configuration.finish] using result

end HyphenMeasurementMachine
