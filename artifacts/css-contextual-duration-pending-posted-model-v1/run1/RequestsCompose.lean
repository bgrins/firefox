import PendingPosted
open PendingPosted
example : (repeatRequests 4 witness).composedGeneration = (repeatRequests 4 witness).appliedGeneration := by decide
