import NativeRemoval
set_option linter.unusedSectionVars false
namespace NativeRemovalAPI
open AllOrder PublicStorage PublicRemoval
variable {ι ν : Type} [DecidableEq ι]
local notation "E" => Entry ι ν

def seek (selected : ι → Bool) : List (ι × ν) → Option Nat
  | [] => none
  | old::rest => if selected old.1 then some 0 else (seek selected rest).map Nat.succ

theorem seek_projection (selected : ι → Bool) (xs : List E) :
    seek selected (xs.map payload) = firstIndex selected xs := by
  induction xs with
  | nil => rfl
  | cons old rest ih => simp [seek,firstIndex,ih,payload]

def query (raw : Storage ι ν) (property : PublicAPI.Property ι) : Option Nat :=
  match property with
  | .single id => if raw.present id then seek (PublicAPI.selected property) raw.declarations else none
  | .shorthand _ => seek (PublicAPI.selected property) raw.declarations

theorem query_connection (raw : Storage ι ν) (xs : List E) (property : PublicAPI.Property ι)
    (hr : Represents raw xs) : query raw property = PublicAPI.query raw property := by
  classical
  cases property <;> simp [query,PublicAPI.query,hr.1,seek_projection,decode_representation raw xs hr]

def remove (raw : Storage ι ν) (property : PublicAPI.Property ι) (n : Nat) : Storage ι ν :=
  match raw.declarations[n]? with
  | none => raw
  | some old =>
    let deleted := rawDelete raw old.1 n
    match property with
    | .single _ => deleted
    | .shorthand member => (NativeRemoval.loop member deleted n deleted.declarations.length).raw

theorem remove_connection (raw : Storage ι ν) (xs : List E) (property : PublicAPI.Property ι)
    (n : Nat) (hu : unique xs) (hr : Represents raw xs)
    (hq : firstIndex (PublicAPI.selected property) xs = some n) :
    remove raw property n = PublicAPI.remove raw property n := by
  classical
  obtain ⟨pre,old,post,rfl,rfl,ho,hp⟩ := index_certificate (PublicAPI.selected property) xs n hq
  have ht := deletion_target raw pre post old hr
  have hd := raw_delete_refinement raw pre post old hu hr
  have hn := delete_unique pre post old hu
  have hl : (rawDelete raw old.id pre.length).declarations.length = pre.length+post.length := by simp [hd.1]
  have hz : pre.drop (pre.length+1) = [] := List.drop_eq_nil_of_le (by omega)
  cases property with
  | single id => simp [remove,PublicAPI.remove,ht.2.1,decode_representation raw _ hr,payload]
  | shorthand member =>
    have hloop := congrArg NativeRemoval.Result.raw (NativeRemoval.split_connection member
      (rawDelete raw old.id pre.length) pre post hn hd)
    simp only at hloop
    simp [remove,PublicAPI.remove,removeAt,ht.2.1,payload,decode_representation raw _ hr,hl,hloop,List.drop_append,hz]

def removeQueried (raw : Storage ι ν) (property : PublicAPI.Property ι) : Storage ι ν :=
  match query raw property with
  | none => raw
  | some n => remove raw property n

theorem queried_connection (raw : Storage ι ν) (xs : List E) (property : PublicAPI.Property ι)
    (hu : unique xs) (hr : Represents raw xs) :
    removeQueried raw property = PublicAPI.removeQueried raw property := by
  unfold removeQueried PublicAPI.removeQueried
  rw [query_connection raw xs property hr]
  cases hq : PublicAPI.query raw property with
  | none => rfl
  | some n =>
    rw [PublicAPI.query_refinement raw xs property hr] at hq
    exact remove_connection raw xs property n hu hr hq

theorem queried_refinement (raw : Storage ι ν) (xs : List E) (property : PublicAPI.Property ι)
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (removeQueried raw property) (xs.filter (fun e => !PublicAPI.selected property e.id)) := by
  rw [queried_connection raw xs property hu hr]
  exact PublicAPI.queried_api_refinement raw xs property hu hr

def step (raw : Storage ι ν) : PublicAPI.PublicOperation ι ν → Storage ι ν
  | .parse actions => rawExtend raw actions
  | .remove property => removeQueried raw property
  | .clear => rawClear

theorem step_connection (raw : Storage ι ν) (xs : List E) (op : PublicAPI.PublicOperation ι ν)
    (hu : unique xs) (hr : Represents raw xs) : step raw op = PublicAPI.rawPublicStep raw op := by
  cases op with
  | parse _ | clear => rfl
  | remove property => exact queried_connection raw xs property hu hr

theorem history_refinement (raw : Storage ι ν) (xs : List E) (ops : List (PublicAPI.PublicOperation ι ν))
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (ops.foldl step raw) (ops.foldl PublicAPI.referenceStep xs) ∧
      unique (ops.foldl PublicAPI.referenceStep xs) := by
  induction ops generalizing raw xs with
  | nil => exact ⟨hr,hu⟩
  | cons op rest ih =>
    simp only [List.foldl_cons]
    rw [step_connection raw xs op hu hr]
    have h := PublicAPI.public_step_refinement raw xs op hu hr
    exact ih _ _ h.2 h.1

theorem every_prefix (raw : Storage ι ν) (xs : List E) (ops : List (PublicAPI.PublicOperation ι ν))
    (hu : unique xs) (hr : Represents raw xs) (n : Nat) :
    Represents ((ops.take n).foldl step raw) ((ops.take n).foldl PublicAPI.referenceStep xs) ∧
      unique ((ops.take n).foldl PublicAPI.referenceStep xs) :=
  history_refinement raw xs (ops.take n) hu hr

theorem callback_refinement (beforeRaw afterRaw : Storage ι ν) (before after : List E)
    (property : PublicAPI.Property ι) (n : Nat) (hb : Represents beforeRaw before)
    (ha : Represents afterRaw after) (hu : unique after)
    (frame : before.map Entry.id = after.map Entry.id) (hq : query beforeRaw property = some n) :
    Represents (remove afterRaw property n) (after.filter (fun e => !PublicAPI.selected property e.id)) := by
  rw [query_connection beforeRaw before property hb,PublicAPI.query_refinement beforeRaw before property hb] at hq
  have h : firstIndex (PublicAPI.selected property) after = some n :=
    (query_depends_on_ids (PublicAPI.selected property) before after frame).symm.trans hq
  rw [remove_connection afterRaw after property n hu ha h]
  exact PublicAPI.remove_refinement afterRaw after property n hu ha h

end NativeRemovalAPI
