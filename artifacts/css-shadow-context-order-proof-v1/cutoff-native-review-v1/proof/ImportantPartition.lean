import Base
namespace ShadowOrder
set_option maxHeartbeats 800000
structure Buckets where
 normal : List Entry
 author : List Entry
 user : List Entry
 ua : List Entry
 found : Bool
 deriving DecidableEq, Repr

def hasImportant (entry : Entry) : Bool := entry.rule.declarations.any Declaration.important

def partitionStep (state : Buckets) (entry : Entry) : Buckets :=
 let state := {state with normal := state.normal ++ [entry]}
 if hasImportant entry then
   let state := {state with found := true}
   if entry.origin = 3 then {state with author := state.author ++ [entry]}
   else if entry.origin = 1 then {state with user := state.user ++ [entry]}
   else if entry.origin = 0 then {state with ua := state.ua ++ [entry]}
   else state
 else state

def partitionLoop : List Entry → Buckets → Buckets
 | [], state => state
 | entry::rest, state => partitionLoop rest (partitionStep state entry)

def directBuckets (entries : List Entry) (state : Buckets) : Buckets :=
 {normal := state.normal ++ entries,
  author := state.author ++ entries.filter (fun e => hasImportant e && e.origin == 3),
  user := state.user ++ entries.filter (fun e => hasImportant e && e.origin == 1),
  ua := state.ua ++ entries.filter (fun e => hasImportant e && e.origin == 0),
  found := state.found || entries.any hasImportant}

theorem partition_refinement (entries : List Entry) (state : Buckets) :
 partitionLoop entries state = directBuckets entries state := by
 induction entries generalizing state with
 | nil => simp [partitionLoop,directBuckets]
 | cons e rest ih =>
   simp only [partitionLoop,ih,directBuckets,partitionStep,List.filter_cons,List.any_cons]
   cases hi : hasImportant e <;>
   by_cases ha : e.origin = 3 <;> by_cases hu : e.origin = 1 <;> by_cases hg : e.origin = 0 <;>
     simp_all [List.append_assoc]

#print axioms partition_refinement
end ShadowOrder
