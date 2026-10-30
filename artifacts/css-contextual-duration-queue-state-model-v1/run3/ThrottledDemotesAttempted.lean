import QueueState
open QueueState
example : (request .attempted .throttled safe).entry = .throttled := by decide
