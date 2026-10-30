import Std

namespace DefaultClosure

abbrev Edges (V : Type) := V → V → Prop
abbrev Enabled (V : Type) := V → Bool
def Subset (E F : Edges V) : Prop := ∀ u v, E u v → F u v
def Below (a b : Enabled V) : Prop := ∀ v, a v = true → b v = true

inductive Path (E : Edges V) : V → V → Prop
  | edge {u v} : E u v → Path E u v
  | append {u v w} : Path E u v → E v w → Path E u w

def Cyclic (E : Edges V) (v : V) : Prop := Path E v v

theorem path_mono (h : Subset E F) (p : Path E u v) : Path F u v := by
  induction p with
  | edge e => exact .edge (h _ _ e)
  | append p e ih => exact .append ih (h _ _ e)

theorem cyclic_mono (h : Subset E F) : Cyclic E v → Cyclic F v := path_mono h

structure System (V : Type) where
  base : Edges V
  target : V
  eligible : V → Bool
  cycle : Edges V → V → Bool
  correct : ∀ E v, cycle E v = true ↔ Cyclic E v

def graph (S : System V) (a : Enabled V) : Edges V :=
  fun u v => S.base u v ∨ (a u = true ∧ S.eligible u = true ∧ v = S.target)

def round (S : System V) (a : Enabled V) : Enabled V :=
  fun v => a v || (S.eligible v && S.cycle (graph S a) v)

theorem graph_mono (S : System V) (h : Below a b) : Subset (graph S a) (graph S b) := by
  intro u v e
  rcases e with e | ⟨ha, he, ht⟩
  · exact Or.inl e
  · exact Or.inr ⟨h u ha, he, ht⟩

theorem round_inflationary (S : System V) (a : Enabled V) : Below a (round S a) := by
  intro v h
  simp [round, h]

theorem round_mono (S : System V) (h : Below a b) : Below (round S a) (round S b) := by
  intro v hv
  simp only [round, Bool.or_eq_true, Bool.and_eq_true] at hv ⊢
  rcases hv with old | ⟨eligible, cycle⟩
  · exact Or.inl (h v old)
  · exact Or.inr ⟨eligible, (S.correct _ _).mpr (cyclic_mono (graph_mono S h) ((S.correct _ _).mp cycle))⟩

def count (xs : List V) (a : Enabled V) : Nat :=
  match xs with
  | [] => 0
  | v :: vs => (if a v then 1 else 0) + count vs a

theorem count_bound (xs : List V) (a : Enabled V) : count xs a ≤ xs.length := by
  induction xs with
  | nil => simp [count]
  | cons v vs ih => cases h : a v <;> simp [count, h] <;> omega

theorem count_mono (xs : List V) (h : Below a b) : count xs a ≤ count xs b := by
  induction xs with
  | nil => simp [count]
  | cons v vs ih =>
    have hv := h v
    cases ha : a v <;> cases hb : b v <;> simp_all [count] <;> omega

theorem count_equal (xs : List V) (h : Below a b) (eq : count xs a = count xs b) :
    ∀ v ∈ xs, a v = b v := by
  induction xs with
  | nil => simp
  | cons u us ih =>
    have tail := count_mono us h
    have hu := h u
    have heads : a u = b u := by
      cases ha : a u <;> cases hb : b u <;> simp_all [count] <;> omega
    have tails : count us a = count us b := by
      simp only [count, heads] at eq
      omega
    intro v member
    rcases List.mem_cons.mp member with rfl | member
    · exact heads
    · exact ih tails v member

def iterate (f : Enabled V → Enabled V) (a : Enabled V) : Nat → Enabled V
  | 0 => a
  | n + 1 => f (iterate f a n)

theorem finite_stabilization (xs : List V) (complete : ∀ v, v ∈ xs)
    (f : Enabled V → Enabled V) (grows : ∀ a, Below a (f a))
    (fuel : Nat) : ∀ a, xs.length - count xs a ≤ fuel →
    ∃ k ≤ fuel, iterate f a k = f (iterate f a k) := by
  induction fuel with
  | zero =>
    intro a gap
    have bound := count_bound xs (f a)
    have eq : count xs a = count xs (f a) := by omega
    have fixed : a = f a := funext (fun v => count_equal xs (grows a) eq v (complete v))
    exact ⟨0, Nat.le_refl 0, fixed⟩
  | succ fuel ih =>
    intro a gap
    by_cases same : count xs a = count xs (f a)
    · have fixed : a = f a := funext (fun v => count_equal xs (grows a) same v (complete v))
      exact ⟨0, Nat.zero_le _, fixed⟩
    · have inc := count_mono xs (grows a)
      have bound := count_bound xs a
      have next : xs.length - count xs (f a) ≤ fuel := by omega
      obtain ⟨k, hk, fixed⟩ := ih (f a) next
      have shift : ∀ n, iterate f a (n + 1) = iterate f (f a) n := by
        intro n
        induction n with
        | zero => rfl
        | succ n hn => simp only [iterate, hn]
      exact ⟨k + 1, by omega, by simpa only [shift] using fixed⟩

def run (S : System V) : Nat → Enabled V := iterate (round S) (fun _ => false)

def Closed (S : System V) (E : Edges V) : Prop :=
  ∀ v, S.eligible v = true → Cyclic E v → E v S.target

theorem run_contained (S : System V) (contains : Subset S.base E)
    (closed : Closed S E) (n : Nat) : Subset (graph S (run S n)) E := by
  induction n with
  | zero =>
    intro u v edge
    rcases edge with edge | ⟨h, _, _⟩
    · exact contains u v edge
    · simp [run, iterate] at h
  | succ n ih =>
    intro u v edge
    rcases edge with edge | ⟨h, he, rfl⟩
    · exact contains u v edge
    · change round S (run S n) u = true at h
      simp only [round, Bool.or_eq_true, Bool.and_eq_true] at h
      rcases h with old | ⟨eligible, cycle⟩
      · exact ih _ _ (Or.inr ⟨old, he, rfl⟩)
      · exact closed u eligible (cyclic_mono ih ((S.correct _ _).mp cycle))

theorem fixed_closed (S : System V) (fixed : a = round S a) : Closed S (graph S a) := by
  intro v eligible cycle
  have enabled : a v = true := by
    have h : round S a v = true := by simp [round, eligible, (S.correct _ _).mpr cycle]
    rw [← fixed] at h
    exact h
  exact Or.inr ⟨enabled, eligible, rfl⟩

theorem finite_least_closure (S : System V) (xs : List V) (complete : ∀ v, v ∈ xs) :
    ∃ k ≤ xs.length,
      run S k = round S (run S k) ∧
      Subset S.base (graph S (run S k)) ∧
      Closed S (graph S (run S k)) ∧
      ∀ E, Subset S.base E → Closed S E → Subset (graph S (run S k)) E := by
  obtain ⟨k, bound, fixed⟩ := finite_stabilization xs complete (round S) (round_inflationary S) xs.length (fun _ => false) (by omega)
  refine ⟨k, bound, fixed, ?_, fixed_closed S fixed, ?_⟩
  · intro u v h; exact Or.inl h
  · intro E base closed; exact run_contained S base closed k

end DefaultClosure
