import Completion
open Completion
example : (QueueState.request .pending .standard QueueState.safe).entry = .absent := by decide
