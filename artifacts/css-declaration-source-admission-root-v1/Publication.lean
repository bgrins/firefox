import Std

namespace Publication

structure Entry (ι ν : Type) where
  id : ι
  value : ν

def publish (ids : List ι) (value : ι → Option ν) : List (Entry ι ν) :=
  ids.filterMap (fun id => (value id).map (fun v => ⟨id, v⟩))

theorem published_ids (ids : List ι) (value : ι → Option ν) :
    (publish ids value).map Entry.id = ids.filter (fun id => (value id).isSome) := by
  induction ids with
  | nil => rfl
  | cons id rest ih =>
    cases h : value id <;> simp_all [publish]

theorem unique_publication (ids : List ι) (value : ι → Option ν)
    (unique : ids.Nodup) :
    ((publish ids value).map Entry.id).Nodup := by
  rw [published_ids]
  exact unique.filter _

theorem uniform_publication (ids : List ι) (value : ι → Option ν)
    (compatible : ι → ι → Prop) (uniform : ids.Pairwise compatible) :
    ((publish ids value).map Entry.id).Pairwise compatible := by
  rw [published_ids]
  exact uniform.filter _

theorem publication_capacity (ids : List ι) (value : ι → Option ν) :
    (publish ids value).length ≤ ids.length := by
  have h := List.length_filter_le (fun id => (value id).isSome) ids
  rw [← published_ids ids value] at h
  simpa using h

theorem admitted_source (ids : List ι) (value : ι → Option ν)
    (compatible : ι → ι → Prop) (capacity : Nat)
    (unique : ids.Nodup) (uniform : ids.Pairwise compatible)
    (fits : ids.length ≤ capacity) :
    ((publish ids value).map Entry.id).Nodup ∧
    ((publish ids value).map Entry.id).Pairwise compatible ∧
    (publish ids value).length ≤ capacity := by
  exact ⟨unique_publication ids value unique,
    uniform_publication ids value compatible uniform,
    Nat.le_trans (publication_capacity ids value) fits⟩

end Publication
