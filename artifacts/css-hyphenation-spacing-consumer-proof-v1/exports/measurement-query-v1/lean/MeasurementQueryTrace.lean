import MeasurementMachine

namespace MeasurementQueryTrace
open HyphenMeasurementMachine HyphenMeasurementSelection HyphenMeasurementRescanProgress

inductive Event where
  | spacing (first finish : Nat)
  | ligature (first finish : Nat)
  | measure (first finish : Nat)
  deriving DecidableEq, Repr

def adjusted (enabled : Bool) (first finish : Nat) : List Event :=
  if enabled && first < finish then [.spacing first finish] else []

def initialEvents (config : Configuration α) : List Event :=
  adjusted config.spacingEnabled config.start (min config.finish (config.start+100))

def fetchEvents (config : Configuration α) (machine : Machine α) : List Event :=
  adjusted config.spacingEnabled machine.cursor.position (min config.finish (machine.cursor.position+100))

def considerEvents (config : Configuration α) (providers : Providers α μ) (machine : Machine α) : List Event :=
  if (consider config providers machine).selection.aborted || machine.cursor.position < machine.cursor.rescanLimit then []
  else if config.ligatureStart ≤ machine.cursor.position ∧ machine.cursor.position < config.ligatureEnd then []
  else [.ligature machine.cursor.position (machine.cursor.position+1)]

def tracedLoop (config : Configuration α) (providers : Providers α μ) (machine : Machine α) : Machine α × List Event :=
  if _active : machine.cursor.position < config.finish then
    if _exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position then
      let fetched := fetch config providers machine
      let next := refreshed config machine fetched
      let preceding :=  fetchEvents config machine
      if fetched.rewind then
        let later := tracedLoop config providers next
        (later.1,preceding ++ later.2)
      else
        let measured := consider config providers next
        let events := preceding ++ considerEvents config providers next
        if measured.selection.aborted then (measured,events)
        else
          let later := tracedLoop config providers (advanced measured)
          (later.1,events ++ later.2)
    else
      let measured := consider config providers machine
      let events := considerEvents config providers machine
      if measured.selection.aborted then (measured,events)
      else
        let later := tracedLoop config providers (advanced measured)
        (later.1,events ++ later.2)
  else (machine,[])
termination_by budget config.finish machine.cursor
decreasing_by
  · exact refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ _active _exhausted
  · exact Nat.lt_of_le_of_lt (advance_budget_nonstrict config.finish _)
      (refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ _active _exhausted)
  · exact advance_budget_decreases config.finish machine.cursor _active

theorem trace_erases (config : Configuration α) (providers : Providers α μ) (machine : Machine α) :
    (tracedLoop config providers machine).1 = loop config providers machine := by
  rw [tracedLoop,loop]
  split
  next active =>
    split
    next exhausted =>
      dsimp only
      split
      · exact trace_erases config providers _
      · split
        · rfl
        · exact trace_erases config providers _
    next buffered =>
      dsimp only
      split
      · rfl
      · exact trace_erases config providers _
  next finished => rfl
termination_by budget config.finish machine.cursor
decreasing_by
  all_goals first
    | exact advance_budget_decreases config.finish machine.cursor (by assumption)
    | exact refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ (by assumption) (by assumption)
    | exact Nat.lt_of_le_of_lt (advance_budget_nonstrict config.finish _)
        (refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ (by assumption) (by assumption))

def run (config : Configuration α) (providers : Providers α μ) : Result α μ × List Event :=
  let result := tracedLoop config providers (initialMachine config providers)
  let answer := finalize providers.arithmetic config.width config.start (config.finish-config.start)
    config.incomingLast providers.measure result.1.selection
  (answer,initialEvents config ++ result.2 ++ [.measure config.start (config.start+answer.fit)])

theorem run_erases (config : Configuration α) (providers : Providers α μ) :
    (run config providers).1 = HyphenMeasurementMachine.run config providers := by
  simp only [run,HyphenMeasurementMachine.run,trace_erases]

theorem final_metric_call (config : Configuration α) (providers : Providers α μ) :
    (run config providers).2.getLast? = some (.measure config.start (config.start+(run config providers).1.fit)) := by
  simp [run]

theorem empty_adjusted (enabled : Bool) (first : Nat) : adjusted enabled first first = [] := by
  simp [adjusted]

