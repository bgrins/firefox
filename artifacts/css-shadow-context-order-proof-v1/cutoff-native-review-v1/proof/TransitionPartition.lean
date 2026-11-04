import ImportantPartition
import SortSkip
namespace ShadowOrder
structure PartitionState where
 buckets : Buckets
 transition : Option Entry
 deriving DecidableEq, Repr

def treePartitionStep (state : PartitionState) (entry : Entry) : PartitionState :=
 let next := partitionStep state.buckets entry
 if entry.origin = 7 && next.found then
   ⟨{next with normal := state.buckets.normal},some entry⟩
 else ⟨next,state.transition⟩

def treePartition : List Entry → PartitionState → PartitionState
 | [], state => state
 | entry::rest, state => treePartition rest (treePartitionStep state entry)

theorem tree_partition_without_transitions (entries : List Entry) (state : PartitionState)
 (h : ∀ e ∈ entries, e.origin ≠ 7) :
 treePartition entries state = ⟨partitionLoop entries state.buckets,state.transition⟩ := by
 induction entries generalizing state with
 | nil => rfl
 | cons e rest ih =>
   have he := h e (by simp)
   have hr : ∀ e ∈ rest, e.origin ≠ 7 := fun e he => h e (by simp [he])
   simp [treePartition,treePartitionStep,he,ih _ hr,partitionLoop]

theorem tree_partition_append (a b : List Entry) (state : PartitionState) :
 treePartition (a++b) state = treePartition b (treePartition a state) := by
 induction a generalizing state with
 | nil => rfl
 | cons e rest ih => simp [treePartition,ih]

def emptyBuckets : Buckets := ⟨[],[],[],[],false⟩
def emptyPartition : PartitionState := ⟨emptyBuckets,none⟩

def allPathItems (sortImportant : List Entry → List Entry) (state : PartitionState) :
 List (Entry × Bool) :=
 state.buckets.normal.map (fun e => (e,false)) ++
 (sortImportant state.buckets.author).map (fun e => (e,true)) ++
 (sortImportant state.buckets.user).map (fun e => (e,true)) ++
 (sortImportant state.buckets.ua).map (fun e => (e,true)) ++
 state.transition.toList.map (fun e => (e,false))

def directPath (sortImportant : List Entry → List Entry)
 (body : List Entry) (transition : Option Entry) : List (Entry × Bool) :=
 body.map (fun e => (e,false)) ++
 (sortImportant (body.filter (fun e => hasImportant e && e.origin == 3))).map (fun e => (e,true)) ++
 (sortImportant (body.filter (fun e => hasImportant e && e.origin == 1))).map (fun e => (e,true)) ++
 (sortImportant (body.filter (fun e => hasImportant e && e.origin == 0))).map (fun e => (e,true)) ++
 transition.toList.map (fun e => (e,false))

theorem tree_partition_no_tail (sortImportant : List Entry → List Entry)
 (body : List Entry) (h : ∀ e ∈ body, e.origin ≠ 7) :
 allPathItems sortImportant (treePartition body emptyPartition) =
 directPath sortImportant body none := by
 rw [tree_partition_without_transitions _ _ h,partition_refinement]
 simp [allPathItems,directPath,directBuckets,emptyPartition,emptyBuckets]

theorem tree_partition_transition_tail (sortImportant : List Entry → List Entry)
 (sortEmpty : sortImportant [] = []) (body : List Entry) (transition : Entry)
 (bodyNoTransition : ∀ e ∈ body, e.origin ≠ 7)
 (origin : transition.origin = 7) (normalOnly : hasImportant transition = false) :
 allPathItems sortImportant (treePartition (body++[transition]) emptyPartition) =
 directPath sortImportant body (some transition) := by
 rw [tree_partition_append,tree_partition_without_transitions _ _ bodyNoTransition,partition_refinement]
 simp only [treePartition,treePartitionStep,partitionStep,normalOnly,↓reduceIte]
 cases found : body.any hasImportant
 · have authorEmpty : body.filter (fun e => hasImportant e && e.origin == 3) = [] := by
     apply List.filter_eq_nil_iff.mpr
     intro e he
     have no := List.any_eq_false.mp found e he
     simp [no]
   have userEmpty : body.filter (fun e => hasImportant e && e.origin == 1) = [] := by
     apply List.filter_eq_nil_iff.mpr
     intro e he
     have no := List.any_eq_false.mp found e he
     simp [no]
   have uaEmpty : body.filter (fun e => hasImportant e && e.origin == 0) = [] := by
     apply List.filter_eq_nil_iff.mpr
     intro e he
     have no := List.any_eq_false.mp found e he
     simp [no]
   simp [allPathItems,directPath,directBuckets,emptyPartition,emptyBuckets,origin,found,
     authorEmpty,userEmpty,uaEmpty,sortEmpty,List.map_append]
 · simp [allPathItems,directPath,directBuckets,emptyPartition,emptyBuckets,origin,found]

#print axioms tree_partition_no_tail
#print axioms tree_partition_transition_tail
end ShadowOrder
