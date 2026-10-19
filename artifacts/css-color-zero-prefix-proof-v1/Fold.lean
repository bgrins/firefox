import Std
import Init.Data.Rat.Lemmas

namespace ZeroPrefix

structure Item (C : Type) where
  color : C
  weight : Rat
  deriving DecidableEq

def specPair (interpolate : C → C → Rat → C) (a b : Item C) : Item C :=
  let total := a.weight + b.weight
  let progress := if 0 < total then b.weight / total else 1/2
  ⟨interpolate a.color b.color progress, total⟩

def specStack (interpolate : C → C → Rat → C) : List (Item C) → Option (Item C)
  | [] => none
  | [a] => some a
  | a :: b :: rest => specStack interpolate (specPair interpolate a b :: rest)
termination_by items => items.length

def nativeStep (mix : C → Rat → C → Rat → C) (normalize : Bool)
    (a b : Item C) : Item C :=
  let combined := a.weight + b.weight
  if !normalize && combined == 0 then a
  else
    let weights := if normalize then
      if combined == 0 then ((1/2 : Rat), (1/2 : Rat))
      else (a.weight / combined, b.weight / combined)
    else (a.weight, b.weight)
    ⟨mix a.color weights.1 b.color weights.2, combined⟩

def oldStep (mix : C → Rat → C → Rat → C) (normalize : Bool)
    (a b : Item C) : Item C :=
  let combined := a.weight + b.weight
  if combined == 0 then a
  else
    let weights := if normalize then
      (a.weight / combined, b.weight / combined)
    else (a.weight, b.weight)
    ⟨mix a.color weights.1 b.color weights.2, combined⟩

def nativeFold (mix : C → Rat → C → Rat → C) (normalize : Bool)
    (a : Item C) (rest : List (Item C)) : Item C :=
  rest.foldl (nativeStep mix normalize) a

def Nonnegative (a : Item C) : Prop := 0 ≤ a.weight

def Compatible (mix : C → Rat → C → Rat → C)
    (interpolate : C → C → Rat → C) : Prop :=
  ∀ a b p, mix a (1-p) b p = interpolate a b p

theorem complementary_ratio (a b : Rat) (h : a+b ≠ 0) :
    1-b/(a+b) = a/(a+b) := by
  have h1 : (a/(a+b))*(a+b)=a := Rat.div_mul_cancel h
  have h2 : (b/(a+b))*(a+b)=b := Rat.div_mul_cancel h
  grind

theorem step_refinement (mix : C → Rat → C → Rat → C)
    (interpolate : C → C → Rat → C) (compat : Compatible mix interpolate)
    (a b : Item C) (ha : Nonnegative a) (hb : Nonnegative b) :
    nativeStep mix true a b = specPair interpolate a b := by
  have nonneg : 0 ≤ a.weight + b.weight := Rat.add_nonneg ha hb
  by_cases zero : a.weight + b.weight = 0
  · have notpos : ¬0 < a.weight + b.weight := by rw [zero]; decide
    simp only [nativeStep, Bool.not_true, Bool.false_and, Bool.false_eq_true,
      ↓reduceIte, beq_iff_eq, zero, specPair]
    simp only [show ¬(0 : Rat) < 0 by decide +kernel, ↓reduceIte]
    have half : (1 : Rat) - 1/2 = 1/2 := by decide +kernel
    have eq := compat a.color b.color (1/2)
    rw [half] at eq
    rw [eq]
  · have pos : 0 < a.weight + b.weight := Rat.lt_of_le_of_ne nonneg (Ne.symm zero)
    simp only [nativeStep, Bool.not_true, Bool.false_and, Bool.false_eq_true,
      ↓reduceIte, beq_iff_eq, zero, specPair, pos]
    rw [← complementary_ratio a.weight b.weight zero, compat]

theorem step_nonnegative (interpolate : C → C → Rat → C)
    (a b : Item C) (ha : Nonnegative a) (hb : Nonnegative b) :
    Nonnegative (specPair interpolate a b) := Rat.add_nonneg ha hb

theorem fold_refinement (mix : C → Rat → C → Rat → C)
    (interpolate : C → C → Rat → C) (compat : Compatible mix interpolate)
    (a : Item C) (rest : List (Item C)) (ha : Nonnegative a)
    (hr : ∀ b ∈ rest, Nonnegative b) :
    some (nativeFold mix true a rest) = specStack interpolate (a :: rest) := by
  induction rest generalizing a with
  | nil => simp [nativeFold, specStack]
  | cons b rest ih =>
    have hb := hr b (by simp)
    have tail : ∀ c ∈ rest, Nonnegative c := fun c hc => hr c (by simp [hc])
    simp only [nativeFold, List.foldl_cons, specStack]
    rw [step_refinement mix interpolate compat a b ha hb]
    exact ih _ (step_nonnegative interpolate a b ha hb) tail

