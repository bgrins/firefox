import Handoff
open CancellationEntry CancellationRoute CancellationHandoff
example : (enter (entryGate (broad true CancellationHandoff.observed)) deepRoute).visited = deepRoute := by decide +kernel
