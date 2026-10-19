import IndexAllocation
namespace NativeAttributeIndices
open QualifiedAttributes

def ownership (state : State) : Prop :=
 ∀ node index, lookup state.maps node = some index →
   state.infos[index]? = some (some node) ∨ state.infos[index]? = some none

theorem enter_preserves_node_ownership (state : State) (valid : coherent state)
 (owned : ownership state) (node : Node) : ownership (enter state node).1 := by
 unfold enter
 cases found : lookup state.maps node with
 | some index => exact owned
 | none =>
   intro other index hit
   rw [index_bucket_insert_is_tagged_write] at hit
   by_cases same : other = node
   · simp [same] at hit
     subst index
     subst other
     left
     simp [valid.1]
   · simp [same] at hit
     have bound : index < state.infos.length := by rw [← valid.1]; exact valid.2.1 other index hit
     simpa only [List.getElem?_append_left bound] using owned other index hit

theorem finish_preserves_node_ownership (state : State) (valid : coherent state)
 (owned : ownership state) : ownership (finishTop state) := by
 unfold finishTop
 cases shape : state.stack with
 | nil => exact owned
 | cons popped rest =>
   intro node index hit
   by_cases same : popped = index
   · right
     have bound : popped < state.infos.length := by
       rw [← valid.1]
       exact valid.2.2.2 popped (by simp [shape])
     simpa only [same] using List.getElem?_set_self (a := (none : Option Node)) bound
   · simpa only [List.getElem?_set_ne same] using owned node index hit

theorem initial_ownership : ownership initial := by
 intro node index hit
 cases node <;> simp [initial,lookup,emptyMaps] at hit

theorem arbitrary_index_history_preserves_identity (operations : List Operation)
 (state : State) (valid : coherent state ∧ ownership state) :
 coherent (execute operations state) ∧ ownership (execute operations state) := by
 induction operations generalizing state with
 | nil => exact valid
 | cons operation rest ih =>
   apply ih
   cases operation with
   | enter node => exact ⟨enter_preserves_coherence state valid.1 node,
       enter_preserves_node_ownership state valid.1 valid.2 node⟩
   | finish => exact ⟨finish_preserves_coherence state valid.1,
       finish_preserves_node_ownership state valid.1 valid.2⟩
   | reset => exact ⟨initial_coherent,initial_ownership⟩

theorem fresh_histories_return_own_node_or_finished_marker (operations : List Operation)
 (node : Node) (index : Nat) (found : lookup (execute operations initial).maps node = some index) :
 (execute operations initial).infos[index]? = some (some node) ∨
 (execute operations initial).infos[index]? = some none :=
 (arbitrary_index_history_preserves_identity operations initial ⟨initial_coherent,initial_ownership⟩).2
   node index found

end NativeAttributeIndices
