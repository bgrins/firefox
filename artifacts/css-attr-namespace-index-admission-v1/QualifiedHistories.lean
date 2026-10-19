import QualifiedKeys
namespace QualifiedAttributes

structure State (Value : Type) where
 values : AttributeMap Value
 seen : List Key

def preload (state : State Value) (key : Key) (result : Option Value) : State Value :=
 if key ∈ state.seen then state else
 ⟨match result with | none => state.values | some value => write state.values key (some value),
  key :: state.seen⟩

theorem preload_deduplicates_exact_key (state : State Value) (key : Key)
 (first second : Option Value) :
 preload (preload state key first) key second = preload state key first := by
 by_cases seen : key ∈ state.seen
 · simp [preload,seen]
 · cases first <;> simp [preload,seen]

theorem failed_preload_marks_only_seen (state : State Value) (key : Key)
 (fresh : key ∉ state.seen) :
 (preload state key none).values = state.values ∧
 (preload state key none).seen = key :: state.seen := by simp [preload,fresh]

theorem preload_seen_membership (state : State Value) (key other : Key) (result : Option Value) :
 other ∈ (preload state key result).seen ↔ other = key ∨ other ∈ state.seen := by
 by_cases seen : key ∈ state.seen
 · simp [preload,seen]
   rintro rfl
   exact seen
 · cases result <;> simp [preload,seen]

theorem preload_preserves_other (state : State Value) (key other : Key)
 (different : other ≠ key) (result : Option Value) :
 (preload state key result).values other = state.values other := by
 by_cases seen : key ∈ state.seen
 · simp [preload,seen]
 · cases result <;> simp [preload,seen,write,different]

theorem different_namespace_preloads_both_survive (name left right : Nat)
 (different : left ≠ right) (leftValue rightValue : Value) :
 let initial : State Value := ⟨fun _ => none,[]⟩
 let final := preload (preload initial ⟨name,left⟩ (some leftValue)) ⟨name,right⟩ (some rightValue)
 final.values ⟨name,left⟩ = some (some leftValue) ∧
 final.values ⟨name,right⟩ = some (some rightValue) := by
 have keys := different_namespaces_are_distinct name left right different
 simp [preload,write,keys,Ne.symm keys]

inductive Operation (Value : Type) where
 | preload (key : Key) (result : Option Value)
 | store (key : Key) (value : Value)
 | invalidate (key : Key)

def operationKey : Operation Value → Key
 | .preload key _ => key
 | .store key _ => key
 | .invalidate key => key

def step (state : State Value) : Operation Value → State Value
 | .preload key result => preload state key result
 | .store key value => ⟨write state.values key (some value),state.seen⟩
 | .invalidate key => ⟨invalidate state.values key,state.seen⟩

def execute (operations : List (Operation Value)) (state : State Value) :=
 operations.foldl step state

theorem step_preserves_other_key (state : State Value) (operation : Operation Value)
 (key : Key) (untouched : key ≠ operationKey operation) :
 (step state operation).values key = state.values key := by
 cases operation with
 | preload other result => exact preload_preserves_other state other key untouched result
 | store other value => exact write_preserves_other state.values other key untouched _
 | invalidate other => exact write_preserves_other state.values other key untouched _

theorem arbitrary_history_preserves_untouched_key (operations : List (Operation Value))
 (state : State Value) (key : Key)
 (untouched : ∀ operation ∈ operations, key ≠ operationKey operation) :
 (execute operations state).values key = state.values key := by
 induction operations generalizing state with
 | nil => rfl
 | cons operation rest ih =>
   simp only [execute,List.foldl_cons]
   rw [← execute,ih _ (fun op member => untouched op (List.mem_cons_of_mem _ member))]
   exact step_preserves_other_key state operation key (untouched operation (by simp))

theorem arbitrary_other_namespace_history_cannot_clobber
 (operations : List (Operation Value)) (state : State Value) (name ns : Nat)
 (otherNamespaces : ∀ operation ∈ operations, (operationKey operation).ns ≠ ns) :
 (execute operations state).values ⟨name,ns⟩ = state.values ⟨name,ns⟩ := by
 apply arbitrary_history_preserves_untouched_key
 intro operation member same
 exact otherNamespaces operation member (congrArg Key.ns same).symm

end QualifiedAttributes
