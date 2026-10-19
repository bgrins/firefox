import CollectionLayers
import ProviderMaps
namespace ShadowOrder

theorem raw_root_data_valid (raw : RawProviderInput) (valid : rawFieldsValid raw = true)
 (identity : Nat) (root : RawShadowRoot) (found : raw.roots[identity]? = some root) :
 root.styleData.toList.all rawDataValid = true := by
 simp only [rawFieldsValid,Bool.and_eq_true] at valid
 exact List.all_eq_true.mp valid.1.1.2 root (List.mem_of_getElem? found)

theorem part_lookup_admitted (table : List RawStyleRule) (maps : PartPseudoMap)
 (pseudos : List Nat) (valid : rawPartMapValid table maps = true) :
 ((partMapLookup maps pseudos).toList.flatten).all
   (fun named => named.2.all (rawRuleAdmission table)) = true := by
 simp only [rawPartMapValid,Bool.and_eq_true] at valid
 have entries := valid.2
 clear valid
 induction maps with
 | nil => rfl
 | cons entry rest ih =>
   simp only [List.all_cons,Bool.and_eq_true] at entries
   by_cases found : entry.1 == pseudos
   · simpa [partMapLookup,List.find?,found] using entries.1.2
   · simpa [partMapLookup,List.find?,found] using ih entries.2

theorem part_rules_numeric (tree : Nat) (data : RawCascadeData) (pseudos : List Nat)
 (valid : rawDataValid data = true) (named : PartRule)
 (member : named ∈ partRules tree data pseudos) : ruleNumericBounds named.rule := by
 simp only [rawDataValid,Bool.and_eq_true] at valid
 have admitted := part_lookup_admitted data.table data.part pseudos valid.2
 rcases List.mem_flatMap.mp member with ⟨group,hg,hm⟩
 rcases List.mem_map.mp hm with ⟨rule,hr,eq⟩
 subst named
 have good := List.all_eq_true.mp admitted group hg
 apply matched_numeric_bounds tree data.table group.2 good rule
 simpa [mapRules,rawMatchedRules] using hr

theorem slot_context_layers (pseudos : List Nat) (identity : Nat) (root : RawShadowRoot)
 (valid : root.styleData.toList.all rawDataValid = true) :
 (slotContext pseudos identity root).rules.Pairwise (fun a b => a.layer ≤ b.layer) := by
 cases data : root.styleData with
 | none => simp [slotContext,data]
 | some styles =>
   simp only [data,Option.toList_some,List.all_cons,List.all_nil,Bool.and_true] at valid
   have maps : rawMapValid styles.table styles.slotted = true := by
     simp only [rawDataValid,Bool.and_eq_true] at valid
     exact valid.1.2
   simpa [slotContext,data] using
     sorted_exact_map_layer_order (identity+1) styles styles.slotted pseudos maps

theorem slot_trace_layers (raw : RawProviderInput) (pseudos : List Nat)
 (valid : rawFieldsValid raw = true) (start : Option Nat) (slots : List InnerContext)
 (trace : SlotTrace raw pseudos start slots) :
 ∀ slot ∈ slots, slot.rules.Pairwise (fun a b => a.layer ≤ b.layer) := by
 induction trace with
 | endPath => simp
 | slot identity rootIdentity element root rest elementFound containing rootFound tail ih =>
   intro slot member
   rcases List.mem_cons.mp member with same | later
   · subst slot
     exact slot_context_layers pseudos rootIdentity root (raw_root_data_valid raw valid _ _ rootFound)
   · exact ih slot later

theorem shadow_context_bounds (raw : RawProviderInput) (pseudos : List Nat)
 (valid : rawFieldsValid raw = true) (identity : Nat) (root : RawShadowRoot)
 (host : RawElement) (found : raw.roots[identity]? = some root) :
 ∀ named ∈ (shadowOuterContext pseudos identity root host).rules, ruleNumericBounds named.rule := by
 have dataValid := raw_root_data_valid raw valid identity root found
 cases data : root.styleData with
 | none => simp [shadowOuterContext,data]
 | some styles =>
   simp only [data,Option.toList_some,List.all_cons,List.all_nil,Bool.and_true] at dataValid
   simpa [shadowOuterContext,data] using part_rules_numeric (identity+1) styles pseudos dataValid

