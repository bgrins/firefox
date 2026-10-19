import RawAuthorOrder
import BoundedSortSkip
import ImportantPartition
namespace ShadowOrder

theorem own_host_numeric (raw : RawProviderInput) (pseudos : List Nat)
 (target : RawElement) (elementBacked : Bool) (rules : List Rule)
 (valid : rawFieldsValid raw = true)
 (normalized : normalizeOwnHost raw pseudos target elementBacked = some rules) :
 ∀ rule ∈ rules, ruleNumericBounds rule := by
 cases own : target.ownShadow with
 | none => simp [normalizeOwnHost,own] at normalized; subst rules; simp
 | some identity =>
   cases found : raw.roots[identity]? with
   | none => simp [normalizeOwnHost,own,found] at normalized
   | some root =>
     have dataValid := raw_root_data_valid raw valid identity root found
     cases data : root.styleData with
     | none => simp [normalizeOwnHost,own,found,data] at normalized; subst rules; simp [localSort]
     | some styles =>
       simp only [data,Option.toList_some,List.all_cons,List.all_nil,Bool.and_true] at dataValid
       simp [normalizeOwnHost,own,found,data] at normalized
       subst rules
       intro rule member
       exact host_data_bounds (identity+1) styles pseudos elementBacked dataValid rule
         ((sort_perm _ _).mem_iff.mp member)

theorem slot_context_numeric (pseudos : List Nat) (identity : Nat) (root : RawShadowRoot)
 (valid : root.styleData.toList.all rawDataValid = true) :
 ∀ rule ∈ (slotContext pseudos identity root).rules, ruleNumericBounds rule := by
 cases data : root.styleData with
 | none => simp [slotContext,data]
 | some styles =>
   simp only [data,Option.toList_some,List.all_cons,List.all_nil,Bool.and_true] at valid
   have maps : rawMapValid styles.table styles.slotted = true := by
     simp only [rawDataValid,Bool.and_eq_true] at valid
     exact valid.1.2
   intro rule member
   simp only [slotContext,data,Option.toList_some,List.flatMap_cons,List.flatMap_nil,List.append_nil] at member
   exact exact_map_numeric_bounds (identity+1) styles styles.slotted pseudos maps rule
     ((sort_perm _ _).mem_iff.mp member)

theorem slot_trace_numeric (raw : RawProviderInput) (pseudos : List Nat)
 (valid : rawFieldsValid raw = true) (start : Option Nat) (slots : List InnerContext)
 (trace : SlotTrace raw pseudos start slots) :
 ∀ slot ∈ slots, ∀ rule ∈ slot.rules, ruleNumericBounds rule := by
 induction trace with
 | endPath => simp
 | slot identity rootIdentity element root rest elementFound containing rootFound tail ih =>
   intro slot member
   rcases List.mem_cons.mp member with same | later
   · subst slot
     exact slot_context_numeric pseudos rootIdentity root (raw_root_data_valid raw valid _ _ rootFound)
   · exact ih slot later

theorem at_order_numeric (order : Int) (rules : List Rule)
 (valid : ∀ rule ∈ rules, ruleNumericBounds rule) :
 ∀ entry ∈ atOrder order rules, ruleNumericBounds entry.rule := by
 intro entry member
 rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
 exact valid rule hr

theorem inner_collected_numeric (slots : List InnerContext) (limit index : Nat)
 (valid : ∀ slot ∈ slots, ∀ rule ∈ slot.rules, ruleNumericBounds rule) :
 ∀ entry ∈ reverseSlotCollector limit index slots, ruleNumericBounds entry.rule := by
 induction slots generalizing index with
 | nil => simp [reverseSlotCollector]
 | cons slot rest ih =>
   intro entry member
   rcases List.mem_append.mp member with later | here
   · exact ih (index+1) (fun c hc => valid c (by simp [hc])) entry later
   · by_cases bound : index < limit
     · simp only [inner,bound,↓reduceIte] at here
       exact at_order_numeric _ _ (valid slot (by simp)) entry here
     · simp [inner,bound] at here

theorem outer_collected_numeric (contexts : List Context) (limit rank : Nat) (parts : List Nat)
 (valid : ∀ context ∈ contexts, ∀ named ∈ context.rules, ruleNumericBounds named.rule) :
 ∀ entry ∈ physicalReference limit rank parts contexts, ruleNumericBounds entry.rule := by
 induction contexts generalizing rank parts with
 | nil => simp [physicalReference]
 | cons context rest ih =>
   intro entry member
   simp only [physicalReference] at member
   split at member
   · simp at member
   · rcases List.mem_append.mp member with here | later
     · split at here
       · apply at_order_numeric _ _ _ entry here
         intro rule hr
         exact matching_bounds context parts (valid context (by simp)) rule
           ((sort_perm _ _).mem_iff.mp hr)
       · simp at here
     · exact ih _ _ (fun c hc => valid c (by simp [hc])) entry later

theorem host_collected_entry_bounds (rules : List Rule) (count : Nat)
 (valid : ∀ rule ∈ rules, ruleNumericBounds rule) :
 ∀ entry ∈ hostCollector maxOrder count rules, entryBounds entry := by
 intro entry member
 by_cases bound : count < maxOrder
 · simp only [hostCollector,inner,bound,↓reduceIte] at member
   have order := at_order_member _ _ _ member
   have numeric := (at_order_numeric _ _ valid entry member).1
   change entry.order = -((count+1 : Nat) : Int) at order
   unfold entryBounds
   constructor
   · omega
   constructor <;> omega
 · simp [hostCollector,inner,bound] at member

