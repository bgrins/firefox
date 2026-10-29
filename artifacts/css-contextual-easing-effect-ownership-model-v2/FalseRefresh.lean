import Ownership
open EffectOwnershipV2
example : (step (step initial (.setKeyframes (.ok [5])))
    (.refresh nextSelection targetContext)).frames = computed nextSelection targetContext := by decide
