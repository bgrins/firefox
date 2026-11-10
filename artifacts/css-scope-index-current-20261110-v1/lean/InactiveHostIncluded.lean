import Vectors
open ScopeCache
example : (collectVectors shifted).hostContexts = [false, false] := by decide +kernel
