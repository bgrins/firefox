import Coalesced
open CoalescedChain
example : droppedChild.map (fun n => n.installed.value) = expected 1 double 0 droppedChild.length := by decide +kernel
