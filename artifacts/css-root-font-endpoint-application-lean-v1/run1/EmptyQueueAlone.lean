import Application
open EndpointApplication
example : ready (State.mk ⟨1, 64⟩ ⟨0, 46⟩ []) := by decide +kernel