theorem document_context_bounds (raw : RawProviderInput) (pseudos : List Nat)
 (valid : rawFieldsValid raw = true) (host : RawElement) :
 ∀ named ∈ (documentOuterContext raw pseudos host).rules, ruleNumericBounds named.rule := by
 simp only [rawFieldsValid,Bool.and_eq_true] at valid
 exact part_rules_numeric 0 raw.document pseudos valid.1.1.1.2

theorem outer_trace_bounds (raw : RawProviderInput) (pseudos : List Nat)
 (valid : rawFieldsValid raw = true) (identity : Nat) (contexts : List Context)
 (trace : OuterTrace raw pseudos identity contexts) :
 ∀ context ∈ contexts, ∀ named ∈ context.rules, ruleNumericBounds named.rule := by
 induction trace with
 | document identity inner host rootFound hostFound outside =>
   simpa using document_context_bounds raw pseudos valid host
 | shadow identity outerIdentity inner outer host rest rootFound hostFound outside outerFound tail ih =>
   intro context member
   rcases List.mem_cons.mp member with same | later
   · subst context
     exact shadow_context_bounds raw pseudos valid outerIdentity outer host outerFound
   · exact ih context later

theorem raw_slot_layer_order (raw : RawProviderInput) (pseudos : List Nat)
 (valid : rawFieldsValid raw = true) (fuel limit : Nat) (start : Option Nat)
 (slots : List InnerContext) (normalized : normalizeSlots raw pseudos fuel start = some slots) :
 (reverseSlotCollector limit 0 slots).Pairwise contextLayerLE :=
 inner_context_layer_order slots limit 0 (slot_trace_layers raw pseudos valid start slots
   (slot_normalization_sound raw pseudos fuel start slots normalized))

theorem raw_outer_layer_order (raw : RawProviderInput) (pseudos parts : List Nat)
 (valid : rawFieldsValid raw = true) (fuel identity limit : Nat) (contexts : List Context)
 (normalized : normalizeOuter raw pseudos fuel identity = some contexts) :
 (collectParts limit 1 parts contexts).Pairwise contextLayerLE := by
 rw [parts_refinement]
 exact outer_context_layer_order contexts limit 1 parts
   (outer_trace_bounds raw pseudos valid identity contexts
     (outer_normalization_sound raw pseudos fuel identity contexts normalized))


def hostDataRules (tree : Nat) (data : RawCascadeData) (pseudos : List Nat)
 (elementBacked : Bool) : List Rule :=
 mapRules tree data (pseudoMapLookup data.host pseudos) ++
 if elementBacked then mapRules tree data (pseudoMapLookup data.normal []) else []

theorem host_data_bounds (tree : Nat) (data : RawCascadeData) (pseudos : List Nat)
 (elementBacked : Bool) (valid : rawDataValid data = true) :
 ∀ rule ∈ hostDataRules tree data pseudos elementBacked, ruleNumericBounds rule := by
 simp only [rawDataValid,Bool.and_eq_true] at valid
 intro rule member
 rcases List.mem_append.mp member with host | normal
 · exact exact_map_numeric_bounds tree data data.host pseudos valid.1.1.2 rule host
 · cases elementBacked with
   | false => simp at normal
   | true => exact exact_map_numeric_bounds tree data data.normal [] valid.1.1.1.2 rule normal

theorem own_host_layer_order (raw : RawProviderInput) (pseudos : List Nat)
 (target : RawElement) (elementBacked : Bool) (rules : List Rule)
 (valid : rawFieldsValid raw = true)
 (normalized : normalizeOwnHost raw pseudos target elementBacked = some rules) :
 rules.Pairwise (fun a b => a.layer ≤ b.layer) := by
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
       exact sorted_rule_layers (hostDataRules (identity+1) styles pseudos elementBacked)
         (host_data_bounds (identity+1) styles pseudos elementBacked dataValid)

