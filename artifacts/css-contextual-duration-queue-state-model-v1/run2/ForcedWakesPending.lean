import QueueState
open QueueState
example : (forced .pending safe).attempt = true := by decide
