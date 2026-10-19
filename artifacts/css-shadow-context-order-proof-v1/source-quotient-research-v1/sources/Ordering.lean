import Base
namespace ShadowOrder
set_option maxRecDepth 4096
set_option maxHeartbeats 800000

def insertKey (key : α → Nat) (value : α) : List α → List α
 | [] => [value]
 | head::tail => if key value ≤ key head then value::head::tail
   else head::insertKey key value tail

def localSort (key : α → Nat) : List α → List α
 | [] => []
 | head::tail => insertKey key head (localSort key tail)

theorem insert_perm (key : α → Nat) (a : α) (xs : List α) :
 (insertKey key a xs).Perm (a::xs) := by
 induction xs with
 | nil => exact List.Perm.refl _
 | cons b xs ih =>
   simp only [insertKey]
   split
   · exact List.Perm.refl _
   · exact (List.Perm.cons b ih).trans (List.Perm.swap _ _ _)

theorem sort_perm (key : α → Nat) (xs : List α) :
 (localSort key xs).Perm xs := by
 induction xs with
 | nil => exact List.Perm.refl _
 | cons a xs ih => exact (insert_perm key a _).trans (List.Perm.cons _ ih)

theorem insert_sorted (key : α → Nat) (a : α) (xs : List α)
 (h : xs.Pairwise (fun x y => key x ≤ key y)) :
 (insertKey key a xs).Pairwise (fun x y => key x ≤ key y) := by
 induction xs with
 | nil => simp [insertKey]
 | cons b xs ih =>
   simp only [List.pairwise_cons] at h
   simp only [insertKey]
   split
   · rename_i hab
     simp only [List.pairwise_cons, List.mem_cons, forall_eq_or_imp]
     exact ⟨⟨hab, fun x hx => Nat.le_trans hab (h.1 _ hx)⟩,h⟩
   · rename_i hab
     apply List.Pairwise.cons _ (ih h.2)
     intro x hx
     have hm := (insert_perm key a xs).mem_iff.mp hx
     simp only [List.mem_cons] at hm
     rcases hm with rfl | hx
     · omega
     · exact h.1 _ hx

theorem sort_sorted (key : α → Nat) (xs : List α) :
 (localSort key xs).Pairwise (fun x y => key x ≤ key y) := by
 induction xs with
 | nil => simp [localSort]
 | cons a xs ih => exact insert_sorted key a _ ih

theorem sorted_same_keys (key : α → Nat) (xs : List α) :
 (localSort key xs).map key = (xs.mergeSort (fun a b => key a ≤ key b)).map key := by
 apply List.Perm.eq_of_pairwise
 · intro a b _ _ hab hba
   exact Nat.le_antisymm hab hba
 · exact (List.pairwise_map).mpr (sort_sorted key xs)
 · apply List.pairwise_map.mpr
   have sorted := List.pairwise_mergeSort (le := fun a b => decide (key a ≤ key b))
     (by intro a b c hab hbc; simp_all only [decide_eq_true_eq]; omega)
     (by intro a b; simp only [Bool.or_eq_true,decide_eq_true_eq]; omega) xs
   simpa only [decide_eq_true_eq] using sorted
 · exact ((sort_perm key xs).trans (List.mergeSort_perm _ _).symm).map key

theorem constant_if_endpoints (key : α → Nat) (first last : α) (middle : List α)
 (h : (first::(middle++[last])).Pairwise (fun a b => key a ≤ key b))
 (heq : key first = key last) :
 ∀ a ∈ first::(middle++[last]), key a = key first := by
 intro a ha
 have bounds := h
 simp only [List.pairwise_cons] at bounds
 simp only [List.mem_cons] at ha
 rcases ha with rfl | ha
 · rfl
 · have lower := bounds.1 a ha
   have upper : key a ≤ key last := by
     have hh := bounds.2
     rw [List.pairwise_append] at hh
     rcases List.mem_append.mp ha with hm | hl
     · exact hh.2.2 a hm last (by simp)
     · simp only [List.mem_singleton] at hl
       subst a
       exact Nat.le_refl _
   omega

