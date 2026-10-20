import BoundaryMutants
open Destruction Destruction.Ownership

example : compareAddressAndRole [⟨30, .itemCache⟩] [⟨30, .itemsBuffer⟩] = false := by decide
