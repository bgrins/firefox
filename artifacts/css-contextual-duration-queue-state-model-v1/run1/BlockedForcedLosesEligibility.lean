import QueueState
open QueueState
example : eligible (forced .throttled blocked).entry false = false := by decide
