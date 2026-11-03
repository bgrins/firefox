import Handoff
open CancellationEntry CancellationRoute CancellationHandoff
example : (broad false CancellationHandoff.observed).descendantHint = true := by decide +kernel
