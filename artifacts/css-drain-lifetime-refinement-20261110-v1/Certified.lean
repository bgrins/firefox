import Std

namespace CertifiedPath

structure Tree where
  size : Nat
  parent : Nat → Nat
  lower : ∀ n, parent (n + 1) < n + 1

def path (t : Tree) : Nat → List Nat
  | 0 => [0]
  | n + 1 => (n + 1) :: path t (t.parent (n + 1))
termination_by n => n
decreasing_by exact t.lower n

def Closed (t : Tree) (cert : List Nat) : Prop :=
  ∀ n ∈ cert, n = 0 ∨ t.parent n ∈ cert

structure Visit where
  cert : List Nat
  fresh : Nat
  hits : Nat
  queries : Nat
  scans : Nat

def walk (t : Tree) (n : Nat) (cert : List Nat) : Visit :=
  if n ∈ cert then ⟨cert, 0, 1, 0, 1⟩ else
  match n with
  | 0 => ⟨0 :: cert, 1, 1, 0, 1⟩
  | k + 1 =>
    let r := walk t (t.parent (k + 1)) cert
    ⟨(k + 1) :: r.cert, r.fresh + 1, r.hits, r.queries + 1, r.scans + 1⟩
termination_by n
decreasing_by exact t.lower k

theorem path_zero (t : Tree) : path t 0 = [0] := by simp [path]

theorem path_start (t : Tree) (n : Nat) : n ∈ path t n := by
  cases n <;> simp [path]

theorem walk_hit (t : Tree) (n : Nat) (cert : List Nat) (h : n ∈ cert) :
    walk t n cert = ⟨cert, 0, 1, 0, 1⟩ := by
  cases n <;> simp [walk, h]

theorem walk_contains (t : Tree) (n : Nat) (cert : List Nat) :
    n ∈ (walk t n cert).cert := by
  by_cases h : n ∈ cert
  · simpa only [walk_hit t n cert h] using h
  · cases n <;> simp [walk, h]

theorem walk_monotone (t : Tree) (n : Nat) (cert : List Nat) :
    ∀ x ∈ cert, x ∈ (walk t n cert).cert := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    intro x hx
    by_cases hn : n ∈ cert
    · simpa only [walk_hit t n cert hn] using hx
    · cases n with
      | zero => simp [walk, hn, hx]
      | succ k =>
        have hi := ih (t.parent (k + 1)) (t.lower k) cert x hx
        simpa [walk, hn] using Or.inr hi

theorem walk_upper (t : Tree) (n : Nat) (cert : List Nat) :
    ∀ x ∈ (walk t n cert).cert, x ∈ cert ∨ x ≤ n := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    intro x hx
    by_cases hn : n ∈ cert
    · exact Or.inl (by simpa only [walk_hit t n cert hn] using hx)
    · cases n with
      | zero =>
        simp only [walk, hn, ↓reduceIte, List.mem_cons] at hx
        rcases hx with rfl | hx
        · exact Or.inr (Nat.le_refl _)
        · exact Or.inl hx
      | succ k =>
        simp only [walk, hn, ↓reduceIte, List.mem_cons] at hx
        rcases hx with rfl | hx
        · exact Or.inr (Nat.le_refl _)
        · rcases ih (t.parent (k + 1)) (t.lower k) cert x hx with hc | hl
          · exact Or.inl hc
          · exact Or.inr (Nat.le_trans hl (Nat.le_of_lt (t.lower k)))

theorem walk_closed (t : Tree) (n : Nat) (cert : List Nat) (hc : Closed t cert) :
    Closed t (walk t n cert).cert := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    by_cases hn : n ∈ cert
    · simpa only [walk_hit t n cert hn] using hc
    · cases n with
      | zero =>
        intro x hx
        simp only [walk, hn, ↓reduceIte, List.mem_cons] at hx
        rcases hx with rfl | hx
        · exact Or.inl rfl
        · rcases hc x hx with hz | hp
          · exact Or.inl hz
          · exact Or.inr (by simp [walk, hn, hp])
      | succ k =>
        have hr := ih (t.parent (k + 1)) (t.lower k) cert hc
        intro x hx
        simp only [walk, hn, ↓reduceIte, List.mem_cons] at hx
        rcases hx with rfl | hx
        · exact Or.inr (by simpa [walk, hn] using Or.inr (walk_contains t (t.parent (k + 1)) cert))
        · rcases hr x hx with hz | hp
          · exact Or.inl hz
          · exact Or.inr (by simpa [walk, hn] using Or.inr hp)


