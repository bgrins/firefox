import MeasurementMachine

namespace HyphenMeasurementBoundedStorage

open HyphenMeasurementClassification HyphenMeasurementSelection HyphenMeasurementRescanProgress HyphenMeasurementMachine

def ProviderLengths (limit : Nat) (providers : Providers α μ) : Prop :=
  ∀ first finish, first ≤ finish → finish ≤ limit →
    (providers.spacing first finish).length = finish-first ∧
    (providers.hyphenation first finish).length = finish-first

def Stored (config : Configuration α) (machine : Machine α) : Prop :=
  LoopReady config machine ∧ machine.cursor.position ≤ machine.cursor.bufferEnd ∧
    (machine.haveHyphenation = true → config.start+machine.classification.buffer.length = machine.cursor.bufferEnd) ∧
    (config.spacingEnabled = true → machine.spacing.length = machine.cursor.bufferEnd-machine.cursor.bufferStart)

theorem initial_hyphen_cover (config : Configuration α) (providers : Providers α μ) (lengths : ProviderLengths config.finish providers) :
    (initialMachine config providers).haveHyphenation = true →
      config.start+(initialMachine config providers).classification.buffer.length =
        (initialMachine config providers).cursor.bufferEnd := by
  have finishBound : config.start ≤ config.finish := by simp [Configuration.finish]
  have bufferBound : config.start ≤ min config.finish (config.start+100) := by omega
  have providerLength := (lengths config.start (min config.finish (config.start+100)) bufferBound (Nat.min_le_left _ _)).2
  cases option : config.hyphens <;> cases suppressed : config.suppressAll <;>
    cases manual : config.hyphenBreaksEnabled <;>
    by_cases allocated : providers.allocation 0 0 (min config.finish (config.start+100)-config.start) = true <;>
    simp_all [initialMachine,HyphenMeasurementRescanProgress.initial,complete_range_length,Id.run,Pure.pure] <;> omega

theorem initial_spacing_cover (config : Configuration α) (providers : Providers α μ) (lengths : ProviderLengths config.finish providers) :
    config.spacingEnabled = true → (initialMachine config providers).spacing.length =
      (initialMachine config providers).cursor.bufferEnd-(initialMachine config providers).cursor.bufferStart := by
  have finishBound : config.start ≤ config.finish := by simp [Configuration.finish]
  have bufferBound : config.start ≤ min config.finish (config.start+100) := by omega
  have providerLength := (lengths config.start (min config.finish (config.start+100)) bufferBound (Nat.min_le_left _ _)).1
  have projection : (initialMachine config providers).spacing =
      if config.spacingEnabled then providers.spacing config.start (min config.finish (config.start+100)) else [] := by
    cases option : config.hyphens <;> cases suppressed : config.suppressAll <;>
      cases manual : config.hyphenBreaksEnabled <;>
      by_cases allocated : providers.allocation 0 0 (min config.finish (config.start+100)-config.start) = true <;>
      simp_all [initialMachine,HyphenMeasurementRescanProgress.initial,Id.run,Pure.pure]
  rw [projection,initial_cursor]
  intro enabled
  simpa [enabled,HyphenMeasurementRescanProgress.initial] using providerLength

theorem initial_stored (config : Configuration α) (providers : Providers α μ) (lengths : ProviderLengths config.finish providers) :
    Stored config (initialMachine config providers) := by
  refine ⟨initial_loop_ready config providers,?_,initial_hyphen_cover config providers lengths,
    initial_spacing_cover config providers lengths⟩
  rw [initial_cursor]
  have bound : config.start ≤ config.finish := by simp [Configuration.finish]
  dsimp [HyphenMeasurementRescanProgress.initial]
  omega

theorem fetched_hyphen_cover (config : Configuration α) (providers : Providers α μ) (lengths : ProviderLengths config.finish providers)
    (machine : Machine α) (stored : Stored config machine)
    (active : machine.cursor.position < config.finish) (exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position) :
    (fetch config providers machine).payload.haveHyphenation = true →
      config.start+(fetch config providers machine).payload.classification.buffer.length =
        min config.finish (machine.cursor.position+100) := by
  have same : machine.cursor.bufferEnd = machine.cursor.position := by have h := stored.2.1;omega
  have oldCover := stored.2.2.1
  have bufferBound : machine.cursor.position ≤ min config.finish (machine.cursor.position+100) := by omega
  have newLength := (lengths machine.cursor.position (min config.finish (machine.cursor.position+100)) bufferBound (Nat.min_le_left _ _)).2
  cases spacing : config.spacingEnabled <;> cases hyphenEnabled : machine.haveHyphenation <;>
    cases option : config.hyphens <;>
    by_cases allocated : providers.allocation machine.allocations machine.classification.buffer.length
      (min config.finish (machine.cursor.position+100)-machine.cursor.position) = true <;>
    simp_all [fetch,Id.run,Pure.pure,complete_range_length] <;> omega

theorem fetched_spacing_cover (config : Configuration α) (providers : Providers α μ) (lengths : ProviderLengths config.finish providers)
    (machine : Machine α) (active : machine.cursor.position < config.finish) :
    config.spacingEnabled = true → (fetch config providers machine).payload.spacing.length =
      min config.finish (machine.cursor.position+100)-machine.cursor.position := by
  have bufferBound : machine.cursor.position ≤ min config.finish (machine.cursor.position+100) := by omega
  have newLength := (lengths machine.cursor.position (min config.finish (machine.cursor.position+100)) bufferBound (Nat.min_le_left _ _)).1
  cases spacing : config.spacingEnabled <;> cases hyphenEnabled : machine.haveHyphenation <;>
    cases option : config.hyphens <;>
    by_cases allocated : providers.allocation machine.allocations machine.classification.buffer.length
      (min config.finish (machine.cursor.position+100)-machine.cursor.position) = true <;>
    simp_all [fetch,Id.run,Pure.pure]

