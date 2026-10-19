import PublicAPI
set_option linter.unusedSectionVars false
namespace NativeRemoval
open AllOrder PublicStorage PublicRemoval
variable {ι ν : Type} [DecidableEq ι]
local notation "E" => Entry ι ν

structure Result (ι ν : Type) where
  raw : Storage ι ν
  index : Nat
  len : Nat
  fault : Bool
  steps : Nat

def loop (selected : ι → Bool) (raw : Storage ι ν) (index len : Nat) : Result ι ν :=
  if _h : index < len then
    match raw.declarations[index]? with
    | none => ⟨raw,index,len,true,0⟩
    | some old =>
      let next := if selected old.1 then
        loop selected (rawDelete raw old.1 index) index (len-1)
      else loop selected raw (index+1) len
      {next with steps := next.steps+1}
  else ⟨raw,index,len,false,0⟩
termination_by len-index
decreasing_by all_goals omega

theorem split_connection (selected : ι → Bool) (raw : Storage ι ν)
    (pre rest : List E) (hu : unique (pre ++ rest)) (hr : Represents raw (pre ++ rest)) :
    loop selected raw pre.length (pre.length+rest.length) =
      ⟨removeLoop selected raw pre rest,
       pre.length+(rest.filter (fun e => !selected e.id)).length,
       pre.length+(rest.filter (fun e => !selected e.id)).length,false,rest.length⟩ := by
  induction rest generalizing raw pre with
  | nil => simp [loop,removeLoop]
  | cons old rest ih =>
    have ht := deletion_target raw pre rest old hr
    have hb : pre.length < pre.length+(old::rest).length := by simp
    rw [loop, dite_eq_left hb, ht.2.1]
    cases hs : selected old.id with
    | true =>
      have hd := raw_delete_refinement raw pre rest old hu hr
      have hn := delete_unique pre rest old hu
      have he : pre.length+(old::rest).length-1 = pre.length+rest.length := by simp
      simp only [he]
      rw [ih _ _ hn hd]
      simp [removeLoop,hs]
    | false =>
      have he : (pre++[old])++rest = pre++old::rest := by simp
      have hn := ih raw (pre++[old]) (he.symm ▸ hu) (he.symm ▸ hr)
      have hi : (pre++[old]).length = pre.length+1 := by simp
      rw [hi] at hn
      have hl : pre.length+(old::rest).length = pre.length+1+rest.length := by simp; omega
      simp only [hl]
      rw [hn]
      simp [removeLoop,hs,Nat.add_assoc,Nat.add_comm]

inductive Safe (selected : ι → Bool) : Storage ι ν → Nat → Nat → Prop where
  | done (raw : Storage ι ν) (n : Nat)
      (hd : raw.declarations.length = n) (hb : raw.importance.length = n) :
      Safe selected raw n n
  | keep (raw : Storage ι ν) (i len : Nat) (old : E)
      (hd : raw.declarations.length = len) (hb : raw.importance.length = len)
      (hi : i < len) (hr : raw.declarations[i]? = some (payload old))
      (hp : raw.importance[i]? = some old.important) (hs : selected old.id = false)
      (next : Safe selected raw (i+1) len) : Safe selected raw i len
  | erase (raw : Storage ι ν) (i len : Nat) (old : E)
      (hd : raw.declarations.length = len) (hb : raw.importance.length = len)
      (hi : i < len) (hr : raw.declarations[i]? = some (payload old))
      (hp : raw.importance[i]? = some old.important) (hs : selected old.id = true)
      (next : Safe selected (rawDelete raw old.id i) i (len-1)) : Safe selected raw i len

theorem invariant_safe (selected : ι → Bool) (raw : Storage ι ν)
    (pre rest : List E) (hu : unique (pre++rest)) (hr : Represents raw (pre++rest)) :
    Safe selected raw pre.length (pre.length+rest.length) := by
  induction rest generalizing raw pre with
  | nil =>
    simpa using Safe.done raw pre.length (by simp [hr.1]) (by simp [hr.2.1])
  | cons old rest ih =>
    have ht := deletion_target raw pre rest old hr
    have hd : raw.declarations.length = pre.length+(old::rest).length := by simp [hr.1]
    have hb : raw.importance.length = pre.length+(old::rest).length := by simp [hr.2.1]
    cases hs : selected old.id with
    | true =>
      apply Safe.erase raw _ _ old hd hb (by simp) ht.2.1 ht.2.2 hs
      have h := ih (rawDelete raw old.id pre.length) pre
        (delete_unique pre rest old hu) (raw_delete_refinement raw pre rest old hu hr)
      simpa using h
    | false =>
      apply Safe.keep raw _ _ old hd hb (by simp) ht.2.1 ht.2.2 hs
      have he : (pre++[old])++rest = pre++old::rest := by simp
      have h := ih raw (pre++[old]) (he.symm ▸ hu) (he.symm ▸ hr)
      simpa [Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using h

theorem safe_head (selected : ι → Bool) (raw : Storage ι ν) (i len : Nat)
    (h : Safe selected raw i len) :
    i ≤ len ∧ raw.declarations.length = len ∧ raw.importance.length = len ∧
      (i < len → ∃ old : E, raw.declarations[i]? = some (payload old) ∧
          raw.importance[i]? = some old.important) := by
  cases h with
  | done raw n hd hb => exact ⟨Nat.le_refl _,hd,hb,by omega⟩
  | keep raw i len old hd hb hi hr hp hs next => exact ⟨Nat.le_of_lt hi,hd,hb,by intro _; exact ⟨old,hr,hp⟩⟩
  | erase raw i len old hd hb hi hr hp hs next => exact ⟨Nat.le_of_lt hi,hd,hb,by intro _; exact ⟨old,hr,hp⟩⟩

theorem removal_measure_decreases (i len : Nat) (h : i < len) :
    (len-1)-i < len-i ∧ len-(i+1) < len-i := by omega

theorem terminal_invariants (selected : ι → Bool) (raw : Storage ι ν)
    (pre rest : List E) (hu : unique (pre++rest)) (hr : Represents raw (pre++rest)) :
    let result := loop selected raw pre.length (pre.length+rest.length)
    result.fault = false ∧ result.index = result.len ∧
      result.raw.declarations.length = result.len ∧ result.raw.importance.length = result.len ∧
      result.steps = rest.length ∧
      Represents result.raw (pre++rest.filter (fun e => !selected e.id)) := by
  rw [split_connection selected raw pre rest hu hr]
  have h := removal_loop_refinement selected raw pre rest hu hr
  exact ⟨rfl,rfl,by simp [h.1],by simp [h.2.1],rfl,h⟩

theorem delete_transition (selected : ι → Bool) (raw : Storage ι ν) (i len : Nat)
    (old : ι × ν) (hi : i < len) (hr : raw.declarations[i]? = some old)
    (hs : selected old.1 = true) :
    loop selected raw i len =
      let next := loop selected (rawDelete raw old.1 i) i (len-1)
      {next with steps := next.steps+1} := by
  rw [loop,dite_eq_left hi,hr]
  simp [hs]

theorem keep_transition (selected : ι → Bool) (raw : Storage ι ν) (i len : Nat)
    (old : ι × ν) (hi : i < len) (hr : raw.declarations[i]? = some old)
    (hs : selected old.1 = false) :
    loop selected raw i len =
      let next := loop selected raw (i+1) len
      {next with steps := next.steps+1} := by
  rw [loop,dite_eq_left hi,hr]
  simp [hs]

end NativeRemoval
