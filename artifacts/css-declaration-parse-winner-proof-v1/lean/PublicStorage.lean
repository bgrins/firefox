import AllOrder
set_option linter.unusedSectionVars false

namespace PublicStorage
open AllOrder
variable {ι ν : Type} [DecidableEq ι]
local notation "E" => Entry ι ν

def parseSet : List E → E → List E
  | [], new => [new]
  | old :: rest, new =>
    if old.id = new.id then
      if old.important && !new.important then old :: rest else rest ++ [new]
    else old :: parseSet rest new

def pushScan (new : E) : Nat → List E → Plan
  | _, [] => .append
  | n, old :: rest =>
    if old.id = new.id then
      if old.important && !new.important then .none else .move n
    else pushScan new (n + 1) rest

theorem parse_absent (xs : List E) (new : E) (ha : absent new.id xs) :
    parseSet xs new = xs ++ [new] := by
  induction xs with
  | nil => rfl
  | cons old rest ih =>
    have hn := ha old (by simp)
    have ht : absent new.id rest := fun e he => ha e (by simp [he])
    simp [parseSet, hn, ih ht]

theorem scan_absent (xs : List E) (new : E) (ha : absent new.id xs) (n : Nat) :
    pushScan new n xs = .append := by
  induction xs generalizing n with
  | nil => rfl
  | cons old rest ih =>
    have hn := ha old (by simp)
    have ht : absent new.id rest := fun e he => ha e (by simp [he])
    simp [pushScan, hn, ih ht]

theorem parse_split (pre post : List E) (old new : E)
    (ha : absent new.id pre) (he : old.id = new.id) :
    parseSet (pre ++ old :: post) new =
      if old.important && !new.important then pre ++ old :: post else pre ++ post ++ [new] := by
  induction pre with
  | nil => simp [parseSet, he]
  | cons first rest ih =>
    have hn := ha first (by simp)
    have ht : absent new.id rest := fun e hm => ha e (by simp [hm])
    simp only [List.cons_append, parseSet, ite_eq_right hn, ih ht]
    split <;> rfl

theorem scan_split (pre post : List E) (old new : E)
    (ha : absent new.id pre) (he : old.id = new.id) (n : Nat) :
    pushScan new n (pre ++ old :: post) =
      if old.important && !new.important then .none else .move (n + pre.length) := by
  induction pre generalizing n with
  | nil => simp [pushScan, he]
  | cons first rest ih =>
    have hn := ha first (by simp)
    have ht : absent new.id rest := fun e hm => ha e (by simp [hm])
    simp [pushScan, hn, ih ht, Nat.add_comm, Nat.add_left_comm]

theorem push_refinement (xs : List E) (new : E) (hu : unique xs) :
    execute xs new (pushScan new 0 xs) = parseSet xs new := by
  classical
  rcases unique_split xs new hu with ha | ⟨pre, old, post, rfl, he, hp, _⟩
  · simp [scan_absent xs new ha, parse_absent xs new ha, execute]
  · rw [scan_split pre post old new hp he, parse_split pre post old new hp he]
    split
    · rfl
    · simpa using execute_split_move pre post old new

theorem push_plan_valid (xs : List E) (new : E) (hu : unique xs) :
    ValidPlan xs new (pushScan new 0 xs) := by
  classical
  rcases unique_split xs new hu with ha | ⟨pre, old, post, rfl, he, hp, _⟩
  · rw [scan_absent xs new ha]; exact .append
  · rw [scan_split pre post old new hp he]
    split
    · exact .none
    · simpa using ValidPlan.move pre post old rfl he

theorem parse_membership (xs : List E) (new : E) (id : ι) :
    id ∈ (parseSet xs new).map Entry.id ↔ id = new.id ∨ id ∈ xs.map Entry.id := by
  induction xs with
  | nil => simp [parseSet]
  | cons old rest ih =>
    simp only [parseSet]
    split
    · next he => split <;> simp [he, or_comm]
    · simp [ih, or_left_comm]

