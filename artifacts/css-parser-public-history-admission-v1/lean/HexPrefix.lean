import Std
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace HexPrefix
abbrev Byte := Fin 256

def nativeDigit (b : Byte) : Option Nat :=
  if 48 ≤ b.val ∧ b.val ≤ 57 then some (b.val - 48)
  else if 97 ≤ b.val ∧ b.val ≤ 102 then some (b.val - 97 + 10)
  else if 65 ≤ b.val ∧ b.val ≤ 70 then some (b.val - 65 + 10)
  else none

def digitTable : List (Nat × Nat) :=
  [(48,0),(49,1),(50,2),(51,3),(52,4),(53,5),(54,6),(55,7),(56,8),(57,9),
   (65,10),(66,11),(67,12),(68,13),(69,14),(70,15),
   (97,10),(98,11),(99,12),(100,13),(101,14),(102,15)]

def referenceDigit (b : Byte) : Option Nat :=
  (digitTable.find? fun p => p.1 == b.val).map Prod.snd

theorem digit_classification : ∀ b : Byte, nativeDigit b = referenceDigit b := by decide

theorem digit_bound (b : Byte) (d : Nat) (h : nativeDigit b = some d) : d < 16 := by
  unfold nativeDigit at h
  split at h
  · cases h; omega
  · split at h
    · cases h; omega
    · split at h
      · cases h; omega
      · contradiction

structure Result where
  value : Nat
  count : Nat
  rest : List Byte
  deriving DecidableEq, Repr

def run : Nat → List Byte → Nat → Result
  | 0, xs, value => ⟨value,0,xs⟩
  | _+1, [], value => ⟨value,0,[]⟩
  | n+1, b::xs, value =>
    match nativeDigit b with
    | none => ⟨value,0,b::xs⟩
    | some d =>
      let r := run n xs (value*16+d)
      ⟨r.value,r.count+1,r.rest⟩

def selected (fuel : Nat) (xs : List Byte) : List Byte :=
  (xs.takeWhile fun b => (referenceDigit b).isSome).take fuel

def reference (fuel : Nat) (xs : List Byte) (value : Nat) : Result :=
  let picked := selected fuel xs
  ⟨(picked.filterMap referenceDigit).foldl (fun v d => v*16+d) value,
    picked.length, xs.drop picked.length⟩

theorem selected_none (n : Nat) (b : Byte) (xs : List Byte)
    (h : referenceDigit b = none) : selected (n+1) (b::xs) = [] := by
  simp [selected,h]

theorem selected_some (n : Nat) (b : Byte) (xs : List Byte) (d : Nat)
    (h : referenceDigit b = some d) : selected (n+1) (b::xs) = b :: selected n xs := by
  simp [selected,h]

theorem run_reference (fuel : Nat) (xs : List Byte) (value : Nat) :
    run fuel xs value = reference fuel xs value := by
  induction fuel generalizing xs value with
  | zero => simp [run,reference,selected]
  | succ fuel ih =>
    cases xs with
    | nil => simp [run,reference,selected]
    | cons b xs =>
      cases hd : nativeDigit b with
      | none =>
        have hr : referenceDigit b = none := by simpa [digit_classification] using hd
        simp [run,hd,reference,selected_none _ _ _ hr]
      | some d =>
        have hr : referenceDigit b = some d := by simpa [digit_classification] using hd
        simp [run,hd,ih,reference,selected_some _ _ _ _ hr,hr]

theorem selected_length_le (fuel : Nat) (xs : List Byte) :
    (selected fuel xs).length ≤ xs.length ∧ (selected fuel xs).length ≤ fuel := by
  simp only [selected,List.length_take]
  have h : (List.takeWhile (fun b => (referenceDigit b).isSome) xs).length ≤ xs.length := by
    induction xs with
    | nil => simp
    | cons b bs ih =>
      cases hc : (referenceDigit b).isSome <;> simp [hc, ih]
  omega

theorem count_bound (fuel : Nat) (xs : List Byte) (value : Nat) :
    (run fuel xs value).count ≤ xs.length ∧ (run fuel xs value).count ≤ fuel := by
  rw [run_reference]
  exact selected_length_le fuel xs

theorem exact_remainder (fuel : Nat) (xs : List Byte) (value : Nat) :
    (run fuel xs value).rest = xs.drop (run fuel xs value).count := by
  simp [run_reference,reference]

theorem consumed_plus_remaining (fuel : Nat) (xs : List Byte) (value : Nat) :
    (run fuel xs value).count + (run fuel xs value).rest.length = xs.length := by
  rw [exact_remainder,List.length_drop]
  have := (count_bound fuel xs value).1
  omega

theorem value_bound (fuel : Nat) (xs : List Byte) (initial : Nat) :
    (run fuel xs initial).value < (initial+1) * 16^fuel := by
  induction fuel generalizing xs initial with
  | zero => simp [run]
  | succ fuel ih =>
    have hp : 1 ≤ 16^(fuel+1) := Nat.one_le_pow _ _ (by decide)
    have hi : initial+1 ≤ (initial+1)*16^(fuel+1) := by
      calc initial+1 = (initial+1)*1 := by omega
           _ ≤ _ := Nat.mul_le_mul_left _ hp
    cases xs with
    | nil => simp only [run]; omega
    | cons b bs =>
      cases hd : nativeDigit b with
      | none => simp only [run,hd]; omega
      | some d =>
        have hb := digit_bound b d hd
        have hm : initial*16+d+1 ≤ (initial+1)*16 := by omega
        simp only [run,hd]
        calc (run fuel bs (initial*16+d)).value < (initial*16+d+1)*16^fuel := ih _ _
             _ ≤ ((initial+1)*16)*16^fuel := Nat.mul_le_mul_right _ hm
             _ = (initial+1)*16^(fuel+1) := by rw [Nat.pow_succ]; ac_rfl

theorem six_digits_u32 (xs : List Byte) : (run 6 xs 0).value < 4294967296 := by
  have h := value_bound 6 xs 0
  change (run 6 xs 0).value < 16777216 at h
  omega

#print axioms value_bound
#print axioms six_digits_u32
example : (run 6 [48,48,48,48,54,49,66] 0) = ⟨97,6,[66]⟩ := by decide
example : (run 6 [49,103] 0) = ⟨1,1,[103]⟩ := by decide
example : (run 6 [102,102,102,102,102,102] 0).value = 16777215 := by decide

#print axioms digit_classification
#print axioms digit_bound
#print axioms run_reference
#print axioms count_bound
#print axioms exact_remainder
#print axioms consumed_plus_remaining
end HexPrefix
