import Range
open CounterRangeRepresentation

def boxedOne : Range := ⟨.finite (.boxedResolved 1), .finite (.boxedResolved 1)⟩
def lowerDeferred : Range := ⟨.finite .unresolved, .infinite⟩
def upperDeferred : Range := ⟨.infinite, .finite .unresolved⟩

example : oldAdmitted boxedOne = true := by decide +kernel
example : admitted boxedOne = true := by decide +kernel
example : exportWith inlineGet boxedOne 1 = none := by decide +kernel
example : exportWith resolve boxedOne 1 = some true := by decide +kernel
example : exportWith resolve boxedOne 0 = some false := by decide +kernel
example : exportWith resolve boxedOne 2 = some false := by decide +kernel
example : oldAdmitted lowerDeferred = true ∧ admitted lowerDeferred = false ∧
    exportWith resolve lowerDeferred 0 = none := by decide +kernel
example : oldAdmitted upperDeferred = true ∧ admitted upperDeferred = false ∧
    exportWith resolve upperDeferred 0 = none := by decide +kernel
example : admitted ⟨.finite (.boxedResolved 2), .finite (.inline 1)⟩ = false := by decide +kernel
example : admitted ⟨.infinite, .infinite⟩ = true ∧
    exportWith resolve ⟨.infinite, .infinite⟩ (-100) = some true := by decide +kernel
example : admitted ⟨.finite (.boxedResolved (-3)), .infinite⟩ = true ∧
    exportWith resolve ⟨.finite (.boxedResolved (-3)), .infinite⟩ (-3) = some true := by decide +kernel
example : admitted ⟨.infinite, .finite (.boxedResolved 3)⟩ = true ∧
    exportWith resolve ⟨.infinite, .finite (.boxedResolved 3)⟩ 3 = some true := by decide +kernel
example : exportWith resolve ⟨.finite (.inline 3), .finite .unresolved⟩ 2 = some false ∧
    admitted ⟨.finite (.inline 3), .finite .unresolved⟩ = false := by decide +kernel
example : exportWith inlineGet ⟨.finite (.inline 1), .finite (.inline 1)⟩ 1 = some true := by decide +kernel
