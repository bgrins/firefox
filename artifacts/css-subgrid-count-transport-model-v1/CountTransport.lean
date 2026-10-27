import Std

namespace SubgridCountTransport

def addCap (cap left right : Nat) : Nat :=
  let bounded := min cap left
  if cap - bounded ≤ right then cap else bounded + right

def mulCap (cap left right : Nat) : Nat :=
  if right = 0 then 0
  else if left ≤ cap / right then left * right else cap

theorem addCap_correct (cap left right budget : Nat) (fits : cap ≤ budget) :
    addCap cap left right = min cap (left + right) ∧
    addCap cap left right ≤ budget ∧
    (right < cap - min cap left → min cap left + right ≤ budget) := by
  dsimp only [addCap]
  split <;> omega

theorem mulCap_correct (cap left right budget : Nat) (fits : cap ≤ budget) :
    mulCap cap left right = min cap (left * right) ∧
    mulCap cap left right ≤ budget ∧
    (left ≤ cap / right → left * right ≤ budget) := by
  have guarded : left ≤ cap / right → left * right ≤ cap :=
    fun h => Nat.mul_le_of_le_div right left cap h
  unfold mulCap
  split
  next zero => simp_all
  next nonzero =>
    have pos : 0 < right := by omega
    split
    next h => have := guarded h; omega
    next h =>
      have above : cap < left * right := (Nat.div_lt_iff_lt_mul pos).mp (by omega)
      omega

def total : List (Nat × Nat) → Nat
  | [] => 0
  | (count, groups) :: rest => count * groups + total rest

def cacheFrom (cap accumulator : Nat) : List (Nat × Nat) → Nat
  | [] => min cap accumulator
  | (count, groups) :: rest =>
      cacheFrom cap (addCap cap accumulator (mulCap cap count groups)) rest

def cache (cap : Nat) (terms : List (Nat × Nat)) : Nat := cacheFrom cap 0 terms

theorem cache_correct (cap accumulator : Nat) (terms : List (Nat × Nat)) :
    cacheFrom cap accumulator terms = min cap (accumulator + total terms) := by
  induction terms generalizing accumulator with
  | nil => simp [cacheFrom, total]
  | cons pair rest ih =>
    rcases pair with ⟨count, groups⟩
    simp only [cacheFrom, total]
    rw [ih, (addCap_correct cap _ _ cap (by omega)).1,
        (mulCap_correct cap count groups cap (by omega)).1]
    omega

theorem remaining_capacity_preserved (capacity cap : Nat)
    (within : capacity ≤ cap) (terms : List (Nat × Nat)) :
    capacity - cache cap terms = capacity - total terms := by
  simp only [cache, cache_correct, Nat.zero_add]
  omega

theorem signed_transport_safe (capacity cap signedMax : Nat)
    (within : capacity ≤ cap) (fits : cap ≤ signedMax)
    (terms : List (Nat × Nat)) :
    cache cap terms ≤ signedMax ∧
    -(signedMax : Int) ≤ (capacity : Int) - (cache cap terms : Int) ∧
    (capacity : Int) - (cache cap terms : Int) ≤ (signedMax : Int) ∧
    max 0 ((capacity : Int) - (cache cap terms : Int)) =
      ((capacity - total terms : Nat) : Int) := by
  simp only [cache, cache_correct, Nat.zero_add]
  omega

def narrow32 (value : Nat) : Int :=
  let low := value % 4294967296
  if low < 2147483648 then (low : Int) else (low : Int) - 4294967296

example : narrow32 (2147483647 * 2) = -2 ∧
    max 0 (3 - narrow32 (2147483647 * 2)) = 5 ∧
    (3 : Nat) - (2147483647 * 2) = 0 := by decide +kernel

example : ¬ (∀ n : Nat, max 0 (3 - narrow32 n) = ((3 - n : Nat) : Int)) := by
  intro all
  have h := all (2147483647 * 2)
  have wrong : max 0 (3 - narrow32 (2147483647 * 2)) ≠
      ((3 - (2147483647 * 2) : Nat) : Int) := by decide +kernel
  exact wrong h

example : ¬ ((3 : Nat) - min 2 10 = 3 - 10) := by decide +kernel
example : ¬ (2147483647 * 3 ≤ 4294967295) := by decide +kernel
example : 2147483647 ≤ 4294967295 ∧ 2147483647 ≤ 18446744073709551615 := by decide +kernel
example : cache 2147483647 [(2147483647, 2)] = 2147483647 ∧
    (3 : Nat) - cache 2147483647 [(2147483647, 2)] = 0 := by decide +kernel

example : min 2147483647 ((2147483647 * 3) % 4294967296) ≠
    min 2147483647 (2147483647 * 3) := by decide +kernel
example : narrow32 18446744073709551615 = -1 ∧
    max 0 (3 - narrow32 18446744073709551615) = 4 := by decide +kernel

#print axioms addCap_correct
#print axioms mulCap_correct
#print axioms cache_correct
#print axioms remaining_capacity_preserved
#print axioms signed_transport_safe
end SubgridCountTransport
