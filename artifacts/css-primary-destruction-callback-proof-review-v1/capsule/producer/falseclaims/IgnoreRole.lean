import Witnesses

open Destruction

example : let wrong := write sample 30 (some (.allocation .fragment))
    (badIgnoreRole wrong ⟨30, .itemCache⟩).isSome =
      (freeOne wrong ⟨30, .itemCache⟩).isSome := by decide
