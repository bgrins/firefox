import Scope
open ScopeCache
example : (compile shifted).map Compiled.index = [0] := by decide +kernel
