import CollectionLayers
import SortSkip
import Priority
namespace ShadowOrder

def entryBounds (e : Entry) : Prop :=
 -(maxOrder : Int) ≤ e.order ∧ e.order ≤ maxOrder ∧ e.rule.layer ≤ 65535

def entryNormalKey (e : Entry) : Nat :=
 (e.order + maxOrder).toNat * 65536 + e.rule.layer

def entryImportantKey (e : Entry) : Nat :=
 (-e.order + maxOrder).toNat * 65536 + layerKey true e.rule.layer

theorem context_key_order (a b : Entry) (ba : entryBounds a) (bb : entryBounds b)
 (order : contextLayerLE a b) : entryNormalKey a ≤ entryNormalKey b := by
 simp only [entryBounds] at ba bb
 simp only [contextLayerLE] at order
 simp only [entryNormalKey]
 omega

theorem context_key_injective (a b : Entry) (ba : entryBounds a) (bb : entryBounds b)
 (keys : entryNormalKey a = entryNormalKey b) : a.order = b.order ∧ a.rule.layer = b.rule.layer := by
 simp only [entryBounds] at ba bb
 simp only [entryNormalKey] at keys
 omega

theorem important_key_constant (a b : Entry) (ba : entryBounds a) (bb : entryBounds b)
 (keys : entryNormalKey a = entryNormalKey b) : entryImportantKey a = entryImportantKey b := by
 rcases context_key_injective a b ba bb keys with ⟨order,layer⟩
 simp [entryImportantKey,order,layer]

theorem skip_sort_reference_members (identity : α → β) [DecidableEq β]
 (normalKey importantKey : α → Nat) (xs : List α)
 (ordered : xs.Pairwise (fun a b => normalKey a ≤ normalKey b))
 (identity_preserves : ∀ a b, identity a = identity b → normalKey a = normalKey b)
 (transform : ∀ a ∈ xs, ∀ b ∈ xs, normalKey a = normalKey b → importantKey a = importantKey b) :
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
     apply transform a ha first (by simp)
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

def entryPriorityIdentity (e : Entry) : Int × Nat × Nat := ⟨e.order,e.rule.layer,e.rule.flags⟩

theorem bounded_important_skip (entries : List Entry)
 (bounded : ∀ e ∈ entries, entryBounds e)
 (ordered : entries.Pairwise contextLayerLE) :
 skipSort entryPriorityIdentity entryImportantKey entries = localSort entryImportantKey entries := by
 apply skip_sort_reference_members entryPriorityIdentity entryNormalKey entryImportantKey entries
 · apply List.Pairwise.imp_of_mem _ ordered
   intro a b ha hb h
   exact context_key_order a b (bounded a ha) (bounded b hb) h
 · intro a b eq
   have order := congrArg Prod.fst eq
   have layer := congrArg (fun value : Int × Nat × Nat => value.2.1) eq
   simp only [entryPriorityIdentity] at order layer
   simp [entryNormalKey,order,layer]
 · intro a ha b hb eq
   exact important_key_constant a b (bounded a ha) (bounded b hb) eq

def authorPriority (e : Entry) (important : Bool) : Priority :=
 ⟨3,important,e.order,e.rule.layer,e.rule.flags⟩

theorem bounded_author_priority (entry : Entry) (important : Bool) (bounds : entryBounds entry) :
 (authorPriority entry important).admitted := by
 rcases bounds with ⟨lower,upper,layer⟩
 exact ⟨by change 3 < 8; decide,by intro h; exact Or.inr (Or.inr rfl),lower,upper,layer⟩

theorem important_entry_priority_key (entry : Entry) (bounds : entryBounds entry) :
 priorityKey (authorPriority entry true) = (entryImportantKey entry : Int) + 7*268435455*65536 := by
 unfold priorityKey levelKey bucket authorPriority entryImportantKey
 simp only [↓reduceIte]
 have nonnegative : 0 ≤ -entry.order + (maxOrder : Int) := by rcases bounds with ⟨lo,hi,layer⟩; omega
 omega

theorem important_entry_comparator (a b : Entry) (ba : entryBounds a) (bb : entryBounds b) :
 priorityKey (authorPriority a true) ≤ priorityKey (authorPriority b true) ↔
 entryImportantKey a ≤ entryImportantKey b := by
 rw [important_entry_priority_key a ba,important_entry_priority_key b bb]
 omega

#print axioms bounded_important_skip
end ShadowOrder
