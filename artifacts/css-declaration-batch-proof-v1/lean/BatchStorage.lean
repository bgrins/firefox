import BatchOrder
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false
namespace BatchStorage
open AllOrder BatchOrder
open BatchBase (Comparator)
variable {ι ν : Type} [DecidableEq ι] [DecidableEq ν]
local notation "E" => Entry ι ν

def Aligned (raw : Storage ι ν) (xs : List E) : Prop :=
  raw.declarations = xs.map payload ∧ raw.importance = xs.map Entry.important

def rawRemove (raw : Storage ι ν) : List Nat → Storage ι ν
  | [] => raw
  | n::rest => rawRemove ⟨raw.declarations.eraseIdx n, raw.importance.eraseIdx n, raw.present⟩ rest

theorem removal_alignment (raw : Storage ι ν) (xs : List E) (positions : List Nat)
    (ha : Aligned raw xs) : Aligned (rawRemove raw positions) (BatchIndices.removeIndices xs positions) := by
  induction positions generalizing raw xs with
  | nil => exact ha
  | cons n rest ih =>
    apply ih
    rcases ha with ⟨hd,hb⟩
    constructor
    · simp only [hd]
      exact (BatchIndices.map_remove_indices payload xs [n]).symm
    · simp only [hb]
      exact (BatchIndices.map_remove_indices Entry.important xs [n]).symm

theorem removal_membership_retained (raw : Storage ι ν) (positions : List Nat) :
    (rawRemove raw positions).present = raw.present := by
  induction positions generalizing raw with
  | nil => rfl
  | cons n rest ih => exact ih _

theorem step_alignment (raw : Storage ι ν) (xs : List E) (new : E) (plan : Plan)
    (ha : Aligned raw xs) : Aligned (rawStep raw new plan) (execute xs new plan) := by
  rcases ha with ⟨hd,hb⟩
  cases plan <;> simp [Aligned,rawStep,execute,hd,hb,List.map_take,List.map_drop]

def rawAfter (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E)
    (positions : List Nat) : Storage ι ν → List E → Storage ι ν
  | raw, [] => raw
  | raw, new::rest => rawAfter cmp op initial positions
      (rawStep raw new (corrected positions (BatchBase.planner cmp op initial new))) rest

theorem after_alignment (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial current actions : List E)
    (positions : List Nat) (raw : Storage ι ν) (ha : Aligned raw current) :
    Aligned (rawAfter cmp op initial positions raw actions)
      (numericAfter cmp op initial positions current actions) := by
  induction actions generalizing raw current with
  | nil => exact ha
  | cons new rest ih => exact ih _ _ (step_alignment raw current new _ ha)

theorem nonappend_present (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E)
    (new : E) (hu : unique initial)
    (hp : BatchBase.planner cmp op initial new ≠ .append) : new.id ∈ initial.map Entry.id := by
  rcases unique_split initial new hu with ha | ⟨pre,old,post,he,hi,_,_⟩
  · have h := BatchBase.scan_absent cmp op new initial ha 0
    simp [BatchBase.planner,h] at hp
  · subst initial
    simp [hi]

theorem step_membership (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E)
    (positions : List Nat) (raw : Storage ι ν) (new : E) (hu : unique initial)
    (hb : ∀ id ∈ initial.map Entry.id, raw.present id = true) (id : ι) :
    (rawStep raw new (corrected positions (BatchBase.planner cmp op initial new))).present id =
      (raw.present id || decide (id = new.id)) := by
  cases hp : BatchBase.planner cmp op initial new with
  | append | move n => simp [corrected,rawStep,Bool.or_comm]
  | none | replace n =>
    have hn := nonappend_present cmp op initial new hu (by simp [hp])
    by_cases he : id = new.id
    · subst id
      simp [corrected,rawStep,hb new.id hn]
    · simp [corrected,rawStep,he]

theorem after_membership (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (positions : List Nat) (raw : Storage ι ν) (hu : unique initial)
    (hb : ∀ id ∈ initial.map Entry.id, raw.present id = true) (id : ι) :
    (rawAfter cmp op initial positions raw actions).present id =
      (raw.present id || decide (id ∈ actions.map Entry.id)) := by
  induction actions generalizing raw with
  | nil => simp [rawAfter]
  | cons new rest ih =>
    simp only [rawAfter]
    rw [ih]
    · rw [step_membership cmp op initial positions raw new hu hb]
      simp [Bool.or_assoc]
    · intro id hi
      rw [step_membership cmp op initial positions raw new hu hb, hb id hi]
      rfl

def rawBatch (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (raw : Storage ι ν) : Storage ι ν :=
  let positions := descending (movePositions cmp op initial actions)
  rawAfter cmp op initial positions (rawRemove raw positions) actions

theorem run_membership (op : ι → ι → Bool) (initial actions : List E) (id : ι) :
    id ∈ (directRun op initial actions).map Entry.id ↔
      id ∈ initial.map Entry.id ∨ id ∈ actions.map Entry.id := by
  induction actions generalizing initial with
  | nil => simp [directRun]
  | cons new rest ih =>
    change id ∈ (directRun op (reference op initial new) rest).map Entry.id ↔ _
    rw [ih, reference_membership]
    simp [or_assoc,or_left_comm]

theorem raw_batch_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (raw : Storage ι ν) (hu : unique initial) (hs : unique actions)
    (hc : compatible cmp op actions) (hr : Represents raw initial) :
    Represents (rawBatch cmp op initial actions raw) (directRun op initial actions) := by
  have ha := after_alignment cmp op initial
    (BatchIndices.removeIndices initial (descending (movePositions cmp op initial actions)))
    actions (descending (movePositions cmp op initial actions))
    (rawRemove raw (descending (movePositions cmp op initial actions)))
    (removal_alignment raw initial _ ⟨hr.1,hr.2.1⟩)
  change Aligned (rawBatch cmp op initial actions raw) (numericBatch cmp op initial actions) at ha
  rw [numeric_batch_refinement cmp op initial actions hu hs hc] at ha
  refine ⟨ha.1,ha.2,?_⟩
  intro id
  unfold rawBatch
  rw [after_membership cmp op initial actions _ _ hu]
  · rw [removal_membership_retained, hr.2.2]
    simp [run_membership]
  · intro id hi
    rw [removal_membership_retained, hr.2.2]
    simp [hi]

theorem final_storage_invariants (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (raw : Storage ι ν) (hu : unique initial) (hs : unique actions)
    (hc : compatible cmp op actions) (hr : Represents raw initial) :
    let result := rawBatch cmp op initial actions raw
    result.declarations.length = result.importance.length ∧
    (result.declarations.map Prod.fst).Nodup := by
  have h := raw_batch_refinement cmp op initial actions raw hu hs hc hr
  refine ⟨aligned_storage_lengths _ _ h,?_⟩
  rw [h.1,List.map_map]
  exact sequence_unique op initial actions hu

end BatchStorage
