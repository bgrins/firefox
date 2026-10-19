import Std

namespace Priority

structure TotalPreorder (α : Type) where
  le : α → α → Prop
  dec : DecidableRel le
  refl : ∀ x, le x x
  trans : ∀ {x y z}, le x y → le y z → le x z
  total : ∀ x y, le x y ∨ le y x

instance (r : TotalPreorder α) : DecidableRel r.le := r.dec

def lex (r s : TotalPreorder α) : TotalPreorder α where
  le x y := r.le x y ∧ (r.le y x → s.le x y)
  dec := fun _ _ => inferInstance
  refl x := ⟨r.refl x, fun _ => s.refl x⟩
  trans := by
    intro x y z hxy hyz
    refine ⟨r.trans hxy.1 hyz.1, ?_⟩
    intro hzx
    exact s.trans (hxy.2 (r.trans hyz.1 hzx)) (hyz.2 (r.trans hzx hxy.1))
  total x y := by
    by_cases hxy : r.le x y
    · by_cases hyx : r.le y x
      · rcases s.total x y with h | h
        · exact Or.inl ⟨hxy, fun _ => h⟩
        · exact Or.inr ⟨hyx, fun _ => h⟩
      · exact Or.inl ⟨hxy, fun h => False.elim (hyx h)⟩
    · exact Or.inr ⟨(r.total x y).resolve_left hxy, fun h => False.elim (hxy h)⟩

def isMinimum (r : TotalPreorder α) (xs : List α) (x : α) : Prop :=
  ∀ y ∈ xs, r.le x y

def minima (r : TotalPreorder α) (xs : List α) : List α :=
  xs.filter (fun x => xs.all (fun y => decide (r.le x y)))

theorem mem_minima (r : TotalPreorder α) (xs : List α) (x : α) :
    x ∈ minima r xs ↔ x ∈ xs ∧ isMinimum r xs x := by
  simp [minima, isMinimum, List.all_eq_true]

theorem lex_minimum (r s : TotalPreorder α) (xs : List α) (x : α)
    (hx : x ∈ xs) :
    isMinimum (lex r s) xs x ↔
      isMinimum r xs x ∧ isMinimum s (minima r xs) x := by
  constructor
  · intro h
    refine ⟨fun y hy => (h y hy).1, ?_⟩
    intro y hy
    have hm := (mem_minima r xs y).mp hy
    exact (h y hm.1).2 (hm.2 x hx)
  · rintro ⟨hr, hs⟩ y hy
    refine ⟨hr y hy, ?_⟩
    intro hyx
    apply hs y
    apply (mem_minima r xs y).mpr
    exact ⟨hy, fun z hz => r.trans hyx (hr z hz)⟩

theorem minima_lex (r s : TotalPreorder α) (xs : List α) :
    minima s (minima r xs) = minima (lex r s) xs := by
  unfold minima
  rw [List.filter_filter]
  apply List.filter_congr
  intro x hx
  apply Bool.eq_iff_iff.mpr
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq]
  simpa only [isMinimum, minima, and_comm] using (lex_minimum r s xs x hx).symm

def scan (r : TotalPreorder α) : List α → List α
  | [] => []
  | x :: xs =>
      match scan r xs with
      | [] => [x]
      | y :: ys =>
          if r.le x y then
            if r.le y x then x :: y :: ys else [x]
          else y :: ys

theorem scan_nil (r : TotalPreorder α) : scan r [] = [] := rfl

theorem scan_singleton (r : TotalPreorder α) (x : α) : scan r [x] = [x] := rfl

theorem exists_minimum (r : TotalPreorder α) (x : α) (xs : List α) :
    ∃ y, y ∈ x :: xs ∧ isMinimum r (x :: xs) y := by
  induction xs generalizing x with
  | nil =>
    refine ⟨x, by simp, ?_⟩
    intro y hy
    have h : y = x := by simpa using hy
    subst y
    exact r.refl x
  | cons z zs ih =>
    obtain ⟨y, hy, hmin⟩ := ih z
    by_cases hxy : r.le x y
    · refine ⟨x, by simp, ?_⟩
      intro a ha
      rcases List.mem_cons.mp ha with h | h
      · subst a; exact r.refl x
      · exact r.trans hxy (hmin a h)
    · refine ⟨y, List.mem_cons_of_mem x hy, ?_⟩
      intro a ha
      rcases List.mem_cons.mp ha with h | h
      · subst a; exact (r.total x y).resolve_left hxy
      · exact hmin a h

theorem minima_nil (r : TotalPreorder α) : minima r [] = [] := rfl

theorem minima_empty_iff (r : TotalPreorder α) (xs : List α) :
    minima r xs = [] ↔ xs = [] := by
  constructor
  · intro h
    cases xs with
    | nil => rfl
    | cons x xs =>
      obtain ⟨y, hy, hmin⟩ := exists_minimum r x xs
      have hm := (mem_minima r (x :: xs) y).mpr ⟨hy, hmin⟩
      rw [h] at hm
      contradiction
  · intro h; subst xs; rfl

