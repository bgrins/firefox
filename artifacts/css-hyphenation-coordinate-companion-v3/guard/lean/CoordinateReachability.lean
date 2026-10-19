import MeasurementSpacingProvider
import MeasurementCoordinates

namespace CoordinateReachability

open HyphenMeasurementMachine HyphenMeasurementBoundedStorage

inductive Reachable (config : Configuration α) (providers : Providers α μ) : Machine α → Prop where
  | initial : Reachable config providers (initialMachine config providers)
  | refill {machine : Machine α} : Reachable config providers machine →
      machine.cursor.position < config.finish → machine.cursor.bufferEnd ≤ machine.cursor.position →
      Reachable config providers (refreshed config machine (fetch config providers machine))
  | consider {machine : Machine α} : Reachable config providers machine →
      machine.cursor.position < config.finish →
      Reachable config providers (HyphenMeasurementMachine.consider config providers machine)
  | advance {machine : Machine α} : Reachable config providers machine →
      machine.cursor.position < machine.cursor.bufferEnd →
      Reachable config providers (advanced machine)

theorem reachable_storage (config : Configuration α) (providers : Providers α μ)
    (lengths : ProviderLengths config.finish providers) (machine : Machine α)
    (reachable : Reachable config providers machine) : Stored config machine := by
  induction reachable with
  | initial => exact initial_stored config providers lengths
  | refill previous active exhausted ih =>
    exact refreshed_stored config providers lengths _ ih active exhausted
  | consider previous active ih => exact considered_stored config providers _ ih active
  | advance previous buffered ih => exact advanced_stored config _ ih buffered

theorem reachable_native_guard (config : Configuration α) (providers : Providers α μ)
    (lengths : ProviderLengths config.finish providers) (machine : Machine α)
    (reachable : Reachable config providers machine)
    (exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position)
    (enabled : machine.haveHyphenation = true)
    (automatic : config.hyphens = .auto) (repaired : config.repairedCoordinates = true)
    (allocated : providers.allocation machine.allocations machine.classification.buffer.length
      (min config.finish (machine.cursor.position + 100) - machine.cursor.position) = true) :
    (fetch config providers machine).rewind =
      decide (machine.classification.word.boundary < machine.cursor.position) := by
  have contiguous := exhausted_buffer_is_contiguous config machine
    (reachable_storage config providers lengths machine reachable) exhausted enabled
  cases spacing : config.spacingEnabled <;>
    simp [fetch,spacing,enabled,automatic,repaired,allocated,Id.run,Pure.pure,← contiguous]

theorem reachable_relative_guard (config : Configuration α) (providers : Providers α μ)
    (lengths : ProviderLengths config.finish providers) (machine : Machine α)
    (reachable : Reachable config providers machine)
    (exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position)
    (enabled : machine.haveHyphenation = true) :
    decide (machine.classification.word.boundary < machine.cursor.position) =
      decide (machine.classification.word.boundary - config.start < machine.classification.buffer.length) := by
  have stored := reachable_storage config providers lengths machine reachable
  have contiguous := exhausted_buffer_is_contiguous config machine stored exhausted enabled
  have lower := stored.1.2.1.1
  have equivalent : machine.classification.word.boundary < machine.cursor.position ↔
      machine.classification.word.boundary - config.start < machine.classification.buffer.length := by omega
  simp only [equivalent]

theorem failed_allocation_does_not_rewind (config : Configuration α) (providers : Providers α μ)
    (machine : Machine α)
    (failed : providers.allocation machine.allocations machine.classification.buffer.length
      (min config.finish (machine.cursor.position + 100) - machine.cursor.position) = false) :
    (fetch config providers machine).rewind = false := by
  cases spacing : config.spacingEnabled <;> cases enabled : machine.haveHyphenation <;>
    simp [fetch,spacing,enabled,failed,Id.run,Pure.pure]

