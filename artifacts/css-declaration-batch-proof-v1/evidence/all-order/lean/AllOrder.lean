import Std
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace AllOrder

structure Entry (ι ν : Type) where
  id : ι
  value : ν
  important : Bool
  deriving DecidableEq, Repr

inductive Plan where
  | none | append | replace (pos : Nat) | move (pos : Nat)
  deriving DecidableEq, Repr

inductive Search where
  | pending (oppositeSeen : Bool)
  | found (plan : Plan)
  deriving DecidableEq, Repr

variable {ι ν : Type} [DecidableEq ι] [DecidableEq ν]

local notation "E" => Entry ι ν

def opposite (group : ι → Option Nat) (logical : ι → Bool) (a b : ι) : Bool :=
  group a != none && group a == group b && logical a != logical b

theorem opposite_irrefl (group : ι → Option Nat) (logical : ι → Bool) (a : ι) :
    opposite group logical a a = false := by simp [opposite]

def decideFound (old new : E) (seen : Bool) (pos : Nat) : Plan :=
  if seen then .move pos else if old = new then .none else .replace pos

def scan (op : ι → ι → Bool) (new : E) : Nat → List E → Search
  | _, [] => .pending false
  | n, old :: tail =>
    match scan op new (n + 1) tail with
    | .found p => .found p
    | .pending seen =>
      if old.id = new.id then .found (decideFound old new seen n)
      else .pending (op new.id old.id || seen)

def planner (op : ι → ι → Bool) (xs : List E) (new : E) : Plan :=
  match scan op new 0 xs with
  | .pending _ => .append
  | .found p => p

def execute (xs : List E) (new : E) : Plan → List E
  | .none => xs
  | .append => xs ++ [new]
  | .replace pos => xs.take pos ++ [new] ++ xs.drop (pos + 1)
  | .move pos => xs.take pos ++ xs.drop (pos + 1) ++ [new]

def reference (op : ι → ι → Bool) : List E → E → List E
  | [], new => [new]
  | old :: tail, new =>
    if old.id = new.id then
      if tail.any (fun e => op new.id e.id) then tail ++ [new] else new :: tail
    else old :: reference op tail new

def unique (xs : List E) : Prop := (xs.map Entry.id).Nodup

def absent (id : ι) (xs : List E) : Prop := ∀ e ∈ xs, e.id ≠ id

theorem scan_absent (op : ι → ι → Bool) (new : E) (xs : List E) (h : absent new.id xs)
    (n : Nat) : scan op new n xs = .pending (xs.any (fun e => op new.id e.id)) := by
  induction xs generalizing n with
  | nil => rfl
  | cons old tail ih =>
    have ho := h old (by simp)
    have ht : absent new.id tail := by intro e he; exact h e (by simp [he])
    simp [scan, ih ht, ho]

