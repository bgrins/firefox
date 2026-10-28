import Std
namespace PageSelectorBuckets

structure Selector where
  name : Option Nat
  pseudoMatches : Bool
  specificity : Nat
  deriving DecidableEq, Repr

def score (s : Selector) : Nat := if s.pseudoMatches then s.specificity + 1 else 0

def selected (name : Option Nat) (s : Selector) : Nat :=
  if s.name = name then score s else 0

def bucket (name : Option Nat) (xs : List Selector) : Nat :=
  xs.foldr (fun s best => max (selected name s) best) 0

def exhaustive (page : Nat) (xs : List Selector) : Nat :=
  xs.foldr (fun s best => max
    (if s.name = none ∨ s.name = some page then score s else 0) best) 0

def oldAllNames (xs : List Selector) : Nat :=
  xs.foldr (fun s best => max (score s) best) 0

theorem selected_partition (page : Nat) (s : Selector) :
    (if s.name = none ∨ s.name = some page then score s else 0) =
      max (selected none s) (selected (some page) s) := by
  by_cases empty : s.name = none <;> by_cases named : s.name = some page <;>
    simp [selected, empty, named]

theorem exhaustive_eq_two_buckets (page : Nat) (xs : List Selector) :
    exhaustive page xs = max (bucket none xs) (bucket (some page) xs) := by
  induction xs with
  | nil => rfl
  | cons s xs ih =>
    simp only [exhaustive, bucket, List.foldr_cons] at *
    rw [selected_partition, ih]
    omega

theorem bucket_eq_filtered (name : Option Nat) (xs : List Selector) :
    bucket name xs = (xs.filter (fun s => s.name == name)).foldr
      (fun s best => max (score s) best) 0 := by
  induction xs with
  | nil => rfl
  | cons s xs ih =>
    by_cases same : s.name = name <;> simp [bucket, selected, same] at * <;> simp_all

def ruleScore (page : Nat) (xs : List Selector) : Nat :=
  if xs.isEmpty then 1 else exhaustive page xs

def indexedRuleScore (page : Nat) (xs : List Selector) : Nat :=
  if xs.isEmpty then 1 else max (bucket none xs) (bucket (some page) xs)

theorem rule_equivalence (page : Nat) (xs : List Selector) :
    ruleScore page xs = indexedRuleScore page xs := by
  simp [ruleScore, indexedRuleScore, exhaustive_eq_two_buckets]

def applicabilityWitness : List Selector :=
  [⟨some 1, false, 2⟩, ⟨some 2, true, 1⟩]

def specificityWitness : List Selector :=
  [⟨some 1, true, 1⟩, ⟨some 2, true, 2⟩]

theorem old_cross_name_applicability :
    exhaustive 1 applicabilityWitness = 0 ∧ oldAllNames applicabilityWitness = 2 := by
  decide +kernel

theorem old_cross_name_specificity :
    exhaustive 1 specificityWitness = 2 ∧ oldAllNames specificityWitness = 3 := by
  decide +kernel

#print axioms selected_partition
#print axioms exhaustive_eq_two_buckets
#print axioms bucket_eq_filtered
#print axioms rule_equivalence
#print axioms old_cross_name_applicability
#print axioms old_cross_name_specificity
end PageSelectorBuckets
