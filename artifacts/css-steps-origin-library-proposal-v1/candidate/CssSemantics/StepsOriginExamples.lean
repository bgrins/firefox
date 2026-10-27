import CssSemantics.StepsOrigin

open CssSemantics.StepsOrigin

example : calculation 4 .nan = .calculation (some 1) := by decide +kernel
example : calculation 4 (.finite ⟨0, false⟩) = .calculation (some 1) := by decide +kernel
example : calculation 4 (.finite ⟨1, false⟩) = .calculation (some 1) := by decide +kernel
example : repaired .jumpNone (calculation 4 .nan) = some 2 := by decide +kernel
example : old .jumpNone (calculation 4 .nan) = none := by decide +kernel
example : repaired .jumpNone (calculation 4 (.finite ⟨-10, false⟩)) = some 2 := by decide +kernel
example : repaired .jumpNone (calculation 4 (.finite ⟨7 / 5, false⟩)) = some 2 := by decide +kernel
example : repaired .jumpNone (calculation 4 (.finite ⟨3 / 2, false⟩)) = some 2 := by decide +kernel
example : repaired .ordinary (calculation 4 .nan) = some 1 := by decide +kernel
example : repaired .jumpNone (.literal 1) = none := by decide +kernel
example : repaired .jumpNone (.calculation none) = none := by decide +kernel

namespace CssSemantics.StepsOrigin.Examples

def checks : List (String × Bool) := [
  ("steps origin normalize NaN to one", decide (calculation 4 .nan = .calculation (some 1))),
  ("steps origin normalize zero to one", decide (calculation 4 (.finite ⟨0, false⟩) = .calculation (some 1))),
  ("steps origin normalize one to one", decide (calculation 4 (.finite ⟨1, false⟩) = .calculation (some 1))),
  ("steps origin calculated NaN clamps to two", decide (repaired .jumpNone (calculation 4 .nan) = some 2)),
  ("steps origin old calculated NaN rejects", decide (old .jumpNone (calculation 4 .nan) = none)),
  ("steps origin calculated negative clamps to two", decide (repaired .jumpNone (calculation 4 (.finite ⟨-10, false⟩)) = some 2)),
  ("steps origin calculated fraction clamps to two", decide (repaired .jumpNone (calculation 4 (.finite ⟨7 / 5, false⟩)) = some 2)),
  ("steps origin calculated tie reaches two", decide (repaired .jumpNone (calculation 4 (.finite ⟨3 / 2, false⟩)) = some 2)),
  ("steps origin ordinary calculation remains one", decide (repaired .ordinary (calculation 4 .nan) = some 1)),
  ("steps origin literal one rejects", decide (repaired .jumpNone (.literal 1) = none)),
  ("steps origin unresolved calculation rejects", decide (repaired .jumpNone (.calculation none) = none)),
  ("steps origin reject literal origin clamping", decide (repaired .jumpNone (.literal 1) = some 2)),
  ("steps origin reject calculated NaN invalidation", decide (repaired .jumpNone (calculation 4 .nan) = none)),
  ("steps origin reject unresolved admission", decide (repaired .jumpNone (.calculation none) = some 2))
]

end CssSemantics.StepsOrigin.Examples
