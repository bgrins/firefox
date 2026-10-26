import Refresh
import Schedule

namespace CommitRefresh

theorem scheduled_provider_prefix_current {Effect Value : Type} [DecidableEq Effect]
    (graph : KeyframeGraph.Graph n) (progress : Fin n → Rat)
    (providerCache : Fin n → Rat)
    (resolve : (Fin n → Rat) → Cache Effect Value)
    (stack tasks : List Effect) (cache : Cache Effect Value) (base : Value)
    (covered : ∀ effect ∈ stack, effect ∈ tasks) :
    compose stack (refresh resolve
      (KeyframeGraph.run graph progress (KeyframeGraph.beginSample providerCache)
        (KeyframeGraph.schedule graph)).cache tasks cache) base =
      compose stack (resolve (KeyframeGraph.value graph progress)) base := by
  apply refresh_context_transport
  · exact KeyframeGraph.constructed_sample_correct graph progress providerCache
  · exact covered

end CommitRefresh
