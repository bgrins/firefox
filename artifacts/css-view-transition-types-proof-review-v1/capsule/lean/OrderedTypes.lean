import Std
namespace OrderedTypes
variable {α : Type} [DecidableEq α]

def firsts (seen : List α) : List α → List α
  | [] => []
  | x :: xs => if x ∈ seen then firsts seen xs else x :: firsts (x :: seen) xs

def appendNew (xs : List α) (x : α) : List α :=
  if x ∈ xs then xs else xs ++ [x]

theorem mem_firsts (seen xs : List α) (a : α) :
    a ∈ firsts seen xs ↔ a ∈ xs ∧ a ∉ seen := by
  induction xs generalizing seen with
  | nil => simp [firsts]
  | cons x xs ih =>
    simp only [firsts]
    split <;> simp_all only [List.mem_cons, ih] <;> grind

theorem firsts_nodup (seen xs : List α) : (firsts seen xs).Nodup := by
  induction xs generalizing seen with
  | nil => simp [firsts]
  | cons x xs ih =>
    simp only [firsts]
    split
    · exact ih seen
    · simp [List.nodup_cons, mem_firsts, ih]

theorem firsts_sublist (seen xs : List α) : List.Sublist (firsts seen xs) xs := by
  induction xs generalizing seen with
  | nil => exact List.Sublist.refl []
  | cons x xs ih =>
    simp only [firsts]
    split
    · exact (ih seen).cons x
    · exact (ih (x :: seen)).cons_cons x

theorem firsts_seen_congr (s t xs : List α)
    (same : ∀ a, a ∈ s ↔ a ∈ t) : firsts s xs = firsts t xs := by
  induction xs generalizing s t with
  | nil => rfl
  | cons x xs ih =>
    simp only [firsts]
    by_cases h : x ∈ s
    · simp [h, (same x).mp h, ih s t same]
    · have ht : x ∉ t := fun v => h ((same x).mpr v)
      simp only [h, ht, ↓reduceIte]
      congr 1
      apply ih
      intro a
      simp only [List.mem_cons]
      rw [same a]

theorem firsts_unique (xs : List α) (h : xs.Nodup) : firsts [] xs = xs := by
  suffices ∀ s, (∀ a, a ∈ xs → a ∉ s) → firsts s xs = xs from
    this [] (by simp)
  induction xs with
  | nil => simp [firsts]
  | cons x xs ih =>
    intro s hd
    have hn := List.nodup_cons.mp h
    have hx : x ∉ s := hd x (by simp)
    simp only [firsts, hx, ↓reduceIte]
    congr 1
    exact ih hn.2 (x :: s) (by intro a ha; simp only [List.mem_cons]; grind)

theorem mem_appendNew (xs : List α) (x a : α) :
    a ∈ appendNew xs x ↔ a ∈ xs ∨ a = x := by
  unfold appendNew
  split <;> simp_all <;> grind

theorem nodup_appendNew (xs : List α) (x : α) (h : xs.Nodup) :
    (appendNew xs x).Nodup := by
  unfold appendNew
  split
  · exact h
  · simp_all [List.nodup_append] <;> grind

theorem erase_matches_filter (xs : List α) (x : α) (h : xs.Nodup) :
    xs.erase x = xs.filter (fun a => decide (a ≠ x)) := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    have hn := List.nodup_cons.mp h
    by_cases eq : a = x
    · subst a
      simp only [List.erase_cons_head, List.filter_cons, ne_eq, not_true_eq_false,
        decide_false, Bool.false_eq_true, ↓reduceIte]
      symm
      apply List.filter_eq_self.mpr
      intro b hb
      simp only [decide_eq_true_eq]
      grind
    · simp [List.erase_cons_tail, eq, ih hn.2]

theorem erase_nodup (xs : List α) (x : α) (h : xs.Nodup) :
    (xs.erase x).Nodup := by
  rw [erase_matches_filter xs x h]
  exact h.filter _

theorem deletion_membership (xs : List α) (x a : α) (h : xs.Nodup) :
    a ∈ xs.erase x ↔ a ∈ xs ∧ a ≠ x := by
  rw [erase_matches_filter xs x h]
  simp [and_comm]

structure Initial (α : Type) where
  seen : List α
  native : List α
  deriving Repr, DecidableEq

def initialStep (s : Initial α) (x : α) : Initial α :=
  if x ∈ s.seen then s else ⟨x :: s.seen, s.native ++ [x]⟩

def initialRun (s : Initial α) : List α → Initial α
  | [] => s
  | x :: xs => initialRun (initialStep s x) xs

def InitInvariant (s : Initial α) : Prop :=
  s.native.Nodup ∧ ∀ a, a ∈ s.seen ↔ a ∈ s.native

theorem initial_empty : InitInvariant (⟨[], []⟩ : Initial α) := by
  simp [InitInvariant]

theorem initial_step_preserves (s : Initial α) (x : α) (h : InitInvariant s) :
    InitInvariant (initialStep s x) := by
  unfold initialStep
  split
  · exact h
  · rcases h with ⟨hn, hm⟩
    simp only [InitInvariant]
    constructor
    · simp_all [List.nodup_append] <;> grind
    · intro a; simp only [List.mem_cons, List.mem_append, List.not_mem_nil, or_false]
      rw [hm a]; exact or_comm

theorem initial_run_preserves (s : Initial α) (xs : List α) (h : InitInvariant s) :
    InitInvariant (initialRun s xs) := by
  induction xs generalizing s with
  | nil => exact h
  | cons x xs ih => exact ih _ (initial_step_preserves s x h)

theorem initial_run_reference (s : Initial α) (xs : List α) :
    (initialRun s xs).native = s.native ++ firsts s.seen xs := by
  induction xs generalizing s with
  | nil => simp [initialRun, firsts]
  | cons x xs ih =>
    simp only [initialRun, ih, initialStep, firsts]
    split <;> simp_all [List.append_assoc]

theorem initial_prefix (pre : List α) :
    (initialRun ⟨[], []⟩ pre).native = firsts [] pre ∧
    InitInvariant (initialRun ⟨[], []⟩ pre) := by
  constructor
  · simpa using initial_run_reference (⟨[], []⟩ : Initial α) pre
  · exact initial_run_preserves _ _ initial_empty

theorem initial_membership (xs : List α) (a : α) :
    a ∈ (initialRun ⟨[], []⟩ xs).native ↔ a ∈ xs := by
  rw [(initial_prefix xs).1]
  simp [mem_firsts]

theorem initial_order (xs : List α) :
    List.Sublist (initialRun ⟨[], []⟩ xs).native xs := by
  rw [(initial_prefix xs).1]
  exact firsts_sublist [] xs

theorem initial_idempotent (xs : List α) :
    firsts [] (firsts [] xs) = firsts [] xs :=
  firsts_unique _ (firsts_nodup [] xs)

theorem weak_keys_owned_at_boundary (s : Initial α) (h : InitInvariant s) :
    ∀ a, a ∈ s.seen → a ∈ s.native := fun a => (h.2 a).mp

theorem weak_keys_owned_during_insert (s : Initial α) (x : α)
    (h : InitInvariant s) : ∀ a, a ∈ x :: s.seen → a = x ∨ a ∈ s.native := by
  intro a ha
  simp only [List.mem_cons] at ha
  exact ha.elim Or.inl (fun z => Or.inr ((h.2 a).mp z))

end OrderedTypes
