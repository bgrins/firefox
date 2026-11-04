import RuleAdmission
import Numeric
namespace ShadowOrder
set_option maxRecDepth 4096
set_option maxHeartbeats 800000

def collectParts (limit rank : Nat) (parts : List Nat) : List Context → List Entry
 | [] => []
 | c::rest =>
   if parts.isEmpty then []
   else if c.mapPresent then
     if rank ≤ limit then
       atOrder (Int.ofNat rank) (localSort completeLocalKey (matching c parts)) ++
       match nextOuter limit rank with
       | none => []
       | some next => collectParts limit next (exported c parts) rest
     else []
   else collectParts limit rank (exported c parts) rest

def physicalReference (limit rank : Nat) (parts : List Nat) : List Context → List Entry
 | [] => []
 | c::rest =>
   if parts.isEmpty then []
   else
     let here := if c.mapPresent && rank ≤ limit then
       atOrder (Int.ofNat rank) (localSort completeLocalKey (matching c parts)) else []
     here ++ physicalReference limit (rank + if c.mapPresent then 1 else 0)
       (exported c parts) rest

theorem reference_beyond (contexts : List Context) (limit rank : Nat)
    (parts : List Nat) (h : limit < rank) :
    physicalReference limit rank parts contexts = [] := by
 induction contexts generalizing rank parts with
 | nil => rfl
 | cons c rest ih =>
   simp only [physicalReference]
   split
   · rfl
   · have hr : limit < rank + (if c.mapPresent then 1 else 0) := by split <;> omega
     rw [ih _ _ hr]
     simp [show ¬rank ≤ limit by omega]

theorem parts_refinement (contexts : List Context) (limit rank : Nat) (parts : List Nat) :
    collectParts limit rank parts contexts = physicalReference limit rank parts contexts := by
 induction contexts generalizing rank parts with
 | nil => rfl
 | cons c rest ih =>
   simp only [collectParts, physicalReference]
   by_cases hp : parts.isEmpty
   · simp [hp]
   · simp only [hp, Bool.false_eq_true, ↓reduceIte]
     cases hm : c.mapPresent
     · simp [hm, ih]
     · simp only [hm, ↓reduceIte, Bool.true_and, decide_eq_true_eq, Nat.add_zero]
       by_cases hbound : rank ≤ limit
       · simp only [hbound, ↓reduceIte]
         by_cases hnext : rank < limit
         · simp [nextOuter,hnext,ih]
         · have hend : rank = limit := by omega
           simp [nextOuter,hnext, reference_beyond rest limit (rank+1) (exported c parts) (by omega)]
       · have hfar : limit < rank+1 := by omega
         simp [hbound, reference_beyond rest limit (rank+1) (exported c parts) hfar]

structure InnerContext where
 identity : Nat
 rules : List Rule
 deriving DecidableEq, Repr

def nearSlots (limit index : Nat) : List InnerContext → List Entry
 | [] => []
 | s::rest =>
   let here := match inner limit index with
     | none => []
     | some order => atOrder order s.rules
   here ++ nearSlots limit (index+1) rest

def reverseSlotCollector (limit index : Nat) : List InnerContext → List Entry
 | [] => []
 | s::rest =>
   reverseSlotCollector limit (index+1) rest ++
   match inner limit index with
   | none => []
   | some order => atOrder order s.rules

def slotReference (limit index : Nat) : List InnerContext → List (List Entry)
 | [] => []
 | s::rest =>
   (if index+1 ≤ limit then atOrder (-Int.ofNat (index+1)) s.rules else []) ::
     slotReference limit (index+1) rest

theorem slots_refinement (slots : List InnerContext) (limit index : Nat) :
    reverseSlotCollector limit index slots = (slotReference limit index slots).reverse.flatten := by
 induction slots generalizing index with
 | nil => rfl
 | cons s rest ih =>
   simp only [reverseSlotCollector,slotReference,List.reverse_cons,List.flatten_append,List.flatten_cons,List.flatten_nil,List.append_nil]
   rw [ih]
   congr 1
   simp only [inner]
   by_cases h : index < limit <;> simp [h, show (index+1 ≤ limit) ↔ index < limit by omega]

def hostCollector (limit count : Nat) (rules : List Rule) : List Entry :=
 match inner limit count with
 | none => []
 | some order => atOrder order rules

def hostReference (limit count : Nat) (rules : List Rule) : List Entry :=
 if count+1 ≤ limit then atOrder (-Int.ofNat (count+1)) rules else []

theorem host_refinement (limit count : Nat) (rules : List Rule) :
 hostCollector limit count rules = hostReference limit count rules := by
 simp only [hostCollector,hostReference,inner]
 by_cases h : count < limit <;> simp [h, show (count+1 ≤ limit) ↔ count < limit by omega]

def eligibleCount (contexts : List Context) : Nat :=
 (contexts.filter Context.mapPresent).length

def mathematicalRank (before : List Context) : Nat := eligibleCount before + 1

theorem eligible_append (a b : List Context) :
 eligibleCount (a++b) = eligibleCount a + eligibleCount b := by
 simp [eligibleCount,List.filter_append]

theorem strict_physical_order (before middle : List Context) (earlier : Context)
 (h : earlier.mapPresent = true) :
 mathematicalRank before < mathematicalRank (before ++ earlier::middle) := by
 simp [mathematicalRank,eligibleCount,List.filter_append,h]

theorem missing_map_does_not_consume_rank (before : List Context) (c : Context)
 (h : c.mapPresent = false) :
 mathematicalRank (before++[c]) = mathematicalRank before := by
 simp [mathematicalRank,eligibleCount,List.filter_append,h]

#print axioms parts_refinement
#print axioms slots_refinement
#print axioms host_refinement
#print axioms strict_physical_order
end ShadowOrder
