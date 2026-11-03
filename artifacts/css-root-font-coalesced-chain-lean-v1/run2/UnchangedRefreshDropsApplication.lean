import Coalesced
open CoalescedChain
example : (refreshNode 64 { pending64 with refresh := true }).queued = false := by decide +kernel
