import NumericParts
namespace NumericLexical
open NumericDigits NumericEntry NumericParts

structure Result where
  text : List Byte
  rest : List Byte
  integralDigits : List Byte
  fractionalDigits : List Byte
  exponentDigits : List Byte
  hasSign : Bool
  negative : Bool
  exponentNegative : Bool
  isInteger : Bool
  deriving DecidableEq, Repr

def signText (xs : List Byte) : List Byte := if NumericEntry.hasSign xs then xs.take 1 else []

def native (xs : List Byte) : Result :=
  let integral := scan (stripSign xs)
  let frac := fraction integral.rest
  let expo := exponent frac.rest
  ⟨signText xs ++ integral.digits ++ frac.text ++ expo.text,expo.rest,
   integral.digits,frac.digits,expo.digits,NumericEntry.hasSign xs,
   xs.head?.any (fun b => b.val == 45),expo.negative,!frac.used && !expo.used⟩

def reference (xs : List Byte) : Result :=
  let body := stripSign xs
  let ints := picked body
  let frac := refFraction (body.drop ints.length)
  let expo := refExponent frac.rest
  ⟨signText xs ++ ints ++ frac.text ++ expo.text,expo.rest,
   ints,frac.digits,expo.digits,NumericEntry.hasSign xs,
   xs.head?.any (fun b => b.val == 45),expo.negative,!frac.used && !expo.used⟩

theorem native_reference (xs : List Byte) : native xs = reference xs := by
  simp [native,reference,NumericDigits.exact_suffix,digits_picked,fraction_reference,exponent_reference]

theorem cover (xs : List Byte) : (native xs).text ++ (native xs).rest = xs := by
  simp only [native,List.append_assoc]
  rw [exponent_cover,fraction_cover,NumericDigits.cover]
  exact signed_cover xs

theorem count_bound (xs : List Byte) : (native xs).text.length ≤ xs.length := by
  have h := congrArg List.length (cover xs)
  simp only [List.length_append] at h
  omega

theorem exact_suffix (xs : List Byte) : (native xs).rest = xs.drop (native xs).text.length := by
  have h := cover xs
  calc (native xs).rest = ((native xs).text ++ (native xs).rest).drop (native xs).text.length := by simp
       _ = _ := by rw [h]

theorem frac_active_nonempty (xs : List Byte) (h : dotDigit xs = true) :
    (fraction xs).text ≠ [] := by
  have he := fraction_entry xs h
  cases xs with
  | nil => simp at he
  | cons b bs => simp [fraction,h]

theorem scan_empty_rest (xs : List Byte) (h : (scan xs).digits = []) : (scan xs).rest = xs := by
  simpa [h] using NumericDigits.cover xs

theorem positive (xs : List Byte) (h : nativeStart xs = true) : 0 < (native xs).text.length := by
  have he := entry_first_digit_or_fraction xs h
  by_cases hi : (scan (stripSign xs)).digits = []
  · have hr := scan_empty_rest _ hi
    have hd : (stripSign xs).head?.any digit = false := by
      have hp : picked (stripSign xs) = [] := by simpa [digits_picked] using hi
      have hn := picked_nonempty (stripSign xs)
      simp [hp] at hn
      simpa using hn
    have hf : dotDigit (stripSign xs) = true := by simpa [hd] using he
    have ht := frac_active_nonempty _ hf
    have hl : 0 < (fraction (stripSign xs)).text.length := List.length_pos_iff.mpr ht
    simp only [native,List.length_append]
    rw [hr]
    omega
  · have hl : 0 < (scan (stripSign xs)).digits.length := List.length_pos_iff.mpr hi
    simp only [native,List.length_append]
    omega

theorem fraction_ascii (xs : List Byte) : ∀ b ∈ (fraction xs).text, b.val < 128 := by
  unfold fraction
  split
  · rename_i h
    cases xs with
    | nil => simp [dotDigit] at h
    | cons c cs =>
      have hc : c.val = 46 := by cases cs <;> simp_all [dotDigit]
      simp only [List.take_succ_cons,List.take_zero,List.drop_succ_cons,List.drop_zero,List.singleton_append,List.mem_cons]
      intro b hb
      rcases hb with rfl | hb
      · omega
      · exact digit_ascii b (consumed_digits cs b hb)
  · simp [emptyPart]

theorem sign_ascii (xs : List Byte) : ∀ b ∈ signText xs, b.val < 128 := by
  cases xs with
  | nil => simp [signText]
  | cons c cs =>
    by_cases hs : signByte c = true
    · simp only [signText,NumericEntry.hasSign,List.head?_cons,Option.any_some,hs,↓reduceIte,
        List.take_succ_cons,List.take_zero,List.mem_singleton]
      intro b hb
      subst b
      simp [signByte] at hs
      omega
    · simp [signText,NumericEntry.hasSign,hs]

theorem exponent_ascii (xs : List Byte) : ∀ b ∈ (exponent xs).text, b.val < 128 := by
  unfold exponent
  split
  · rename_i h
    cases xs with
    | nil => simp [exponentGuard] at h
    | cons c cs =>
      have hc : c.val = 69 ∨ c.val = 101 := by cases cs <;> simp_all [exponentGuard,exponentByte]
      simp only [List.take_succ_cons,List.take_zero,List.drop_succ_cons,List.drop_zero,List.singleton_append,List.mem_cons,List.mem_append]
      intro b hb
      rcases hb with (rfl | hb) | hb
      · omega
      · exact sign_ascii cs b hb
      · exact digit_ascii b (consumed_digits (stripSign cs) b hb)
  · simp [emptyPart]

theorem consumed_ascii (xs : List Byte) : ∀ b ∈ (native xs).text, b.val < 128 := by
  simp only [native,List.mem_append]
  intro b hb
  rcases hb with ((hb | hb) | hb) | hb
  · exact sign_ascii xs b hb
  · exact digit_ascii b (consumed_digits (stripSign xs) b hb)
  · exact fraction_ascii _ b hb
  · exact exponent_ascii _ b hb

#print axioms native_reference
#print axioms cover
#print axioms count_bound
#print axioms exact_suffix
#print axioms positive
#print axioms fraction_ascii
#print axioms sign_ascii
#print axioms exponent_ascii
#print axioms consumed_ascii
end NumericLexical
