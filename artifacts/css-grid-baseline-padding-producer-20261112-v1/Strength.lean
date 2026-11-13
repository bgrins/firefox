import Lean.Elab.Tactic.Omega

namespace BaselinePadding

def inCoord (x : Int) : Prop := -2147483648 ≤ x ∧ x ≤ 2147483647

def encode (offset : Int) (content last : Bool) : Int :=
  let adjustment := if content then offset else 0
  if adjustment < 0 then 0 else if last then -adjustment else adjustment

def stored (offset : Int) (content last : Bool) : Option Int :=
  let value := encode offset content last
  if value = 0 then none else some value

def magnitude (value : Int) : Int := if value > 0 then value else -value

structure Obligations : Prop where
  encoded_range : ∀ offset content last, inCoord offset →
    -2147483647 ≤ encode offset content last ∧ encode offset content last ≤ 2147483647
  stored_not_min : ∀ offset content last value, inCoord offset →
    stored offset content last = some value → value ≠ -2147483648
  stored_nonzero : ∀ offset content last value,
    stored offset content last = some value → value ≠ 0
  no_content : ∀ offset last, stored offset false last = none
  nonpositive_removed : ∀ offset content last, offset ≤ 0 →
    stored offset content last = none
  positive_first : ∀ offset, 0 < offset → stored offset true false = some offset
  positive_last : ∀ offset, 0 < offset → stored offset true true = some (-offset)
  magnitude_range : ∀ offset content last, inCoord offset →
    0 ≤ magnitude (encode offset content last) ∧
      magnitude (encode offset content last) ≤ 2147483647
  padding_side_range : ∀ offset content last padding,
    inCoord offset → inCoord padding →
    -2147483648 ≤ padding + magnitude (encode offset content last) ∧
      padding + magnitude (encode offset content last) ≤ 4294967294
  border_padding_side_range : ∀ offset content last padding border,
    inCoord offset → inCoord padding → inCoord border →
    -4294967296 ≤ border + padding + magnitude (encode offset content last) ∧
      border + padding + magnitude (encode offset content last) ≤ 6442450941
  border_padding_axis_range : ∀ offset content last pStart pEnd bStart bEnd,
    inCoord offset → inCoord pStart → inCoord pEnd → inCoord bStart → inCoord bEnd →
    -8589934592 ≤ pStart + pEnd + bStart + bEnd + magnitude (encode offset content last) ∧
      pStart + pEnd + bStart + bEnd + magnitude (encode offset content last) ≤ 10737418235
  nonnegative_side : ∀ offset content last padding,
    0 ≤ padding → 0 ≤ padding + magnitude (encode offset content last)
  border_reconstruction : ∀ (padding border delta : Int),
    (border + (padding + delta)) - (padding + delta) = border
  largest_last_witness : inCoord 2147483647 ∧
    stored 2147483647 true true = some (-2147483647) ∧
    magnitude (-2147483647) = 2147483647
  smallest_removed_witness : inCoord (-2147483648) ∧
    stored (-2147483648) true true = none
  addition_overflow_witness : inCoord 2147483647 ∧ inCoord 1 ∧
    stored 1 true false = some 1 ∧
    ¬ inCoord (2147483647 + magnitude (encode 1 true false))

end BaselinePadding

namespace BaselinePadding

theorem encoded_range : ∀ offset content last, inCoord offset →
    -2147483647 ≤ encode offset content last ∧ encode offset content last ≤ 2147483647 := by
  intro offset content last h
  unfold inCoord at h
  cases content <;> cases last <;> simp only [encode, Bool.false_eq_true, ↓reduceIte]
  all_goals split <;> omega

theorem stored_not_min : ∀ offset content last value, inCoord offset →
    stored offset content last = some value → value ≠ -2147483648 := by
  intro offset content last value h hs
  have bounds := encoded_range offset content last h
  simp only [stored] at hs
  split at hs
  · cases hs
  · have eq := Option.some.inj hs
    omega

theorem stored_nonzero : ∀ offset content last value,
    stored offset content last = some value → value ≠ 0 := by
  intro offset content last value hs
  simp only [stored] at hs
  split at hs
  · cases hs
  · have eq := Option.some.inj hs
    omega

theorem no_content : ∀ offset last, stored offset false last = none := by
  intro offset last
  simp [stored, encode]

theorem nonpositive_removed : ∀ offset content last, offset ≤ 0 →
    stored offset content last = none := by
  intro offset content last h
  cases content <;> cases last <;> simp [stored, encode]
  all_goals omega

theorem positive_first : ∀ offset, 0 < offset → stored offset true false = some offset := by
  intro offset h
  simp [stored, encode, show ¬offset < 0 from by omega, show offset ≠ 0 from by omega]

theorem positive_last : ∀ offset, 0 < offset → stored offset true true = some (-offset) := by
  intro offset h
  simp [stored, encode, show ¬offset < 0 from by omega, show offset ≠ 0 from by omega]

