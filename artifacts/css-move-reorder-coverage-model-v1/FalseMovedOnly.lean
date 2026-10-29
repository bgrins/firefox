import Reorder
open ReorderCoverage
open ParentCoverage (values)
example : MoveCoverage.refresh (fun n => (values ReorderCoverage.exampleBefore n).2)
    (fun n => (values ReorderCoverage.exampleAfter n).2) movedOnly 0 =
    (values ReorderCoverage.exampleAfter 0).2 := by decide
