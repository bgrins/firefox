import BatchInterface
import BatchSchedule
import Publication
set_option linter.unusedSectionVars false
namespace BatchPublication
open AllOrder BatchOrder BatchInterface
open BatchBase (Comparator)
variable {ι ν : Type} [DecidableEq ι] [DecidableEq ν]

def withPriority (e : Publication.Entry ι ν) (important : Bool) : Entry ι ν :=
  ⟨e.id,e.value,important⟩

def source (ids : List ι) (value : ι → Option ν) (important : Bool) : List (Entry ι ν) :=
  (Publication.publish ids value).map (fun e => withPriority e important)

theorem source_ids (ids : List ι) (value : ι → Option ν) (important : Bool) :
    (source ids value important).map AllOrder.Entry.id = ids.filter (fun id => (value id).isSome) := by
  simpa [source,List.map_map,withPriority,Function.comp_def] using Publication.published_ids ids value

theorem source_unique (ids : List ι) (value : ι → Option ν) (important : Bool)
    (hu : ids.Nodup) : unique (source ids value important) := by
  unfold unique
  rw [source_ids]
  exact hu.filter _

theorem source_compatible (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (ids : List ι) (value : ι → Option ν) (important : Bool)
    (hc : ∀ a ∈ ids, ∀ b ∈ ids, op a b = false) :
    compatible cmp op (source ids value important) := by
  intro a ha b hb
  have hai : a.id ∈ ids := by
    have h : a.id ∈ (source ids value important).map AllOrder.Entry.id := List.mem_map.mpr ⟨a,ha,rfl⟩
    rw [source_ids] at h
    exact (List.mem_filter.mp h).1
  have hbi : b.id ∈ ids := by
    have h : b.id ∈ (source ids value important).map AllOrder.Entry.id := List.mem_map.mpr ⟨b,hb,rfl⟩
    rw [source_ids] at h
    exact (List.mem_filter.mp h).1
  exact hc a.id hai b.id hbi

theorem source_capacity (ids : List ι) (value : ι → Option ν) (important : Bool) :
    (source ids value important).length ≤ ids.length := by
  simpa [source] using Publication.publication_capacity ids value

theorem published_batch_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial : List (Entry ι ν)) (raw : Storage ι ν) (ids : List ι) (value : ι → Option ν)
    (important : Bool) (hu : unique initial) (hs : ids.Nodup)
    (hc : ∀ a ∈ ids, ∀ b ∈ ids, op a b = false) (hr : Represents raw initial) :
    Represents (guardedBatch cmp op initial (source ids value important) raw)
      (directRun op initial (source ids value important)) :=
  guarded_batch_refinement cmp op initial _ raw hu (source_unique ids value important hs)
    (source_compatible cmp op ids value important hc) hr

end BatchPublication