theorem minima_cons (r : TotalPreorder α) (x : α) (xs : List α) :
    minima r (x :: xs) =
      (if xs.all (fun y => decide (r.le x y)) then [x] else []) ++
      (minima r xs).filter (fun y => decide (r.le y x)) := by
  simp only [minima, List.all_cons, r.refl, decide_true, Bool.true_and,
    List.filter_cons, List.filter_filter]
  split <;> simp only [List.cons_append, List.nil_append]

theorem compare_minima_head (r : TotalPreorder α) (xs : List α) (x y : α)
    (ys : List α) (h : minima r xs = y :: ys) :
    (xs.all (fun z => decide (r.le x z))) = decide (r.le x y) := by
  have hy : y ∈ minima r xs := by rw [h]; simp
  obtain ⟨hy, hmin⟩ := (mem_minima r xs y).mp hy
  apply Bool.eq_iff_iff.mpr
  simp only [List.all_eq_true, decide_eq_true_eq]
  constructor
  · intro hm; exact hm y hy
  · intro hxy z hz; exact r.trans hxy (hmin z hz)

theorem filter_minima_head (r : TotalPreorder α) (xs : List α) (x y : α)
    (ys : List α) (h : minima r xs = y :: ys) :
    (minima r xs).filter (fun z => decide (r.le z x)) =
      if r.le y x then minima r xs else [] := by
  have hy : y ∈ minima r xs := by rw [h]; simp
  obtain ⟨hy, hmin⟩ := (mem_minima r xs y).mp hy
  by_cases hyx : r.le y x
  · simp only [hyx, ite_true]
    apply List.filter_eq_self.mpr
    intro z hz
    have hzmin := (mem_minima r xs z).mp hz
    exact decide_eq_true (r.trans (hzmin.2 y hy) hyx)
  · simp only [hyx, ite_false]
    apply List.filter_eq_nil_iff.mpr
    intro z hz
    have hzmin := (mem_minima r xs z).mp hz
    intro hzx
    exact hyx (r.trans (hmin z hzmin.1) (of_decide_eq_true hzx))

theorem scan_eq_minima (r : TotalPreorder α) (xs : List α) :
    scan r xs = minima r xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    cases h : scan r xs with
    | nil =>
      have he : minima r xs = [] := ih.symm.trans h
      have hx := (minima_empty_iff r xs).mp he
      subst xs
      simp [scan, minima, r.refl]
    | cons y ys =>
      have hm : minima r xs = y :: ys := ih.symm.trans h
      rw [minima_cons, compare_minima_head r xs x y ys hm,
        filter_minima_head r xs x y ys hm, hm]
      simp only [scan, h, decide_eq_true_eq]
      by_cases hxy : r.le x y <;> by_cases hyx : r.le y x
      · simp [hxy, hyx]
      · simp [hxy, hyx]
      · simp [hxy, hyx]
      · exact False.elim ((r.total x y).elim hxy hyx)

def pullback (r : TotalPreorder β) (key : α → β) : TotalPreorder α where
  le x y := r.le (key x) (key y)
  dec := fun x y => r.dec (key x) (key y)
  refl x := r.refl (key x)
  trans := r.trans
  total x y := r.total (key x) (key y)

def successive (width style weight : TotalPreorder α) (xs : List α) : List α :=
  minima weight (minima style (minima width xs))

def priority (width style weight : TotalPreorder α) : TotalPreorder α :=
  lex (lex width style) weight

theorem ordered_successive_eq_scan (width style weight : TotalPreorder α)
    (xs : List α) :
    successive width style weight xs = scan (priority width style weight) xs := by
  rw [scan_eq_minima]
  exact (minima_lex style weight (minima width xs)).trans (by
    rw [minima_lex]
    apply List.filter_congr
    intro x _
    apply Bool.eq_iff_iff.mpr
    simp only [List.all_eq_true, priority, lex]
    grind)

theorem scan_membership (r : TotalPreorder α) (xs : List α) (x : α) :
    x ∈ scan r xs ↔ x ∈ xs ∧ isMinimum r xs x := by
  rw [scan_eq_minima, mem_minima]

theorem scan_preserves_order (r : TotalPreorder α) (xs : List α) :
    (scan r xs).Sublist xs := by
  rw [scan_eq_minima]
  exact List.filter_sublist

theorem ties_preserved (r : TotalPreorder α) (xs : List α) (x y : α)
    (hx : x ∈ scan r xs) (hy : y ∈ xs) (hyx : r.le y x) :
    y ∈ scan r xs := by
  obtain ⟨_, hmin⟩ := (scan_membership r xs x).mp hx
  exact (scan_membership r xs y).mpr ⟨hy, fun z hz => r.trans hyx (hmin z hz)⟩

theorem permutation_selected_set (r : TotalPreorder α) (xs ys : List α)
    (hperm : xs.Perm ys) (x : α) :
    x ∈ scan r xs ↔ x ∈ scan r ys := by
  simp only [scan_membership, isMinimum]
  constructor
  · rintro ⟨hx, hm⟩
    exact ⟨hperm.mem_iff.mp hx, fun y hy => hm y (hperm.mem_iff.mpr hy)⟩
  · rintro ⟨hx, hm⟩
    exact ⟨hperm.mem_iff.mpr hx, fun y hy => hm y (hperm.mem_iff.mp hy)⟩

