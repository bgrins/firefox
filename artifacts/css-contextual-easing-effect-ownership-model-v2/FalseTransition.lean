import Ownership
open EffectOwnershipV2
example : (step (step initial (.setKeyframes (.ok [5]))) .startTransition).transition =
    some ⟨50, 7, 7, 100, 1, 10, 42, [5]⟩ := by decide
