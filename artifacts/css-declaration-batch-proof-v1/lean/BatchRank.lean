import BatchIndices
namespace BatchRank

def walk (count : Nat) : List (Nat × Bool) → List (Nat × Nat)
  | [] => []
  | (p,true)::rest => walk (count+1) rest
  | (p,false)::rest => (p,p-count)::walk count rest

def before (events : List (Nat × Bool)) (p : Nat) : Nat :=
  (events.filter (fun e => e.2 && decide (e.1 < p))).length

def projected (count : Nat) (events : List (Nat × Bool)) : List (Nat × Nat) :=
  events.filterMap (fun e => if e.2 then none else some (e.1,e.1-(count+before events e.1)))

theorem filterMap_congr_mem (xs : List α) (f g : α → Option β)
    (h : ∀ x ∈ xs, f x = g x) : xs.filterMap f = xs.filterMap g := by
  induction xs with
  | nil => rfl
  | cons x rest ih =>
    simp only [List.filterMap_cons]
    rw [h x (by simp), ih (by intro y hy; exact h y (by simp [hy]))]

theorem ascending_rank_loop (events : List (Nat × Bool)) (count : Nat)
    (hs : events.Pairwise (fun a b => a.1 < b.1)) : walk count events = projected count events := by
  induction events generalizing count with
  | nil => rfl
  | cons e rest ih =>
    obtain ⟨p,b⟩ := e
    have ht := (List.pairwise_cons.mp hs).2
    have hp := (List.pairwise_cons.mp hs).1
    have hbefore : before rest p = 0 := by
      unfold before
      have hz : rest.filter (fun e => e.2 && decide (e.1 < p)) = [] := by
        apply List.filter_eq_nil_iff.mpr
        intro e he
        have := hp e he
        simp [show ¬e.1 < p by omega]
      rw [hz]
      rfl
    cases b with
    | true =>
      simp only [walk]
      rw [ih (count+1) ht]
      unfold projected
      simp only [List.filterMap_cons, Bool.true_eq, ↓reduceIte]
      apply filterMap_congr_mem
      intro e he
      have hlt := hp e he
      simp [before,hlt,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
    | false =>
      simp only [walk]
      rw [ih count ht]
      unfold projected
      simp only [List.filterMap_cons, Bool.false_eq_true, ↓reduceIte]
      have hzero : before ((p,false)::rest) p = 0 := by
        change before rest p = 0
        exact hbefore
      rw [hzero,Nat.add_zero]
      simp [before]

end BatchRank
