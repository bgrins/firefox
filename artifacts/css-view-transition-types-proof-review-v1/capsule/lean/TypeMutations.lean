import OrderedTypes
namespace TypeMutations
open OrderedTypes
variable {α : Type} [DecidableEq α]

structure State (α : Type) where
  native : List α
  backing : Option (List α)
  transition : Nat
  document : Nat
  deriving Repr, DecidableEq

def Good (s : State α) : Prop :=
  s.native.Nodup ∧ ∀ p, s.backing = some p → p = s.native

def materialize (s : State α) : State α :=
  match s.backing with
  | none => {s with backing := some (firsts [] s.native)}
  | some _ => s

def observed (s : State α) : List α := (materialize s).backing.getD []

def publish (s : State α) (n p : List α) : State α :=
  {s with native := n, backing := some p}

inductive Op (α : Type) where
  | add (value : α)
  | delete (value : α)
  | clear
  | observe
  deriving Repr, DecidableEq

inductive Reply where
  | self (identity : Nat)
  | deleted (present : Bool)
  | undefined
  | observed
  deriving Repr, DecidableEq

def reference (identity : Nat) (xs : List α) : Op α → List α × Reply
  | .add x => (appendNew xs x, .self identity)
  | .delete x => (xs.filter (fun a => decide (a ≠ x)), .deleted (decide (x ∈ xs)))
  | .clear => ([], .undefined)
  | .observe => (xs, .observed)

def operation (s : State α) (op : Op α) : State α × Reply :=
  let t := materialize s
  let p := t.backing.getD []
  match op with
  | .add x => if x ∈ p then (t, .self t.transition)
      else (publish t (t.native ++ [x]) (p ++ [x]), .self t.transition)
  | .delete x => if x ∈ p then
      (publish t (t.native.erase x) (p.filter (fun a => decide (a ≠ x))), .deleted true)
      else (t, .deleted false)
  | .clear => (publish t [] [], .undefined)
  | .observe => (t, .observed)

theorem materialize_native (s : State α) : (materialize s).native = s.native := by
  unfold materialize; split <;> rfl

theorem materialize_frame (s : State α) :
    (materialize s).transition = s.transition ∧
    (materialize s).document = s.document := by
  unfold materialize; split <;> exact ⟨rfl, rfl⟩

theorem materialize_good (s : State α) (h : Good s) : Good (materialize s) := by
  unfold materialize; split
  · simp only [Good]
    constructor
    · exact h.1
    · intro p hp
      have : firsts [] s.native = p := Option.some.inj hp
      rw [← this, firsts_unique _ h.1]
  · exact h

theorem materialize_backing (s : State α) (h : Good s) :
    (materialize s).backing = some s.native := by
  unfold materialize; split
  · simp [firsts_unique _ h.1]
  · rename_i p hp
    rw [hp, h.2 p hp]

theorem materialize_idempotent (s : State α) :
    materialize (materialize s) = materialize s := by
  cases hb : s.backing <;> simp [materialize, hb]

theorem public_native (s : State α) (h : Good s) : observed s = s.native := by
  simp [observed, materialize_backing s h]

theorem operation_frame (s : State α) (op : Op α) :
    (operation s op).1.transition = s.transition ∧
    (operation s op).1.document = s.document := by
  have hf := materialize_frame s
  cases op <;> simp only [operation] <;> (try split) <;> simp_all [publish]

theorem reference_nodup (id : Nat) (xs : List α) (op : Op α) (h : xs.Nodup) :
    (reference id xs op).1.Nodup := by
  cases op with
  | add x => exact nodup_appendNew xs x h
  | delete x => exact h.filter _
  | clear => simp [reference]
  | observe => exact h

