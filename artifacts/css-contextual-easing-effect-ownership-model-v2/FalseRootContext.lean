import Ownership
open EffectOwnershipV2
example :
    let relabeled := { initial with referenceRoot := 9, selection := { firstSelection with ruleRoot := 9 } }
    computed relabeled.selection relabeled.elementContext = [3] := by decide
