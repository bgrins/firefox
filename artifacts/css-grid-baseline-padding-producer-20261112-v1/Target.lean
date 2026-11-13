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
