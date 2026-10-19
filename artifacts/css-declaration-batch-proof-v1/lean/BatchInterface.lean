import BatchStorage
import BatchRank
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false
namespace BatchInterface
open AllOrder BatchOrder BatchStorage
open BatchBase (Comparator)
variable {ι ν : Type} [DecidableEq ι] [DecidableEq ν]
local notation "E" => Entry ι ν

def uniform (group : ι → Option Nat) (logical : ι → Bool) (actions : List E) : Prop :=
  ∀ a ∈ actions, ∀ b ∈ actions, group a.id ≠ none → group a.id = group b.id → logical a.id = logical b.id

theorem uniform_compatible (cmp : Comparator ι ν) (group : ι → Option Nat) (logical : ι → Bool)
    (actions : List E) (h : uniform group logical actions) :
    compatible cmp (opposite group logical) actions := by
  intro a ha b hb
  by_cases hg : group a.id = none
  · simp [opposite,hg]
  · by_cases he : group a.id = group b.id
    · have hl := h a ha b hb hg he
      simp [opposite,he,hl]
    · simp [opposite,he]

def plans (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : List Plan :=
  actions.map (BatchBase.planner cmp op initial)

def newCount (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : Nat :=
  ((plans cmp op initial actions).filter (fun p => decide (p = .append))).length

def anyChange (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : Bool :=
  (plans cmp op initial actions).any (fun p => decide (p ≠ .none))

theorem plan_zip_length (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) :
    (plans cmp op initial actions).length = actions.length := by simp [plans]

theorem reserve_bound (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) :
    newCount cmp op initial actions ≤ actions.length := by
  have h := List.length_filter_le (fun p => decide (p = Plan.append)) (plans cmp op initial actions)
  simpa [newCount,plans] using h

def step (cmp : Comparator ι ν) (op : ι → ι → Bool) (current : List E) (new : E) : List E :=
  execute current new (BatchBase.planner cmp op current new)

def changing (cmp : Comparator ι ν) (op : ι → ι → Bool) : List E → List E → Bool
  | _, [] => false
  | current, new::rest => decide (BatchBase.planner cmp op current new ≠ .none) ||
      changing cmp op (step cmp op current new) rest

theorem none_preserves (cmp : Comparator ι ν) (op : ι → ι → Bool) (current : List E) (new : E)
    (h : BatchBase.planner cmp op current new = .none) : step cmp op current new = current := by
  simp [step,h,execute]

theorem first_changing_step (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) :
    anyChange cmp op initial actions = changing cmp op initial actions := by
  induction actions generalizing initial with
  | nil => rfl
  | cons new rest ih =>
    by_cases hp : BatchBase.planner cmp op initial new = .none
    · simp [anyChange,plans,changing,hp,none_preserves cmp op initial new hp,←ih]
    · simp [anyChange,plans,changing,hp]

theorem false_gate_direct (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) (h : anyChange cmp op initial actions = false) :
    directRun op initial actions = initial := by
  induction actions generalizing initial with
  | nil => rfl
  | cons new rest ih =>
    have hs : BatchBase.planner cmp op initial new = .none ∧ anyChange cmp op initial rest = false := by
      simpa [anyChange,plans] using h
    have he : reference op initial new = initial := by
      rw [←BatchBase.planner_refinement cmp op initial new hu, hs.1]
      rfl
    change directRun op (reference op initial new) rest = initial
    rw [he]
    exact ih initial hu hs.2

def guardedBatch (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (raw : Storage ι ν) : Storage ι ν :=
  if anyChange cmp op initial actions then rawBatch cmp op initial actions raw else raw

theorem guarded_batch_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (raw : Storage ι ν) (hu : unique initial) (hs : unique actions)
    (hc : compatible cmp op actions) (hr : Represents raw initial) :
    Represents (guardedBatch cmp op initial actions raw) (directRun op initial actions) := by
  unfold guardedBatch
  split
  · exact raw_batch_refinement cmp op initial actions raw hu hs hc hr
  · next h =>
    have hf : anyChange cmp op initial actions = false := by simpa using h
    rw [false_gate_direct cmp op initial actions hu hf]
    exact hr

def SafeAfter (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E) (positions : List Nat) :
    List E → List E → Prop
  | _, [] => True
  | current,new::rest =>
    ValidPlan current new (corrected positions (BatchBase.planner cmp op initial new)) ∧
    SafeAfter cmp op initial positions
      (execute current new (corrected positions (BatchBase.planner cmp op initial new))) rest

theorem after_indices_safe (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial current actions : List E)
    (positions : List Nat) (hs : unique actions) (hr : TargetsReady cmp op initial current actions positions) :
    SafeAfter cmp op initial positions current actions := by
  induction actions generalizing current with
  | nil => trivial
  | cons new rest ih =>
    have hv : ValidPlan current new (corrected positions (BatchBase.planner cmp op initial new)) := by
      cases hp : BatchBase.planner cmp op initial new with
      | none => exact .none
      | append | move n => exact .append
      | replace n =>
        obtain ⟨pre,old,post,he,hl,hi,_,_⟩ := hr new (by simp) n hp
        rw [corrected,←hl]
        exact .replace pre post old he hi
    refine ⟨hv,?_⟩
    rw [corrected_step_matches_after cmp op initial current positions new (hr new (by simp))]
    apply ih _ (List.nodup_cons.mp hs).2
    intro target hm n hp
    have hn : new.id ≠ target.id := by
      intro he; exact (List.nodup_cons.mp hs).1 (List.mem_map.mpr ⟨target,hm,he.symm⟩)
    exact after_preserves_identity current new _ target.id _ hn (hr target (by simp [hm]) n hp)

def growth : Kind → Nat
  | .append => 1
  | _ => 0

theorem source_newcount (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) : newCount cmp op initial actions =
    (actions.map (fun new => growth (decision cmp op initial new))).sum := by
  induction actions with
  | nil => rfl
  | cons new rest ih =>
    simp only [newCount,plans,List.map_cons,List.filter_cons]
    rw [←planner_kind]
    cases BatchBase.planner cmp op initial new <;>
      simp only [planKind,growth,List.map_cons,List.sum_cons,decide_false,decide_true,↓reduceIte,List.length_cons,Nat.zero_add] <;>
      simpa [newCount,plans,growth,Nat.add_comm] using ih

theorem reference_length (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (xs : List E) (new : E) (hu : unique xs) :
    (reference op xs new).length = xs.length + growth (decision cmp op xs new) := by
  rw [←BatchBase.planner_refinement cmp op xs new hu,←planner_kind]
  have hv := BatchBase.planner_valid cmp op xs new hu
  cases hp : BatchBase.planner cmp op xs new <;> rw [hp] at hv
  · rfl
  · simp [execute,planKind,growth]
  · cases hv
    simp_all [execute,planKind,growth,List.drop_append]
  · cases hv
    simp_all [execute,planKind,growth,List.drop_append]

theorem frozen_length_aux (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial current actions : List E) (hu : unique current) (hs : unique actions)
    (hc : compatible cmp op actions)
    (ha : ∀ new ∈ actions, decision cmp op current new = decision cmp op initial new) :
    (directRun op current actions).length = current.length + newCount cmp op initial actions := by
  induction actions generalizing current with
  | nil => simp [directRun,newCount,plans]
  | cons new rest ih =>
    have ht : unique rest := (List.nodup_cons.mp hs).2
    have hct : compatible cmp op rest := by intro a ha b hb; exact hc a (by simp [ha]) b (by simp [hb])
    have hn : ∀ other ∈ rest, decision cmp op (reference op current new) other = decision cmp op initial other := by
      intro other ho
      have hd : new.id ≠ other.id := by
        intro he; exact (List.nodup_cons.mp hs).1 (List.mem_map.mpr ⟨other,ho,he.symm⟩)
      rw [initial_decision_stable cmp op current other new hd (hc other (by simp [ho]) new (by simp))]
      exact ha other (by simp [ho])
    change (directRun op (reference op current new) rest).length = _
    rw [ih _ (reference_unique op current new hu) ht hct hn,
      reference_length cmp op current new hu,ha new (by simp),source_newcount]
    simp [source_newcount,Nat.add_assoc]

theorem exact_reserve_growth (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) (hu : unique initial) (hs : unique actions)
    (hc : compatible cmp op actions) :
    (directRun op initial actions).length = initial.length + newCount cmp op initial actions :=
  frozen_length_aux cmp op initial initial actions hu hs hc (by intros; rfl)

def SafeRemovals (xs : List α) : List Nat → Prop
  | [] => True
  | n::rest => n < xs.length ∧ SafeRemovals (xs.eraseIdx n) rest

theorem descending_indices_safe (xs : List α) (positions : List Nat)
    (hd : positions.Pairwise (fun a b => b<a)) (hb : ∀ p ∈ positions, p < xs.length) :
    SafeRemovals xs positions := by
  induction positions generalizing xs with
  | nil => trivial
  | cons p rest ih =>
    have hp := hb p (by simp)
    refine ⟨hp,ih _ (List.pairwise_cons.mp hd).2 ?_⟩
    intro q hq
    have hqp := (List.pairwise_cons.mp hd).1 q hq
    simp only [List.length_eraseIdx,ite_eq_left hp]
    omega

theorem batching_indices_safe (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) (hu : unique initial) (hs : unique actions) :
    let positions := descending (movePositions cmp op initial actions)
    SafeRemovals initial positions ∧
    SafeAfter cmp op initial positions (BatchIndices.removeIndices initial positions) actions ∧
    ∀ n, n-(BatchIndices.earlierRemovals positions n).length +
      (BatchIndices.earlierRemovals positions n).length = n := by
  dsimp only
  have hd := descending_strict _ (move_positions_unique cmp op initial actions hu hs)
  have hn := (descending_permutation _).nodup_iff.mpr (move_positions_unique cmp op initial actions hu hs)
  refine ⟨descending_indices_safe initial _ hd ?_,?_,?_⟩
  · intro p hp
    exact move_position_bounds cmp op initial actions hu p ((descending_permutation _).mem_iff.mp hp)
  · apply after_indices_safe cmp op initial _ actions _ hs
    intro new hm n hp
    obtain ⟨old,hl,hi⟩ := planner_position_lookup cmp op initial new hu n (by simp [hp,planPosition])
    have hnot := replace_not_removed cmp op initial actions hu hs new hm n hp
    have hsn : n ∉ descending (movePositions cmp op initial actions) := by
      simpa only [(descending_permutation _).mem_iff] using hnot
    have h := corrected_target_survives initial _ n old hu hd hsn hl
    simpa [hi] using h
  · intro n
    exact BatchIndices.rank_correction_no_underflow _ n hn

end BatchInterface
