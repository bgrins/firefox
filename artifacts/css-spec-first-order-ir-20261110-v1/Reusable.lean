import Lowering

namespace CssDerivation.FirstOrder

def readCode : Stmt [] .nat := .read (.ret (.nat 0)) (.ret (.code (.var .here)))

def sumTwoCodes : Stmt [] .nat :=
  .scan 2 (.bool true)
    (.ret (.foldNat (.var .here) (.nat 0) (.add (.var (.there .here)) (.code (.var .here)))))

def shadowedLocal : Stmt [] .nat :=
  .letE (.nat 7) (.letE (.nat 2) (.ret (.sub (.var (.there .here)) (.var .here))))

theorem shadowed_local (state : State) : interpret shadowedLocal .nil state = (5, state) := rfl

example : interpret readCode .nil ⟨['z'], false⟩ = (122, ⟨[], false⟩) := by decide
example : interpret sumTwoCodes .nil ⟨['A', 'B', 'C'], false⟩ = (131, ⟨['C'], false⟩) := by decide
example : interpret sumTwoCodes .nil ⟨['A'], true⟩ = (65, ⟨[], true⟩) := by decide
example : interpret sumTwoCodes .nil ⟨[], false⟩ = (0, ⟨[], false⟩) := by decide
example : run (lower sumTwoCodes .nil) ⟨['A', 'B', 'C'], false⟩ =
    interpret sumTwoCodes .nil ⟨['A', 'B', 'C'], false⟩ :=
  lowering_correct _ _ _

end CssDerivation.FirstOrder