theorem operation_refines (s : State α) (op : Op α) (h : Good s) :
    (operation s op).1.native = (reference s.transition s.native op).1 ∧
    (operation s op).1.backing = some (reference s.transition s.native op).1 ∧
    (operation s op).2 = (reference s.transition s.native op).2 := by
  have hb := materialize_backing s h
  have hn := materialize_native s
  have hf := (materialize_frame s).1
  cases op with
  | add x =>
    simp only [operation, hb, Option.getD_some, hn, reference, hf, appendNew]
    split <;> simp_all [publish]
  | delete x =>
    simp only [operation, hb, Option.getD_some, hn, reference]
    split
    · simp_all [publish, erase_matches_filter _ _ h.1]
    · have he : s.native.filter (fun a => decide (a ≠ x)) = s.native := by
        apply List.filter_eq_self.mpr
        intro a ha; simp only [decide_eq_true_eq]; grind
      rw [he]
      simp [hn, hb, ‹x ∉ s.native›]
  | clear => simp [operation, publish, reference]
  | observe => simp_all [operation, reference]

theorem operation_good (s : State α) (op : Op α) (h : Good s) :
    Good (operation s op).1 := by
  obtain ⟨hn, hb, _⟩ := operation_refines s op h
  constructor
  · rw [hn]; exact reference_nodup _ _ _ h.1
  · intro p hp
    rw [hb] at hp
    exact (Option.some.inj hp).symm.trans hn.symm

def history (s : State α) : List (Op α) → State α × List Reply
  | [] => (s, [])
  | op :: ops =>
      let one := operation s op
      let rest := history one.1 ops
      (rest.1, one.2 :: rest.2)

def referenceHistory (id : Nat) (xs : List α) : List (Op α) → List α × List Reply
  | [] => (xs, [])
  | op :: ops =>
      let one := reference id xs op
      let rest := referenceHistory id one.1 ops
      (rest.1, one.2 :: rest.2)

theorem history_good (s : State α) (ops : List (Op α)) (h : Good s) :
    Good (history s ops).1 := by
  induction ops generalizing s with
  | nil => exact h
  | cons op ops ih => exact ih _ (operation_good s op h)

theorem history_frame (s : State α) (ops : List (Op α)) :
    (history s ops).1.transition = s.transition ∧
    (history s ops).1.document = s.document := by
  induction ops generalizing s with
  | nil => exact ⟨rfl, rfl⟩
  | cons op ops ih =>
    exact ⟨(ih _).1.trans (operation_frame s op).1,
      (ih _).2.trans (operation_frame s op).2⟩

theorem history_refines (s : State α) (ops : List (Op α)) (h : Good s) :
    (history s ops).1.native = (referenceHistory s.transition s.native ops).1 ∧
    (history s ops).2 = (referenceHistory s.transition s.native ops).2 := by
  induction ops generalizing s with
  | nil => exact ⟨rfl, rfl⟩
  | cons op ops ih =>
    have hr := operation_refines s op h
    have hi := ih (operation s op).1 (operation_good s op h)
    have hf := (operation_frame s op).1
    simp only [history, referenceHistory]
    rw [hf, hr.1] at hi
    constructor
    · exact hi.1
    · rw [hr.2.2, hi.2]

def start (input : List α) (transition document : Nat) : State α :=
  ⟨(initialRun ⟨[], []⟩ input).native, none, transition, document⟩

theorem start_good (input : List α) (transition document : Nat) :
    Good (start input transition document) := by
  constructor
  · exact (initial_prefix input).2.1
  · simp [start]

theorem arbitrary_successful_observations (input : List α) (ops : List (Op α))
    (transition document : Nat) :
    observed (history (start input transition document) ops).1 =
      (referenceHistory transition (firsts [] input) ops).1 ∧
    (history (start input transition document) ops).2 =
      (referenceHistory transition (firsts [] input) ops).2 := by
  rw [public_native _ (history_good _ _ (start_good input transition document))]
  have h := history_refines (start input transition document) ops
    (start_good input transition document)
  simpa only [start, (initial_prefix input).1] using h

end TypeMutations
