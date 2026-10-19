import ProviderSorting
namespace ShadowOrder

theorem at_order_member (order : Int) (rules : List Rule) (entry : Entry)
 (member : entry ∈ atOrder order rules) : entry.order = order := by
 rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
 rfl

theorem at_order_pairwise (order : Int) (rules : List Rule) :
 (atOrder order rules).Pairwise (fun a b => a.order ≤ b.order) := by
 apply List.pairwise_iff_getElem.mpr
 intro i j hi hj hij
 have ai := at_order_member order rules ((atOrder order rules)[i]) (List.getElem_mem hi)
 have aj := at_order_member order rules ((atOrder order rules)[j]) (List.getElem_mem hj)
 omega

theorem outer_reference_bounds (contexts : List Context) (limit rank : Nat)
 (parts : List Nat) (entry : Entry)
 (member : entry ∈ physicalReference limit rank parts contexts) :
 (rank : Int) ≤ entry.order ∧ entry.order ≤ (limit : Int) := by
 induction contexts generalizing rank parts with
 | nil => simp [physicalReference] at member
 | cons context rest ih =>
   simp only [physicalReference] at member
   split at member
   · simp at member
   · rcases List.mem_append.mp member with here | later
     · split at here
       · rename_i condition
         have exactOrder := at_order_member _ _ _ here
         change entry.order = (rank : Int) at exactOrder
         simp only [Bool.and_eq_true,decide_eq_true_eq] at condition
         constructor <;> omega
       · simp at here
     · have bounds := ih _ _ later
       constructor <;> omega

theorem outer_reference_ordered (contexts : List Context) (limit rank : Nat)
 (parts : List Nat) :
 (physicalReference limit rank parts contexts).Pairwise (fun a b => a.order ≤ b.order) := by
 induction contexts generalizing rank parts with
 | nil => simp [physicalReference]
 | cons context rest ih =>
   simp only [physicalReference]
   split
   · simp
   · apply List.pairwise_append.mpr
     refine ⟨?_,ih _ _,?_⟩
     · split
       · exact at_order_pairwise _ _
       · simp
     · intro a ha b hb
       split at ha
       · have ea := at_order_member _ _ _ ha
         change a.order = (rank : Int) at ea
         have bb := outer_reference_bounds rest limit
           (rank + if context.mapPresent then 1 else 0) (exported context parts) b hb
         omega
       · simp at ha

theorem raw_outer_ordered (raw : RawProviderInput) (pseudos parts : List Nat)
 (fuel root limit : Nat) (contexts : List Context)
 (_normalization : normalizeOuter raw pseudos fuel root = some contexts) :
 (collectParts limit 1 parts contexts).Pairwise (fun a b => a.order ≤ b.order) := by
 rw [parts_refinement]
 exact outer_reference_ordered contexts limit 1 parts


theorem inner_collected_bounds (slots : List InnerContext) (limit index : Nat)
 (entry : Entry) (member : entry ∈ reverseSlotCollector limit index slots) :
 -(limit : Int) ≤ entry.order ∧ entry.order ≤ -((index : Int)+1) := by
 induction slots generalizing index with
 | nil => simp [reverseSlotCollector] at member
 | cons slot rest ih =>
   simp only [reverseSlotCollector] at member
   rcases List.mem_append.mp member with later | here
   · have bounds := ih (index+1) later
     constructor <;> omega
   · by_cases bound : index < limit
     · simp only [inner,bound,↓reduceIte] at here
       have exactOrder := at_order_member _ _ _ here
       change entry.order = -((index+1 : Nat) : Int) at exactOrder
       constructor <;> omega
     · simp [inner,bound] at here

theorem inner_collected_ordered (slots : List InnerContext) (limit index : Nat) :
 (reverseSlotCollector limit index slots).Pairwise (fun a b => a.order ≤ b.order) := by
 induction slots generalizing index with
 | nil => simp [reverseSlotCollector]
 | cons slot rest ih =>
   simp only [reverseSlotCollector]
   apply List.pairwise_append.mpr
   refine ⟨ih _,?_,?_⟩
   · by_cases bound : index < limit
     · simp only [inner,bound,↓reduceIte]
       exact at_order_pairwise _ _
     · simp [inner,bound]
   · intro a ha b hb
     have bounds := inner_collected_bounds rest limit (index+1) a ha
     by_cases bound : index < limit
     · simp only [inner,bound,↓reduceIte] at hb
       have exactOrder := at_order_member _ _ _ hb
       change b.order = -((index+1 : Nat) : Int) at exactOrder
       omega
     · simp [inner,bound] at hb


theorem inner_length_bound (slots : List InnerContext) (limit index : Nat)
 (entry : Entry) (member : entry ∈ reverseSlotCollector limit index slots) :
 -((index+slots.length : Nat) : Int) ≤ entry.order := by
 induction slots generalizing index with
 | nil => simp [reverseSlotCollector] at member
 | cons slot rest ih =>
   simp only [reverseSlotCollector] at member
   rcases List.mem_append.mp member with later | here
   · have bound := ih (index+1) later
     simp only [List.length_cons]
     omega
   · by_cases bound : index < limit
     · simp only [inner,bound,↓reduceIte] at here
       have exactOrder := at_order_member _ _ _ here
       change entry.order = -((index+1 : Nat) : Int) at exactOrder
       simp only [List.length_cons]
       omega
     · simp [inner,bound] at here

theorem host_precedes_slots (rules : List Rule) (slots : List InnerContext)
 (limit : Nat) (host slot : Entry)
 (hh : host ∈ hostCollector limit slots.length rules)
 (hs : slot ∈ reverseSlotCollector limit 0 slots) : host.order ≤ slot.order := by
 by_cases bound : slots.length < limit
 · simp only [hostCollector,inner,bound,↓reduceIte] at hh
   have exactOrder := at_order_member _ _ _ hh
   have lower := inner_length_bound slots limit 0 slot hs
   change host.order = -((slots.length+1 : Nat) : Int) at exactOrder
   omega
 · simp [hostCollector,inner,bound] at hh

theorem host_slot_collection_ordered (rules : List Rule) (slots : List InnerContext)
 (limit : Nat) :
 (hostCollector limit slots.length rules ++ reverseSlotCollector limit 0 slots).Pairwise
   (fun a b => a.order ≤ b.order) := by
 apply List.pairwise_append.mpr
 refine ⟨?_,inner_collected_ordered slots limit 0,?_⟩
 · by_cases bound : slots.length < limit
   · simp only [hostCollector,inner,bound,↓reduceIte]
     exact at_order_pairwise _ _
   · simp [hostCollector,inner,bound]
 · intro a ha b hb
   exact host_precedes_slots rules slots limit a b ha hb

#print axioms outer_reference_bounds
#print axioms outer_reference_ordered
end ShadowOrder
