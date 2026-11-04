import Std
namespace ShadowOrder
set_option maxRecDepth 4096
set_option maxHeartbeats 800000

def maxOrder : Nat := 134217727
structure Fields where
  origin : Nat
  important : Bool
  magnitude : Nat
  negative : Bool
  deriving DecidableEq, Repr

def Fields.admitted (f : Fields) : Prop :=
  f.origin < 8 ∧ f.magnitude ≤ maxOrder ∧ (f.magnitude = 0 → f.negative = false)

def boolNat (b : Bool) : Nat := if b then 1 else 0

def pack (f : Fields) : Nat :=
  f.origin + 8 * boolNat f.important + 16 * f.magnitude + 2147483648 * boolNat f.negative

def unpack (word : Nat) : Fields :=
  ⟨word % 8, word / 8 % 2 = 1, word / 16 % 134217728, word / 2147483648 % 2 = 1⟩

def signed (f : Fields) : Int :=
  if f.negative then -(Int.ofNat f.magnitude) else Int.ofNat f.magnitude

theorem pack_bounded (f : Fields) (h : f.admitted) : pack f < 4294967296 := by
  rcases f with ⟨origin, important, magnitude, negative⟩
  simp only [Fields.admitted, maxOrder] at h
  cases important <;> cases negative <;> simp [pack, boolNat] <;> omega

theorem unpack_pack (f : Fields) (h : f.admitted) : unpack (pack f) = f := by
  rcases f with ⟨origin, important, magnitude, negative⟩
  simp only [Fields.admitted, maxOrder] at h
  cases important <;> cases negative <;> simp [pack, unpack, boolNat, Fields.mk.injEq] <;> omega

theorem pack_injective (a b : Fields) (ha : a.admitted) (hb : b.admitted)
    (h : pack a = pack b) : a = b := by
  have := congrArg unpack h
  simpa [unpack_pack a ha, unpack_pack b hb] using this

def inner (limit index : Nat) : Option Int :=
  if index < limit then some (-Int.ofNat (index+1)) else none

def checkedInner (usizeMax limit index : Nat) : Option Int :=
  if index < usizeMax then
    if index+1 ≤ limit then some (-Int.ofNat (index+1)) else none
  else none

theorem checked_inner_refines (limit index wordMax : Nat) (h : limit ≤ wordMax) :
    checkedInner wordMax limit index = inner limit index := by
  simp only [checkedInner, inner]
  by_cases hi : index < limit
  · have hw : index < wordMax := by omega
    simp [hi, hw, show index + 1 ≤ limit by omega]
  · by_cases hw : index < wordMax <;> simp [hi, hw, show ¬index + 1 ≤ limit by omega]

theorem inner_exact (limit index : Nat) (h : index < limit) :
    inner limit index = some (-Int.ofNat (index+1)) := by simp [inner,h]

theorem inner_omitted (limit index : Nat) (h : limit ≤ index) :
    inner limit index = none := by simp [inner, Nat.not_lt.mpr h]

theorem inner_negative (limit index : Nat) (order : Int)
    (h : inner limit index = some order) : order < 0 := by
  unfold inner at h
  split at h <;> simp_all <;> omega

theorem inner_injective (limit i j : Nat) (a : Int)
    (hi : inner limit i = some a) (hj : inner limit j = some a) : i = j := by
  unfold inner at hi hj
  split at hi <;> split at hj <;> simp_all <;> omega

def nextOuter (limit current : Nat) : Option Nat :=
  if current < limit then some (current+1) else none

theorem next_exact (limit current : Nat) (h : current < limit) :
    nextOuter limit current = some (current+1) := by simp [nextOuter,h]

theorem next_bound (limit : Nat) : nextOuter limit limit = none := by simp [nextOuter]

theorem no_signed_overflow (m : Nat) (h : m ≤ maxOrder) :
    -(2147483648 : Int) < -Int.ofNat m ∧ Int.ofNat m < 2147483648 := by
  unfold maxOrder at h
  simp only [Int.ofNat_eq_natCast]
  omega

#print axioms unpack_pack
#print axioms pack_injective
#print axioms checked_inner_refines
#print axioms inner_injective
end ShadowOrder
