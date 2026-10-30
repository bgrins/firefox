import QueueState
open QueueState
example : (request .attempted .layer safe).attempt = true := by decide