def containingDataRules (tree : Nat) (data : RawCascadeData) (pseudos parts : List Nat)
 (hasParts : Bool) : List Rule :=
 mapRules tree data (pseudoMapLookup data.normal pseudos) ++
 if hasParts then parts.flatMap fun name =>
   (partRules tree data pseudos).filterMap fun p => if p.name == name then some p.rule else none
 else []

theorem containing_data_bounds (tree : Nat) (data : RawCascadeData) (pseudos parts : List Nat)
 (hasParts : Bool) (valid : rawDataValid data = true) :
 ∀ rule ∈ containingDataRules tree data pseudos parts hasParts, ruleNumericBounds rule := by
 intro rule member
 rcases List.mem_append.mp member with normal | part
 · have mapValid : rawMapValid data.table data.normal = true := by
     simp only [rawDataValid,Bool.and_eq_true] at valid
     exact valid.1.1.1.2
   exact exact_map_numeric_bounds tree data data.normal pseudos mapValid rule normal
 · cases hasParts with
   | false => simp at part
   | true =>
     rcases List.mem_flatMap.mp part with ⟨name,hn,hp⟩
     rcases List.mem_filterMap.mp hp with ⟨named,hm,eq⟩
     split at eq
     · simp only [Option.some.injEq] at eq
       subst rule
       exact part_rules_numeric tree data pseudos valid named hm
     · contradiction

theorem containing_layer_order (raw : RawProviderInput) (pseudos : List Nat)
 (target : RawElement) (entries : List Entry) (document : Bool)
 (valid : rawFieldsValid raw = true)
 (normalized : normalizeContaining raw pseudos target = some (entries,document)) :
 entries.Pairwise contextLayerLE := by
 cases matchingContent : target.matchesContent with
 | false => simp [normalizeContaining,matchingContent] at normalized; rcases normalized with ⟨rfl,rfl⟩; simp
 | true =>
   cases containing : target.containingIgnoringSvgUse with
   | none => simp [normalizeContaining,matchingContent,containing] at normalized; rcases normalized with ⟨rfl,rfl⟩; simp
   | some identity =>
     cases found : raw.roots[identity]? with
     | none => simp [normalizeContaining,matchingContent,containing,found] at normalized
     | some root =>
       have dataValid := raw_root_data_valid raw valid identity root found
       cases data : root.styleData with
       | none =>
         simp [normalizeContaining,matchingContent,containing,found,data] at normalized
         rcases normalized with ⟨rfl,rfl⟩
         simp [localSort,originEntries]
       | some styles =>
         simp only [data,Option.toList_some,List.all_cons,List.all_nil,Bool.and_true] at dataValid
         simp [normalizeContaining,matchingContent,containing,found,data] at normalized
         rcases normalized with ⟨rfl,rfl⟩
         simpa [containingDataRules,atOrder,originEntries] using at_order_layer_sorted 0 _ (sorted_rule_layers
           (containingDataRules (identity+1) styles pseudos target.parts target.hasPartAttribute)
           (containing_data_bounds (identity+1) styles pseudos target.parts target.hasPartAttribute dataValid))

theorem origin_entries_zero (origin tree : Nat) (rules : List Rule) :
 ∀ entry ∈ originEntries origin tree rules, entry.order = 0 := by
 intro entry member
 rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
 rfl

theorem containing_shape (raw : RawProviderInput) (pseudos : List Nat)
 (target : RawElement) (entries : List Entry) (document : Bool)
 (normalized : normalizeContaining raw pseudos target = some (entries,document)) :
 (document = true → entries = []) ∧ (∀ entry ∈ entries, entry.order = 0) := by
 cases content : target.matchesContent with
 | false => simp [normalizeContaining,content] at normalized; rcases normalized with ⟨rfl,rfl⟩; simp
 | true =>
   cases containing : target.containingIgnoringSvgUse with
   | none => simp [normalizeContaining,content,containing] at normalized; rcases normalized with ⟨rfl,rfl⟩; simp
   | some identity =>
     cases found : raw.roots[identity]? with
     | none => simp [normalizeContaining,content,containing,found] at normalized
     | some root =>
       simp [normalizeContaining,content,containing,found] at normalized
       rcases normalized with ⟨rfl,rfl⟩
       exact ⟨by simp,origin_entries_zero _ _ _⟩

