import Examples
open RegisteredZoom.Structural RegisteredZoom.Structural.Examples
example : skippedImage 8 (.length 6) = mapLengths (fun n => n * 2) (.image 8 (.length 6) : V) := by
  decide +kernel
