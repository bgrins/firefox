import HexPrefix
namespace Escape
open HexPrefix

def byte (n : Nat) : Byte := ⟨n % 256, Nat.mod_lt _ (by decide)⟩

def encode (n : Nat) : List Byte :=
  if n < 128 then [byte n]
  else if n < 2048 then [byte (192+n/64), byte (128+n%64)]
  else if n < 65536 then [byte (224+n/4096), byte (128+n/64%64),byte (128+n%64)]
  else [byte (240+n/262144),byte (128+n/4096%64),byte (128+n/64%64),byte (128+n%64)]

def nativeScalar (n : Nat) : Nat :=
  if n = 0 then 65533
  else if n > 1114111 ∨ 55296 ≤ n ∧ n ≤ 57343 then 65533 else n

def referenceScalar (n : Nat) : Nat :=
  if 1 ≤ n ∧ n ≤ 1114111 ∧ (n < 55296 ∨ 57344 ≤ n) then n else 65533

theorem scalar_mapping (n : Nat) : nativeScalar n = referenceScalar n := by
  unfold nativeScalar referenceScalar
  split <;> split <;> try omega
  all_goals split <;> omega

def width (b : Byte) : Nat :=
  if b.val < 128 then 1 else if b.val < 224 then 2 else if b.val < 240 then 3 else 4

def nativeWhitespace (xs : List Byte) : Nat :=
  match xs with
  | [] => 0
  | b::bs =>
    if b.val = 32 ∨ b.val = 9 then 1
    else if b.val = 10 ∨ b.val = 12 ∨ b.val = 13 then
      if b.val = 13 ∧ bs.head? = some (byte 10) then 2 else 1
    else 0

def referenceWhitespace (xs : List Byte) : Nat :=
  if xs.take 2 = [byte 13,byte 10] then 2
  else if xs.head?.any (fun b => [9,10,12,13,32].contains b.val) then 1 else 0

theorem whitespace_reference (xs : List Byte) : nativeWhitespace xs = referenceWhitespace xs := by
  cases xs with
  | nil => decide
  | cons b bs =>
    cases bs with
    | nil =>
      simp [nativeWhitespace, referenceWhitespace, byte]
      split <;> split <;> simp_all <;> omega
    | cons c cs =>
      simp [nativeWhitespace, referenceWhitespace, byte, Fin.ext_iff]
      split <;> split <;> simp_all <;> try omega
      all_goals split <;> simp_all <;> omega

theorem whitespace_bound (xs : List Byte) : nativeWhitespace xs ≤ xs.length := by
  cases xs with
  | nil => simp [nativeWhitespace]
  | cons b bs =>
    simp only [nativeWhitespace,List.length_cons]
    split
    · omega
    · split
      · split
        · rename_i h
          cases bs <;> simp_all
        · omega
      · omega

structure Result where
  output : List Byte
  count : Nat
  deriving DecidableEq, Repr

def native (xs : List Byte) : Result :=
  match xs with
  | [] => ⟨encode 65533,0⟩
  | b::_ =>
    match nativeDigit b with
    | some _ =>
      let h := HexPrefix.run 6 xs 0
      ⟨encode (nativeScalar h.value), h.count + nativeWhitespace h.rest⟩
    | none =>
      if b.val = 0 then ⟨encode 65533,1⟩
      else ⟨xs.take (width b), (xs.take (width b)).length⟩

def reference (xs : List Byte) : Result :=
  match xs with
  | [] => ⟨encode 65533,0⟩
  | b::_ =>
    if (referenceDigit b).isSome then
      let h := HexPrefix.reference 6 xs 0
      ⟨encode (referenceScalar h.value), h.count + referenceWhitespace h.rest⟩
    else if b.val = 0 then ⟨encode 65533,1⟩
    else ⟨xs.take (width b), (xs.take (width b)).length⟩

theorem native_reference (xs : List Byte) : native xs = reference xs := by
  cases xs with
  | nil => rfl
  | cons b bs =>
    cases h : nativeDigit b <;>
      simp [native, reference, ← digit_classification, h, HexPrefix.run_reference,
        scalar_mapping, whitespace_reference]

theorem consumption_bound (xs : List Byte) : (native xs).count ≤ xs.length := by
  cases xs with
  | nil => simp [native]
  | cons b bs =>
    simp only [native]
    split
    · have h := HexPrefix.consumed_plus_remaining 6 (b::bs) 0
      have w := whitespace_bound (HexPrefix.run 6 (b::bs) 0).rest
      simp only; omega
    · split
      · simp
      · simp only [List.length_take,List.length_cons]; omega

theorem residual_bound (xs : List Byte) : (xs.drop (native xs).count).length ≤ xs.length := by
  simp

example : native [] = ⟨encode 65533,0⟩ := by decide
example : native [byte 0,byte 65] = ⟨encode 65533,1⟩ := by decide
example : native [byte 54,byte 49,byte 13,byte 10,byte 66] = ⟨encode 97,4⟩ := by decide
example : native [byte 48,byte 48,byte 48,byte 48,byte 54,byte 49,byte 66] = ⟨encode 97,6⟩ := by decide
example : native [byte 100,byte 56,byte 48,byte 48] = ⟨encode 65533,4⟩ := by decide
example : native [byte 195,byte 169,byte 65] = ⟨[byte 195,byte 169],2⟩ := by decide

#print axioms native_reference
#print axioms whitespace_reference
#print axioms scalar_mapping
#print axioms whitespace_bound
#print axioms consumption_bound
#print axioms residual_bound
end Escape
