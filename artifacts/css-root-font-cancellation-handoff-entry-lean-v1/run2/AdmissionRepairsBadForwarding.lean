import Handoff
open CancellationEntry CancellationRoute CancellationHandoff
example : (run onlyAnimated deepRoute.length (enter (entryGate (selective true CancellationHandoff.observed)) deepRoute)).visited = deepRoute := by decide +kernel