theorem containing_numeric_bounds (raw : RawProviderInput) (pseudos : List Nat)
 (target : RawElement) (entries : List Entry) (document : Bool)
 (valid : rawFieldsValid raw = true)
 (normalized : normalizeContaining raw pseudos target = some (entries,document)) :
 ∀ entry ∈ entries, ruleNumericBounds entry.rule := by
 cases content : target.matchesContent with
 | false => simp [normalizeContaining,content] at normalized; rcases normalized with ⟨rfl,rfl⟩; simp
 | true =>
   cases containing : target.containingIgnoringSvgUse with
   | none => simp [normalizeContaining,content,containing] at normalized; rcases normalized with ⟨rfl,rfl⟩; simp
   | some identity =>
     cases found : raw.roots[identity]? with
     | none => simp [normalizeContaining,content,containing,found] at normalized
     | some root =>
       have dataValid := raw_root_data_valid raw valid identity root found
       cases data : root.styleData with
       | none =>
         simp [normalizeContaining,content,containing,found,data] at normalized
         rcases normalized with ⟨rfl,rfl⟩
         simp [localSort,originEntries]
       | some styles =>
         simp only [data,Option.toList_some,List.all_cons,List.all_nil,Bool.and_true] at dataValid
         simp [normalizeContaining,content,containing,found,data] at normalized
         rcases normalized with ⟨rfl,rfl⟩
         intro entry member
         rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
         have hm := (sort_perm _ _).mem_iff.mp hr
         apply containing_data_bounds (identity+1) styles pseudos target.parts target.hasPartAttribute dataValid rule
         simpa [containingDataRules] using hm

theorem document_layer_order (raw : RawProviderInput) (pseudos : List Nat)
 (valid : rawFieldsValid raw = true) :
 (originEntries 3 0 (sortedMapRules 0 raw.document
   (pseudoMapLookup raw.document.normal pseudos))).Pairwise contextLayerLE := by
 simp only [rawFieldsValid,Bool.and_eq_true] at valid
 have dataValid := valid.1.1.1.2
 simp only [rawDataValid,Bool.and_eq_true] at dataValid
 exact at_order_layer_sorted 0 _ (sorted_exact_map_layer_order 0 raw.document
   raw.document.normal pseudos dataValid.1.1.1.2)

theorem document_numeric_bounds (raw : RawProviderInput) (pseudos : List Nat)
 (valid : rawFieldsValid raw = true) :
 ∀ entry ∈ originEntries 3 0 (sortedMapRules 0 raw.document
   (pseudoMapLookup raw.document.normal pseudos)), ruleNumericBounds entry.rule := by
 simp only [rawFieldsValid,Bool.and_eq_true] at valid
 have dataValid := valid.1.1.1.2
 simp only [rawDataValid,Bool.and_eq_true] at dataValid
 intro entry member
 rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
 exact exact_map_numeric_bounds 0 raw.document raw.document.normal pseudos dataValid.1.1.1.2 rule
   ((sort_perm _ _).mem_iff.mp hr)

def normalizedAuthorGroups (raw : RawProviderInput) (target : RawElement)
 (pseudos : List Nat) (host : List Rule) (slots : List InnerContext)
 (containing : List Entry × Bool) (contexts : List Context) (limit : Nat) : List Entry :=
 let document := if containing.2 then originEntries 3 0
   (sortedMapRules 0 raw.document (pseudoMapLookup raw.document.normal pseudos)) else []
 let targetTree := target.containingShadow.map (·+1) |>.getD 0
 let inlineRules := raw.inlineStyle.toList.map fun rule =>
   plainRule targetTree 0 {rule with layer := 65535,flags := 0}
 hostCollector limit slots.length host ++ reverseSlotCollector limit 0 slots ++
 containing.1 ++ document ++ originEntries 3 targetTree inlineRules ++
 collectParts limit 1 target.parts contexts

