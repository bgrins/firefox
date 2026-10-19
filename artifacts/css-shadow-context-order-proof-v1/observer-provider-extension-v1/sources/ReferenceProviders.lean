import RawOuterReference
import RawSlotReference
namespace ShadowOrder

def referenceHostRules (raw : RawProviderInput) (target : RawElement) (pseudos : List Nat)
 (elementBacked : Bool) : Option (List Rule) := do
 match target.ownShadow with
 | none => return []
 | some identity =>
   let root ← raw.roots[identity]?
   match root.styleData with
   | none => return []
   | some data =>
     return localSort completeLocalKey
       (mapRules (identity+1) data (pseudoMapLookup data.host pseudos) ++
        if elementBacked then mapRules (identity+1) data (pseudoMapLookup data.normal []) else [])

def referenceContaining (raw : RawProviderInput) (target : RawElement) (pseudos : List Nat) :
 Option (List Entry × Bool) := do
 if target.matchesContent then
   match target.containingIgnoringSvgUse with
   | none => return ([],true)
   | some identity =>
     let root ← raw.roots[identity]?
     match root.styleData with
     | none => return ([],false)
     | some data =>
       let rules := mapRules (identity+1) data (pseudoMapLookup data.normal pseudos)
       let ownParts := if target.hasPartAttribute then
         directPartRules (identity+1) data pseudos target.parts else []
       return (atOrder 0 (localSort completeLocalKey (rules ++ ownParts)),false)
 else return ([],false)

theorem reference_host_rules (raw : RawProviderInput) (target : RawElement) (pseudos : List Nat)
 (elementBacked : Bool) : referenceHostRules raw target pseudos elementBacked =
 normalizeOwnHost raw pseudos target elementBacked := by
 cases own : target.ownShadow with
 | none => simp [referenceHostRules,normalizeOwnHost,own]
 | some identity =>
   cases found : raw.roots[identity]? with
   | none => simp [referenceHostRules,normalizeOwnHost,own,found]
   | some root =>
     cases data : root.styleData <;>
       simp [referenceHostRules,normalizeOwnHost,own,found,data,localSort]

theorem matching_filter_map (rules : List PartRule) (name : Nat) :
 (rules.filter fun p => p.name == name).map PartRule.rule =
 rules.filterMap (fun p => if p.name == name then some p.rule else none) := by
 induction rules with
 | nil => rfl
 | cons rule rest ih =>
   by_cases same : rule.name = name <;> simp [same,ih]

theorem reference_containing (raw : RawProviderInput) (target : RawElement) (pseudos : List Nat) :
 referenceContaining raw target pseudos = normalizeContaining raw pseudos target := by
 cases content : target.matchesContent with
 | false => simp [referenceContaining,normalizeContaining,content]
 | true =>
   cases containing : target.containingIgnoringSvgUse with
   | none => simp [referenceContaining,normalizeContaining,content,containing]
   | some identity =>
     cases found : raw.roots[identity]? with
     | none => simp [referenceContaining,normalizeContaining,content,containing,found]
     | some root =>
       cases data : root.styleData <;>
         simp [referenceContaining,normalizeContaining,content,containing,found,data,
           localSort,originEntries,atOrder,directPartRules,matching_filter_map]

def directAuthorReference (raw : RawProviderInput) (target : RawElement)
 (pseudos : List Nat) (elementBacked : Bool) (limit : Nat) : Option (List Entry) := do
 let rows ← directSlotRows raw pseudos (raw.elements.length+1) target.assignedSlot 0 limit
 let host ← referenceHostRules raw target pseudos elementBacked
 let containing ← referenceContaining raw target pseudos
 let outer ← if target.hasPartAttribute then
   match target.containingShadow with
   | none => some []
   | some identity => directOuterReference raw pseudos (raw.roots.length+1) identity limit 1 target.parts
   else some []
 let doc := if containing.2 then atOrder 0
   (sortedMapRules 0 raw.document (pseudoMapLookup raw.document.normal pseudos)) else []
 let targetTree := target.containingShadow.map (·+1) |>.getD 0
 let inlineRules := atOrder 0 (raw.inlineStyle.toList.map fun rule =>
   plainRule targetTree 0 {rule with layer := 65535,flags := 0})
 let own := if rows.length+1 ≤ limit then atOrder (-Int.ofNat (rows.length+1)) host else []
 return own ++ rows.reverse.flatten ++ containing.1 ++ doc ++ inlineRules ++ outer

theorem slot_reference_length (slots : List InnerContext) (limit index : Nat) :
 (slotReference limit index slots).length = slots.length := by
 induction slots generalizing index with
 | nil => rfl
 | cons slot rest ih => simp [slotReference,ih]

def outerProviderChoice (raw : RawProviderInput) (target : RawElement) (pseudos : List Nat) : Option (List Context) :=
 if target.hasPartAttribute then
   match target.containingShadow with
   | none => some []
   | some identity => normalizeOuter raw pseudos (raw.roots.length+1) identity
 else some []

theorem direct_author_reference_refinement (raw : RawProviderInput) (target : RawElement)
 (pseudos : List Nat) (elementBacked : Bool) (limit : Nat) (slots : List InnerContext)
 (host : List Rule) (containing : List Entry × Bool) (contexts : List Context)
 (slotsMade : normalizeSlots raw pseudos (raw.elements.length+1) target.assignedSlot = some slots)
 (hostMade : normalizeOwnHost raw pseudos target elementBacked = some host)
 (containingMade : normalizeContaining raw pseudos target = some containing)
 (outerMade : outerProviderChoice raw target pseudos = some contexts) :
 directAuthorReference raw target pseudos elementBacked limit =
 some (normalizedAuthorGroups raw target pseudos host slots containing contexts limit) := by
 have rows := direct_slot_rows_refinement raw pseudos (raw.elements.length+1) 0 limit target.assignedSlot slots slotsMade
 cases partFlag : target.hasPartAttribute with
 | false =>
   simp [outerProviderChoice,partFlag] at outerMade
   subst contexts
   cases doc : containing.2 <;>
     simp [directAuthorReference,rows,reference_host_rules,reference_containing,hostMade,containingMade,
       partFlag,normalizedAuthorGroups,doc,slot_reference_length,host_refinement,hostReference,slots_refinement,
       originEntries,atOrder,collectParts]
 | true =>
   cases outerRoot : target.containingShadow with
   | none =>
     simp [outerProviderChoice,partFlag,outerRoot] at outerMade
     subst contexts
     cases doc : containing.2 <;>
       simp [directAuthorReference,rows,reference_host_rules,reference_containing,hostMade,containingMade,
         partFlag,outerRoot,normalizedAuthorGroups,doc,slot_reference_length,host_refinement,hostReference,slots_refinement,
         originEntries,atOrder,collectParts]
   | some identity =>
     simp only [outerProviderChoice,partFlag,↓reduceIte,outerRoot] at outerMade
     have outerRef := direct_outer_reference_refinement raw pseudos target.parts
       (raw.roots.length+1) identity limit 1 contexts outerMade
     cases doc : containing.2 <;>
       simp [directAuthorReference,rows,reference_host_rules,reference_containing,hostMade,containingMade,
         partFlag,outerRoot,outerRef,normalizedAuthorGroups,doc,slot_reference_length,host_refinement,hostReference,
         slots_refinement,originEntries,atOrder,parts_refinement]

#print axioms reference_containing
#print axioms reference_host_rules
end ShadowOrder