theorem slot_collected_entry_bounds (slots : List InnerContext)
 (valid : ∀ slot ∈ slots, ∀ rule ∈ slot.rules, ruleNumericBounds rule) :
 ∀ entry ∈ reverseSlotCollector maxOrder 0 slots, entryBounds entry := by
 intro entry member
 have order := inner_collected_bounds slots maxOrder 0 entry member
 have numeric := (inner_collected_numeric slots maxOrder 0 valid entry member).1
 unfold entryBounds
 exact ⟨order.1,by omega,by omega⟩

theorem outer_collected_entry_bounds (contexts : List Context) (parts : List Nat)
 (valid : ∀ context ∈ contexts, ∀ named ∈ context.rules, ruleNumericBounds named.rule) :
 ∀ entry ∈ collectParts maxOrder 1 parts contexts, entryBounds entry := by
 rw [parts_refinement]
 intro entry member
 have order := outer_reference_bounds contexts maxOrder 1 parts entry member
 have numeric := (outer_collected_numeric contexts maxOrder 1 parts valid entry member).1
 unfold entryBounds
 exact ⟨by omega,order.2,by omega⟩

theorem bounded_entries_append (left right : List Entry)
 (a : ∀ e ∈ left, entryBounds e) (b : ∀ e ∈ right, entryBounds e) :
 ∀ e ∈ left ++ right, entryBounds e := by
 intro e member
 rcases List.mem_append.mp member with hl | hr
 · exact a e hl
 · exact b e hr

theorem raw_author_construction_bounds (raw : RawProviderInput) (valid : rawFieldsValid raw = true) :
 AuthorConstructionProperty raw (fun entries => ∀ entry ∈ entries, entryBounds entry) := by
 intro target pseudos host slots containing contexts elementBacked hostMade slotsMade containingMade outerMade
 have hb := host_collected_entry_bounds host slots.length
   (own_host_numeric raw pseudos target elementBacked host valid hostMade)
 have sb := slot_collected_entry_bounds slots (slot_trace_numeric raw pseudos valid target.assignedSlot slots
   (slot_normalization_sound raw pseudos (raw.elements.length+1) target.assignedSlot slots slotsMade))
 have containingShape := containing_shape raw pseudos target containing.1 containing.2 containingMade
 have containingNumeric := containing_numeric_bounds raw pseudos target containing.1 containing.2 valid containingMade
 have cb : ∀ entry ∈ containing.1, entryBounds entry := by
   intro entry member
   have zero := containingShape.2 entry member
   have layer := (containingNumeric entry member).1
   unfold entryBounds
   exact ⟨by omega,by omega,by omega⟩
 have db : ∀ entry ∈ (if containing.2 then originEntries 3 0
     (sortedMapRules 0 raw.document (pseudoMapLookup raw.document.normal pseudos)) else []), entryBounds entry := by
   intro entry member
   split at member
   · have zero := origin_entries_zero _ _ _ entry member
     have layer := (document_numeric_bounds raw pseudos valid entry member).1
     unfold entryBounds
     exact ⟨by omega,by omega,by omega⟩
   · simp at member
 have ib : ∀ entry ∈ originEntries 3 (target.containingShadow.map (·+1) |>.getD 0)
     (raw.inlineStyle.toList.map fun rule => plainRule (target.containingShadow.map (·+1) |>.getD 0) 0
       {rule with layer := 65535,flags := 0}), entryBounds entry := by
   intro entry member
   rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
   rcases List.mem_map.mp hr with ⟨block,hb,rfl⟩
   simp [entryBounds,plainRule,maxOrder]
 have outerNumeric : ∀ context ∈ contexts, ∀ named ∈ context.rules, ruleNumericBounds named.rule := by
   rcases outerMade with empty | made
   · subst contexts; simp
   · rcases made with ⟨root,fuel,normalized⟩
     exact outer_trace_bounds raw pseudos valid root contexts
       (outer_normalization_sound raw pseudos fuel root contexts normalized)
 have ob := outer_collected_entry_bounds contexts target.parts outerNumeric
 exact bounded_entries_append _ _
   (bounded_entries_append _ _
     (bounded_entries_append _ _
       (bounded_entries_append _ _ (bounded_entries_append _ _ hb sb) cb) db) ib) ob

theorem raw_author_normalization_bounds (raw : RawProviderInput) (normalized : RawInput)
 (valid : rawFieldsValid raw = true) (made : normalizeRawProviders raw = some normalized) :
 ∀ entry ∈ authorOnlyEntries normalized, entryBounds entry :=
 raw_author_normalization_property raw normalized (fun entries => ∀ entry ∈ entries, entryBounds entry)
   (by simp) (raw_author_construction_bounds raw valid) made

theorem raw_author_important_skip (raw : RawProviderInput) (normalized : RawInput)
 (valid : rawFieldsValid raw = true) (made : normalizeRawProviders raw = some normalized) :
 skipSort entryPriorityIdentity entryImportantKey (authorOnlyEntries normalized) =
 localSort entryImportantKey (authorOnlyEntries normalized) :=
 bounded_important_skip _ (raw_author_normalization_bounds raw normalized valid made)
   (raw_author_normalization_order raw normalized valid made)

theorem raw_author_important_partition_skip (raw : RawProviderInput) (normalized : RawInput)
 (valid : rawFieldsValid raw = true) (made : normalizeRawProviders raw = some normalized) :
 skipSort entryPriorityIdentity entryImportantKey ((authorOnlyEntries normalized).filter hasImportant) =
 localSort entryImportantKey ((authorOnlyEntries normalized).filter hasImportant) := by
 apply bounded_important_skip
 · intro entry member
   exact raw_author_normalization_bounds raw normalized valid made entry (List.mem_filter.mp member).1
 · exact (raw_author_normalization_order raw normalized valid made).filter _

#print axioms host_collected_entry_bounds
#print axioms outer_collected_entry_bounds
end ShadowOrder
