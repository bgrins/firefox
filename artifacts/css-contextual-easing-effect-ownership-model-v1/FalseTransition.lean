import Ownership
open EffectOwnership
example : (step (step initial (.setKeyframes (.ok [5]))) .startTransition).transition = some ⟨10, 7, [5]⟩ := by decide
