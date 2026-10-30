import QueueState
open QueueState
example : (post .absent safe).entry = .attempted := by decide
