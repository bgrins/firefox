import Witness
open Binary32Magnitude FiniteModRemWitness

example : SpecRemainder 2 := (spec_remainder_unique 2).2 rfl
example : decode (BitVec.ofNat 32 0x4bffffff) = 33554430 * unit := by decide +kernel
example : decode (BitVec.ofNat 32 0x4c000001) = 33554436 * unit := by decide +kernel
example : decode (BitVec.ofNat 32 0x4b2aaaaa) = 11184810 * unit := by decide +kernel
example : decode (BitVec.ofNat 32 0x4b2aaaac) = 11184812 * unit := by decide +kernel
example : roundedFormula localRound = 0 := rounded_formula_zero localRound rounding_contract_inhabited
