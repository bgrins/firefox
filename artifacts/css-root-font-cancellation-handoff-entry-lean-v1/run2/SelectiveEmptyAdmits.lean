import Handoff
open CancellationEntry CancellationRoute CancellationHandoff
example : normalEligible (entryGate (selective true noStyled)) = true := by decide +kernel
