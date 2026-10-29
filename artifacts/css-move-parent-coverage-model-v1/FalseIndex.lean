import Parent
open ParentCoverage
example :
    (MoveCoverage.refresh (values exampleBefore) (values exampleAfter) destinationOnly 0).2 =
      (values exampleAfter 0).2 := by decide
