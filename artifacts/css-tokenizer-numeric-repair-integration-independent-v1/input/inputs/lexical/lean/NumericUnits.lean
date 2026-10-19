import NumericReads
namespace NumericUnits
open NumericDigits

def lower (b : Byte) : Nat := if 65 ≤ b.val ∧ b.val ≤ 90 then b.val+32 else b.val

def caseless (xs : List Byte) (unit : List Nat) : Bool :=
  match xs,unit with
  | [],[] => true
  | x::xs,u::us => (lower x == u) && caseless xs us
  | _,_ => false

def nativeFlags (xs : List Byte) : Nat :=
  if caseless xs [108,104] then 5
  else if caseless xs [101,109] || caseless xs [101,120] || caseless xs [99,97,112] ||
      caseless xs [99,104] || caseless xs [105,99] then 1
  else if caseless xs [114,108,104] then 10
  else if caseless xs [114,101,109] || caseless xs [114,101,120] || caseless xs [114,99,104] ||
      caseless xs [114,99,97,112] || caseless xs [114,105,99] then 2
  else 0

def referenceFlags (xs : List Nat) : Nat :=
  match xs with
  | [108,104] => 5
  | [101,109] | [101,120] | [99,97,112] | [99,104] | [105,99] => 1
  | [114,108,104] => 10
  | [114,101,109] | [114,101,120] | [114,99,104] | [114,99,97,112] | [114,105,99] => 2
  | _ => 0

theorem caseless_fold (xs : List Byte) (unit : List Nat) :
    caseless xs unit = decide (xs.map lower = unit) := by
  induction xs generalizing unit with
  | nil => cases unit <;> rfl
  | cons x xs ih => cases unit with
    | nil => rfl
    | cons u us =>
      apply Bool.eq_iff_iff.mpr
      simp [caseless,ih]

theorem classifier (xs : List Byte) : nativeFlags xs = referenceFlags (xs.map lower) := by
  simp only [nativeFlags,caseless_fold,decide_eq_true_eq,Bool.or_eq_true,decide_eq_true_eq]
  generalize xs.map lower = s
  split
  · rename_i h; simp [h,referenceFlags]
  · split
    · rename_i h
      rcases h with (((h|h)|h)|h)|h <;> simp [h,referenceFlags]
    · split
      · rename_i h; simp [h,referenceFlags]
      · split
        · rename_i h
          rcases h with (((h|h)|h)|h)|h <;> simp [h,referenceFlags]
        · rename_i h1 h2 h3 h4
          unfold referenceFlags
          split <;> simp_all

 def tokenFlags (r : NumericToken.Result) : Nat :=
  if r.kind = .dimension then nativeFlags r.unit else 0

theorem dimension_decoded (xs : List Byte) (h : (NumericToken.native xs).kind = .dimension) :
    tokenFlags (NumericToken.native xs) =
      referenceFlags ((SemanticName.reference (NumericLexical.native xs).rest).output.map lower) := by
  simp only [tokenFlags,h,ite_true,NumericToken.dimension_unit xs h]
  exact classifier _

theorem nondimension_zero (r : NumericToken.Result) (h : r.kind ≠ .dimension) : tokenFlags r = 0 := by
  simp [tokenFlags,h]

theorem flag_range (xs : List Byte) : nativeFlags xs = 0 ∨ nativeFlags xs = 1 ∨
    nativeFlags xs = 2 ∨ nativeFlags xs = 5 ∨ nativeFlags xs = 10 := by
  simp only [classifier]
  unfold referenceFlags
  split <;> simp

#print axioms caseless_fold
#print axioms classifier
#print axioms dimension_decoded
#print axioms nondimension_zero
#print axioms flag_range
end NumericUnits
