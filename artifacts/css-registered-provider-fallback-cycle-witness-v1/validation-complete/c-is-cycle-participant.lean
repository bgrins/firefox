import Witness
open FallbackCycleWitness
example : AttributeGuard.Key.property 2 ∈ participantResult.state.poisoned := by
  decide +kernel