theorem insert_refined (priority key : α → Nat)
 (strict : ∀ a b, priority a < priority b → key a ≤ key b)
 (a : α) (xs : List α)
 (sorted : xs.Pairwise (fun x y => key x ≤ key y))
 (ties : ∀ b ∈ xs, priority a = priority b → key a ≤ key b) :
 (insertKey priority a xs).Pairwise (fun x y => key x ≤ key y) := by
 induction xs with
 | nil => simp [insertKey]
 | cons b xs ih =>
   simp only [List.pairwise_cons] at sorted
   simp only [insertKey]
   split
   · rename_i hab
     have kab : key a ≤ key b := by
       by_cases eq : priority a = priority b
       · exact ties b (by simp) eq
       · exact strict a b (by omega)
     apply List.Pairwise.cons
     · intro x hx
       simp only [List.mem_cons] at hx
       rcases hx with rfl | hx
       · exact kab
       · exact Nat.le_trans kab (sorted.1 x hx)
     · exact List.Pairwise.cons sorted.1 sorted.2
   · rename_i hab
     apply List.Pairwise.cons
     · intro x hx
       have hm := (insert_perm priority a xs).mem_iff.mp hx
       simp only [List.mem_cons] at hm
       rcases hm with rfl | hx
       · apply strict; omega
       · exact sorted.1 x hx
     · exact ih sorted.2 (fun x hx => ties x (by simp [hx]))

theorem stable_sort_refined (priority key : α → Nat)
 (strict : ∀ a b, priority a < priority b → key a ≤ key b)
 (xs : List α)
 (ties : xs.Pairwise (fun a b => priority a = priority b → key a ≤ key b)) :
 (localSort priority xs).Pairwise (fun x y => key x ≤ key y) := by
 induction xs with
 | nil => simp [localSort]
 | cons a xs ih =>
   simp only [List.pairwise_cons] at ties
   apply insert_refined priority key strict a _ (ih ties.2)
   intro b hb hab
   exact ties.1 b ((sort_perm priority xs).mem_iff.mp hb) hab

theorem stable_sort_reference (priority key : α → Nat)
 (strict : ∀ a b, priority a < priority b → key a ≤ key b)
 (xs : List α)
 (ties : xs.Pairwise (fun a b => priority a = priority b → key a ≤ key b)) :
 (localSort priority xs).map key = (localSort key xs).map key := by
 apply List.Perm.eq_of_pairwise
 · intro a b _ _ hab hba; exact Nat.le_antisymm hab hba
 · exact List.pairwise_map.mpr (stable_sort_refined priority key strict xs ties)
 · exact List.pairwise_map.mpr (sort_sorted key xs)
 · exact ((sort_perm priority xs).trans (sort_perm key xs).symm).map key

def localKey (specificity proximity sourceOrder : Nat) : Nat :=
 specificity * 1099511627776 + proximity * 16777216 + sourceOrder

theorem local_key_bound (specificity proximity sourceOrder : Nat)
 (hs : specificity < 4294967296) (hp : proximity < 65536)
 (ho : sourceOrder < 16777216) :
 localKey specificity proximity sourceOrder < 4722366482869645213696 := by
 unfold localKey
 omega

theorem local_key_lex (aspec aprox aorder bspec bprox border : Nat)
 (hap : aprox < 65536) (hao : aorder < 16777216)
 (hbp : bprox < 65536) (hbo : border < 16777216) :
 localKey aspec aprox aorder ≤ localKey bspec bprox border ↔
 aspec < bspec ∨ (aspec = bspec ∧ (aprox < bprox ∨ (aprox = bprox ∧ aorder ≤ border))) := by
 unfold localKey
 omega

#print axioms sort_perm
#print axioms sort_sorted
#print axioms sorted_same_keys
#print axioms constant_if_endpoints
#print axioms stable_sort_reference
#print axioms local_key_lex
end ShadowOrder