theorem scan_prepend_found (op : ι → ι → Bool) (new : E) (pre tail : List E)
    (n : Nat) (p : Plan) (h : scan op new (n + pre.length) tail = .found p) :
    scan op new n (pre ++ tail) = .found p := by
  induction pre generalizing n with
  | nil => simpa using h
  | cons e pre ih =>
    have h' : scan op new (n + 1 + pre.length) tail = .found p := by
      simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using h
    simp [scan, ih (n + 1) h']

theorem scan_split (op : ι → ι → Bool) (new old : E) (pre post : List E)
    (h : old.id = new.id) (ha : absent new.id post) :
    scan op new 0 (pre ++ old :: post) =
      .found (decideFound old new (post.any (fun e => op new.id e.id)) pre.length) := by
  apply scan_prepend_found
  simp [scan, scan_absent op new post ha, h]

theorem execute_split_replace (pre post : List E) (old new : E) :
    execute (pre ++ old :: post) new (.replace pre.length) = pre ++ new :: post := by
  simp [execute, List.take_append, List.drop_append, List.append_assoc]

theorem execute_split_move (pre post : List E) (old new : E) :
    execute (pre ++ old :: post) new (.move pre.length) = pre ++ post ++ [new] := by
  simp [execute, List.take_append, List.drop_append]

theorem reference_absent (op : ι → ι → Bool) (new : E) (xs : List E)
    (h : absent new.id xs) : reference op xs new = xs ++ [new] := by
  induction xs with
  | nil => rfl
  | cons old tail ih =>
    have ho := h old (by simp)
    have ht : absent new.id tail := by intro e he; exact h e (by simp [he])
    simp [reference, ho, ih ht]

theorem reference_split (op : ι → ι → Bool) (new old : E) (pre post : List E)
    (hp : absent new.id pre) (h : old.id = new.id) :
    reference op (pre ++ old :: post) new =
      if post.any (fun e => op new.id e.id) then pre ++ post ++ [new] else pre ++ new :: post := by
  induction pre with
  | nil => simp [reference, h]
  | cons e pre ih =>
    have he := hp e (by simp)
    have ht : absent new.id pre := by intro e he; exact hp e (by simp [he])
    simp [reference, he, ih ht]
    split <;> rfl

theorem unique_split (xs : List E) (new : E) (hu : unique xs) :
    absent new.id xs ∨ ∃ pre old post, xs = pre ++ old :: post ∧
      old.id = new.id ∧ absent new.id pre ∧ absent new.id post := by
  induction xs with
  | nil => left; intro e h; simp at h
  | cons old tail ih =>
    have hu' : unique tail := (List.nodup_cons.mp hu).2
    by_cases h : old.id = new.id
    · right
      refine ⟨[], old, tail, rfl, h, ?_, ?_⟩
      · intro e he; simp at he
      · intro e he hid
        have : old.id ∈ tail.map Entry.id := by
          apply List.mem_map.mpr; exact ⟨e, he, hid.trans h.symm⟩
        exact (List.nodup_cons.mp hu).1 this
    · rcases ih hu' with ha | ⟨pre, e, post, ht, he, hp, hs⟩
      · left; intro e hm; rcases List.mem_cons.mp hm with rfl | hm
        · exact h
        · exact ha e hm
      · right
        refine ⟨old :: pre, e, post, by simp [ht], he, ?_, hs⟩
        intro e hm; rcases List.mem_cons.mp hm with rfl | hm
        · exact h
        · exact hp e hm

theorem planner_refinement (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) : execute xs new (planner op xs new) = reference op xs new := by
  rcases unique_split xs new hu with ha | ⟨pre, old, post, rfl, he, hp, hs⟩
  · simp [planner, scan_absent op new xs ha, execute, reference_absent op new xs ha]
  · rw [reference_split op new old pre post hp he]
    simp only [planner, scan_split op new old pre post he hs]
    unfold decideFound
    split
    · exact execute_split_move pre post old new
    · split
      · next h => subst old; rfl
      · exact execute_split_replace pre post old new


theorem reference_filter (op : ι → ι → Bool) (xs : List E) (new : E)
    (keep : E → Bool) (hn : keep new = false)
    (ht : ∀ e, e.id = new.id → keep e = false) :
    (reference op xs new).filter keep = xs.filter keep := by
  induction xs with
  | nil => simp [reference, hn]
  | cons old tail ih =>
    simp only [reference]
    split
    · next h => simp [ht old h, hn]; split <;> simp [hn]
    · simp [List.filter_cons, ih]

theorem reference_membership (op : ι → ι → Bool) (xs : List E) (new : E) (id : ι) :
    id ∈ (reference op xs new).map Entry.id ↔ id = new.id ∨ id ∈ xs.map Entry.id := by
  induction xs with
  | nil => simp [reference]
  | cons old tail ih =>
    simp only [reference]
    split
    · next h => split <;> simp [h, or_comm]
    · simp [ih, or_left_comm]

theorem reference_unique (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) : unique (reference op xs new) := by
  induction xs with
  | nil => simp [reference, unique]
  | cons old tail ih =>
    have hh := (List.nodup_cons.mp hu).1
    have ht : unique tail := (List.nodup_cons.mp hu).2
    simp only [reference]
    split
    · next h =>
      have hn : new.id ∉ tail.map Entry.id := by simpa [h] using hh
      split
      · simp only [unique, List.map_append, List.map_cons, List.map_nil]
        apply List.nodup_append.mpr
        refine ⟨ht, by simp, ?_⟩
        intro a ha b hb hab
        have hbnew : b = new.id := by simpa using hb
        exact hn ((hab.trans hbnew) ▸ ha)
      · exact List.nodup_cons.mpr ⟨hn, ht⟩
    · next h =>
      apply List.nodup_cons.mpr
      constructor
      · intro hm
        rcases (reference_membership op tail new old.id).mp hm with he | he
        · exact h he
        · exact hh he
      · exact ih ht

def nativeStep (op : ι → ι → Bool) (xs : List E) (new : E) : List E :=
  execute xs new (planner op xs new)

def nativeRun (op : ι → ι → Bool) (xs actions : List E) : List E :=
  actions.foldl (nativeStep op) xs

def directRun (op : ι → ι → Bool) (xs actions : List E) : List E :=
  actions.foldl (reference op) xs

theorem sequence_refinement (op : ι → ι → Bool) (xs actions : List E)
    (hu : unique xs) : nativeRun op xs actions = directRun op xs actions := by
  induction actions generalizing xs with
  | nil => rfl
  | cons new rest ih =>
    simp only [nativeRun, directRun, List.foldl_cons, nativeStep]
    rw [planner_refinement op xs new hu]
    exact ih (reference op xs new) (reference_unique op xs new hu)

theorem sequence_unique (op : ι → ι → Bool) (xs actions : List E)
    (hu : unique xs) : unique (directRun op xs actions) := by
  induction actions generalizing xs with
  | nil => exact hu
  | cons new rest ih => exact ih _ (reference_unique op xs new hu)

theorem every_prefix_refinement (op : ι → ι → Bool) (xs actions : List E)
    (hu : unique xs) (n : Nat) :
    nativeRun op xs (actions.take n) = directRun op xs (actions.take n) :=
  sequence_refinement op xs (actions.take n) hu

def gate (op : ι → ι → Bool) (xs actions : List E) : Bool :=
  actions.any (fun new => decide (planner op xs new ≠ .none))

def changingSteps (op : ι → ι → Bool) : List E → List E → Bool
  | _, [] => false
  | xs, new :: rest =>
    (decide (planner op xs new ≠ .none)) || changingSteps op (nativeStep op xs new) rest

theorem none_keeps_state (op : ι → ι → Bool) (xs : List E) (new : E)
    (h : planner op xs new = .none) : nativeStep op xs new = xs := by
  simp [nativeStep, h, execute]

theorem first_change_gate (op : ι → ι → Bool) (xs actions : List E) :
    gate op xs actions = changingSteps op xs actions := by
  induction actions generalizing xs with
  | nil => rfl
  | cons new rest ih =>
    by_cases hp : planner op xs new = .none
    · simp [gate, changingSteps, hp, none_keeps_state op xs new hp, ← ih]
    · simp [gate, changingSteps, hp]

theorem false_gate_no_change (op : ι → ι → Bool) (xs actions : List E)
    (h : gate op xs actions = false) : nativeRun op xs actions = xs := by
  induction actions generalizing xs with
  | nil => rfl
  | cons new rest ih =>
    have hs : planner op xs new = .none ∧ gate op xs rest = false := by
      simpa [gate] using h
    simp only [nativeRun, List.foldl_cons]
    rw [none_keeps_state op xs new hs.1]
    exact ih xs hs.2

def guardedRun (op : ι → ι → Bool) (xs actions : List E) : List E :=
  if gate op xs actions then nativeRun op xs actions else xs

theorem guarded_sequence_refinement (op : ι → ι → Bool) (xs actions : List E)
    (hu : unique xs) : guardedRun op xs actions = directRun op xs actions := by
  unfold guardedRun
  split
  · exact sequence_refinement op xs actions hu
  · next h =>
    have hf : gate op xs actions = false := by simpa using h
    rw [← sequence_refinement op xs actions hu, false_gate_no_change op xs actions hf]


theorem planner_none_iff_unchanged (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) : planner op xs new = .none ↔ nativeStep op xs new = xs := by
  constructor
  · exact none_keeps_state op xs new
  · intro hstate
    rcases unique_split xs new hu with ha | ⟨pre, old, post, rfl, he, hp, hs⟩
    · have hp : planner op xs new = .append := by simp [planner, scan_absent op new xs ha]
      have hl := congrArg List.length hstate
      simp [nativeStep, hp, execute] at hl
    · have hp : planner op (pre ++ old :: post) new =
          decideFound old new (post.any (fun e => op new.id e.id)) pre.length := by
        simp [planner, scan_split op new old pre post he hs]
      rw [hp]
      simp only [nativeStep, hp] at hstate
      unfold decideFound at *
      split at hstate
      · next hseen =>
        rw [execute_split_move] at hstate
        have hc : post ++ [new] = old :: post := by simpa [List.append_assoc] using hstate
        cases post with
        | nil => simp at hseen
        | cons e tail =>
          have hh : e = old := (List.cons.inj hc).1
          have hn := hs e (by simp)
          exact False.elim (hn (hh ▸ he))
      · next hseen =>
        split at hstate
        · next hold => simp [hseen, hold]
        · next hold =>
          rw [execute_split_replace] at hstate
          have hc : new :: post = old :: post := List.append_cancel_left hstate
          exact False.elim (hold (List.cons.inj hc).1.symm)

def actualChangingSteps (op : ι → ι → Bool) : List E → List E → Bool
  | _, [] => false
  | xs, new :: rest =>
    decide (nativeStep op xs new ≠ xs) || actualChangingSteps op (nativeStep op xs new) rest

theorem changing_steps_are_actual (op : ι → ι → Bool) (xs actions : List E)
    (hu : unique xs) : changingSteps op xs actions = actualChangingSteps op xs actions := by
  induction actions generalizing xs with
  | nil => rfl
  | cons new rest ih =>
    have hv : unique (nativeStep op xs new) := by
      rw [nativeStep, planner_refinement op xs new hu]
      exact reference_unique op xs new hu
    simp only [changingSteps, actualChangingSteps, ih _ hv]
    simp [planner_none_iff_unchanged op xs new hu]

theorem preparation_gate_actual_changes (op : ι → ι → Bool) (xs actions : List E)
    (hu : unique xs) : gate op xs actions = actualChangingSteps op xs actions := by
  rw [first_change_gate, changing_steps_are_actual op xs actions hu]

inductive ValidPlan (xs : List E) (new : E) : Plan → Prop where
  | none : ValidPlan xs new .none
  | append : ValidPlan xs new .append
  | replace (pre post : List E) (old : E) (hs : xs = pre ++ old :: post)
      (hi : old.id = new.id) : ValidPlan xs new (.replace pre.length)
  | move (pre post : List E) (old : E) (hs : xs = pre ++ old :: post)
      (hi : old.id = new.id) : ValidPlan xs new (.move pre.length)

theorem planner_valid (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) : ValidPlan xs new (planner op xs new) := by
  rcases unique_split xs new hu with ha | ⟨pre, old, post, rfl, he, hp, hs⟩
  · simp [planner, scan_absent op new xs ha]; exact .append
  · simp only [planner, scan_split op new old pre post he hs]
    unfold decideFound
    split
    · exact .move pre post old rfl he
    · split
      · exact .none
      · exact .replace pre post old rfl he

theorem planner_index_bounds (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) (n : Nat)
    (h : planner op xs new = .replace n ∨ planner op xs new = .move n) : n < xs.length := by
  have hv := planner_valid op xs new hu
  rcases h with h | h <;> rw [h] at hv <;> cases hv <;> simp_all

structure Storage (ι ν : Type) where
  declarations : List (ι × ν)
  importance : List Bool
  present : ι → Bool

abbrev payload (e : E) : ι × ν := (e.id, e.value)

def Represents (raw : Storage ι ν) (xs : List E) : Prop :=
  raw.declarations = xs.map payload ∧ raw.importance = xs.map Entry.important ∧
    ∀ id, raw.present id = decide (id ∈ xs.map Entry.id)

def rawStep (raw : Storage ι ν) (new : E) : Plan → Storage ι ν
  | .none => raw
  | .append => ⟨raw.declarations ++ [payload new], raw.importance ++ [new.important],
      fun id => if id = new.id then true else raw.present id⟩
  | .replace n => ⟨raw.declarations.take n ++ [payload new] ++ raw.declarations.drop (n+1),
      raw.importance.take n ++ [new.important] ++ raw.importance.drop (n+1), raw.present⟩
  | .move n => ⟨raw.declarations.take n ++ raw.declarations.drop (n+1) ++ [payload new],
      raw.importance.take n ++ raw.importance.drop (n+1) ++ [new.important],
      fun id => if id = new.id then true else raw.present id⟩

theorem raw_operation_representation (raw : Storage ι ν) (xs : List E) (new : E)
    (plan : Plan) (hr : Represents raw xs) (hv : ValidPlan xs new plan) :
    Represents (rawStep raw new plan) (execute xs new plan) := by
  rcases hr with ⟨hd, hb, hi⟩
  cases hv with
  | none => exact ⟨hd,hb,hi⟩
  | append =>
    refine ⟨by simp [rawStep, execute, hd], by simp [rawStep, execute, hb], ?_⟩
    intro id
    simp [rawStep, execute, hi]
    simp [Bool.or_comm]
  | replace pre post old hs he =>
    subst xs
    rw [execute_split_replace]
    refine ⟨by simp [rawStep, hd, List.drop_append, List.append_assoc],
      by simp [rawStep, hb, List.drop_append, List.append_assoc], ?_⟩
    intro id; simp [rawStep, hi, he]
  | move pre post old hs he =>
    subst xs
    rw [execute_split_move]
    refine ⟨by simp [rawStep, hd, List.drop_append], by simp [rawStep, hb, List.drop_append], ?_⟩
    intro id; simp [rawStep, hi, he]
    simp [Bool.or_assoc, Bool.or_left_comm, Bool.or_comm]

theorem concrete_storage_refinement (op : ι → ι → Bool) (raw : Storage ι ν)
    (xs : List E) (new : E) (hu : unique xs) (hr : Represents raw xs) :
    Represents (rawStep raw new (planner op xs new)) (reference op xs new) := by
  rw [← planner_refinement op xs new hu]
  exact raw_operation_representation raw xs new _ hr (planner_valid op xs new hu)

theorem aligned_storage_lengths (raw : Storage ι ν) (xs : List E)
    (hr : Represents raw xs) : raw.declarations.length = raw.importance.length := by
  simp [hr.1, hr.2.1]

def rawMoveRemoval (raw : Storage ι ν) (n : Nat) : Storage ι ν :=
  ⟨raw.declarations.take n ++ raw.declarations.drop (n+1),
   raw.importance.take n ++ raw.importance.drop (n+1), raw.present⟩

theorem move_transient_retains_membership (raw : Storage ι ν) (n : Nat) :
    (rawMoveRemoval raw n).present = raw.present := rfl

theorem move_remove_then_append (raw : Storage ι ν) (new : E) (n : Nat) :
    rawStep raw new (.move n) = rawStep (rawMoveRemoval raw n) new .append := rfl


def pairView (a b : ι) (xs : List E) : List ι :=
  (xs.map Entry.id).filter (fun id => decide (id = a ∨ id = b))

theorem pairView_cons (a b : ι) (e : E) (xs : List E) :
    pairView a b (e :: xs) = if e.id = a ∨ e.id = b then e.id :: pairView a b xs else pairView a b xs := by
  simp [pairView, List.filter_cons]

theorem pairView_append (a b : ι) (xs ys : List E) :
    pairView a b (xs ++ ys) = pairView a b xs ++ pairView a b ys := by
  simp [pairView, List.filter_append]

theorem pairView_single (a b : ι) (xs : List E) (hu : unique xs)
    (ha : a ∈ xs.map Entry.id) (hb : b ∉ xs.map Entry.id) : pairView a b xs = [a] := by
  induction xs with
  | nil => simp at ha
  | cons old tail ih =>
    have ht : unique tail := (List.nodup_cons.mp hu).2
    have hna : old.id ∉ tail.map Entry.id := (List.nodup_cons.mp hu).1
    have hnb : b ∉ tail.map Entry.id := by intro h; exact hb (by simp [h])
    have hob : old.id ≠ b := by intro h; exact hb (by simp [h])
    by_cases hoa : old.id = a
    · have hz : pairView a b tail = [] := by
        apply List.filter_eq_nil_iff.mpr
        intro id hm
        simp only [decide_eq_true_eq, not_or]
        constructor
        · intro h; exact hna (by simpa [hoa, h] using hm)
        · intro h; exact hnb (h ▸ hm)
      simp [pairView_cons, hoa, hz]
    · have hat : a ∈ tail.map Entry.id := by simpa [Ne.symm hoa] using ha
      simp [pairView_cons, hoa, hob, ih ht hat hnb]

theorem pairView_symm (a b : ι) (xs : List E) : pairView a b xs = pairView b a xs := by
  simp [pairView, or_comm]

theorem pairView_other_setter (op : ι → ι → Bool) (a b : ι) (xs : List E) (new : E)
    (ha : new.id ≠ a) (hb : new.id ≠ b) :
    pairView a b (reference op xs new) = pairView a b xs := by
  simp only [pairView, List.filter_map]
  congr 1
  apply reference_filter
  · simp [Function.comp_def, ha, hb]
  · intro e he; simp [Function.comp_def, he, ha, hb]

theorem pairView_target_last (op : ι → ι → Bool) (a b : ι) (xs : List E) (new : E)
    (hu : unique xs) (hab : a ≠ b) (hn : new.id = b)
    (ha : a ∈ xs.map Entry.id) (hop : op b a = true) :
    pairView a b (reference op xs new) = [a,b] := by
  induction xs with
  | nil => simp at ha
  | cons old tail ih =>
    have ht : unique tail := (List.nodup_cons.mp hu).2
    have hnot : old.id ∉ tail.map Entry.id := (List.nodup_cons.mp hu).1
    by_cases hob : old.id = b
    · have hat : a ∈ tail.map Entry.id := by simpa [hob, hab] using ha
      have hbt : b ∉ tail.map Entry.id := by simpa [hob] using hnot
      have hseen : tail.any (fun e => op new.id e.id) = true := by
        obtain ⟨e, he, hid⟩ := List.mem_map.mp hat
        exact List.any_eq_true.mpr ⟨e, he, by simpa [hn, hid] using hop⟩
      have he : old.id = new.id := hob.trans hn.symm
      simp only [reference, he, if_true, hseen]
      rw [pairView_append, pairView_single a b tail ht hat hbt]
      simp [pairView, hn]
    · by_cases hoa : old.id = a
      · have hat : a ∉ tail.map Entry.id := by simpa [hoa] using hnot
        have hat' : a ∉ (reference op tail new).map Entry.id := by
          intro hm
          rcases (reference_membership op tail new a).mp hm with hm | hm
          · exact hab (hm.trans hn)
          · exact hat hm
        have hbt' : b ∈ (reference op tail new).map Entry.id :=
          (reference_membership op tail new b).mpr (Or.inl hn.symm)
        have hp := pairView_single b a (reference op tail new) (reference_unique op tail new ht) hbt' hat'
        have hp' : pairView a b (reference op tail new) = [b] := by rw [pairView_symm]; exact hp
        simp only [reference, hn, if_neg hob]
        simp [pairView_cons, hoa, hp']
      · have hat : a ∈ tail.map Entry.id := by simpa [Ne.symm hoa] using ha
        simp only [reference, hn, if_neg hob]
        simp [pairView_cons, hoa, hob, ih ht hat]

theorem pairView_untouched_sequence (op : ι → ι → Bool) (a b : ι)
    (xs actions : List E) (ha : absent a actions) (hb : absent b actions) :
    pairView a b (directRun op xs actions) = pairView a b xs := by
  induction actions generalizing xs with
  | nil => rfl
  | cons new rest ih =>
    have hna := ha new (by simp)
    have hnb := hb new (by simp)
    have hta : absent a rest := by intro e he; exact ha e (by simp [he])
    have htb : absent b rest := by intro e he; exact hb e (by simp [he])
    change pairView a b (directRun op (reference op xs new) rest) = _
    rw [ih _ hta htb, pairView_other_setter op a b xs new hna hnb]

theorem sequence_membership (op : ι → ι → Bool) (xs actions : List E) (id : ι) :
    id ∈ (directRun op xs actions).map Entry.id ↔ id ∈ xs.map Entry.id ∨ id ∈ actions.map Entry.id := by
  induction actions generalizing xs with
  | nil => simp [directRun]
  | cons new rest ih =>
    change id ∈ (directRun op (reference op xs new) rest).map Entry.id ↔ _
    rw [ih, reference_membership]
    simp [or_assoc, or_left_comm]

theorem pair_last_action_convergence (op : ι → ι → Bool) (a b : ι)
    (xs before after : List E) (last : E)
    (hu : unique xs) (hab : a ≠ b) (hl : last.id = b)
    (ha : a ∈ before.map Entry.id) (haa : absent a after) (hba : absent b after)
    (hop : op b a = true) :
    pairView a b (directRun op xs (before ++ last :: after)) = [a,b] := by
  change pairView a b ((before ++ last :: after).foldl (reference op) xs) = _
  rw [List.foldl_append, List.foldl_cons]
  change pairView a b (directRun op (reference op (directRun op xs before) last) after) = _
  rw [pairView_untouched_sequence op a b _ after haa hba]
  apply pairView_target_last op a b _ last
  · exact sequence_unique op xs before hu
  · exact hab
  · exact hl
  · exact (sequence_membership op xs before a).mpr (Or.inr ha)
  · exact hop


theorem unique_parts (pre post : List E) (hu : unique (pre ++ post)) :
    unique pre ∧ unique post ∧ ∀ id, id ∈ pre.map Entry.id → id ∉ post.map Entry.id := by
  have h : (pre.map Entry.id ++ post.map Entry.id).Nodup := by simpa [unique] using hu
  rcases List.nodup_append.mp h with ⟨hp, hs, hd⟩
  refine ⟨hp, hs, ?_⟩
  intro id hi hj
  exact hd id hi id hj rfl

theorem pairView_none (a b : ι) (xs : List E) (ha : absent a xs) (hb : absent b xs) :
    pairView a b xs = [] := by
  apply List.filter_eq_nil_iff.mpr
  intro id hm
  obtain ⟨e, he, rfl⟩ := List.mem_map.mp hm
  simp [ha e he, hb e he]

theorem pair_expansion_convergence (op : ι → ι → Bool) (a b : ι)
    (xs actions : List E) (hu : unique xs) (he : unique actions) (hab : a ≠ b)
    (ha : a ∈ actions.map Entry.id) (hb : b ∈ actions.map Entry.id)
    (hopab : op a b = true) (hopba : op b a = true) :
    pairView a b (directRun op xs actions) = pairView a b actions := by
  obtain ⟨eb, heb, hidb⟩ := List.mem_map.mp hb
  rcases unique_split actions eb he with hn | ⟨pre, old, post, hs, hid, hp, ht⟩
  · exact False.elim (hn eb heb rfl)
  · have hbid : old.id = b := hid.trans hidb
    have hpre : absent b pre := by simpa [hidb] using hp
    have hpost : absent b post := by simpa [hidb] using ht
    subst actions
    have parts := unique_parts pre (old :: post) he
    have hup := parts.1
    have hus : unique post := (List.nodup_cons.mp parts.2.1).2
    have hap : a ∈ pre.map Entry.id ∨ a ∈ post.map Entry.id := by
      simpa [hbid, hab] using ha
    rcases hap with hap | has
    · have hpa : absent a post := by
        intro e hem hie
        exact parts.2.2 a hap (by simp [List.mem_map.mpr ⟨e,hem,hie⟩])
      rw [pair_last_action_convergence op a b xs pre post old hu hab hbid hap hpa hpost hopba]
      rw [pairView_append, pairView_cons]
      have hnb : b ∉ pre.map Entry.id := by
        intro hm; obtain ⟨e,hm,hi⟩ := List.mem_map.mp hm; exact hpre e hm hi
      rw [pairView_single a b pre hup hap hnb, pairView_none a b post hpa hpost]
      simp [hbid]
    · obtain ⟨ea, hea, hida⟩ := List.mem_map.mp has
      rcases unique_split post ea hus with hn | ⟨mid, last, after, heq, hlast, hm, hf⟩
      · exact False.elim (hn ea hea rfl)
      · have hlast' : last.id = a := hlast.trans hida
        have hfa : absent a after := by simpa [hida] using hf
        have hfb : absent b after := by
          intro e hem; exact hpost e (by simp [heq, hem])
        have hbm : b ∈ (pre ++ old :: mid).map Entry.id := by simp [hbid]
        have hbefore := unique_parts (pre ++ old :: mid) (last :: after)
          (by simpa [heq, List.append_assoc] using he)
        have hna : a ∉ (pre ++ old :: mid).map Entry.id := by
          intro hi; exact hbefore.2.2 a hi (by simp [hlast'])
        have run := pair_last_action_convergence op b a xs (pre ++ old :: mid) after last
          hu (Ne.symm hab) hlast' hbm hfb hfa hopab
        rw [pairView_symm] at run
        have seqeq : pre ++ old :: post = (pre ++ old :: mid) ++ last :: after := by simp [heq, List.append_assoc]
        rw [seqeq, run]
        rw [pairView_append, pairView_cons]
        have view := pairView_single b a (pre ++ old :: mid) hbefore.1 hbm hna
        rw [pairView_symm] at view
        rw [view, pairView_none a b after hfa hfb]
        simp [hlast']

theorem guarded_pair_expansion_convergence (op : ι → ι → Bool) (a b : ι)
    (xs actions : List E) (hu : unique xs) (he : unique actions) (hab : a ≠ b)
    (ha : a ∈ actions.map Entry.id) (hb : b ∈ actions.map Entry.id)
    (hopab : op a b = true) (hopba : op b a = true) :
    pairView a b (guardedRun op xs actions) = pairView a b actions := by
  rw [guarded_sequence_refinement op xs actions hu]
  exact pair_expansion_convergence op a b xs actions hu he hab ha hb hopab hopba


def decode (raw : Storage ι ν) : List E :=
  List.zipWith (fun p i => ⟨p.1,p.2,i⟩) raw.declarations raw.importance

theorem decode_representation (raw : Storage ι ν) (xs : List E) (hr : Represents raw xs) :
    decode raw = xs := by
  simp only [decode, hr.1, hr.2.1]
  induction xs with
  | nil => rfl
  | cons e xs ih => cases e; simp_all [payload]

def rawNativeStep (op : ι → ι → Bool) (raw : Storage ι ν) (new : E) : Storage ι ν :=
  rawStep raw new (planner op (decode raw) new)

def rawNativeRun (op : ι → ι → Bool) (raw : Storage ι ν) (actions : List E) : Storage ι ν :=
  actions.foldl (rawNativeStep op) raw

theorem arbitrary_raw_sequence (op : ι → ι → Bool) (raw : Storage ι ν)
    (xs actions : List E) (hu : unique xs) (hr : Represents raw xs) :
    Represents (rawNativeRun op raw actions) (directRun op xs actions) := by
  induction actions generalizing raw xs with
  | nil => exact hr
  | cons new rest ih =>
    have hs : Represents (rawNativeStep op raw new) (reference op xs new) := by
      unfold rawNativeStep
      rw [decode_representation raw xs hr]
      exact concrete_storage_refinement op raw xs new hu hr
    exact ih _ _ (reference_unique op xs new hu) hs

theorem arbitrary_raw_prefix (op : ι → ι → Bool) (raw : Storage ι ν)
    (xs actions : List E) (hu : unique xs) (hr : Represents raw xs) (n : Nat) :
    Represents (rawNativeRun op raw (actions.take n)) (directRun op xs (actions.take n)) :=
  arbitrary_raw_sequence op raw xs (actions.take n) hu hr

def rawGuardedRun (op : ι → ι → Bool) (raw : Storage ι ν) (actions : List E) : Storage ι ν :=
  if gate op (decode raw) actions then rawNativeRun op raw actions else raw

theorem guarded_raw_refinement (op : ι → ι → Bool) (raw : Storage ι ν)
    (xs actions : List E) (hu : unique xs) (hr : Represents raw xs) :
    Represents (rawGuardedRun op raw actions) (directRun op xs actions) := by
  unfold rawGuardedRun
  rw [decode_representation raw xs hr]
  split
  · exact arbitrary_raw_sequence op raw xs actions hu hr
  · next h =>
    have hf : gate op xs actions = false := by simpa using h
    rw [← sequence_refinement op xs actions hu, false_gate_no_change op xs actions hf]
    exact hr

def demoOp (a b : Nat) : Bool := a != b && a < 2 && b < 2

def demoA : Entry Nat Nat := ⟨0,7,false⟩
def demoB : Entry Nat Nat := ⟨1,7,false⟩
def demoC : Entry Nat Nat := ⟨2,9,true⟩

theorem intermediate_change_restores_final_state :
    gate demoOp [demoA,demoB] [demoA,demoB] = true ∧
    actualChangingSteps demoOp [demoA,demoB] [demoA,demoB] = true ∧
    guardedRun demoOp [demoA,demoB] [demoA,demoB] = [demoA,demoB] := by decide

def legacySet (xs : List E) (new : E) : List E :=
  if xs.any (fun e => decide (e.id = new.id)) then
    xs.map (fun old => if old.id = new.id then new else old)
  else xs ++ [new]

def legacyGate (xs actions : List E) : Bool :=
  actions.any (fun new => !xs.any (fun old => decide (old = new)))

theorem legacy_update_witness :
    [demoB,demoA].foldl legacySet [demoA,demoB] = [demoA,demoB] ∧
    directRun demoOp [demoA,demoB] [demoB,demoA] = [demoB,demoA] := by decide

theorem legacy_gate_witness :
    legacyGate [demoA,demoB] [demoB,demoA] = false ∧
    gate demoOp [demoA,demoB] [demoB,demoA] = true := by decide

theorem missing_order_check_witness :
    nativeStep (fun _ _ => false) [demoA,demoB] demoA ≠
      reference demoOp [demoA,demoB] demoA := by decide

def demoRaw : Storage Nat Nat := ⟨[(0,7),(1,7)], [false,true], fun i => decide (i < 2)⟩

theorem priority_downgrade_witness :
    (rawStep demoRaw demoB (.replace 1)).importance = [false,false] ∧
    demoRaw.importance ≠ (rawStep demoRaw demoB (.replace 1)).importance := by decide

theorem missing_move_bit_removal_witness :
    demoRaw.importance ++ [demoA.important] ≠ (rawStep demoRaw demoA (.move 0)).importance := by decide

theorem missing_membership_insert_witness :
    demoRaw.present 2 = false ∧ (rawStep demoRaw demoC .append).present 2 = true := by decide

theorem nonvacuous_raw_admission :
    Represents demoRaw [demoA,⟨1,7,true⟩] ∧ unique [demoA,⟨1,7,true⟩] := by
  constructor
  · refine ⟨rfl,rfl,?_⟩
    intro id
    cases id with
    | zero => decide
    | succ id =>
      cases id with
      | zero => decide
      | succ id => simp [demoRaw, demoA, Nat.succ_lt_succ_iff]
  · simp [unique, demoA]

end AllOrder