theorem closed_path (t : Tree) (cert : List Nat) (hc : Closed t cert)
    (n : Nat) (hn : n ∈ cert) : ∀ x ∈ path t n, x ∈ cert := by
  induction n using Nat.strongRecOn with
  | ind n ih =>
    cases n with
    | zero => simpa [path] using hn
    | succ k =>
      have hp : t.parent (k + 1) ∈ cert := (hc (k + 1) hn).resolve_left (by omega)
      intro x hx
      simp only [path, List.mem_cons] at hx
      rcases hx with rfl | hx
      · exact hn
      · exact ih (t.parent (k + 1)) (t.lower k) hp x hx

theorem walk_coverage (t : Tree) (n : Nat) (cert : List Nat) (hc : Closed t cert) :
    ∀ x, x ∈ (walk t n cert).cert ↔ x ∈ cert ∨ x ∈ path t n := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    intro x
    by_cases hn : n ∈ cert
    · rw [walk_hit t n cert hn]
      constructor
      · exact Or.inl
      · intro h
        exact h.elim id (closed_path t cert hc n hn x)
    · cases n with
      | zero => simp [walk, hn, path, or_comm]
      | succ k =>
        have hr := ih (t.parent (k + 1)) (t.lower k) cert hc x
        simpa [walk, hn, path, or_assoc, or_comm, or_left_comm] using
          (or_congr (Iff.rfl : x = k + 1 ↔ x = k + 1) hr)

theorem walk_fresh_head (t : Tree) (k : Nat) (cert : List Nat) (hn : k + 1 ∉ cert) :
    k + 1 ∉ (walk t (t.parent (k + 1)) cert).cert := by
  intro h
  rcases walk_upper t (t.parent (k + 1)) cert (k + 1) h with old | lower
  · exact hn old
  · have := t.lower k
    omega

theorem walk_nodup (t : Tree) (n : Nat) (cert : List Nat) (hc : cert.Nodup) :
    (walk t n cert).cert.Nodup := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    by_cases hn : n ∈ cert
    · simpa only [walk_hit t n cert hn] using hc
    · cases n with
      | zero => simpa [walk, hn] using (List.nodup_cons.mpr ⟨hn, hc⟩)
      | succ k =>
        have hr := ih (t.parent (k + 1)) (t.lower k) cert hc
        simpa [walk, hn] using (List.nodup_cons.mpr ⟨walk_fresh_head t k cert hn, hr⟩)

theorem walk_growth (t : Tree) (n : Nat) (cert : List Nat) :
    (walk t n cert).cert.length = cert.length + (walk t n cert).fresh := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    by_cases hn : n ∈ cert
    · simp only [walk_hit t n cert hn, Nat.add_zero]
    · cases n with
      | zero => simp [walk, hn]
      | succ k =>
        have hr := ih (t.parent (k + 1)) (t.lower k) cert
        simp only [walk, hn, ↓reduceIte, List.length_cons]
        omega

theorem walk_one_hit (t : Tree) (n : Nat) (cert : List Nat) :
    (walk t n cert).hits = 1 := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    by_cases hn : n ∈ cert
    · simp only [walk_hit t n cert hn]
    · cases n with
      | zero => simp [walk, hn]
      | succ k => simpa [walk, hn] using ih (t.parent (k + 1)) (t.lower k) cert

theorem walk_parent_queries (t : Tree) (n : Nat) (cert : List Nat) :
    (walk t n cert).queries ≤ (walk t n cert).fresh := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    by_cases hn : n ∈ cert
    · simp only [walk_hit t n cert hn, Nat.le_refl]
    · cases n with
      | zero => simp [walk, hn]
      | succ k =>
        have hr := ih (t.parent (k + 1)) (t.lower k) cert
        simpa [walk, hn] using Nat.add_le_add_right hr 1

