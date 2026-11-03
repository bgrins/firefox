import Route
open CancellationRoute
example : (run onlyAnimated 2 (load [root, dependent] [])).visited = [root] := by decide +kernel
