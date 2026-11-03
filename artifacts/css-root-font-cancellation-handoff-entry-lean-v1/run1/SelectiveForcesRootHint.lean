import Handoff
open CancellationEntry CancellationRoute CancellationHandoff
example : (selective true CancellationHandoff.observed).gate.localHint = true := by decide +kernel
