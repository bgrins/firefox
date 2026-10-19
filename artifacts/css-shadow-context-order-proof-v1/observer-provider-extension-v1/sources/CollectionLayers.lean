import CollectionOrder
namespace ShadowOrder

def contextLayerLE (a b : Entry) : Prop :=
 a.order < b.order ∨ (a.order = b.order ∧ a.rule.layer ≤ b.rule.layer)

theorem sorted_rule_layers (rules : List Rule)
 (bounds : ∀ rule ∈ rules, ruleNumericBounds rule) :
 (localSort completeLocalKey rules).Pairwise (fun a b => a.layer ≤ b.layer) := by
 apply List.Pairwise.imp_of_mem _ (sort_sorted completeLocalKey rules)
 intro a b ha hb keys
 exact local_layer_order a b
   (bounds a ((sort_perm _ _).mem_iff.mp ha)).2
   (bounds b ((sort_perm _ _).mem_iff.mp hb)).2 keys

theorem at_order_layer_sorted (order : Int) (rules : List Rule)
 (sorted : rules.Pairwise (fun a b => a.layer ≤ b.layer)) :
 (atOrder order rules).Pairwise contextLayerLE := by
 simpa [atOrder,List.pairwise_map,contextLayerLE] using sorted

theorem matching_bounds (context : Context) (parts : List Nat)
 (bounds : ∀ named ∈ context.rules, ruleNumericBounds named.rule)
 (rule : Rule) (member : rule ∈ matching context parts) : ruleNumericBounds rule := by
 rcases List.mem_flatMap.mp member with ⟨part,hpart,hm⟩
 rcases List.mem_map.mp hm with ⟨named,hn,rfl⟩
 exact bounds named ((List.mem_filter.mp hn).1)

theorem outer_context_layer_order (contexts : List Context) (limit rank : Nat)
 (parts : List Nat)
 (bounds : ∀ context ∈ contexts, ∀ named ∈ context.rules, ruleNumericBounds named.rule) :
 (physicalReference limit rank parts contexts).Pairwise contextLayerLE := by
 induction contexts generalizing rank parts with
 | nil => simp [physicalReference]
 | cons context rest ih =>
   simp only [physicalReference]
   split
   · simp
   · apply List.pairwise_append.mpr
     refine ⟨?_,ih _ _ (fun c hc => bounds c (by simp [hc])),?_⟩
     · split
       · apply at_order_layer_sorted
         apply sorted_rule_layers
         exact matching_bounds context parts (bounds context (by simp))
       · simp
     · intro a ha b hb
       split at ha
       · rename_i present
         have ea := at_order_member _ _ _ ha
         change a.order = (rank : Int) at ea
         have bb := outer_reference_bounds rest limit
           (rank + if context.mapPresent then 1 else 0) (exported context parts) b hb
         simp only [Bool.and_eq_true,decide_eq_true_eq] at present
         simp only [present.1,↓reduceIte] at bb
         exact Or.inl (by omega)
       · simp at ha

theorem inner_context_layer_order (slots : List InnerContext) (limit index : Nat)
 (sorted : ∀ slot ∈ slots, slot.rules.Pairwise (fun a b => a.layer ≤ b.layer)) :
 (reverseSlotCollector limit index slots).Pairwise contextLayerLE := by
 induction slots generalizing index with
 | nil => simp [reverseSlotCollector]
 | cons slot rest ih =>
   simp only [reverseSlotCollector]
   apply List.pairwise_append.mpr
   refine ⟨ih _ (fun c hc => sorted c (by simp [hc])),?_,?_⟩
   · by_cases bound : index < limit
     · simp only [inner,bound,↓reduceIte]
       exact at_order_layer_sorted _ _ (sorted slot (by simp))
     · simp [inner,bound]
   · intro a ha b hb
     have ab := inner_collected_bounds rest limit (index+1) a ha
     by_cases bound : index < limit
     · simp only [inner,bound,↓reduceIte] at hb
       have eb := at_order_member _ _ _ hb
       change b.order = -((index+1 : Nat) : Int) at eb
       exact Or.inl (by omega)
     · simp [inner,bound] at hb

theorem host_slot_layer_order (host : List Rule) (slots : List InnerContext) (limit : Nat)
 (hostSorted : host.Pairwise (fun a b => a.layer ≤ b.layer))
 (slotSorted : ∀ slot ∈ slots, slot.rules.Pairwise (fun a b => a.layer ≤ b.layer)) :
 (hostCollector limit slots.length host ++ reverseSlotCollector limit 0 slots).Pairwise contextLayerLE := by
 apply List.pairwise_append.mpr
 refine ⟨?_,inner_context_layer_order slots limit 0 slotSorted,?_⟩
 · by_cases bound : slots.length < limit
   · simp only [hostCollector,inner,bound,↓reduceIte]
     exact at_order_layer_sorted _ _ hostSorted
   · simp [hostCollector,inner,bound]
 · intro a ha b hb
   by_cases bound : slots.length < limit
   · simp only [hostCollector,inner,bound,↓reduceIte] at ha
     have ea := at_order_member _ _ _ ha
     have bb := inner_length_bound slots limit 0 b hb
     change a.order = -((slots.length+1 : Nat) : Int) at ea
     exact Or.inl (by omega)
   · simp [hostCollector,inner,bound] at ha

