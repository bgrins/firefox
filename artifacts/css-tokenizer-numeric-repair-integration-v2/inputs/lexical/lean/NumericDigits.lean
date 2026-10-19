import Std
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace NumericDigits
abbrev Byte := Fin 256

def digit (b : Byte) : Bool := 48 ≤ b.val && b.val ≤ 57

def referenceDigit (b : Byte) : Bool :=
  "0123456789".toList.any (fun c => c.toNat == b.val)

theorem classifier : ∀ b : Byte, digit b = referenceDigit b := by decide

theorem digit_ascii (b : Byte) (h : digit b = true) : b.val < 128 := by
  simp [digit] at h
  omega

structure Scan where
  digits : List Byte
  rest : List Byte
  reads : List Nat
  deriving DecidableEq, Repr

def scan : List Byte → Scan
  | [] => ⟨[],[],[]⟩
  | b::bs =>
    if digit b then
      let r := scan bs
      ⟨b::r.digits,r.rest,0::r.reads.map (·+1)⟩
    else ⟨[],b::bs,[0]⟩

def reference (xs : List Byte) : List Byte × List Byte :=
  (xs.takeWhile referenceDigit,xs.dropWhile referenceDigit)

theorem scan_reference (xs : List Byte) :
    ((scan xs).digits,(scan xs).rest) = reference xs := by
  induction xs with
  | nil => rfl
  | cons b bs ih =>
    cases h : digit b <;> simp [scan,h,reference,← classifier] at *
    exact ih

theorem cover (xs : List Byte) : (scan xs).digits ++ (scan xs).rest = xs := by
  have h := scan_reference xs
  have hd := congrArg Prod.fst h
  have hr := congrArg Prod.snd h
  simp only [reference] at hd hr
  rw [hd,hr]
  exact List.takeWhile_append_dropWhile

theorem count_bound (xs : List Byte) : (scan xs).digits.length ≤ xs.length := by
  have h := congrArg List.length (cover xs)
  simp only [List.length_append] at h
  omega

theorem exact_suffix (xs : List Byte) : (scan xs).rest = xs.drop (scan xs).digits.length := by
  have h := cover xs
  calc (scan xs).rest = ((scan xs).digits ++ (scan xs).rest).drop (scan xs).digits.length := by simp
       _ = _ := by rw [h]

theorem consumed_digits (xs : List Byte) : ∀ b ∈ (scan xs).digits, digit b = true := by
  induction xs with
  | nil => simp [scan]
  | cons b bs ih => cases hb : digit b <;> simp_all [scan]

theorem maximal (xs : List Byte) : (scan xs).rest = [] ∨
    ∃ b bs, (scan xs).rest = b::bs ∧ digit b = false := by
  induction xs with
  | nil => simp [scan]
  | cons b bs ih =>
    cases hb : digit b
    · exact Or.inr ⟨b,bs,by simp [scan,hb],hb⟩
    · simpa [scan,hb] using ih

theorem reads_bounded (xs : List Byte) : ∀ i ∈ (scan xs).reads, i < xs.length := by
  induction xs with
  | nil => simp [scan]
  | cons b bs ih =>
    cases hb : digit b <;> simp only [scan,hb,Bool.false_eq_true,↓reduceIte,List.mem_cons,List.mem_singleton,List.not_mem_nil,or_false,List.length_cons]
    · intro i hi; subst i; omega
    · intro i hi
      rcases hi with rfl | hi
      · omega
      · obtain ⟨j,hj,rfl⟩ := List.mem_map.mp hi
        have := ih j hj
        omega

theorem nonempty_first_read (b : Byte) (bs : List Byte) : (scan (b::bs)).reads.head? = some 0 := by
  cases h : digit b <;> simp [scan,h]

#print axioms classifier
#print axioms digit_ascii
#print axioms scan_reference
#print axioms cover
#print axioms count_bound
#print axioms exact_suffix
#print axioms consumed_digits
#print axioms maximal
#print axioms reads_bounded
#print axioms nonempty_first_read
end NumericDigits
