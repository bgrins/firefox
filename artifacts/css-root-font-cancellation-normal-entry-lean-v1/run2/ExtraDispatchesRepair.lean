import Entry
open CancellationEntry CancellationRoute
example : (run forwardAll 5 (enter observed deepRoute)).visited = deepRoute := by decide +kernel
