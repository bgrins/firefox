import FontDemand
open FontConsumerDemand
example : summary ([Use.alias 0].flatMap (expansion (fun (_ : Nat) => [Unit.ch]))) = Demand.size := by decide