inductive MarkHistory (t : Tree) : List Nat → List Nat → Prop
  | same (cert) : MarkHistory t cert cert
  | mark {before after n} : MarkHistory t before after → n ∉ after →
      (n = 0 ∨ t.parent n ∈ after) → MarkHistory t before (n :: after)

theorem walk_mark_history (t : Tree) (n : Nat) (cert : List Nat) :
    MarkHistory t cert (walk t n cert).cert := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    by_cases hn : n ∈ cert
    · rw [walk_hit t n cert hn]
      exact .same cert
    · cases n with
      | zero => simpa [walk, hn] using MarkHistory.mark (.same cert) hn (Or.inl rfl)
      | succ k =>
        have hr := ih (t.parent (k + 1)) (t.lower k) cert
        simpa [walk, hn] using MarkHistory.mark hr (walk_fresh_head t k cert hn)
          (Or.inr (walk_contains t (t.parent (k + 1)) cert))

theorem closed_insert (t : Tree) (cert : List Nat) (n : Nat)
    (hc : Closed t cert) (hp : n = 0 ∨ t.parent n ∈ cert) : Closed t (n :: cert) := by
  intro x hx
  rcases List.mem_cons.mp hx with rfl | hx
  · exact hp.imp_right (List.mem_cons_of_mem x)
  · exact (hc x hx).imp_right (List.mem_cons_of_mem n)

theorem mark_history_closed (t : Tree) {before after : List Nat}
    (h : MarkHistory t before after) (hc : Closed t before) : Closed t after := by
  induction h with
  | same => exact hc
  | mark h _ hp ih => exact closed_insert t _ _ ih hp

theorem walk_scans (t : Tree) (n : Nat) (cert : List Nat) :
    (walk t n cert).scans ≤ (walk t n cert).fresh + 1 := by
  induction n using Nat.strongRecOn generalizing cert with
  | ind n ih =>
    by_cases hn : n ∈ cert
    · simp [walk_hit t n cert hn]
    · cases n with
      | zero => simp [walk, hn]
      | succ k =>
        have hr := ih (t.parent (k + 1)) (t.lower k) cert
        simp only [walk, hn, ↓reduceIte]
        omega

structure Drain where
  cert : List Nat
  hinted : List Nat
  fresh : Nat
  hits : Nat
  queries : Nat
  scans : Nat

def drain (t : Tree) : List Nat → List Nat → Drain
  | [], cert => ⟨cert, [], 0, 0, 0, 0⟩
  | child :: tasks, cert =>
    let v := walk t (t.parent child) cert
    let r := drain t tasks v.cert
    ⟨r.cert, child :: r.hinted, v.fresh + r.fresh, v.hits + r.hits,
      1 + v.queries + r.queries, v.scans + r.scans⟩

def naive (t : Tree) (tasks : List Nat) : List Nat :=
  tasks.flatMap (fun child => path t (t.parent child))

theorem every_child_hinted (t : Tree) (tasks cert : List Nat) :
    (drain t tasks cert).hinted = tasks := by
  induction tasks generalizing cert with
  | nil => rfl
  | cons child tasks ih => simp [drain, ih]

theorem drain_closed (t : Tree) (tasks cert : List Nat) (hc : Closed t cert) :
    Closed t (drain t tasks cert).cert := by
  induction tasks generalizing cert with
  | nil => exact hc
  | cons child tasks ih => exact ih _ (walk_closed t _ _ hc)

theorem drain_nodup (t : Tree) (tasks cert : List Nat) (hc : cert.Nodup) :
    (drain t tasks cert).cert.Nodup := by
  induction tasks generalizing cert with
  | nil => exact hc
  | cons child tasks ih => exact ih _ (walk_nodup t _ _ hc)

theorem drain_coverage (t : Tree) (tasks cert : List Nat) (hc : Closed t cert) (x : Nat) :
    x ∈ (drain t tasks cert).cert ↔ x ∈ cert ∨ x ∈ naive t tasks := by
  induction tasks generalizing cert with
  | nil => simp [drain, naive]
  | cons child tasks ih =>
    have hr := ih (walk t (t.parent child) cert).cert (walk_closed t _ _ hc)
    simpa only [drain, walk_coverage t _ _ hc, naive, List.flatMap_cons,
      List.mem_append, or_assoc] using hr

