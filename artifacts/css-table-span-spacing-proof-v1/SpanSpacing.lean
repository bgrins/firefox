import Std
set_option autoImplicit false

namespace SpanSpacing

def raw (extent spacing span : Int) : Int :=
  (extent + spacing).tdiv span - spacing

def allocated (extent spacing span : Int) : Int :=
  max 0 (raw extent spacing span)

def finalAllocation (extent spacing span : Int) : Int :=
  let value := raw extent spacing span
  if value < 0 then 0 else value

def minimumContribution (extent spacing span : Int) : Int :=
  if span > 1 then allocated extent spacing span else extent

def leastNonnegativeShare (quotient spacing value : Int) : Prop :=
  0 ≤ value ∧ quotient - spacing ≤ value ∧
    ∀ other, 0 ≤ other → quotient - spacing ≤ other → value ≤ other

def int32 (value : Int) : Prop := -2147483648 ≤ value ∧ value ≤ 2147483647

theorem nonnegative (extent spacing span : Int) :
    0 ≤ allocated extent spacing span := by
  simp only [allocated]
  omega

theorem allocation_matches_final (extent spacing span : Int) :
    allocated extent spacing span = finalAllocation extent spacing span := by
  simp only [allocated, finalAllocation]
  split <;> omega

theorem least_share_contract (extent spacing span : Int)
    (he : 0 ≤ extent) (hs : 0 ≤ spacing) :
    leastNonnegativeShare ((extent + spacing) / span) spacing
      (allocated extent spacing span) := by
  have hn : 0 ≤ extent + spacing := by omega
  rw [allocated, raw, Int.tdiv_eq_ediv_of_nonneg hn]
  simp only [leastNonnegativeShare]
  constructor
  · omega
  constructor
  · omega
  intro other ho hq
  omega

theorem least_share_unique (q s a b : Int)
    (ha : leastNonnegativeShare q s a) (hb : leastNonnegativeShare q s b) :
    a = b := by
  have hab := ha.2.2 b hb.1 hb.2.1
  have hba := hb.2.2 a ha.1 ha.2.1
  omega

theorem unchanged_when_nonnegative (extent spacing span : Int)
    (h : 0 ≤ raw extent spacing span) :
    allocated extent spacing span = raw extent spacing span := by
  simp [allocated, Int.max_eq_right h]

theorem contribution_bounds (extent spacing span : Int)
    (he : 0 ≤ extent) (hs : 0 ≤ spacing) (_hk : 0 < span) :
    0 ≤ minimumContribution extent spacing span ∧
      minimumContribution extent spacing span ≤ extent := by
  have hn : 0 ≤ extent + spacing := by omega
  have hq := Int.ediv_le_self span hn
  simp only [minimumContribution, allocated, raw,
    Int.tdiv_eq_ediv_of_nonneg hn]
  split <;> omega

theorem representable_intermediates (extent spacing span : Int)
    (he : 0 ≤ extent) (hs : 0 ≤ spacing) (hk : 0 < span)
    (hkmax : span ≤ 2147483647) (hsum : extent + spacing ≤ 2147483647) :
    int32 extent ∧ int32 spacing ∧ int32 span ∧
      int32 (extent + spacing) ∧ int32 ((extent + spacing).tdiv span) ∧
      int32 (raw extent spacing span) ∧
      int32 (minimumContribution extent spacing span) := by
  have hn : 0 ≤ extent + spacing := by omega
  have hqlo := Int.ediv_nonneg hn (Int.le_of_lt hk)
  have hqhi := Int.ediv_le_self span hn
  have bounds := contribution_bounds extent spacing span he hs hk
  simp only [int32, raw, Int.tdiv_eq_ediv_of_nonneg hn] at *
  omega

def accumulate (base : Int) : List Int → Int
  | [] => base
  | x :: xs => accumulate (base + x) xs

def safeTrace (base : Int) : List Int → Prop
  | [] => True
  | x :: xs => 0 ≤ x ∧ base + x ≤ 2147483647 ∧ safeTrace (base + x) xs

theorem spacing_lower_bound (xs : List Int) (base : Int)
    (h : ∀ x ∈ xs, 0 ≤ x) : base ≤ accumulate base xs := by
  induction xs generalizing base with
  | nil => simp [accumulate]
  | cons x xs ih =>
    have hx := h x (by simp)
    have ht : ∀ v ∈ xs, 0 ≤ v := by
      intro v hv
      exact h v (by simp [hv])
    have hi := ih (base + x) ht
    simp only [accumulate]
    omega

theorem finite_contribution_sum (xs : List (Int × Int × Int)) (base : Int)
    (h : ∀ p ∈ xs, 0 ≤ p.1 ∧ 0 ≤ p.2.1 ∧ 0 < p.2.2) :
    base ≤ accumulate base
      (xs.map fun p => minimumContribution p.1 p.2.1 p.2.2) := by
  apply spacing_lower_bound
  intro x hx
  obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hx
  exact (contribution_bounds p.1 p.2.1 p.2.2 (h p hp).1
    (h p hp).2.1 (h p hp).2.2).1

theorem accumulation_representable (xs : List Int) (base : Int)
    (hb : 0 ≤ base) (hm : base ≤ 2147483647) (h : safeTrace base xs) :
    int32 (accumulate base xs) ∧ base ≤ accumulate base xs := by
  induction xs generalizing base with
  | nil => simp only [accumulate, int32]; omega
  | cons x xs ih =>
    obtain ⟨hx, hsum, ht⟩ := h
    have hi := ih (base + x) (by omega) hsum ht
    simp only [accumulate, int32] at *
    omega

theorem old_negative_counterexample : raw 0 60 2 = -30 ∧ allocated 0 60 2 = 0 := by
  decide

theorem remainders_not_preserved :
    3 * minimumContribution 10 0 3 ≠ 10 := by decide

theorem percentage_path_excluded :
    accumulate 120 [-60, -60, -60] < 120 := by decide

#print axioms nonnegative
#print axioms allocation_matches_final
#print axioms least_share_contract
#print axioms least_share_unique
#print axioms unchanged_when_nonnegative
#print axioms contribution_bounds
#print axioms representable_intermediates
#print axioms spacing_lower_bound
#print axioms finite_contribution_sum
#print axioms accumulation_representable
#print axioms old_negative_counterexample
#print axioms remainders_not_preserved
#print axioms percentage_path_excluded
end SpanSpacing