theorem zero_prefix_retains_zero (mix : C → Rat → C → Rat → C)
    (a b : Item C) (zero : a.weight + b.weight = 0) :
    nativeStep mix true a b = ⟨mix a.color (1/2) b.color (1/2), 0⟩ := by
  simp [nativeStep, zero]

theorem positive_step_unchanged (mix : C → Rat → C → Rat → C)
    (a b : Item C) (nonzero : a.weight + b.weight ≠ 0) :
    nativeStep mix true a b = oldStep mix true a b := by
  simp [nativeStep, oldStep, nonzero]

theorem raw_step_unchanged (mix : C → Rat → C → Rat → C) (a b : Item C) :
    nativeStep mix false a b = oldStep mix false a b := by
  simp [nativeStep, oldStep]

theorem raw_fold_unchanged (mix : C → Rat → C → Rat → C)
    (a : Item C) (rest : List (Item C)) :
    nativeFold mix false a rest = rest.foldl (oldStep mix false) a := by
  simp only [nativeFold]
  have eq : nativeStep mix false = oldStep mix false := funext fun x => funext fun y => raw_step_unchanged mix x y
  rw [eq]

def specChannel (a b : Option Rat) (p : Rat) : Option Rat :=
  match a, b with
  | none, none => none
  | some x, none => some x
  | none, some y => some y
  | some x, some y => some (x + (y-x)*p)

def nativeChannel (a : Option Rat) (wa : Rat) (b : Option Rat) (wb : Rat) : Option Rat :=
  match a, b with
  | none, none => none
  | some x, none => some (x*wa+x*wb)
  | none, some y => some (y*wa+y*wb)
  | some x, some y => some (x*wa+y*wb)

theorem channel_compatible : Compatible nativeChannel specChannel := by
  intro a b p
  cases a <;> cases b <;> simp only [nativeChannel, specChannel, Option.some.injEq] <;> grind

theorem channel_fold (a : Item (Option Rat)) (rest : List (Item (Option Rat)))
    (ha : Nonnegative a) (hr : ∀ b ∈ rest, Nonnegative b) :
    some (nativeFold nativeChannel true a rest) = specStack specChannel (a :: rest) :=
  fold_refinement nativeChannel specChannel channel_compatible a rest ha hr

def red : Item (Option Rat) := ⟨some 1, 0⟩
def green : Item (Option Rat) := ⟨some 0, 0⟩
def missing : Item (Option Rat) := ⟨none, 1⟩

theorem forward_witness :
    (nativeFold nativeChannel true red [green, missing]).color = some (1/2) ∧
    ([green, missing].foldl (oldStep nativeChannel true) red).color = some 1 := by decide +kernel

theorem reverse_witness :
    (nativeFold nativeChannel true green [red, missing]).color = some (1/2) ∧
    ([red, missing].foldl (oldStep nativeChannel true) green).color = some 0 := by decide +kernel

theorem numeric_final :
    (nativeFold nativeChannel true red [green, ⟨some (1/4), 1⟩]).color = some (1/4) := by decide +kernel

theorem repeated_zero_prefix :
    (nativeFold nativeChannel true red [green, green, missing]).color = some (1/4) := by decide +kernel

theorem alpha_carry :
    (nativeFold nativeChannel true ⟨some (1/4), 0⟩ [⟨some (3/4), 0⟩, missing]).color =
      some (1/2) := by decide +kernel

theorem missing_prefix :
    (nativeFold nativeChannel true ⟨none, 0⟩ [red, missing]).color = some 1 := by decide +kernel

theorem raw_cancellation :
    (nativeFold nativeChannel false ⟨some 1, -1⟩ [⟨some 0, 1⟩]).color = some 1 := by
  decide +kernel

#print axioms complementary_ratio
#print axioms step_refinement
#print axioms step_nonnegative
#print axioms fold_refinement
#print axioms zero_prefix_retains_zero
#print axioms positive_step_unchanged
#print axioms raw_step_unchanged
#print axioms raw_fold_unchanged
#print axioms channel_compatible
#print axioms channel_fold
#print axioms forward_witness
#print axioms reverse_witness
#print axioms numeric_final
#print axioms repeated_zero_prefix
#print axioms alpha_carry
#print axioms missing_prefix
#print axioms raw_cancellation
end ZeroPrefix