theorem no_nested_call_after_abort (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (aborted : (consider config providers machine).selection.aborted = true) :
    considerEvents config providers machine = [] := by simp [considerEvents,aborted]

theorem no_nested_call_during_rescan (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (rewound : machine.cursor.position < machine.cursor.rescanLimit) :
    considerEvents config providers machine = [] := by simp [considerEvents,rewound]

def Bounded (start finish : Nat) : Event → Prop
  | .spacing first last | .ligature first last => start ≤ first ∧ first < last ∧ last ≤ finish
  | .measure first last => start ≤ first ∧ first ≤ last ∧ last ≤ finish

theorem initial_events_bounded (config : Configuration α) :
    ∀ event ∈ initialEvents config, Bounded config.start config.finish event := by
  intro event member
  unfold initialEvents adjusted at member
  split at member
  · simp only [List.mem_singleton] at member
    subst event
    dsimp [Bounded]
    simp_all <;> omega
  · simp at member

theorem fetch_events_bounded (config : Configuration α) (machine : Machine α)
    (low : config.start ≤ machine.cursor.position) :
    ∀ event ∈ fetchEvents config machine, Bounded config.start config.finish event := by
  intro event member
  unfold fetchEvents adjusted at member
  split at member
  · simp only [List.mem_singleton] at member
    subst event
    dsimp [Bounded]
    simp_all <;> omega
  · simp at member

theorem consider_events_bounded (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (low : config.start ≤ machine.cursor.position) (high : machine.cursor.position < config.finish) :
    ∀ event ∈ considerEvents config providers machine, Bounded config.start config.finish event := by
  intro event member
  unfold considerEvents at member
  split at member
  · simp at member
  · split at member
    · simp at member
    · simp only [List.mem_singleton] at member
      subst event
      dsimp [Bounded]
      omega

theorem traced_events_bounded (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (ready : LoopReady config machine) :
    ∀ event ∈ (tracedLoop config providers machine).2, Bounded config.start config.finish event := by
  rw [tracedLoop]
  split
  next active =>
    split
    next exhausted =>
      dsimp only
      have nextReady := refreshed_loop_ready config providers machine ready active exhausted
      have nextActive := refreshed_active config providers machine ready active exhausted
      have fetchedBound := fetch_events_bounded config machine ready.1.1
      split
      · intro event member
        simp only [List.mem_append] at member
        exact member.elim (fetchedBound event) (traced_events_bounded config providers _ nextReady event)
      · have measuredReady := considered_loop_ready config providers _ nextReady nextActive
        have consideredBound := consider_events_bounded config providers _ nextReady.1.1 nextActive
        split
        · intro event member
          simp only [List.mem_append] at member
          exact member.elim (fetchedBound event) (consideredBound event)
        · intro event member
          simp only [List.mem_append] at member
          rcases member with (h|h)|h
          · exact fetchedBound event h
          · exact consideredBound event h
          · exact traced_events_bounded config providers _ (advanced_loop_ready config _ measuredReady nextActive) event h
    next buffered =>
      dsimp only
      have measuredReady := considered_loop_ready config providers machine ready active
      have consideredBound := consider_events_bounded config providers machine ready.1.1 active
      split
      · exact consideredBound
      · intro event member
        simp only [List.mem_append] at member
        exact member.elim (consideredBound event)
          (traced_events_bounded config providers _ (advanced_loop_ready config _ measuredReady active) event)
  next finished => simp
termination_by budget config.finish machine.cursor
decreasing_by
  all_goals first
    | exact advance_budget_decreases config.finish machine.cursor (by assumption)
    | exact refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ (by assumption) (by assumption)
    | exact Nat.lt_of_le_of_lt (advance_budget_nonstrict config.finish _)
        (refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ (by assumption) (by assumption))

theorem complete_events_bounded (config : Configuration α) (providers : Providers α μ) :
    ∀ event ∈ (run config providers).2, Bounded config.start config.finish event := by
  intro event member
  have fitBound := whole_machine_fit_bound config providers
  have erased := run_erases config providers
  have finalBound : Bounded config.start config.finish
      (.measure config.start (config.start+(run config providers).1.fit)) := by
    dsimp [Bounded]
    rw [erased]
    unfold Configuration.finish
    omega
  change event ∈ initialEvents config ++
    (tracedLoop config providers (initialMachine config providers)).2 ++
    [.measure config.start (config.start+(run config providers).1.fit)] at member
  simp only [List.mem_append,List.mem_singleton] at member
  rcases member with (h|h)|h
  · exact initial_events_bounded config event h
  · exact traced_events_bounded config providers _ (initial_loop_ready config providers) event h
  · simpa [h] using finalBound

end MeasurementQueryTrace