theorem empty_closed (t : Tree) : Closed t [] := by simp [Closed]

theorem coverage_equivalent (t : Tree) (tasks : List Nat) (x : Nat) :
    x ∈ (drain t tasks []).cert ↔ x ∈ naive t tasks := by
  simpa using drain_coverage t tasks [] (empty_closed t) x

theorem drain_growth (t : Tree) (tasks cert : List Nat) :
    (drain t tasks cert).cert.length = cert.length + (drain t tasks cert).fresh := by
  induction tasks generalizing cert with
  | nil => simp [drain]
  | cons child tasks ih =>
    have hr := ih (walk t (t.parent child) cert).cert
    have hw := walk_growth t (t.parent child) cert
    simp only [drain]
    omega

theorem drain_hits (t : Tree) (tasks cert : List Nat) :
    (drain t tasks cert).hits = tasks.length := by
  induction tasks generalizing cert with
  | nil => rfl
  | cons child tasks ih => simp [drain, walk_one_hit, ih, Nat.add_comm]

theorem drain_queries (t : Tree) (tasks cert : List Nat) :
    (drain t tasks cert).queries ≤ (drain t tasks cert).fresh + tasks.length := by
  induction tasks generalizing cert with
  | nil => simp [drain]
  | cons child tasks ih =>
    have hr := ih (walk t (t.parent child) cert).cert
    have hw := walk_parent_queries t (t.parent child) cert
    simp only [drain, List.length_cons]
    omega

theorem drain_scans (t : Tree) (tasks cert : List Nat) :
    (drain t tasks cert).scans ≤ (drain t tasks cert).fresh + tasks.length := by
  induction tasks generalizing cert with
  | nil => simp [drain]
  | cons child tasks ih =>
    have hr := ih (walk t (t.parent child) cert).cert
    have hw := walk_scans t (t.parent child) cert
    simp only [drain, List.length_cons]
    omega

theorem unique_work_bound (t : Tree) (tasks : List Nat) :
    (drain t tasks []).cert.Nodup ∧
    (drain t tasks []).queries ≤ (drain t tasks []).cert.length + tasks.length ∧
    (drain t tasks []).scans ≤ (drain t tasks []).cert.length + tasks.length := by
  have hg := drain_growth t tasks []
  have hq := drain_queries t tasks []
  have hs := drain_scans t tasks []
  simp only [List.length_nil, Nat.zero_add] at hg
  exact ⟨drain_nodup t tasks [] (by simp), by omega, by omega⟩

def dirtyAfter (t : Tree) (tasks : List Nat) (initial : Nat → Prop) (n : Nat) : Prop :=
  initial n ∨ n ∈ (drain t tasks []).cert

theorem dirty_equivalent (t : Tree) (tasks : List Nat) (initial : Nat → Prop) (n : Nat) :
    dirtyAfter t tasks initial n ↔ initial n ∨ n ∈ naive t tasks := by
  simp only [dirtyAfter, coverage_equivalent]

theorem history_trans (t : Tree) {a b c : List Nat}
    (hab : MarkHistory t a b) (hbc : MarkHistory t b c) : MarkHistory t a c := by
  induction hbc with
  | same => exact hab
  | mark _ hn hp ih => exact .mark ih hn hp

theorem drain_mark_history (t : Tree) (tasks cert : List Nat) :
    MarkHistory t cert (drain t tasks cert).cert := by
  induction tasks generalizing cert with
  | nil => exact .same cert
  | cons child tasks ih =>
    exact history_trans t (walk_mark_history t _ _) (ih _)

theorem path_upper (t : Tree) (n : Nat) : ∀ x ∈ path t n, x ≤ n := by
  induction n using Nat.strongRecOn with
  | ind n ih =>
    cases n with
    | zero => simp [path]
    | succ k =>
      intro x hx
      simp only [path, List.mem_cons] at hx
      rcases hx with rfl | hx
      · exact Nat.le_refl _
      · exact Nat.le_trans (ih _ (t.lower k) x hx) (Nat.le_of_lt (t.lower k))

