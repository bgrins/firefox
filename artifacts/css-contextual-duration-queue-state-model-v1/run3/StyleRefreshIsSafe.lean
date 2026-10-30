import QueueState
open QueueState
example : (forced .throttled { safe with styleRefresh := true }).attempt = true := by decide
