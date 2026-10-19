import PublicStorage
set_option linter.unusedSectionVars false

namespace PublicRemoval
open AllOrder PublicStorage
variable {ι ν : Type} [DecidableEq ι]
local notation "E" => Entry ι ν

def firstIndex (selected : ι → Bool) : List E → Option Nat
  | [] => none
  | old :: rest => if selected old.id then some 0 else (firstIndex selected rest).map Nat.succ

theorem index_absent (selected : ι → Bool) (xs : List E) :
    firstIndex selected xs = none ↔ ∀ e ∈ xs, selected e.id = false := by
  induction xs with
  | nil => simp [firstIndex]
  | cons old rest ih =>
    cases hm : selected old.id <;> simp [firstIndex,hm,ih]

theorem index_certificate (selected : ι → Bool) (xs : List E) (n : Nat)
    (h : firstIndex selected xs = some n) :
    ∃ pre old post, xs = pre ++ old :: post ∧ n = pre.length ∧
      selected old.id = true ∧ (∀ e ∈ pre, selected e.id = false) := by
  induction xs generalizing n with
  | nil => simp [firstIndex] at h
  | cons old rest ih =>
    cases hm : selected old.id
    · cases ht : firstIndex selected rest with
      | none => simp [firstIndex,hm,ht] at h
      | some k =>
        have hn : n = k + 1 := by simpa [firstIndex,hm,ht] using h.symm
        obtain ⟨pre,target,post,he,hk,hs,hp⟩ := ih k ht
        refine ⟨old::pre,target,post,by simp [he],by simp [hn,hk],hs,?_⟩
        intro e he
        rcases List.mem_cons.mp he with rfl | he
        · exact hm
        · exact hp e he
    · have hn : n = 0 := by simpa [firstIndex,hm] using h.symm
      exact ⟨[],old,rest,rfl,hn,hm,by simp⟩

theorem certificate_index (selected : ι → Bool) (pre post : List E) (old : E)
    (hp : ∀ e ∈ pre, selected e.id = false) (ho : selected old.id = true) :
    firstIndex selected (pre ++ old :: post) = some pre.length := by
  induction pre with
  | nil => simp [firstIndex,ho]
  | cons e rest ih =>
    have ht : ∀ x ∈ rest, selected x.id = false := fun x hx => hp x (by simp [hx])
    simp [firstIndex,hp e (by simp),ih ht]

def removeAt (raw : Storage ι ν) (selected : ι → Bool) (n : Nat) : Storage ι ν :=
  let xs := decode raw
  match xs[n]? with
  | none => raw
  | some old => removeLoop selected (rawDelete raw old.id n) (xs.take n) (xs.drop (n + 1))

def removeProperty (raw : Storage ι ν) (selected : ι → Bool) : Storage ι ν :=
  match firstIndex selected (decode raw) with
  | none => raw
  | some n => removeAt raw selected n

theorem queried_removal_refinement (selected : ι → Bool) (raw : Storage ι ν) (xs : List E)
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (removeProperty raw selected) (xs.filter (fun e => !selected e.id)) := by
  classical
  unfold removeProperty removeAt
  rw [decode_representation raw xs hr]
  cases h : firstIndex selected xs with
  | none =>
    have hf : xs.filter (fun e => !selected e.id) = xs := by
      apply List.filter_eq_self.mpr
      intro e he
      simp [(index_absent selected xs).mp h e he]
    simpa [h,hf] using hr
  | some n =>
    obtain ⟨pre,old,post,rfl,rfl,ho,hp⟩ := index_certificate selected xs n h
    have hd : pre.drop (pre.length + 1) = [] := List.drop_eq_nil_iff.mpr (by omega)
    simpa [h,List.drop_append,hd] using first_removal_refinement selected raw pre post old hu hr hp ho

theorem queried_target_safe (selected : ι → Bool) (raw : Storage ι ν) (xs : List E) (n : Nat)
    (hr : Represents raw xs) (h : firstIndex selected xs = some n) :
    n < raw.declarations.length ∧
      ∃ old, raw.declarations[n]? = some (payload old) ∧
        raw.importance[n]? = some old.important ∧ selected old.id = true := by
  obtain ⟨pre,old,post,rfl,rfl,ho,_⟩ := index_certificate selected xs n h
  have ht := deletion_target raw pre post old hr
  exact ⟨ht.1,old,ht.2.1,ht.2.2,ho⟩

theorem cached_removal_refinement (selected : ι → Bool) (raw : Storage ι ν) (xs : List E) (n : Nat)
    (hu : unique xs) (hr : Represents raw xs) (h : firstIndex selected xs = some n) :
    Represents (removeAt raw selected n) (xs.filter (fun e => !selected e.id)) := by
  classical
  have he : removeProperty raw selected = removeAt raw selected n := by
    simp [removeProperty,decode_representation raw xs hr,h]
  rw [← he]
  exact queried_removal_refinement selected raw xs hu hr

theorem query_depends_on_ids (selected : ι → Bool) (before after : List E)
    (h : before.map Entry.id = after.map Entry.id) :
    firstIndex selected before = firstIndex selected after := by
  induction before generalizing after with
  | nil =>
    cases after <;> simp_all [firstIndex]
  | cons old rest ih =>
    cases after with
    | nil => simp at h
    | cons new tail =>
      have he : old.id = new.id ∧ rest.map Entry.id = tail.map Entry.id := by simpa using h
      simp [firstIndex,he.1,ih tail he.2]

theorem callback_stable_removal (selected : ι → Bool) (raw : Storage ι ν)
    (before after : List E) (n : Nat) (hu : unique after) (hr : Represents raw after)
    (frame : before.map Entry.id = after.map Entry.id)
    (query : firstIndex selected before = some n) :
    Represents (removeAt raw selected n) (after.filter (fun e => !selected e.id)) := by
  have h : firstIndex selected after = some n := (query_depends_on_ids selected before after frame).symm.trans query
  exact cached_removal_refinement selected raw after n hu hr h

theorem stale_index_witness :
    firstIndex (fun id : Nat => id == 1) ([⟨0,7,false⟩,⟨1,8,true⟩] : List (Entry Nat Nat)) = some 1 ∧
    firstIndex (fun id : Nat => id == 1) ([⟨1,8,true⟩] : List (Entry Nat Nat)) = some 0 := by
  decide

end PublicRemoval