theorem ordered_identity_sequence (width style weight : TotalPreorder α)
    (identity : α → β) (xs : List α) :
    (successive width style weight xs).map identity =
      (scan (priority width style weight) xs).map identity := by
  rw [ordered_successive_eq_scan]

theorem first_policy (width style weight : TotalPreorder α) (xs : List α) :
    (successive width style weight xs).head? =
      (scan (priority width style weight) xs).head? := by
  rw [ordered_successive_eq_scan]

theorem last_policy (width style weight : TotalPreorder α) (xs : List α) :
    (successive width style weight xs).getLast? =
      (scan (priority width style weight) xs).getLast? := by
  rw [ordered_successive_eq_scan]

theorem all_ties_preserved (r : TotalPreorder α) (xs : List α)
    (h : ∀ x ∈ xs, ∀ y ∈ xs, r.le x y) : scan r xs = xs := by
  rw [scan_eq_minima]
  apply List.filter_eq_self.mpr
  intro x hx
  simp only [List.all_eq_true, decide_eq_true_eq]
  exact h x hx

theorem scan_empty_iff (r : TotalPreorder α) (xs : List α) :
    scan r xs = [] ↔ xs = [] := by
  rw [scan_eq_minima, minima_empty_iff]

def natural : TotalPreorder Nat where
  le x y := x ≤ y
  dec := fun _ _ => inferInstance
  refl := Nat.le_refl
  trans := Nat.le_trans
  total := Nat.le_total

structure Key where
  presentation : Nat
  width : Nat
  style : Nat
  weight : Nat
  deriving Repr, DecidableEq

def widthOrder : TotalPreorder Key := pullback natural Key.width
def styleOrder : TotalPreorder Key := pullback natural Key.style
def weightOrder : TotalPreorder Key := pullback natural Key.weight
def presentationOrder : TotalPreorder Key := pullback natural Key.presentation

def fallbackOrder : TotalPreorder Key :=
  lex presentationOrder (priority widthOrder styleOrder weightOrder)

def fallbackSuccessive (xs : List Key) : List Key :=
  successive widthOrder styleOrder weightOrder (minima presentationOrder xs)

theorem presentation_extension (xs : List Key) :
    fallbackSuccessive xs = scan fallbackOrder xs := by
  unfold fallbackSuccessive
  rw [ordered_successive_eq_scan, scan_eq_minima, minima_lex, scan_eq_minima]
  rfl

def sentinel : Key := ⟨2, 0, 0, 0⟩
def zeroKey : Key := ⟨0, 0, 0, 0⟩
def mismatch (x : Key) : Key := { x with presentation := 1 }
def optimistic (x : Key) : Key := { x with presentation := 0 }
def isZero (x : Key) : Bool :=
  x.presentation == 0 && x.width == 0 && x.style == 0 && x.weight == 0

def strict (r : TotalPreorder α) (x y : α) : Prop := r.le x y ∧ ¬r.le y x

theorem real_before_sentinel (x : Key) (h : x.presentation ≤ 1) :
    strict fallbackOrder x sentinel := by
  simp only [strict, fallbackOrder, lex, presentationOrder, pullback, natural, sentinel]
  constructor
  · exact ⟨by omega, fun hbad => by omega⟩
  · intro hbad; have := hbad.1; omega

theorem optimistic_lower_bound (x : Key) :
    fallbackOrder.le (optimistic x) (mismatch x) := by
  simp [fallbackOrder, lex, presentationOrder, pullback, natural, optimistic, mismatch]

theorem optimistic_pruning (r : TotalPreorder α) (lower actual incumbent : α)
    (hbound : r.le lower actual) (hprune : ¬strict r lower incumbent) :
    ¬strict r actual incumbent := by
  have hinc : r.le incumbent lower := by
    rcases r.total lower incumbent with h | h
    · by_cases hn : r.le incumbent lower
      · exact hn
      · exact False.elim (hprune ⟨h, hn⟩)
    · exact h
  intro hactual
  exact hactual.2 (r.trans hinc hbound)

theorem zero_lower_bound (x : Key) : fallbackOrder.le zeroKey x := by
  simp [fallbackOrder, priority, lex, presentationOrder, widthOrder,
    styleOrder, weightOrder, pullback, natural, zeroKey]

theorem zero_no_strict_improvement (x : Key) : ¬strict fallbackOrder x zeroKey := by
  intro h
  exact h.2 (zero_lower_bound x)

theorem isZero_iff (x : Key) : isZero x = true ↔ x = zeroKey := by
  cases x
  simp [isZero, zeroKey, Key.mk.injEq, and_assoc]

theorem mismatch_never_zero (x : Key) : isZero (mismatch x) = false := by
  simp [isZero, mismatch]

theorem sentinel_never_zero : isZero sentinel = false := rfl

theorem scaled_coordinate_precision (n : Nat) (h : n ≤ 512000) :
    n < 16777216 := by omega

end Priority
