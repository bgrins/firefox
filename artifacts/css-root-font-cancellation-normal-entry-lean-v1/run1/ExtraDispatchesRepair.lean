import Entry
open CancellationEntry CancellationRoute
example : (run forwardAll 100 (enter observed deepRoute)).visited = deepRoute := by decide +kernel
