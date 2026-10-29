import Reorder
open ReorderCoverage
open ParentCoverage (values)
example : MoveCoverage.refresh (fun n => (values ReorderCoverage.exampleBefore n).2)
    (fun n => (values ReorderCoverage.exampleAfter n).2) (fun _ => false) 2 =
    (values ReorderCoverage.exampleAfter 2).2 := by decide
