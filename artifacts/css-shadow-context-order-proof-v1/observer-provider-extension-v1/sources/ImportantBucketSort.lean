import OriginBuckets
import TransitionPartition
import RawReferenceDispatch
namespace ShadowOrder

def importantBuckets (state : PartitionState) : List Entry × List Entry × List Entry :=
 (state.buckets.author,state.buckets.user,state.buckets.ua)

theorem tree_partition_important_buckets (entries : List Entry) (state : PartitionState) :
 importantBuckets (treePartition entries state) =
 (state.buckets.author ++ importantOrigin 3 entries,
  state.buckets.user ++ importantOrigin 1 entries,
  state.buckets.ua ++ importantOrigin 0 entries) := by
 induction entries generalizing state with
 | nil => simp [treePartition,importantBuckets,importantOrigin]
 | cons entry rest ih =>
   simp only [treePartition,ih]
   cases hi : hasImportant entry <;>
   by_cases ha : entry.origin = 3 <;>
   by_cases hu : entry.origin = 1 <;>
   by_cases hg : entry.origin = 0 <;>
   by_cases ht : entry.origin = 7 <;>
   cases found : state.buckets.found <;>
   simp_all [treePartitionStep,partitionStep,importantOrigin,List.filter_cons,List.append_assoc]

theorem empty_tree_partition_important_buckets (entries : List Entry) :
 importantBuckets (treePartition entries emptyPartition) =
 (importantOrigin 3 entries,importantOrigin 1 entries,importantOrigin 0 entries) := by
 simpa [emptyPartition,emptyBuckets] using tree_partition_important_buckets entries emptyPartition

theorem partition_bucket_sort_refinement (raw : RawProviderInput) (normalized : RawInput)
 (valid : rawFieldsValid raw = true) (made : normalizeRawProviders raw = some normalized) :
 allPathItems (skipSort entryPriorityIdentity entryImportantKey)
   (treePartition (nativeCollected normalized) emptyPartition) =
 allPathItems (localSort entryImportantKey)
   (treePartition (nativeCollected normalized) emptyPartition) := by
 have buckets := empty_tree_partition_important_buckets (nativeCollected normalized)
 have author := congrArg Prod.fst buckets
 have user := congrArg (fun buckets => buckets.2.1) buckets
 have ua := congrArg (fun buckets => buckets.2.2) buckets
 simp only [importantBuckets] at author user ua
 simp only [allPathItems,author,user,ua]
 rw [normalized_collected_buckets_skip raw normalized valid made 3 (by simp),
   normalized_collected_buckets_skip raw normalized valid made 1 (by simp),
   normalized_collected_buckets_skip raw normalized valid made 0 (by simp)]

theorem admitted_raw_path_sort_refinement (raw : RawProviderInput)
 (admitted : rawAdmitted raw = true) :
 (rawProviderExecution raw).map (fun entries =>
   allPathItems (skipSort entryPriorityIdentity entryImportantKey) (treePartition entries emptyPartition)) =
 (directRawReference raw).map (fun entries =>
   allPathItems (localSort entryImportantKey) (treePartition entries emptyPartition)) := by
 have admission := admitted
 simp only [rawAdmitted,Bool.and_eq_true] at admission
 have fields : rawFieldsValid raw = true := admission.1
 rcases admitted_has_normalization raw admitted with ⟨normalized,made,bounded⟩
 rw [direct_raw_reference_normalized raw normalized made]
 simp only [rawProviderExecution,made,Option.map_some]
 exact congrArg some (partition_bucket_sort_refinement raw normalized fields made)

#print axioms admitted_raw_path_sort_refinement
#print axioms partition_bucket_sort_refinement
end ShadowOrder
