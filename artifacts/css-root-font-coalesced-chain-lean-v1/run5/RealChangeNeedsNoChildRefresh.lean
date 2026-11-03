import Coalesced
open CoalescedChain
example : downstream parentPending.installed.value (completeNode parentPending).installed.value [childOld] = [childOld] := by decide +kernel