theorem context_layer_append (left right : List Entry)
 (ls : left.Pairwise contextLayerLE) (rs : right.Pairwise contextLayerLE)
 (cross : ∀ a ∈ left, ∀ b ∈ right, contextLayerLE a b) :
 (left ++ right).Pairwise contextLayerLE := List.pairwise_append.mpr ⟨ls,rs,cross⟩

theorem zero_context_order (rules : List Entry)
 (layers : rules.Pairwise (fun a b => a.rule.layer ≤ b.rule.layer))
 (zero : ∀ entry ∈ rules, entry.order = 0) : rules.Pairwise contextLayerLE := by
 apply List.Pairwise.imp_of_mem _ layers
 intro a b ha hb h
 exact Or.inr ⟨(zero a ha).trans (zero b hb).symm,h⟩

theorem author_group_context_order (host : List Rule) (slots : List InnerContext)
 (localRules inlineRules : List Entry) (contexts : List Context) (parts : List Nat) (limit : Nat)
 (hostSorted : host.Pairwise (fun a b => a.layer ≤ b.layer))
 (slotSorted : ∀ slot ∈ slots, slot.rules.Pairwise (fun a b => a.layer ≤ b.layer))
 (localSorted : localRules.Pairwise contextLayerLE)
 (localZero : ∀ entry ∈ localRules, entry.order = 0)
 (localLayer : ∀ entry ∈ localRules, entry.rule.layer ≤ 65535)
 (inlineShape : ∀ entry ∈ inlineRules, entry.order = 0 ∧ entry.rule.layer = 65535)
 (outerBounds : ∀ context ∈ contexts, ∀ named ∈ context.rules, ruleNumericBounds named.rule) :
 (hostCollector limit slots.length host ++ reverseSlotCollector limit 0 slots ++
   localRules ++ inlineRules ++ collectParts limit 1 parts contexts).Pairwise contextLayerLE := by
 have inlineSorted : inlineRules.Pairwise contextLayerLE := by
   apply List.pairwise_iff_getElem.mpr
   intro i j hi hj hij
   have a := inlineShape _ (List.getElem_mem hi)
   have b := inlineShape _ (List.getElem_mem hj)
   exact Or.inr ⟨by omega,by omega⟩
 have middleSorted := context_layer_append localRules inlineRules localSorted inlineSorted
   (by intro a ha b hb; have ba := localLayer a ha; have bb := inlineShape b hb
       exact Or.inr ⟨by rw [localZero a ha,bb.1],by omega⟩)
 have beforeSorted := host_slot_layer_order host slots limit hostSorted slotSorted
 have beforeNegative : ∀ a ∈ hostCollector limit slots.length host ++ reverseSlotCollector limit 0 slots,
   a.order < 0 := by
   intro a ha
   rcases List.mem_append.mp ha with hh | hs
   · by_cases bound : slots.length < limit
     · simp only [hostCollector,inner,bound,↓reduceIte] at hh
       have exactOrder := at_order_member _ _ _ hh
       change a.order = -((slots.length+1 : Nat) : Int) at exactOrder
       omega
     · simp [hostCollector,inner,bound] at hh
   · have bounds := inner_collected_bounds slots limit 0 a hs
     omega
 have middleZero : ∀ a ∈ localRules ++ inlineRules, a.order = 0 := by
   intro a ha
   rcases List.mem_append.mp ha with hl | hi
   · exact localZero a hl
   · exact (inlineShape a hi).1
 have firstSorted := context_layer_append _ _ beforeSorted middleSorted
   (by intro a ha b hb; exact Or.inl (by have := beforeNegative a ha; rw [middleZero b hb]; omega))
 rw [parts_refinement]
 have outerSorted := outer_context_layer_order contexts limit 1 parts outerBounds
 have fullSorted := context_layer_append _ _ firstSorted outerSorted (by
   intro a ha b hb
   have bb := outer_reference_bounds contexts limit 1 parts b hb
   rcases List.mem_append.mp ha with before | middle
   · exact Or.inl (by have := beforeNegative a before; omega)
   · exact Or.inl (by rw [middleZero a middle]; omega))
 simpa only [List.append_assoc] using fullSorted

#print axioms outer_context_layer_order
#print axioms host_slot_layer_order
end ShadowOrder