theorem magnitude_range : ∀ offset content last, inCoord offset →
    0 ≤ magnitude (encode offset content last) ∧
      magnitude (encode offset content last) ≤ 2147483647 := by
  intro offset content last h
  have bounds := encoded_range offset content last h
  unfold magnitude
  split <;> omega

theorem padding_side_range : ∀ offset content last padding,
    inCoord offset → inCoord padding →
    -2147483648 ≤ padding + magnitude (encode offset content last) ∧
      padding + magnitude (encode offset content last) ≤ 4294967294 := by
  intro offset content last padding ho hp
  have bounds := magnitude_range offset content last ho
  unfold inCoord at hp
  omega

theorem border_padding_side_range : ∀ offset content last padding border,
    inCoord offset → inCoord padding → inCoord border →
    -4294967296 ≤ border + padding + magnitude (encode offset content last) ∧
      border + padding + magnitude (encode offset content last) ≤ 6442450941 := by
  intro offset content last padding border ho hp hb
  have bounds := magnitude_range offset content last ho
  unfold inCoord at hp hb
  omega

theorem border_padding_axis_range : ∀ offset content last pStart pEnd bStart bEnd,
    inCoord offset → inCoord pStart → inCoord pEnd → inCoord bStart → inCoord bEnd →
    -8589934592 ≤ pStart + pEnd + bStart + bEnd + magnitude (encode offset content last) ∧
      pStart + pEnd + bStart + bEnd + magnitude (encode offset content last) ≤ 10737418235 := by
  intro offset content last pStart pEnd bStart bEnd ho hps hpe hbs hbe
  have bounds := magnitude_range offset content last ho
  unfold inCoord at hps hpe hbs hbe
  omega

theorem nonnegative_side : ∀ offset content last padding,
    0 ≤ padding → 0 ≤ padding + magnitude (encode offset content last) := by
  intro offset content last padding hp
  unfold magnitude
  split <;> omega

theorem border_reconstruction : ∀ (padding border delta : Int),
    (border + (padding + delta)) - (padding + delta) = border := by
  intro padding border delta
  omega

theorem largest_last_witness : inCoord 2147483647 ∧
    stored 2147483647 true true = some (-2147483647) ∧
    magnitude (-2147483647) = 2147483647 := by
  unfold inCoord stored encode magnitude
  decide

theorem smallest_removed_witness : inCoord (-2147483648) ∧
    stored (-2147483648) true true = none := by
  unfold inCoord stored encode
  decide

theorem addition_overflow_witness : inCoord 2147483647 ∧ inCoord 1 ∧
    stored 1 true false = some 1 ∧
    ¬ inCoord (2147483647 + magnitude (encode 1 true false)) := by
  unfold inCoord stored encode magnitude
  decide

theorem complete : Obligations :=
  ⟨encoded_range, stored_not_min, stored_nonzero, no_content, nonpositive_removed, positive_first, positive_last, magnitude_range, padding_side_range, border_padding_side_range, border_padding_axis_range, nonnegative_side, border_reconstruction, largest_last_witness, smallest_removed_witness, addition_overflow_witness⟩

#print axioms encoded_range
#print axioms stored_not_min
#print axioms stored_nonzero
#print axioms no_content
#print axioms nonpositive_removed
#print axioms positive_first
#print axioms positive_last
#print axioms magnitude_range
#print axioms padding_side_range
#print axioms border_padding_side_range
#print axioms border_padding_axis_range
#print axioms nonnegative_side
#print axioms border_reconstruction
#print axioms largest_last_witness
#print axioms smallest_removed_witness
#print axioms addition_overflow_witness
#print axioms complete

end BaselinePadding

namespace BaselinePadding

def withoutClamp (offset : Int) (content last : Bool) : Int :=
  if content then if last then -offset else offset else 0

def clampAfterSign (offset : Int) (content last : Bool) : Int :=
  max 0 (if content then if last then -offset else offset else 0)

def keepZero (offset : Int) (content last : Bool) : Option Int :=
  some (encode offset content last)

theorem removing_clamp_breaks_range : inCoord (-2147483648) ∧
    ¬ (-2147483647 ≤ withoutClamp (-2147483648) true false ∧
        withoutClamp (-2147483648) true false ≤ 2147483647) := by
  unfold inCoord withoutClamp
  decide

theorem moving_clamp_breaks_last : inCoord 1 ∧
    stored 1 true true = some (-1) ∧
    clampAfterSign 1 true true ≠ encode 1 true true := by
  unfold inCoord stored encode clampAfterSign
  decide

theorem retaining_zero_breaks_presence : inCoord 0 ∧
    stored 0 true true = none ∧ keepZero 0 true true = some 0 := by
  unfold inCoord stored encode keepZero
  decide

#print axioms removing_clamp_breaks_range
#print axioms moving_clamp_breaks_last
#print axioms retaining_zero_breaks_presence

end BaselinePadding
