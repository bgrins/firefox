import Ownership
open EffectOwnership
example : (run initial [.setKeyframes (.error 2), .refresh nextSelection env]).frames = [2] := by decide
