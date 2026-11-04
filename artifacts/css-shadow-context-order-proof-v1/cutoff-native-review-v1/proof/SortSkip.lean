import Ordering
namespace ShadowOrder

theorem local_sort_constant (key : α → Nat) (xs : List α) (value : Nat)
 (h : ∀ a ∈ xs, key a = value) : localSort key xs = xs := by
 induction xs with
 | nil => rfl
 | cons a rest ih =>
   have ha := h a (by simp)
   have hr : ∀ b ∈ rest, key b = value := fun b hb => h b (by simp [hb])
   simp only [localSort,ih hr]
   cases rest with
   | nil => rfl
   | cons b tail =>
     have hb := hr b (by simp)
     simp [insertKey,ha,hb]

def skipSort (identity : α → β) [DecidableEq β] (key : α → Nat) : List α → List α
 | [] => []
 | first::rest =>
   if identity first = identity ((first::rest).getLast (by simp)) then first::rest
   else localSort key (first::rest)

theorem skip_sort_reference (identity : α → β) [DecidableEq β]
 (normalKey importantKey : α → Nat) (xs : List α)
 (ordered : xs.Pairwise (fun a b => normalKey a ≤ normalKey b))
 (identity_preserves : ∀ a b, identity a = identity b → normalKey a = normalKey b)
 (transform : ∀ a b, normalKey a = normalKey b → importantKey a = importantKey b) :
 skipSort identity importantKey xs = localSort importantKey xs := by
 cases xs with
 | nil => rfl
 | cons first rest =>
   simp only [skipSort]
   split
   · rename_i eq
     apply Eq.symm
     apply local_sort_constant importantKey _ (importantKey first)
     have endEq := identity_preserves _ _ eq
     intro a ha
     apply transform
     by_cases empty : rest = []
     · subst rest
       simp at ha
       subst a
       rfl
     · have decomposition := List.dropLast_concat_getLast empty
       have lastEq : normalKey first = normalKey (rest.getLast empty) := by
         simpa only [List.getLast_cons empty] using endEq
       have sorted : (first::(rest.dropLast++[rest.getLast empty])).Pairwise
           (fun x y => normalKey x ≤ normalKey y) := by simpa only [decomposition] using ordered
       have member : a ∈ first::(rest.dropLast++[rest.getLast empty]) := by
         simpa only [decomposition] using ha
       exact constant_if_endpoints normalKey first (rest.getLast empty) rest.dropLast
         sorted lastEq a member
   · rfl

#print axioms local_sort_constant
#print axioms skip_sort_reference
end ShadowOrder