theorem parse_unique (xs : List E) (new : E) (hu : unique xs) :
    unique (parseSet xs new) := by
  induction xs with
  | nil => simp [parseSet, unique]
  | cons old rest ih =>
    have hh := (List.nodup_cons.mp hu).1
    have ht : unique rest := (List.nodup_cons.mp hu).2
    simp only [parseSet]
    split
    · next he =>
      split
      · exact hu
      · have hn : new.id ∉ rest.map Entry.id := by simpa [he] using hh
        simp only [unique, List.map_append, List.map_cons, List.map_nil]
        apply List.nodup_append.mpr
        refine ⟨ht, by simp, ?_⟩
        intro a ha b hb hab
        have hbnew : b = new.id := by simpa using hb
        exact hn ((hab.trans hbnew) ▸ ha)
    · next he =>
      apply List.nodup_cons.mpr
      refine ⟨?_, ih ht⟩
      intro hm
      rcases (parse_membership rest new old.id).mp hm with hn | hn
      · exact he hn
      · exact hh hn

def rawPush (raw : Storage ι ν) (new : E) : Storage ι ν :=
  let inserted : Storage ι ν := {raw with present := fun id => if id = new.id then true else raw.present id}
  if raw.present new.id then rawStep inserted new (pushScan new 0 (decode raw))
  else rawStep inserted new .append

theorem raw_push_refinement (raw : Storage ι ν) (xs : List E) (new : E)
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (rawPush raw new) (parseSet xs new) := by
  classical
  have hd := decode_representation raw xs hr
  unfold rawPush
  split
  · next hp =>
    have inserted_eq : (fun id => if id = new.id then true else raw.present id) = raw.present := by
      funext id
      by_cases he : id = new.id
      · simp [he, hp]
      · simp [he]
    rw [inserted_eq, hd, ← push_refinement xs new hu]
    exact raw_operation_representation raw xs new _ hr (push_plan_valid xs new hu)
  · next hp =>
    have ha : absent new.id xs := by
      intro e hm he
      have : new.id ∈ xs.map Entry.id := List.mem_map.mpr ⟨e,hm,he⟩
      simp [hr.2.2, this] at hp
    rw [parse_absent xs new ha]
    rcases hr with ⟨hd,hb,hi⟩
    refine ⟨by simp [rawStep,hd],by simp [rawStep,hb],?_⟩
    intro id
    by_cases he : id = new.id
    · simp [rawStep,he]
    · simp [rawStep,he,hi]

theorem parse_downgrade_preserves (pre post : List E) (old new : E)
    (ha : absent new.id pre) (he : old.id = new.id)
    (ho : old.important = true) (hn : new.important = false) :
    parseSet (pre ++ old :: post) new = pre ++ old :: post := by
  simp [parse_split pre post old new ha he, ho, hn]

theorem parse_other_values (xs : List E) (new : E) (keep : E → Bool)
    (hn : keep new = false) (ht : ∀ e, e.id = new.id → keep e = false) :
    (parseSet xs new).filter keep = xs.filter keep := by
  induction xs with
  | nil => simp [parseSet, hn]
  | cons old rest ih =>
    simp only [parseSet]
    split
    · next he => split <;> simp [ht old he, hn]
    · simp [List.filter_cons, ih]

def parseExtend (xs actions : List E) : List E := actions.foldl parseSet xs

def rawExtend (raw : Storage ι ν) (actions : List E) : Storage ι ν :=
  actions.foldl rawPush raw

theorem extend_unique (xs actions : List E) (hu : unique xs) :
    unique (parseExtend xs actions) := by
  induction actions generalizing xs with
  | nil => exact hu
  | cons new rest ih => exact ih _ (parse_unique xs new hu)

theorem raw_extend_refinement (raw : Storage ι ν) (xs actions : List E)
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (rawExtend raw actions) (parseExtend xs actions) := by
  induction actions generalizing raw xs with
  | nil => exact hr
  | cons new rest ih =>
    exact ih _ _ (parse_unique xs new hu) (raw_push_refinement raw xs new hu hr)

def rawDelete (raw : Storage ι ν) (id : ι) (n : Nat) : Storage ι ν :=
  ⟨raw.declarations.take n ++ raw.declarations.drop (n + 1),
   raw.importance.take n ++ raw.importance.drop (n + 1),
   fun target => if target = id then false else raw.present target⟩

