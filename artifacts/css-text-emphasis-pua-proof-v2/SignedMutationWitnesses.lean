import SignedLigature

namespace Emphasis.SignedWitness
open SignedLigature Dispatch

def floorQuotient (width : Int) (total : Nat) : Int :=
  (width-(if width < 0 then (total : Int)-1 else 0)).tdiv total

def narrowedQuotient (width : Int) (total : Nat) : Int :=
  width.tdiv (if total < 2147483648 then (total : Int) else total-4294967296)

theorem floor_negative : (-1 : Int).tdiv 2 ≠ floorQuotient (-1) 2 := by decide +kernel

theorem narrow_denominator : (-2147483648 : Int).tdiv 2147483649 ≠
    narrowedQuotient (-2147483648) 2147483649 := by decide +kernel

theorem unsigned_quotient : quotient .signed (-1) 2 ≠ quotient .legacyUnsigned32 (-1) 2 := by decide +kernel

theorem omit_remainder : partialWidth .signed (-1) 2 1 true 0 0 ≠
    apportioned (-1) 2 1 := by decide +kernel

theorem omit_part_index : apportioned 10 2 1 ≠ 0 := by decide +kernel

end Emphasis.SignedWitness
