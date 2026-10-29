import Ownership
open EffectOwnershipV2
example : (run initial [.setKeyframes (.error 2), .refresh nextSelection targetContext]).frames = [2] := by decide
