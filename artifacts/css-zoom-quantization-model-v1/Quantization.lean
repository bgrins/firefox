import Init

namespace ZoomQuantization

abbrev Positive := { value : Int // 0 < value }

structure Length where
  numerator : Int
  denominator : Positive

structure Zoom where
  numerator : Positive
  denominator : Positive

def rawNumerator (length : Length) (zoom : Zoom) : Int :=
  length.numerator * zoom.numerator.val * 60

def rawDenominator (length : Length) (zoom : Zoom) : Int :=
  length.denominator.val * zoom.denominator.val

def quantize (length : Length) (zoom : Zoom) : Int :=
  (rawNumerator length zoom).tdiv (rawDenominator length zoom)

theorem raw_denominator_positive (length : Length) (zoom : Zoom) :
    0 < rawDenominator length zoom :=
  Int.mul_pos length.denominator.property zoom.denominator.property

def normalize (raw : Int) (zoom : Zoom) : Length :=
  ⟨raw * zoom.denominator.val,
   ⟨60 * zoom.numerator.val, Int.mul_pos (by decide) zoom.numerator.property⟩⟩

def crossError (exact approximation : Length) : Int :=
  exact.numerator * approximation.denominator.val -
    approximation.numerator * exact.denominator.val

theorem error_is_signed_remainder (length : Length) (zoom : Zoom) :
    crossError length (normalize (quantize length zoom) zoom) =
      (rawNumerator length zoom).tmod (rawDenominator length zoom) := by
  simp only [crossError, normalize, quantize, Int.tmod_def,
    rawNumerator, rawDenominator, Int.mul_comm, Int.mul_assoc]

theorem normalized_error_bound (length : Length) (zoom : Zoom) :
    (crossError length (normalize (quantize length zoom) zoom)).natAbs <
      (rawDenominator length zoom).natAbs := by
  rw [error_is_signed_remainder, Int.natAbs_tmod]
  exact Nat.mod_lt _ (Int.natAbs_pos.mpr (Int.ne_of_gt
    (raw_denominator_positive length zoom)))

theorem exact_iff_no_remainder (length : Length) (zoom : Zoom) :
    crossError length (normalize (quantize length zoom) zoom) = 0 ↔
      rawDenominator length zoom ∣ rawNumerator length zoom := by
  rw [error_is_signed_remainder]
  exact Int.dvd_iff_tmod_eq_zero.symm

theorem nonnegative_error_for_nonnegative_length (length : Length) (zoom : Zoom)
    (nonnegative : 0 ≤ length.numerator) :
    0 ≤ crossError length (normalize (quantize length zoom) zoom) := by
  rw [error_is_signed_remainder]
  apply Int.tmod_nonneg
  exact Int.mul_nonneg (Int.mul_nonneg nonnegative
    (Int.le_of_lt zoom.numerator.property)) (by decide)

def negate (length : Length) : Length :=
  ⟨-length.numerator, length.denominator⟩

theorem quantization_preserves_sign_symmetry (length : Length) (zoom : Zoom) :
    quantize (negate length) zoom = -quantize length zoom := by
  simp only [quantize, rawNumerator, rawDenominator, negate,
    Int.neg_mul, Int.neg_tdiv]

theorem error_preserves_sign_symmetry (length : Length) (zoom : Zoom) :
    crossError (negate length) (normalize (quantize (negate length) zoom) zoom) =
      -crossError length (normalize (quantize length zoom) zoom) := by
  rw [error_is_signed_remainder, error_is_signed_remainder]
  simp only [rawNumerator, rawDenominator, negate, Int.neg_mul, Int.neg_tmod]

def tiny : Length := ⟨13, ⟨100, by decide⟩⟩
def one : Zoom := ⟨⟨1, by decide⟩, ⟨1, by decide⟩⟩
def oneAndHalf : Zoom := ⟨⟨3, by decide⟩, ⟨2, by decide⟩⟩
def half : Zoom := ⟨⟨1, by decide⟩, ⟨2, by decide⟩⟩

theorem fractional_witness : quantize tiny oneAndHalf = 11 ∧
    crossError tiny (normalize (quantize tiny oneAndHalf) oneAndHalf) = 140 := by
  decide +kernel

theorem half_zoom_witness : quantize tiny half = 3 ∧
    crossError tiny (normalize (quantize tiny half) half) = 180 := by
  decide +kernel

theorem quantization_does_not_commute_with_zoom :
    crossError (normalize (quantize tiny one) one)
      (normalize (quantize tiny oneAndHalf) oneAndHalf) ≠ 0 := by
  decide +kernel

end ZoomQuantization
