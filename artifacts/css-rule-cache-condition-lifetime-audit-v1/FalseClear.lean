import Accumulation
open CacheExclusion
example : collect false [.untracked, .covered] = false := by decide
