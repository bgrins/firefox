import Phase
open FontConsumerDemand FontReadinessPhase
example : answer (request ⟨.size, .size⟩ .metrics) .size = .pending := by decide
