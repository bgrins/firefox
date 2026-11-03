import Route
open CancellationRoute
example : (run forwardAll 3 (State.mk none deepRoute [])).visited = deepRoute := by decide +kernel