theorem refreshed_stored (config : Configuration α) (providers : Providers α μ) (lengths : ProviderLengths config.finish providers)
    (machine : Machine α) (stored : Stored config machine)
    (active : machine.cursor.position < config.finish) (exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position) :
    Stored config (refreshed config machine (fetch config providers machine)) := by
  refine ⟨refreshed_loop_ready config providers machine stored.1 active exhausted,?_,?_,?_⟩
  · have old := stored.1.2.1
    have covers := exhausted_refill_covers_position config.finish machine.classification.word.boundary machine.cursor
      (fetch config providers machine).rewind active (by omega)
    exact Nat.le_of_lt covers
  · exact fetched_hyphen_cover config providers lengths machine stored active exhausted
  · exact fetched_spacing_cover config providers lengths machine active

theorem considered_stored (config : Configuration α) (providers : Providers α μ) (machine : Machine α)
    (stored : Stored config machine) (active : machine.cursor.position < config.finish) :
    Stored config (consider config providers machine) :=
  ⟨considered_loop_ready config providers machine stored.1 active,stored.2⟩

theorem advanced_stored (config : Configuration α) (machine : Machine α)
    (stored : Stored config machine) (buffered : machine.cursor.position < machine.cursor.bufferEnd) :
    Stored config (advanced machine) := by
  have high := stored.1.1.2.2.2.2.1
  refine ⟨advanced_loop_ready config machine stored.1 (by omega),?_,stored.2.2⟩
  change machine.cursor.position+1 ≤ machine.cursor.bufferEnd
  omega

theorem loop_stored (config : Configuration α) (providers : Providers α μ) (lengths : ProviderLengths config.finish providers)
    (machine : Machine α) (stored : Stored config machine) : Stored config (loop config providers machine) := by
  rw [loop]
  split
  next active =>
    split
    next exhausted =>
      dsimp only
      have nextStored := refreshed_stored config providers lengths machine stored active exhausted
      have nextActive := refreshed_active config providers machine stored.1 active exhausted
      have nextBuffered : (refreshed config machine (fetch config providers machine)).cursor.position <
          (refreshed config machine (fetch config providers machine)).cursor.bufferEnd := by
        have old := stored.1.2.1
        exact exhausted_refill_covers_position config.finish machine.classification.word.boundary machine.cursor
          (fetch config providers machine).rewind active (by omega)
      split
      · exact loop_stored config providers lengths _ nextStored
      · have considered := considered_stored config providers _ nextStored nextActive
        split
        · exact considered
        · exact loop_stored config providers lengths _ (advanced_stored config _ considered nextBuffered)
    next buffered =>
      dsimp only
      have considered := considered_stored config providers machine stored active
      split
      · exact considered
      · exact loop_stored config providers lengths _ (advanced_stored config _ considered (by change machine.cursor.position < machine.cursor.bufferEnd; omega))
  next finished => exact stored
termination_by budget config.finish machine.cursor
decreasing_by
  all_goals first
    | exact advance_budget_decreases config.finish machine.cursor (by assumption)
    | exact refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ (by assumption) (by assumption)
    | exact Nat.lt_of_le_of_lt (advance_budget_nonstrict config.finish _)
        (refill_budget_decreases config.finish machine.classification.word.boundary machine.cursor _ (by assumption) (by assumption))

theorem constructor_storage (config : Configuration α) (providers : Providers α μ) (lengths : ProviderLengths config.finish providers) :
    Stored config (loop config providers (initialMachine config providers)) :=
  loop_stored config providers lengths _ (initial_stored config providers lengths)

theorem enabled_hyphen_index_in_bounds (config : Configuration α) (machine : Machine α)
    (stored : Stored config machine) (buffered : machine.cursor.position < machine.cursor.bufferEnd)
    (enabled : machine.haveHyphenation = true) :
    machine.cursor.position-config.start < machine.classification.buffer.length :=
  hyphen_index_safe config.start config.finish machine.classification.buffer.length machine.cursor stored.1.1 buffered
    (stored.2.2.1 enabled)

theorem enabled_spacing_index_in_bounds (config : Configuration α) (machine : Machine α)
    (stored : Stored config machine) (buffered : machine.cursor.position < machine.cursor.bufferEnd)
    (enabled : config.spacingEnabled = true) (notRescanning : machine.cursor.rescanLimit ≤ machine.cursor.position) :
    machine.cursor.position-machine.cursor.bufferStart < machine.spacing.length ∧
      machine.cursor.position-machine.cursor.bufferStart < 100 := by
  have safe := spacing_index_safe config.start config.finish machine.cursor stored.1.1 buffered notRescanning
  have length := stored.2.2.2 enabled
  constructor <;> omega

theorem exhausted_buffer_is_contiguous (config : Configuration α) (machine : Machine α)
    (stored : Stored config machine) (exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position)
    (enabled : machine.haveHyphenation = true) :
    machine.cursor.position = config.start+machine.classification.buffer.length := by
  have covered := stored.2.2.1 enabled
  have positionBound := stored.2.1
  omega

end HyphenMeasurementBoundedStorage
