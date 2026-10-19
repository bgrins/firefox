import PublicRemoval
set_option linter.unusedSectionVars false

namespace PublicAPI
open AllOrder PublicStorage PublicRemoval
variable {ι ν : Type} [DecidableEq ι]
local notation "E" => Entry ι ν

inductive Property (ι : Type) where
  | single (id : ι)
  | shorthand (member : ι → Bool)

def selected : Property ι → ι → Bool
  | .single target, id => decide (id = target)
  | .shorthand member, id => member id

def query (raw : Storage ι ν) (property : Property ι) : Option Nat :=
  match property with
  | .single id => if raw.present id then firstIndex (selected property) (decode raw) else none
  | .shorthand _ => firstIndex (selected property) (decode raw)

theorem absent_membership_query (raw : Storage ι ν) (xs : List E) (id : ι)
    (hr : Represents raw xs) (h : raw.present id = false) :
    firstIndex (selected (.single id)) xs = none := by
  apply (index_absent _ _).mpr
  intro e he
  have hn : id ∉ xs.map Entry.id := by simpa [hr.2.2] using h
  have hid : e.id ≠ id := by
    intro hid
    exact hn (List.mem_map.mpr ⟨e,he,hid⟩)
  simp [selected,hid]

theorem query_refinement (raw : Storage ι ν) (xs : List E) (property : Property ι)
    (hr : Represents raw xs) : query raw property = firstIndex (selected property) xs := by
  classical
  cases property with
  | shorthand member => simp [query,decode_representation raw xs hr]
  | single id =>
    cases h : raw.present id
    · simp [query,h,absent_membership_query raw xs id hr h]
    · simp [query,h,decode_representation raw xs hr]

theorem singleton_filter (pre post : List E) (old : E) (hu : unique (pre ++ old :: post)) :
    (pre ++ old :: post).filter (fun e => !selected (.single old.id) e.id) = pre ++ post := by
  have hf : (pre ++ post).filter (fun e => !selected (.single old.id) e.id) = pre ++ post := by
    apply List.filter_eq_self.mpr
    intro e he
    have hn : e.id ≠ old.id := by
      intro hn
      exact removed_absent pre post old hu (List.mem_map.mpr ⟨e,he,hn⟩)
    simp [selected,hn]
  simpa [selected] using hf

def remove (raw : Storage ι ν) (property : Property ι) (n : Nat) : Storage ι ν :=
  match property with
  | .single _ => match (decode raw)[n]? with
    | none => raw
    | some old => rawDelete raw old.id n
  | .shorthand member => removeAt raw member n

theorem remove_refinement (raw : Storage ι ν) (xs : List E) (property : Property ι) (n : Nat)
    (hu : unique xs) (hr : Represents raw xs) (hq : firstIndex (selected property) xs = some n) :
    Represents (remove raw property n) (xs.filter (fun e => !selected property e.id)) := by
  classical
  cases property with
  | shorthand member => exact cached_removal_refinement member raw xs n hu hr hq
  | single id =>
    obtain ⟨pre,old,post,rfl,rfl,ho,_⟩ := index_certificate (selected (.single id)) xs n hq
    have he : old.id = id := by simpa [selected] using ho
    have hf := singleton_filter pre post old hu
    rw [he] at hf
    simpa [remove,decode_representation raw (pre ++ old :: post) hr,hf] using
      raw_delete_refinement raw pre post old hu hr

theorem cached_callback_refinement (beforeRaw afterRaw : Storage ι ν) (before after : List E)
    (property : Property ι) (n : Nat) (hb : Represents beforeRaw before)
    (ha : Represents afterRaw after) (hu : unique after)
    (frame : before.map Entry.id = after.map Entry.id) (hq : query beforeRaw property = some n) :
    Represents (remove afterRaw property n) (after.filter (fun e => !selected property e.id)) := by
  rw [query_refinement beforeRaw before property hb] at hq
  have h : firstIndex (selected property) after = some n :=
    (query_depends_on_ids (selected property) before after frame).symm.trans hq
  exact remove_refinement afterRaw after property n hu ha h

def removeQueried (raw : Storage ι ν) (property : Property ι) : Storage ι ν :=
  match query raw property with
  | none => raw
  | some n => remove raw property n

theorem queried_api_refinement (raw : Storage ι ν) (xs : List E) (property : Property ι)
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (removeQueried raw property) (xs.filter (fun e => !selected property e.id)) := by
  unfold removeQueried
  rw [query_refinement raw xs property hr]
  cases h : firstIndex (selected property) xs with
  | none =>
    have hf : xs.filter (fun e => !selected property e.id) = xs := by
      apply List.filter_eq_self.mpr
      intro e he
      simp [(index_absent _ _).mp h e he]
    simpa [h,hf] using hr
  | some n => simpa [h] using remove_refinement raw xs property n hu hr h

inductive PublicOperation (ι ν : Type) where
  | parse (actions : List (Entry ι ν))
  | remove (property : Property ι)
  | clear

def referenceStep (xs : List E) : PublicOperation ι ν → List E
  | .parse actions => parseExtend xs actions
  | .remove property => xs.filter (fun e => !selected property e.id)
  | .clear => []

def rawPublicStep (raw : Storage ι ν) : PublicOperation ι ν → Storage ι ν
  | .parse actions => rawExtend raw actions
  | .remove property => removeQueried raw property
  | .clear => rawClear

theorem public_step_refinement (raw : Storage ι ν) (xs : List E) (op : PublicOperation ι ν)
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (rawPublicStep raw op) (referenceStep xs op) ∧ unique (referenceStep xs op) := by
  cases op with
  | parse actions => exact ⟨raw_extend_refinement raw xs actions hu hr, extend_unique xs actions hu⟩
  | remove property => exact ⟨queried_api_refinement raw xs property hu hr, removal_unique _ xs hu⟩
  | clear => exact ⟨clear_representation, by simp [referenceStep,unique]⟩

theorem public_api_history (raw : Storage ι ν) (xs : List E) (ops : List (PublicOperation ι ν))
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (ops.foldl rawPublicStep raw) (ops.foldl referenceStep xs) ∧
      unique (ops.foldl referenceStep xs) := by
  induction ops generalizing raw xs with
  | nil => exact ⟨hr,hu⟩
  | cons op rest ih =>
    have h := public_step_refinement raw xs op hu hr
    exact ih _ _ h.2 h.1

theorem public_api_prefix (raw : Storage ι ν) (xs : List E) (ops : List (PublicOperation ι ν))
    (hu : unique xs) (hr : Represents raw xs) (n : Nat) :
    Represents ((ops.take n).foldl rawPublicStep raw) ((ops.take n).foldl referenceStep xs) ∧
      unique ((ops.take n).foldl referenceStep xs) :=
  public_api_history raw xs (ops.take n) hu hr

end PublicAPI