theorem delete_unique (pre post : List E) (old : E) (hu : unique (pre ++ old :: post)) :
    unique (pre ++ post) := by
  have hf := List.Nodup.sublist (List.Sublist.map Entry.id
    (List.Sublist.append (List.Sublist.refl pre) (List.Sublist.cons old (List.Sublist.refl post)))) hu
  exact hf

theorem removed_absent (pre post : List E) (old : E) (hu : unique (pre ++ old :: post)) :
    old.id ∉ (pre ++ post).map Entry.id := by
  have h := List.nodup_append.mp (show (pre.map Entry.id ++ old.id :: post.map Entry.id).Nodup by
    simpa [unique] using hu)
  simp only [List.map_append, List.mem_append]
  intro hm
  rcases hm with hp | ht
  · exact h.2.2 old.id hp old.id (by simp) rfl
  · exact (List.nodup_cons.mp h.2.1).1 ht

theorem raw_delete_refinement (raw : Storage ι ν) (pre post : List E) (old : E)
    (hu : unique (pre ++ old :: post)) (hr : Represents raw (pre ++ old :: post)) :
    Represents (rawDelete raw old.id pre.length) (pre ++ post) := by
  rcases hr with ⟨hd,hb,hi⟩
  refine ⟨by simp [rawDelete,hd,List.drop_append],
    by simp [rawDelete,hb,List.drop_append],?_⟩
  intro id
  by_cases he : id = old.id
  · simp only [rawDelete,he,ite_true,removed_absent pre post old hu,decide_false]
  · simp [rawDelete,he,hi]

theorem deletion_target (raw : Storage ι ν) (pre post : List E) (old : E)
    (hr : Represents raw (pre ++ old :: post)) :
    pre.length < raw.declarations.length ∧
    raw.declarations[pre.length]? = some (payload old) ∧
    raw.importance[pre.length]? = some old.important := by
  simp [hr.1,hr.2.1]

def rawClear : Storage ι ν := ⟨[], [], fun _ => false⟩

theorem clear_representation : Represents (rawClear : Storage ι ν) [] := by
  simp [Represents,rawClear]

def removeLoop (selected : ι → Bool) : Storage ι ν → List E → List E → Storage ι ν
  | raw, _, [] => raw
  | raw, pre, old :: rest =>
    if selected old.id then removeLoop selected (rawDelete raw old.id pre.length) pre rest
    else removeLoop selected raw (pre ++ [old]) rest

theorem removal_loop_refinement (selected : ι → Bool) (raw : Storage ι ν) (pre rest : List E)
    (hu : unique (pre ++ rest)) (hr : Represents raw (pre ++ rest)) :
    Represents (removeLoop selected raw pre rest)
      (pre ++ rest.filter (fun e => !selected e.id)) := by
  induction rest generalizing raw pre with
  | nil => simpa [removeLoop] using hr
  | cons old rest ih =>
    simp only [removeLoop]
    split
    · next hm =>
      simpa [hm] using ih (rawDelete raw old.id pre.length) pre
        (delete_unique pre rest old hu) (raw_delete_refinement raw pre rest old hu hr)
    · next hm =>
      have he : (pre ++ [old]) ++ rest = pre ++ old :: rest := by simp
      have result := ih raw (pre ++ [old]) (he.symm ▸ hu) (he.symm ▸ hr)
      simpa [hm] using result

def SafeRemoval (selected : ι → Bool) : Storage ι ν → List E → List E → Prop
  | _, _, [] => True
  | raw, pre, old :: rest =>
    (pre.length < raw.declarations.length ∧
      raw.declarations[pre.length]? = some (payload old) ∧
      raw.importance[pre.length]? = some old.important) ∧
    if selected old.id then SafeRemoval selected (rawDelete raw old.id pre.length) pre rest
    else SafeRemoval selected raw (pre ++ [old]) rest

