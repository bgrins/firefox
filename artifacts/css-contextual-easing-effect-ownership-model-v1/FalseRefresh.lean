import Ownership
open EffectOwnership
example : (step (step initial (.setKeyframes (.ok [5]))) (.refresh nextSelection env)).frames = computed nextSelection env := by decide
