import Handoff
open CancellationEntry CancellationRoute CancellationHandoff
example : (broad true CancellationHandoff.observed).selfHint = true := by decide +kernel
