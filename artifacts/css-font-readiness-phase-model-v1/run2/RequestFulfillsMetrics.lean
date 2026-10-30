import Phase
open FontConsumerDemand FontReadinessPhase
example : answer (request ⟨.size, .size⟩ .metrics) .metrics = .ready := by decide
