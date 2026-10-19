import Std

namespace Emphasis.Raw
set_option linter.unusedSimpArgs false

abbrev Word := BitVec 32
def simple (w : Word) : Bool := w &&& 0x80000000 != 0
def common (w : Word) : Word := w &&& 0x70000000
def glyphId (w : Word) : Word := w &&& 0xffff
def advance (w : Word) : Word := (w &&& 0x0fff0000) >>> 16
def makeSimple (id advance : Word) : Word := 0x80000000 ||| (advance <<< 16) ||| id
def setNoEmphasis (w : Word) : Word := w ||| 0x00400000
def convert (w : Word) : Word := common w ||| 0x00010000 ||| 1
def suppress (w : Word) : Word := setNoEmphasis (if simple w then convert w else w)

private theorem high_mask (w : Word) : w &&& 0x80000000 = (if w.getLsbD 31 then 0x80000000 else 0) := by
  apply BitVec.eq_of_getLsbD_eq
  intro i hi
  have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
  rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  all_goals split <;> simp_all [BitVec.getLsbD_and, BitVec.getLsbD_ofNat]

theorem simple_is_bit (w : Word) : simple w = w.getLsbD 31 := by
  unfold simple
  rw [high_mask]
  cases h : w.getLsbD 31 <;> simp

theorem simple_payload_roundtrip (w : Word) (h : simple w = true) :
    common w ||| makeSimple (glyphId w) (advance w) = w := by
  try simp only [simple_is_bit] at *
  cases hbit : w.getLsbD 31
  all_goals
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals simp_all [simple_is_bit, suppress, setNoEmphasis, convert, common, makeSimple, glyphId, advance,
      BitVec.getLsbD_and, BitVec.getLsbD_or, BitVec.getLsbD_shiftLeft,
      BitVec.getLsbD_ushiftRight, BitVec.getLsbD_ofNat]

theorem common_preserved (w : Word) : common (suppress w) = common w := by
  try simp only [simple_is_bit] at *
  cases hbit : w.getLsbD 31
  all_goals
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals simp_all [simple_is_bit, suppress, setNoEmphasis, convert, common, makeSimple, glyphId, advance,
      BitVec.getLsbD_and, BitVec.getLsbD_or, BitVec.getLsbD_shiftLeft,
      BitVec.getLsbD_ushiftRight, BitVec.getLsbD_ofNat]

theorem complex_all_other_bits_preserved (w : Word) (h : simple w = false) :
    suppress w &&& 0xffbfffff = w &&& 0xffbfffff := by
  try simp only [simple_is_bit] at *
  cases hbit : w.getLsbD 31
  all_goals
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals simp_all [simple_is_bit, suppress, setNoEmphasis, convert, common, makeSimple, glyphId, advance,
      BitVec.getLsbD_and, BitVec.getLsbD_or, BitVec.getLsbD_shiftLeft,
      BitVec.getLsbD_ushiftRight, BitVec.getLsbD_ofNat]

theorem suppression_bit_set (w : Word) : suppress w &&& 0x00400000 = 0x00400000 := by
  try simp only [simple_is_bit] at *
  cases hbit : w.getLsbD 31
  all_goals
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals simp_all [simple_is_bit, suppress, setNoEmphasis, convert, common, makeSimple, glyphId, advance,
      BitVec.getLsbD_and, BitVec.getLsbD_or, BitVec.getLsbD_shiftLeft,
      BitVec.getLsbD_ushiftRight, BitVec.getLsbD_ofNat]

theorem suppressed_is_complex (w : Word) : simple (suppress w) = false := by
  rw [simple_is_bit]
  simp only [suppress, simple_is_bit]
  split
  next h => simp [setNoEmphasis, convert, common]
  next h => simpa [setNoEmphasis] using Bool.eq_false_iff.mpr h

theorem converted_count_and_starts (w : Word) (h : simple w = true) :
    suppress w &&& 0x0007ffff = 0x00010001 := by
  try simp only [simple_is_bit] at *
  cases hbit : w.getLsbD 31
  all_goals
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals simp_all [simple_is_bit, suppress, setNoEmphasis, convert, common, makeSimple, glyphId, advance,
      BitVec.getLsbD_and, BitVec.getLsbD_or, BitVec.getLsbD_shiftLeft,
      BitVec.getLsbD_ushiftRight, BitVec.getLsbD_ofNat]

theorem suppression_idempotent (w : Word) : suppress (suppress w) = suppress w := by
  try simp only [simple_is_bit] at *
  cases hbit : w.getLsbD 31
  all_goals
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals simp_all [simple_is_bit, suppress, setNoEmphasis, convert, common, makeSimple, glyphId, advance,
      BitVec.getLsbD_and, BitVec.getLsbD_or, BitVec.getLsbD_shiftLeft,
      BitVec.getLsbD_ushiftRight, BitVec.getLsbD_ofNat]

theorem original_common_mutant :
    suppress 0xe07b01c8 ≠ (0x00410001 : Word) := by decide +kernel

end Emphasis.Raw