theorem removal_loop_safe (selected : ι → Bool) (raw : Storage ι ν) (pre rest : List E)
    (hu : unique (pre ++ rest)) (hr : Represents raw (pre ++ rest)) :
    SafeRemoval selected raw pre rest := by
  induction rest generalizing raw pre with
  | nil => trivial
  | cons old rest ih =>
    refine ⟨deletion_target raw pre rest old hr, ?_⟩
    split
    · exact ih _ _ (delete_unique pre rest old hu) (raw_delete_refinement raw pre rest old hu hr)
    · have he : (pre ++ [old]) ++ rest = pre ++ old :: rest := by simp
      exact ih _ _ (he.symm ▸ hu) (he.symm ▸ hr)

theorem first_removal_refinement (selected : ι → Bool) (raw : Storage ι ν)
    (pre post : List E) (old : E) (hu : unique (pre ++ old :: post))
    (hr : Represents raw (pre ++ old :: post))
    (hp : ∀ e ∈ pre, selected e.id = false) (ho : selected old.id = true) :
    Represents (removeLoop selected (rawDelete raw old.id pre.length) pre post)
      ((pre ++ old :: post).filter (fun e => !selected e.id)) := by
  have hpre : pre.filter (fun e => !selected e.id) = pre := by
    apply List.filter_eq_self.mpr
    intro e he
    simp [hp e he]
  simpa [hpre,ho] using removal_loop_refinement selected
    (rawDelete raw old.id pre.length) pre post
    (delete_unique pre post old hu) (raw_delete_refinement raw pre post old hu hr)

def rawRemove (raw : Storage ι ν) (selected : ι → Bool) : Storage ι ν :=
  removeLoop selected raw [] (decode raw)

theorem raw_remove_refinement (selected : ι → Bool) (raw : Storage ι ν) (xs : List E)
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (rawRemove raw selected) (xs.filter (fun e => !selected e.id)) := by
  classical
  unfold rawRemove
  rw [decode_representation raw xs hr]
  simpa using removal_loop_refinement selected raw [] xs hu hr

theorem removal_unique (selected : ι → Bool) (xs : List E) (hu : unique xs) :
    unique (xs.filter (fun e => !selected e.id)) := by
  apply List.Nodup.sublist _ hu
  exact List.Sublist.map Entry.id List.filter_sublist

inductive Operation (ι ν : Type) where
  | parse (actions : List (Entry ι ν))
  | remove (selected : ι → Bool)
  | clear

def referenceOperation (xs : List E) : Operation ι ν → List E
  | .parse actions => parseExtend xs actions
  | .remove selected => xs.filter (fun e => !selected e.id)
  | .clear => []

def rawOperation (raw : Storage ι ν) : Operation ι ν → Storage ι ν
  | .parse actions => rawExtend raw actions
  | .remove selected => rawRemove raw selected
  | .clear => rawClear

theorem operation_refinement (raw : Storage ι ν) (xs : List E) (op : Operation ι ν)
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (rawOperation raw op) (referenceOperation xs op) ∧ unique (referenceOperation xs op) := by
  cases op with
  | parse actions => exact ⟨raw_extend_refinement raw xs actions hu hr, extend_unique xs actions hu⟩
  | remove selected => exact ⟨raw_remove_refinement selected raw xs hu hr, removal_unique selected xs hu⟩
  | clear => exact ⟨clear_representation, by simp [referenceOperation,unique]⟩

theorem arbitrary_public_history (raw : Storage ι ν) (xs : List E) (ops : List (Operation ι ν))
    (hu : unique xs) (hr : Represents raw xs) :
    Represents (ops.foldl rawOperation raw) (ops.foldl referenceOperation xs) ∧
      unique (ops.foldl referenceOperation xs) := by
  induction ops generalizing raw xs with
  | nil => exact ⟨hr, hu⟩
  | cons op rest ih =>
    have h := operation_refinement raw xs op hu hr
    exact ih _ _ h.2 h.1

theorem every_public_prefix (raw : Storage ι ν) (xs : List E) (ops : List (Operation ι ν))
    (hu : unique xs) (hr : Represents raw xs) (n : Nat) :
    Represents ((ops.take n).foldl rawOperation raw) ((ops.take n).foldl referenceOperation xs) ∧
      unique ((ops.take n).foldl referenceOperation xs) :=
  arbitrary_public_history raw xs (ops.take n) hu hr

end PublicStorage