theorem complete_provider_guard (config : Configuration α) (providers : Providers α μ)
    (context : HyphenMeasurementSpacingProvider.SpacingContext α)
    (inputs : HyphenationProviderWrites.Inputs) (wrap hyphenEnabled : Bool) (allowSoft : Nat → Bool)
    (ranges : List HyphenSkipRanges.Range) (count : Nat) (valid : HyphenSkipRanges.WellFormed ranges count)
    (bounded : config.finish ≤ count - HyphenSkipRanges.total ranges)
    (machine : Machine α)
    (reachable : Reachable config
      (HyphenMeasurementSpacingProvider.withBoth providers context inputs wrap hyphenEnabled allowSoft ranges count valid) machine)
    (exhausted : machine.cursor.bufferEnd ≤ machine.cursor.position)
    (enabled : machine.haveHyphenation = true)
    (automatic : config.hyphens = .auto) (repaired : config.repairedCoordinates = true)
    (allocated : providers.allocation machine.allocations machine.classification.buffer.length
      (min config.finish (machine.cursor.position + 100) - machine.cursor.position) = true) :
    (fetch config
      (HyphenMeasurementSpacingProvider.withBoth providers context inputs wrap hyphenEnabled allowSoft ranges count valid)
      machine).rewind = decide (machine.classification.word.boundary < machine.cursor.position) := by
  apply reachable_native_guard config _
    (HyphenMeasurementSpacingProvider.both_provider_lengths providers context inputs wrap hyphenEnabled
      allowSoft ranges count config.finish valid bounded) machine reachable exhausted enabled automatic repaired
  exact allocated

theorem old_comparison_disagrees : decide (260 < 100) = false ∧ decide (260 < 340) = true := by decide

def advanceBy (machine : Machine α) (count : Nat) : Machine α :=
  {machine with cursor := {machine.cursor with position := machine.cursor.position + count}}

theorem reachable_advance_prefix (config : Configuration α) (providers : Providers α μ)
    (machine : Machine α) (reachable : Reachable config providers machine) (count : Nat)
    (within : machine.cursor.position + count ≤ machine.cursor.bufferEnd) :
    Reachable config providers (advanceBy machine count) := by
  induction count with
  | zero => simpa [advanceBy] using reachable
  | succ count ih =>
    have previous := ih (by omega)
    have step := Reachable.advance previous (by change machine.cursor.position + count < machine.cursor.bufferEnd; omega)
    simpa [advanceBy,advanced,HyphenMeasurementRescanProgress.advance,Nat.add_assoc] using step

def exampleConfig : Configuration Nat :=
  ⟨240,200,440,1000,false,false,false,false,false,false,false,false,true,.auto,
    240,440,.none,0,true⟩

def exampleProviders : Providers Nat Nat :=
  ⟨⟨0,Nat.add,Nat.sub,fun a b => a ≤ b,fun a b => a > b⟩,
    fun _ => 0,fun _ => true,fun _ => false,fun _ => false,fun _ => false,
    fun _ => 1,fun _ => 1,fun a b => List.replicate (b-a) (0,0),
    fun a b => List.replicate (b-a) .none,fun _ _ _ => true,1,fun a b => b-a⟩

def exampleRefill : Machine Nat := advanceBy (initialMachine exampleConfig exampleProviders) 100

theorem example_reachable : Reachable exampleConfig exampleProviders exampleRefill := by
  apply reachable_advance_prefix _ _ _ Reachable.initial
  decide +kernel

theorem example_lengths : ProviderLengths exampleConfig.finish exampleProviders := by
  intro first finish ordered bounded
  simp [exampleProviders]

theorem example_native_and_old_disagree :
    (fetch exampleConfig exampleProviders exampleRefill).rewind = true ∧
    (fetch {exampleConfig with repairedCoordinates := false} exampleProviders exampleRefill).rewind = false ∧
    exampleRefill.cursor.position = 340 ∧ exampleRefill.classification.buffer.length = 100 := by
  decide +kernel

#print axioms reachable_storage
#print axioms reachable_native_guard
#print axioms reachable_relative_guard
#print axioms failed_allocation_does_not_rewind
#print axioms complete_provider_guard
#print axioms old_comparison_disagrees
#print axioms reachable_advance_prefix
#print axioms example_reachable
#print axioms example_lengths
#print axioms example_native_and_old_disagree
end CoordinateReachability
