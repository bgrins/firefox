import CssSemantics.ImplementationSupport.FiniteModRemWitness

namespace CssSemantics.ImplementationSupport.FiniteModRemWitnessExamples
open CssSemantics.ImplementationSupport.FiniteModRemWitness
open CssSemantics.ImplementationSupport.Binary32Magnitude


example : SpecRemainder 2 := (spec_remainder_unique 2).2 rfl
example : decode (BitVec.ofNat 32 0x4bffffff) = 33554430 * unit := by decide +kernel
example : decode (BitVec.ofNat 32 0x4c000001) = 33554436 * unit := by decide +kernel
example : decode (BitVec.ofNat 32 0x4b2aaaaa) = 11184810 * unit := by decide +kernel
example : decode (BitVec.ofNat 32 0x4b2aaaac) = 11184812 * unit := by decide +kernel
example : roundedFormula localRound = 0 := rounded_formula_zero localRound rounding_contract_inhabited

def checks : List (String × Bool) := [
  ("finite ModRem witness bounded congruence", decide ((33554432 : Int) = 3 * 11184810 + 2 ∧ (0 : Int) ≤ 2 ∧ (2 : Int) < 3)),
  ("finite ModRem witness lower binade neighbor", decide (decode (BitVec.ofNat 32 0x4bffffff) = 33554430 * unit)),
  ("finite ModRem witness upper binade neighbor", decide (decode (BitVec.ofNat 32 0x4c000001) = 33554436 * unit)),
  ("finite ModRem witness quotient predecessor", decide (decode (BitVec.ofNat 32 0x4b2aaaaa) = 11184810 * unit)),
  ("finite ModRem witness quotient successor", decide (decode (BitVec.ofNat 32 0x4b2aaaac) = 11184812 * unit)),
  ("finite ModRem witness rounded reconstruction zero", decide (roundedFormula localRound = 0)),
  ("finite ModRem witness rejects zero congruence", decide ((33554432 : Int) = 3 * 11184810 + 0)),
  ("finite ModRem witness rejects nearer lower quotient", decide (distance (decode a) (3 * decode (BitVec.ofNat 32 0x4b2aaaaa)) ≤ distance (decode a) (3 * decode q))),
  ("finite ModRem witness rejects exact rounded product", decide (decode a = 33554433 * unit)),
  ("finite ModRem witness rejects symmetric predecessor", decide (decode (BitVec.ofNat 32 0x4bffffff) = 33554428 * unit)),
  ("finite ModRem witness rejects backend agreement", decide (roundedFormula localRound = (decode r : Int)))]

end CssSemantics.ImplementationSupport.FiniteModRemWitnessExamples
