import QualifiedHistories
namespace QualifiedAttributes

abbrev Buckets (Value : Type) := Nat → Nat → Option (Option Value)

def flatten (buckets : Buckets Value) : AttributeMap Value := fun key => buckets key.ns key.name

def writeBucket (buckets : Buckets Value) (key : Key) (value : Option Value) : Buckets Value :=
 fun ns name => if ns = key.ns then
   if name = key.name then some value else buckets ns name
 else buckets ns name

theorem bucket_write_is_qualified_write (buckets : Buckets Value) (key : Key) (value : Option Value) :
 flatten (writeBucket buckets key value) = write (flatten buckets) key value := by
 funext other
 by_cases ns : other.ns = key.ns <;> by_cases name : other.name = key.name <;>
   simp [flatten,writeBucket,write,key_equal_iff,ns,name]

def bucketSeen (seen : Nat → List Nat) (key : Key) : Prop := key.name ∈ seen key.ns

def markBucketSeen (seen : Nat → List Nat) (key : Key) : Nat → List Nat :=
 fun ns => if ns = key.ns then key.name :: seen ns else seen ns

theorem bucket_seen_mark_is_qualified_insert (seen : Nat → List Nat) (key other : Key) :
 bucketSeen (markBucketSeen seen key) other ↔ other = key ∨ bucketSeen seen other := by
 by_cases ns : other.ns = key.ns
 · simp [bucketSeen,markBucketSeen,ns,key_equal_iff]
 · simp [bucketSeen,markBucketSeen,ns,key_equal_iff]

structure BucketState (Value : Type) where
 values : Buckets Value
 seen : Nat → List Nat

def bucketPreload (state : BucketState Value) (key : Key) (result : Option Value) : BucketState Value :=
 if key.name ∈ state.seen key.ns then state else
 ⟨match result with | none => state.values | some value => writeBucket state.values key (some value),
  markBucketSeen state.seen key⟩

def corresponds (bucket : BucketState Value) (qualified : State Value) : Prop :=
 flatten bucket.values = qualified.values ∧
 ∀ key, bucketSeen bucket.seen key ↔ key ∈ qualified.seen

theorem bucket_preload_corresponds (bucket : BucketState Value) (qualified : State Value)
 (same : corresponds bucket qualified) (key : Key) (result : Option Value) :
 corresponds (bucketPreload bucket key result) (preload qualified key result) := by
 rcases same with ⟨values,seen⟩
 by_cases existing : key ∈ qualified.seen
 · have existsBucket : key.name ∈ bucket.seen key.ns := (seen key).mpr existing
   simp only [bucketPreload,preload,ite_eq_left existing,ite_eq_left existsBucket]
   exact ⟨values,seen⟩
 · have freshBucket : key.name ∉ bucket.seen key.ns := fun h => existing ((seen key).mp h)
   unfold bucketPreload preload
   rw [ite_eq_right existing,ite_eq_right freshBucket]
   constructor
   · cases result with
     | none => exact values
     | some value => simp only [bucket_write_is_qualified_write,values]
   · intro other
     change bucketSeen (markBucketSeen bucket.seen key) other ↔ other ∈ key :: qualified.seen
     rw [bucket_seen_mark_is_qualified_insert,List.mem_cons,seen]

def bucketStep (state : BucketState Value) : Operation Value → BucketState Value
 | .preload key result => bucketPreload state key result
 | .store key value => ⟨writeBucket state.values key (some value),state.seen⟩
 | .invalidate key => ⟨writeBucket state.values key none,state.seen⟩

def bucketExecute (operations : List (Operation Value)) (state : BucketState Value) :=
 operations.foldl bucketStep state

theorem bucket_step_corresponds (bucket : BucketState Value) (qualified : State Value)
 (same : corresponds bucket qualified) (operation : Operation Value) :
 corresponds (bucketStep bucket operation) (step qualified operation) := by
 cases operation with
 | preload key result => exact bucket_preload_corresponds bucket qualified same key result
 | store key value =>
   exact ⟨(bucket_write_is_qualified_write bucket.values key (some value)).trans
     (congrArg (fun v => write v key (some value)) same.1),same.2⟩
 | invalidate key =>
   exact ⟨(bucket_write_is_qualified_write bucket.values key none).trans
     (congrArg (fun v => write v key none) same.1),same.2⟩

theorem arbitrary_bucket_history_corresponds (operations : List (Operation Value))
 (bucket : BucketState Value) (qualified : State Value) (same : corresponds bucket qualified) :
 corresponds (bucketExecute operations bucket) (execute operations qualified) := by
 induction operations generalizing bucket qualified with
 | nil => exact same
 | cons operation rest ih => exact ih _ _ (bucket_step_corresponds bucket qualified same operation)

theorem fresh_bucket_history_cannot_clobber_other_namespace
 (operations : List (Operation Value)) (bucket : BucketState Value) (qualified : State Value)
 (same : corresponds bucket qualified) (key : Key)
 (untouched : ∀ operation ∈ operations, key ≠ operationKey operation) :
 flatten (bucketExecute operations bucket).values key = flatten bucket.values key := by
 have final := arbitrary_bucket_history_corresponds operations bucket qualified same
 rw [final.1,arbitrary_history_preserves_untouched_key operations qualified key untouched,same.1]

theorem prefix_aliases_with_same_resolved_namespace_share_key (name ns : Nat)
 (leftPrefix rightPrefix : Nat) (resolvePrefix : Nat → Option Nat)
 (left : resolvePrefix leftPrefix = some ns) (right : resolvePrefix rightPrefix = some ns) :
 resolveKey name (resolvePrefix leftPrefix) = resolveKey name (resolvePrefix rightPrefix) := by
 rw [left,right]

end QualifiedAttributes