theorem root_in_path (t : Tree) (n : Nat) : 0 ∈ path t n := by
  induction n using Nat.strongRecOn with
  | ind n ih =>
    cases n with
    | zero => simp [path]
    | succ k => simp [path, ih _ (t.lower k)]

def Eligible (t : Tree) (tasks : List Nat) : Prop :=
  ∀ child ∈ tasks, 0 < child ∧ child ≤ t.size

theorem finite_subtree (t : Tree) (tasks : List Nat) (he : Eligible t tasks)
    (x : Nat) (hx : x ∈ (drain t tasks []).cert) : x ≤ t.size := by
  rw [coverage_equivalent] at hx
  obtain ⟨child, hc, hp⟩ := List.mem_flatMap.mp hx
  have hd := he child hc
  cases child with
  | zero => omega
  | succ k =>
    have hu := path_upper t (t.parent (k + 1)) x hp
    have hl := t.lower k
    omega

theorem first_task_marks_root (t : Tree) (child : Nat) (tasks : List Nat) :
    0 ∈ (drain t (child :: tasks) []).cert := by
  rw [coverage_equivalent]
  simp [naive, root_in_path]

theorem empty_tasks_quiet (t : Tree) :
    (drain t [] []).cert = [] ∧ (drain t [] []).hinted = [] ∧
    (drain t [] []).queries = 0 := by simp [drain]

def chain : Tree := ⟨8, fun n => n - 1, by intro n; omega⟩

def forkParent : Nat → Nat
  | 0 => 0
  | 1 => 0
  | 2 => 0
  | 3 => 1
  | 4 => 1
  | 5 => 2
  | k + 6 => k + 5

def forkTree : Tree := ⟨8, forkParent, by
  intro n
  cases n with
  | zero => decide
  | succ n => cases n with
    | zero => decide
    | succ n => cases n with
      | zero => decide
      | succ n => cases n with
        | zero => decide
        | succ n => cases n with
          | zero => decide
          | succ n => simp [forkParent]⟩

theorem duplicate_task_example :
    (drain forkTree [3, 4, 5, 3] []).cert = [2, 1, 0] ∧
    (drain forkTree [3, 4, 5, 3] []).hinted = [3, 4, 5, 3] ∧
    (drain forkTree [3, 4, 5, 3] []).queries = 6 ∧
    (drain forkTree [3, 4, 5, 3] []).scans = 6 := by decide +kernel

theorem dirty_bits_do_not_cut_path :
    dirtyAfter chain [3] (fun n => n = 2) 0 := by
  exact Or.inr (by decide +kernel)

theorem cache_is_not_dirty_state :
    (drain chain [3] []).fresh = 3 ∧
    (drain chain [3] [2]).fresh = 0 ∧ ¬ Closed chain [2] := by
  constructor
  · decide +kernel
  constructor
  · decide +kernel
  · simp [Closed, chain]

theorem task_order_duplicate_invariant (t : Tree) (as bs : List Nat)
    (same : ∀ child, child ∈ as ↔ child ∈ bs) (x : Nat) :
    x ∈ (drain t as []).cert ↔ x ∈ (drain t bs []).cert := by
  rw [coverage_equivalent, coverage_equivalent]
  simp only [naive, List.mem_flatMap]
  exact exists_congr (fun child => and_congr (same child) Iff.rfl)

theorem no_query_above_root (t : Tree) (cert : List Nat) :
    (walk t 0 cert).queries = 0 := by
  by_cases h : 0 ∈ cert <;> simp [walk, h]

theorem chain_two_orders :
    (drain chain [1, 2, 3, 4, 5, 6, 7, 8] []).cert = [7, 6, 5, 4, 3, 2, 1, 0] ∧
    (drain chain [8, 7, 6, 5, 4, 3, 2, 1] []).cert = [7, 6, 5, 4, 3, 2, 1, 0] ∧
    (drain chain [1, 2, 3, 4, 5, 6, 7, 8] []).queries = 15 ∧
    (drain chain [8, 7, 6, 5, 4, 3, 2, 1] []).queries = 15 := by decide +kernel

theorem cache_reuse_requires_same_tree :
    Closed forkTree [2, 0] ∧ ¬ Closed chain [2, 0] := by
  simp [Closed, forkTree, forkParent, chain]

end CertifiedPath
