import MeasurementHyphenProvider
import SpacingTabComposition

namespace HyphenMeasurementSpacingProvider

open HyphenMeasurementMachine HyphenMeasurementBoundedStorage HyphenMeasurementHyphenProvider
open HyphenSkipRanges

structure SpacingContext (Value : Type) where
  numeric : HyphenTabValues.Numeric Value
  singletonQueries : Nat → HyphenSpacingPhases.Input Value
  tabProviders : HyphenTabValues.Providers Value
  tabContext : Nat → Nat → HyphenTabValues.Context Value
  tabState : Nat → Nat → HyphenTabValues.State Value
  input : Nat → Nat → HyphenSpacingPhases.Input Value

def completeSpacing (context : SpacingContext Value) (first finish : Nat) : List (Value × Value) :=
  let input := {context.input first finish with queryStart := first,queryEnd := finish}
  let calculated := HyphenSpacingTabComposition.calculateAndApply context.numeric context.singletonQueries
    context.tabProviders {context.tabContext first finish with queryEnd := finish}
    (context.tabState first finish) input
  (List.range (finish-first)).map fun index =>
    (calculated.2.store index .before,calculated.2.store index .after)

theorem complete_spacing_length (context : SpacingContext Value) (first finish : Nat) :
    (completeSpacing context first finish).length = finish-first := by simp [completeSpacing]

def withSpacing (providers : Providers α μ) (context : SpacingContext α) : Providers α μ :=
  {providers with spacing := completeSpacing context}

def withBoth (providers : Providers α μ) (context : SpacingContext α)
    (inputs : HyphenationProviderWrites.Inputs) (wrap enabled : Bool) (allowSoft : Nat → Bool)
    (ranges : List Range) (count : Nat) (valid : WellFormed ranges count) : Providers α μ :=
  withHyphenProvider (withSpacing providers context) inputs wrap enabled allowSoft ranges count valid

theorem both_provider_lengths (providers : Providers α μ) (context : SpacingContext α)
    (inputs : HyphenationProviderWrites.Inputs) (wrap enabled : Bool) (allowSoft : Nat → Bool)
    (ranges : List Range) (count limit : Nat) (valid : WellFormed ranges count)
    (bounded : limit ≤ count-total ranges) :
    ProviderLengths limit (withBoth providers context inputs wrap enabled allowSoft ranges count valid) := by
  apply bounded_provider_lengths _ _ _ _ _ _ _ _ _ bounded
  intro first finish ordered within
  exact complete_spacing_length context first finish

theorem complete_both_provider_storage (config : Configuration α) (providers : Providers α μ)
    (context : SpacingContext α) (inputs : HyphenationProviderWrites.Inputs)
    (wrap enabled : Bool) (allowSoft : Nat → Bool)
    (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (bounded : config.finish ≤ count-total ranges) :
    let joined := withBoth providers context inputs wrap enabled allowSoft ranges count valid
    Stored config (loop config joined (initialMachine config joined)) := by
  dsimp only
  exact constructor_storage config _ (both_provider_lengths providers context inputs wrap enabled allowSoft ranges count config.finish valid bounded)

theorem complete_both_provider_metric_range (config : Configuration α) (providers : Providers α μ)
    (context : SpacingContext α) (inputs : HyphenationProviderWrites.Inputs)
    (wrap enabled : Bool) (allowSoft : Nat → Bool)
    (ranges : List Range) (count : Nat) (valid : WellFormed ranges count) :
    let joined := withBoth providers context inputs wrap enabled allowSoft ranges count valid
    (run config joined).metrics = providers.measure config.start (config.start+(run config joined).fit) :=
  whole_machine_metric_request _ _

end HyphenMeasurementSpacingProvider
