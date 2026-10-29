import Accumulation
open CacheExclusion
example : collect false ([] : List Read) = collect false [.untracked] := by decide
