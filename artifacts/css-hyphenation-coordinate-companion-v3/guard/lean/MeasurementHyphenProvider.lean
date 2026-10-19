import MeasurementBoundedStorage
import SkipRunNativeStep

namespace HyphenMeasurementHyphenProvider

open HyphenSkipRanges HyphenSkipRunTraversal HyphenSkipRunNativeStep
open HyphenMeasurementMachine HyphenMeasurementBoundedStorage

 def classificationKind : HyphenationProviderWrites.Kind → HyphenMeasurementClassification.Kind
  | .none => .none
  | .soft => .soft
  | .explicit => .explicit
  | .automatic => .autoWithoutManual

def query (inputs : HyphenationProviderWrites.Inputs) (wrap enabled : Bool)
    (allowSoft : Nat → Bool) (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) (first finish : Nat) : List HyphenMeasurementClassification.Kind :=
  (HyphenationProviderWrites.provide inputs wrap enabled (allowSoft first) (finish-first) first
    (traverse ranges count valid (lookupSkipped ranges first) (finish-first))).map classificationKind

theorem query_length (inputs : HyphenationProviderWrites.Inputs) (wrap enabled : Bool)
    (allowSoft : Nat → Bool) (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) (first finish : Nat)
    (ordered : first ≤ finish) (bounded : finish ≤ count-total ranges) :
    (query inputs wrap enabled allowSoft ranges count valid first finish).length = finish-first := by
  unfold query
  rw [List.length_map]
  exact complete_provider_query_length inputs wrap enabled (allowSoft first) ranges count first
    (finish-first) valid (by omega)

def withHyphenProvider (providers : Providers α μ) (inputs : HyphenationProviderWrites.Inputs)
    (wrap enabled : Bool) (allowSoft : Nat → Bool) (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) : Providers α μ :=
  {providers with hyphenation := query inputs wrap enabled allowSoft ranges count valid}

theorem bounded_provider_lengths (providers : Providers α μ) (inputs : HyphenationProviderWrites.Inputs)
    (wrap enabled : Bool) (allowSoft : Nat → Bool) (ranges : List Range) (count limit : Nat)
    (valid : WellFormed ranges count) (limitBound : limit ≤ count-total ranges)
    (spacingLengths : ∀ first finish, first ≤ finish → finish ≤ limit →
      (providers.spacing first finish).length = finish-first) :
    ProviderLengths limit (withHyphenProvider providers inputs wrap enabled allowSoft ranges count valid) := by
  intro first finish ordered bounded
  exact ⟨spacingLengths first finish ordered bounded,
    query_length inputs wrap enabled allowSoft ranges count valid first finish ordered (by omega)⟩

theorem complete_machine_storage (config : Configuration α) (providers : Providers α μ)
    (inputs : HyphenationProviderWrites.Inputs) (wrap enabled : Bool) (allowSoft : Nat → Bool)
    (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (limitBound : config.finish ≤ count-total ranges)
    (spacingLengths : ∀ first finish, first ≤ finish → finish ≤ config.finish →
      (providers.spacing first finish).length = finish-first) :
    let joined := withHyphenProvider providers inputs wrap enabled allowSoft ranges count valid
    Stored config (loop config joined (initialMachine config joined)) := by
  dsimp only
  exact constructor_storage config _
    (bounded_provider_lengths providers inputs wrap enabled allowSoft ranges count config.finish
      valid limitBound spacingLengths)

end HyphenMeasurementHyphenProvider
