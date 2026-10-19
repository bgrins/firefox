import RawLayers
namespace ShadowOrder

def directSlotRows (raw : RawProviderInput) (pseudos : List Nat) :
 Nat → Option Nat → Nat → Nat → Option (List (List Entry))
 | _, none, _, _ => some []
 | 0, some _, _, _ => none
 | fuel+1, some slotIdentity, index, limit => do
   let slot ← raw.elements[slotIdentity]?
   let rootIdentity ← slot.containingShadow
   let root ← raw.roots[rootIdentity]?
   let rows ← directSlotRows raw pseudos fuel slot.assignedSlot (index+1) limit
   let rules := root.styleData.toList.flatMap fun data =>
     sortedMapRules (rootIdentity+1) data (pseudoMapLookup data.slotted pseudos)
   return (if index+1 ≤ limit then atOrder (-Int.ofNat (index+1)) rules else [])::rows

def directSlotReference (raw : RawProviderInput) (pseudos : List Nat) (fuel limit : Nat)
 (start : Option Nat) : Option (List Entry) :=
 (directSlotRows raw pseudos fuel start 0 limit).map fun rows => rows.reverse.flatten

theorem direct_slot_rows_refinement (raw : RawProviderInput) (pseudos : List Nat)
 (fuel index limit : Nat) (start : Option Nat) (slots : List InnerContext)
 (normalized : normalizeSlots raw pseudos fuel start = some slots) :
 directSlotRows raw pseudos fuel start index limit = some (slotReference limit index slots) := by
 induction fuel generalizing start slots index with
 | zero =>
   cases start
   · simp [normalizeSlots] at normalized; subst slots; rfl
   · simp [normalizeSlots] at normalized
 | succ fuel ih =>
   cases start with
   | none => simp [normalizeSlots] at normalized; subst slots; rfl
   | some identity =>
     cases elementFound : raw.elements[identity]? with
     | none => simp [normalizeSlots,elementFound] at normalized
     | some element =>
       cases containing : element.containingShadow with
       | none => simp [normalizeSlots,elementFound,containing] at normalized
       | some rootIdentity =>
         cases rootFound : raw.roots[rootIdentity]? with
         | none => simp [normalizeSlots,elementFound,containing,rootFound] at normalized
         | some root =>
           cases tail : normalizeSlots raw pseudos fuel element.assignedSlot with
           | none => simp [normalizeSlots,elementFound,containing,tail] at normalized
           | some rest =>
             simp [normalizeSlots,elementFound,containing,rootFound,tail] at normalized
             subst slots
             simp [directSlotRows,elementFound,containing,rootFound,ih (index+1) _ _ tail,slotReference,slotContext]

theorem direct_slot_reference_refinement (raw : RawProviderInput) (pseudos : List Nat)
 (fuel limit : Nat) (start : Option Nat) (slots : List InnerContext)
 (normalized : normalizeSlots raw pseudos fuel start = some slots) :
 directSlotReference raw pseudos fuel limit start = some (reverseSlotCollector limit 0 slots) := by
 rw [slots_refinement]
 simp [directSlotReference,direct_slot_rows_refinement raw pseudos fuel 0 limit start slots normalized]

#print axioms direct_slot_reference_refinement
end ShadowOrder