theorem raw_author_group_order (raw : RawProviderInput) (target : RawElement)
 (pseudos : List Nat) (host : List Rule) (slots : List InnerContext)
 (containing : List Entry × Bool) (contexts : List Context) (elementBacked : Bool)
 (slotFuel limit : Nat) (valid : rawFieldsValid raw = true)
 (hostMade : normalizeOwnHost raw pseudos target elementBacked = some host)
 (slotsMade : normalizeSlots raw pseudos slotFuel target.assignedSlot = some slots)
 (containingMade : normalizeContaining raw pseudos target = some containing)
 (outerMade : contexts = [] ∨ ∃ root fuel, normalizeOuter raw pseudos fuel root = some contexts) :
 (normalizedAuthorGroups raw target pseudos host slots containing contexts limit).Pairwise contextLayerLE := by
 have shape := containing_shape raw pseudos target containing.1 containing.2 containingMade
 have numeric := containing_numeric_bounds raw pseudos target containing.1 containing.2 valid containingMade
 have localSorted := containing_layer_order raw pseudos target containing.1 containing.2 valid containingMade
 have docSorted := document_layer_order raw pseudos valid
 have docNumeric := document_numeric_bounds raw pseudos valid
 unfold normalizedAuthorGroups
 simp only
 have outerBounds : ∀ context ∈ contexts, ∀ named ∈ context.rules, ruleNumericBounds named.rule := by
   rcases outerMade with empty | made
   · subst contexts; simp
   · rcases made with ⟨root,fuel,normalized⟩
     exact outer_trace_bounds raw pseudos valid root contexts
       (outer_normalization_sound raw pseudos fuel root contexts normalized)
 have middleSorted : (containing.1 ++ if containing.2 then originEntries 3 0
     (sortedMapRules 0 raw.document (pseudoMapLookup raw.document.normal pseudos)) else []).Pairwise contextLayerLE := by
   cases doc : containing.2 with
   | false => simpa [doc] using localSorted
   | true => simpa [doc,shape.1 doc] using docSorted
 have middleZero : ∀ entry ∈ containing.1 ++ (if containing.2 then originEntries 3 0
     (sortedMapRules 0 raw.document (pseudoMapLookup raw.document.normal pseudos)) else []), entry.order = 0 := by
   intro entry member
   rcases List.mem_append.mp member with localMember | document
   · exact shape.2 entry localMember
   · split at document
     · exact origin_entries_zero _ _ _ entry document
     · simp at document
 have middleLayer : ∀ entry ∈ containing.1 ++ (if containing.2 then originEntries 3 0
     (sortedMapRules 0 raw.document (pseudoMapLookup raw.document.normal pseudos)) else []), entry.rule.layer ≤ 65535 := by
   intro entry member
   rcases List.mem_append.mp member with localMember | document
   · have := (numeric entry localMember).1; omega
   · split at document
     · have := (docNumeric entry document).1; omega
     · simp at document
 have inlineShape : ∀ entry ∈ originEntries 3 (target.containingShadow.map (·+1) |>.getD 0)
     (raw.inlineStyle.toList.map fun rule => plainRule (target.containingShadow.map (·+1) |>.getD 0) 0
       {rule with layer := 65535,flags := 0}), entry.order = 0 ∧ entry.rule.layer = 65535 := by
   intro entry member
   rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
   rcases List.mem_map.mp hr with ⟨block,hb,rfl⟩
   exact ⟨rfl,rfl⟩
 have result := author_group_context_order host slots _ _ contexts target.parts limit
   (own_host_layer_order raw pseudos target elementBacked host valid hostMade)
   (slot_trace_layers raw pseudos valid target.assignedSlot slots
     (slot_normalization_sound raw pseudos slotFuel target.assignedSlot slots slotsMade))
   middleSorted middleZero middleLayer inlineShape outerBounds
 simpa only [List.append_assoc] using result

#print axioms raw_slot_layer_order
#print axioms raw_outer_layer_order
end ShadowOrder
