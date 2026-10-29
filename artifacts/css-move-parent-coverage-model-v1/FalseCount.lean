import Parent
open ParentCoverage
example :
    (MoveCoverage.refresh (values exampleBefore) (values exampleAfter) destinationOnly 0).1 =
      (values exampleAfter 0).1 := by decide
