import Entry
open CancellationEntry CancellationRoute
example : (run forwardAll 3 (enter observed deepRoute)).visited = deepRoute := by decide +kernel
