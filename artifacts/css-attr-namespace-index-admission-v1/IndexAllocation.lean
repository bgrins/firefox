import IndexBuckets
namespace NativeAttributeIndices
open QualifiedAttributes

structure State where
 maps : IndexMaps
 count : Nat
 infos : List (Option Node)
 stack : List Nat

def coherent (state : State) : Prop :=
 state.count = state.infos.length ∧
 (∀ node index, lookup state.maps node = some index → index < state.count) ∧
 (∀ left right index, lookup state.maps left = some index →
   lookup state.maps right = some index → left = right) ∧
 (∀ index ∈ state.stack, index < state.count)

def enter (state : State) (node : Node) : State × Nat :=
 match lookup state.maps node with
 | some index => (state,index)
 | none => (⟨insert state.maps node state.count,state.count+1,
     state.infos ++ [some node],state.count :: state.stack⟩,state.count)

theorem occupied_entry_reuses_index (state : State) (node : Node) (index : Nat)
 (occupied : lookup state.maps node = some index) : enter state node = (state,index) := by
 simp [enter,occupied]

theorem enter_preserves_coherence (state : State) (valid : coherent state) (node : Node) :
 coherent (enter state node).1 := by
 rcases valid with ⟨length,range,unique,stack⟩
 unfold enter
 cases found : lookup state.maps node with
 | some index => exact ⟨length,range,unique,stack⟩
 | none =>
   refine ⟨by simp [length],?_,?_,?_⟩
   · intro other index hit
     rw [index_bucket_insert_is_tagged_write] at hit
     by_cases same : other = node
     · simp [same] at hit
       subst index
       exact Nat.lt_succ_self _
     · simp [same] at hit
       exact Nat.lt_trans (range other index hit) (Nat.lt_succ_self _)
   · intro left right index lh rh
     rw [index_bucket_insert_is_tagged_write] at lh rh
     by_cases l : left = node <;> by_cases r : right = node
     · exact l.trans r.symm
     · simp [l] at lh
       simp [r] at rh
       have bound := range right index rh
       omega
     · simp [l] at lh
       simp [r] at rh
       have bound := range left index lh
       omega
     · simp [l] at lh
       simp [r] at rh
       exact unique left right index lh rh
   · intro index member
     simp only [List.mem_cons] at member
     rcases member with rfl | old
     · exact Nat.lt_succ_self _
     · exact Nat.lt_trans (stack index old) (Nat.lt_succ_self _)

def finishTop (state : State) : State :=
 match state.stack with
 | [] => state
 | index :: rest => { state with infos := state.infos.set index none, stack := rest }

theorem finish_preserves_coherence (state : State) (valid : coherent state) :
 coherent (finishTop state) := by
 rcases valid with ⟨length,range,unique,stack⟩
 unfold finishTop
 cases shape : state.stack with
 | nil => exact ⟨length,range,unique,stack⟩
 | cons index rest =>
   refine ⟨by simpa using length,range,unique,?_⟩
   intro other member
   exact stack other (by simp [shape,member])

def initial : State := ⟨emptyMaps,0,[],[]⟩

theorem initial_coherent : coherent initial := by
 refine ⟨rfl,?_,?_,?_⟩
 · intro node index hit
   cases node <;> simp [initial,lookup,emptyMaps] at hit
 · intro left right index hit
   cases left <;> simp [initial,lookup,emptyMaps] at hit
 · intro index member
   simp [initial] at member

inductive Operation where
 | enter (node : Node)
 | finish
 | reset

def step (state : State) : Operation → State
 | .enter node => (enter state node).1
 | .finish => finishTop state
 | .reset => initial

def execute (operations : List Operation) (state : State) := operations.foldl step state

theorem arbitrary_index_history_coherent (operations : List Operation)
 (state : State) (valid : coherent state) : coherent (execute operations state) := by
 induction operations generalizing state with
 | nil => exact valid
 | cons operation rest ih =>
   apply ih
   cases operation with
   | enter node => exact enter_preserves_coherence state valid node
   | finish => exact finish_preserves_coherence state valid
   | reset => exact initial_coherent

theorem fresh_index_history_allocates_distinct_nodes_in_range (operations : List Operation) :
 coherent (execute operations initial) := arbitrary_index_history_coherent operations initial initial_coherent

theorem namespace_nodes_cannot_share_allocated_index (operations : List Operation)
 (name left right index : Nat) (different : left ≠ right)
 (leftFound : lookup (execute operations initial).maps (.attr ⟨name,left⟩) = some index)
 (rightFound : lookup (execute operations initial).maps (.attr ⟨name,right⟩) = some index) : False := by
 have unique := (fresh_index_history_allocates_distinct_nodes_in_range operations).2.2.1
 exact distinct_namespace_nodes_are_distinct name left right different
   (unique _ _ index leftFound rightFound)

theorem bounded_count_increment (state : State) (node : Node) (limit : Nat)
 (room : state.count < limit) : (enter state node).1.count ≤ limit := by
 unfold enter
 cases lookup state.maps node <;> simp <;> omega

end NativeAttributeIndices
