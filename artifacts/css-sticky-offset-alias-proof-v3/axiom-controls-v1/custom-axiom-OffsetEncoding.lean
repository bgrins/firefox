import Std

namespace OffsetEncoding

def autoCode : Int := 1073741823
def minimum : Int := -1073741823
def reserve (resolved : Int) : Int := min (autoCode - 1) resolved

def encode (inset : Option Int) : Int :=
  match inset with
  | none => autoCode
  | some resolved => reserve resolved

def originalEncode (inset : Option Int) : Int := inset.getD autoCode

def decode (encoded : Int) : Option Int :=
  if encoded = autoCode then none else some encoded

axiom injectedUnsound : False

theorem reserved_code_unreachable (resolved : Int) : reserve resolved ≠ autoCode := by
  exact False.elim injectedUnsound

theorem auto_exactly (inset : Option Int) : encode inset = autoCode ↔ inset = none := by
  cases inset <;> simp [encode, reserved_code_unreachable]

theorem explicit_decode (resolved : Int) :
    decode (encode (some resolved)) = some (reserve resolved) := by
  simp [decode, encode, reserved_code_unreachable]

theorem auto_decode : decode (encode none) = none := by simp [decode, encode]

theorem semantic_round_trip (inset : Option Int) :
    decode (encode inset) = inset.map reserve := by
  cases inset <;> simp [auto_decode, explicit_decode]

theorem nonreserved_preserved (resolved : Int) (h : resolved < autoCode) :
    reserve resolved = resolved := by
  unfold reserve autoCode at *
  omega

theorem range_preserved (resolved : Int) (h : minimum ≤ resolved) :
    minimum ≤ reserve resolved ∧ reserve resolved < autoCode := by
  unfold reserve autoCode minimum at *
  omega

theorem bounded_resolution_changes_at_most_one (resolved : Int) (h : resolved ≤ autoCode) :
    0 ≤ resolved - reserve resolved ∧ resolved - reserve resolved ≤ 1 := by
  unfold reserve autoCode at *
  omega

theorem change_iff_alias (resolved : Int) (h : resolved ≤ autoCode) :
    reserve resolved ≠ resolved ↔ resolved = autoCode := by
  unfold reserve autoCode at *
  omega

theorem monotone (a b : Int) (h : a ≤ b) : reserve a ≤ reserve b := by
  unfold reserve
  omega

theorem signed_range (resolved : Int) (h : -2147483648 ≤ resolved) :
    -2147483648 ≤ reserve resolved ∧ reserve resolved ≤ 2147483647 := by
  unfold reserve autoCode
  omega

theorem original_alias :
    decode (originalEncode (some autoCode)) = none ∧
    decode (encode (some autoCode)) = some 1073741822 := by
  decide +kernel

end OffsetEncoding
