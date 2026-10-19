import Std

namespace HyphenScalarFilter

structure Scalar where
  point : Nat
  width : Nat
  deriving DecidableEq, Repr

def high (u : Nat) : Bool := 0xd800 ≤ u && u ≤ 0xdbff
def low (u : Nat) : Bool := 0xdc00 ≤ u && u ≤ 0xdfff

def decode : List Nat → List Scalar
  | [] => []
  | [u] => [⟨u, 1⟩]
  | u :: v :: rest =>
    if high u && low v then
      ⟨0x10000 + (u - 0xd800) * 1024 + (v - 0xdc00), 2⟩ :: decode rest
    else ⟨u, 1⟩ :: decode (v :: rest)
termination_by units => units.length

def widths (xs : List Scalar) : Nat := (xs.map Scalar.width).sum

theorem decoder_coverage (units : List Nat) : widths (decode units) = units.length := by
  induction units using decode.induct with
  | case1 => simp [decode, widths]
  | case2 u => simp [decode, widths]
  | case3 u v rest h ih => simp [decode, h, widths] at *; omega
  | case4 u v rest h ih => simp [decode, h, widths] at *; omega

theorem scalar_widths (units : List Nat) :
    ∀ s ∈ decode units, s.width = 1 ∨ s.width = 2 := by
  induction units using decode.induct with
  | case1 => simp [decode]
  | case2 u => simp [decode]
  | case3 u v rest h ih => simp_all [decode]
  | case4 u v rest h ih =>
    have hn : ¬(high u && low v) = true := h
    rw [decode, ite_eq_right hn]
    intro s hs
    rcases List.mem_cons.mp hs with hs | hs
    · subst s; simp
    · exact ih s hs

inductive Category where
  | mn | punctuation | control | format | surrogate | other
  deriving DecidableEq, Repr

def counted : Category → Nat
  | .other => 1
  | _ => 0

def count (category : Nat → Category) (xs : List Scalar) : Nat :=
  (xs.map fun s => counted (category s.point)).sum

structure Visit where
  index : Nat
  countBefore : Nat
  deriving DecidableEq, Repr

def visits (category : Nat → Category) : List Scalar → Nat → Nat → List Visit
  | [], _, _ => []
  | s :: rest, index, countBefore =>
    let next := countBefore + counted (category s.point)
    ⟨index, next⟩ :: visits category rest (index + s.width) next

def referenceVisits (category : Nat → Category) (xs : List Scalar)
    (index countBefore : Nat) : List Visit :=
  xs.zipIdx.map fun (_, i) =>
    ⟨index + widths (xs.take i), countBefore + count category (xs.take (i + 1))⟩

theorem visits_reference (category : Nat → Category) (xs : List Scalar)
    (index countBefore : Nat) :
    visits category xs index countBefore = referenceVisits category xs index countBefore := by
  induction xs generalizing index countBefore with
  | nil => simp [visits, referenceVisits]
  | cons s rest ih =>
    rw [visits, ih]
    simp only [referenceVisits, List.zipIdx_cons', List.map_cons, List.map_map]
    simp [widths, count, Nat.add_assoc]

theorem count_append (category : Nat → Category) (a b : List Scalar) :
    count category (a ++ b) = count category a + count category b := by
  simp [count]

theorem count_le_units (category : Nat → Category) (units : List Nat) :
    count category (decode units) ≤ units.length := by
  have h := scalar_widths units
  rw [← decoder_coverage units]
  generalize decode units = xs at *
  induction xs with
  | nil => simp [count, widths]
  | cons s rest ih =>
    have hw := h s (by simp)
    have hr : ∀ t ∈ rest, t.width = 1 ∨ t.width = 2 := by intro t ht; exact h t (by simp [ht])
    have hc : counted (category s.point) ≤ s.width := by cases category s.point <;> simp [counted] <;> omega
    simp only [count, widths, List.map_cons, List.sum_cons] at *
    have := ih hr
    omega

theorem visits_lower_bounds (category : Nat → Category) (xs : List Scalar)
    (index countBefore : Nat) :
    ∀ v ∈ visits category xs index countBefore,
      index ≤ v.index ∧ countBefore ≤ v.countBefore := by
  induction xs generalizing index countBefore with
  | nil => simp [visits]
  | cons s rest ih =>
    intro v hv
    simp only [visits, List.mem_cons] at hv
    rcases hv with hv | hv
    · subst v; simp
    · have h := ih (index + s.width) (countBefore + counted (category s.point)) v hv
      constructor <;> omega

theorem visits_counts_ordered (category : Nat → Category) (xs : List Scalar)
    (index countBefore : Nat) :
    (visits category xs index countBefore).Pairwise fun a b => a.countBefore ≤ b.countBefore := by
  induction xs generalizing index countBefore with
  | nil => simp [visits]
  | cons s rest ih =>
    rw [visits, List.pairwise_cons]
    constructor
    · intro v hv
      exact (visits_lower_bounds category rest _ _ v hv).2
    · exact ih _ _

theorem visits_indices_ordered (category : Nat → Category) (xs : List Scalar)
    (positive : ∀ s ∈ xs, 0 < s.width) (index countBefore : Nat) :
    (visits category xs index countBefore).Pairwise fun a b => a.index < b.index := by
  induction xs generalizing index countBefore with
  | nil => simp [visits]
  | cons s rest ih =>
    rw [visits, List.pairwise_cons]
    constructor
    · intro v hv
      have h := (visits_lower_bounds category rest (index + s.width) _ v hv).1
      have hp := positive s (by simp)
      change index < v.index
      omega
    · apply ih
      intro t ht
      exact positive t (by simp [ht])

theorem count_le_widths (category : Nat → Category) (xs : List Scalar)
    (positive : ∀ s ∈ xs, 0 < s.width) : count category xs ≤ widths xs := by
  induction xs with
  | nil => simp [count, widths]
  | cons s rest ih =>
    have hp := positive s (by simp)
    have hr := ih (by intro t ht; exact positive t (by simp [ht]))
    have hc : counted (category s.point) ≤ 1 := by cases category s.point <;> simp [counted]
    simp only [count, widths, List.map_cons, List.sum_cons] at *
    omega

theorem visits_suffix_bound (category : Nat → Category) (xs : List Scalar)
    (positive : ∀ s ∈ xs, 0 < s.width) (index before : Nat) :
    ∀ v ∈ visits category xs index before,
      v.countBefore ≤ before + count category xs ∧
      v.index + 1 ≤ index + widths xs ∧
      before + count category xs - v.countBefore ≤ index + widths xs - (v.index + 1) := by
  induction xs generalizing index before with
  | nil => simp [visits]
  | cons s rest ih =>
    have hp := positive s (by simp)
    have ht : ∀ t ∈ rest, 0 < t.width := by intro t ht; exact positive t (by simp [ht])
    have hc := count_le_widths category rest ht
    intro v hv
    rcases List.mem_cons.mp hv with hv | hv
    · subst v
      simp only [count, widths, List.map_cons, List.sum_cons] at *
      change before + counted (category s.point) ≤ _ ∧ index + 1 ≤ _ ∧ _
      omega
    · have h := ih ht (index + s.width) (before + counted (category s.point)) v hv
      simp only [count, widths, List.map_cons, List.sum_cons] at *
      omega

theorem fast_suffix_guard_sound (category : Nat → Category) (units : List Nat)
    (v : Visit) (hv : v ∈ visits category (decode units) 0 0)
    (after : Nat) (suffix : after ≤ count category (decode units) - v.countBefore)
    (interior : v.index + 1 < units.length) :
    v.index < units.length - max 1 after := by
  have hp : ∀ s ∈ decode units, 0 < s.width := by
    intro s hs; have h := scalar_widths units s hs; omega
  have h := visits_suffix_bound category (decode units) hp 0 0 v hv
  rw [decoder_coverage] at h
  simp only [Nat.zero_add] at h
  omega

def nativeEligible (units : List Nat) (total minimum pre after : Nat)
    (mask : Nat → Bool) (v : Visit) : Bool :=
  mask v.index && pre ≤ v.countBefore && v.index < units.length - max 1 after &&
    minimum ≤ total && after ≤ total - v.countBefore

def declarativeEligible (units : List Nat) (total minimum pre after : Nat)
    (mask : Nat → Bool) (v : Visit) : Bool :=
  mask v.index && pre ≤ v.countBefore && v.index + 1 < units.length &&
    minimum ≤ total && after ≤ total - v.countBefore

theorem exact_eligibility (category : Nat → Category) (units : List Nat)
    (minimum pre after : Nat) (mask : Nat → Bool) (v : Visit)
    (hv : v ∈ visits category (decode units) 0 0) :
    nativeEligible units (count category (decode units)) minimum pre after mask v =
      declarativeEligible units (count category (decode units)) minimum pre after mask v := by
  apply Bool.eq_iff_iff.mpr
  simp only [nativeEligible, declarativeEligible, Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · rintro ⟨⟨⟨⟨hm, hp⟩, hi⟩, hw⟩, hs⟩
    exact ⟨⟨⟨⟨hm,hp⟩,by omega⟩,hw⟩,hs⟩
  · rintro ⟨⟨⟨⟨hm, hp⟩, hi⟩, hw⟩, hs⟩
    exact ⟨⟨⟨⟨hm,hp⟩,fast_suffix_guard_sound category units v hv after hs hi⟩,hw⟩,hs⟩

theorem short_unit_guard_sound (category : Nat → Category) (units : List Nat)
    (minimum : Nat) (short : units.length < minimum) :
    count category (decode units) < minimum := by
  have := count_le_units category units
  omega

structure Candidate where
  index : Nat
  countBefore : Nat
  previous : Nat
  deriving DecidableEq, Repr

def keep (total suffix : Nat) (c : Candidate) : Bool := suffix ≤ total - c.countBefore

def rollback (total suffix : Nat) : List Candidate → List Candidate
  | [] => []
  | c :: rest => if keep total suffix c then c :: rest else rollback total suffix rest

def Descending (xs : List Candidate) : Prop :=
  xs.Pairwise fun a b => b.countBefore ≤ a.countBefore

def candidates (category : Nat → Category) (units : List Nat)
    (pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) : List Candidate :=
  ((visits category (decode units) 0 0).filter fun v =>
    v.index < units.length - max 1 after && pre ≤ v.countBefore && mask v.index).map fun v =>
      ⟨v.index + 1, v.countBefore, old (v.index + 1)⟩

theorem candidate_prefix_order (category : Nat → Category) (units : List Nat)
    (pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) :
    Descending (candidates category units pre after mask old).reverse := by
  simp only [Descending, candidates, List.pairwise_reverse, List.pairwise_map]
  exact (visits_counts_ordered category (decode units) 0 0).filter _

theorem candidate_indices_unique (category : Nat → Category) (units : List Nat)
    (pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) :
    (candidates category units pre after mask old).Pairwise fun a b => a.index < b.index := by
  simp only [candidates, List.pairwise_map]
  have hp : ∀ s ∈ decode units, 0 < s.width := by
    intro s hs
    have h := scalar_widths units s hs
    omega
  have h := (visits_indices_ordered category (decode units) hp 0 0).filter
    (fun v => v.index < units.length - max 1 after && pre ≤ v.countBefore && mask v.index)
  apply h.imp
  intro a b hab
  change a.index + 1 < b.index + 1
  omega

theorem keep_monotone (total suffix : Nat) (a b : Candidate)
    (h : b.countBefore ≤ a.countBefore) (ha : keep total suffix a = true) :
    keep total suffix b = true := by
  simp only [keep, decide_eq_true_eq] at *
  omega

theorem all_kept_filter (total suffix : Nat) (xs : List Candidate)
    (h : ∀ x ∈ xs, keep total suffix x = true) :
    xs.filter (keep total suffix) = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    have hx := h x (by simp)
    have ht : ∀ y ∈ xs, keep total suffix y = true := by intro y hy; exact h y (by simp [hy])
    simp [hx, ih ht]

theorem reverse_restore_equivalence (total suffix : Nat) (xs : List Candidate)
    (h : Descending xs) : rollback total suffix xs = xs.filter (keep total suffix) := by
  induction xs with
  | nil => rfl
  | cons c rest ih =>
    have pair := List.pairwise_cons.mp (show List.Pairwise _ (c :: rest) from h)
    by_cases hk : keep total suffix c = true
    · have hr : ∀ x ∈ rest, keep total suffix x = true := by
        intro x hx; exact keep_monotone total suffix c x (pair.1 x hx) hk
      simp [rollback, hk, all_kept_filter total suffix rest hr]
    · simp [rollback, hk, ih pair.2]

def filterWhole (minimum total suffix : Nat) (xs : List Candidate) : List Candidate :=
  if total < minimum then [] else rollback total suffix xs

def referenceFilter (minimum total suffix : Nat) (xs : List Candidate) : List Candidate :=
  xs.filter fun c => minimum ≤ total && suffix ≤ total - c.countBefore

theorem whole_filter_equivalence (minimum total suffix : Nat) (xs : List Candidate)
    (h : Descending xs) : filterWhole minimum total suffix xs = referenceFilter minimum total suffix xs := by
  by_cases hm : total < minimum
  · simp [filterWhole, referenceFilter, hm, show ¬minimum ≤ total by omega]
  · simp [filterWhole, referenceFilter, hm, show minimum ≤ total by omega,
      reverse_restore_equivalence total suffix xs h]
    rfl

theorem native_enumeration_filter_equivalence (category : Nat → Category)
    (units : List Nat) (minimum pre after suffix : Nat) (mask : Nat → Bool) (old : Nat → Nat) :
    filterWhole minimum (count category (decode units)) suffix
      (candidates category units pre after mask old).reverse =
    referenceFilter minimum (count category (decode units)) suffix
      (candidates category units pre after mask old).reverse := by
  exact whole_filter_equivalence _ _ _ _ (candidate_prefix_order category units pre after mask old)

def writes (xs : List Candidate) (value base : Nat → Nat) : Nat → Nat :=
  xs.foldl (fun buffer c => fun i => if i = c.index then value i else buffer i) base

theorem writes_at (xs : List Candidate) (value base : Nat → Nat) (i : Nat) :
    writes xs value base i = if ∃ c ∈ xs, c.index = i then value i else base i := by
  induction xs generalizing base with
  | nil => simp [writes]
  | cons c rest ih =>
    simp only [writes, List.foldl_cons]
    rw [show rest.foldl (fun buffer c => fun i => if i = c.index then value i else buffer i)
      (fun i => if i = c.index then value i else base i) =
      writes rest value (fun i => if i = c.index then value i else base i) from rfl]
    rw [ih]
    by_cases h : ∃ d ∈ rest, d.index = i
    · simp [h]
    · by_cases hc : c.index = i
      · simp [h, hc]
      · simp [h, hc, Ne.symm hc]

def uniqueIndices (xs : List Candidate) : Prop :=
  ∀ a ∈ xs, ∀ b ∈ xs, a.index = b.index → a = b

theorem ordered_unique (xs : List Candidate)
    (h : xs.Pairwise fun a b => a.index < b.index) : uniqueIndices xs := by
  induction xs with
  | nil => simp [uniqueIndices]
  | cons c rest ih =>
    have hp := List.pairwise_cons.mp h
    intro a ha b hb he
    rcases List.mem_cons.mp ha with ha | ha <;>
      rcases List.mem_cons.mp hb with hb | hb
    · subst a; subst b; rfl
    · subst a; have := hp.1 b hb; omega
    · subst b; have := hp.1 a ha; omega
    · exact ih hp.2 a ha b hb he

theorem speculative_array_restores (xs : List Candidate) (accept : Candidate → Bool)
    (old : Nat → Nat) (unique : uniqueIndices xs) :
    writes (xs.filter fun c => !accept c) old (writes xs (fun _ => 2) old) =
      writes (xs.filter accept) (fun _ => 2) old := by
  funext i
  simp only [writes_at]
  by_cases hr : ∃ c ∈ xs.filter (fun c => !accept c), c.index = i
  · obtain ⟨c, hc, hi⟩ := hr
    have hc' := List.mem_filter.mp hc
    have hn : ¬∃ d ∈ xs.filter accept, d.index = i := by
      rintro ⟨d, hd, hdindex⟩
      have hd' := List.mem_filter.mp hd
      have he := unique c hc'.1 d hd'.1 (hi.trans hdindex.symm)
      subst d
      simp [hd'.2] at hc'
    rw [ite_eq_left (show ∃ c ∈ xs.filter (fun c => !accept c), c.index = i from ⟨c,hc,hi⟩), ite_eq_right hn]
  · by_cases ha : ∃ c ∈ xs.filter accept, c.index = i
    · obtain ⟨c,hc,hi⟩ := ha
      have hall : ∃ c ∈ xs, c.index = i := ⟨c,(List.mem_filter.mp hc).1,hi⟩
      rw [ite_eq_right hr, ite_eq_left hall, ite_eq_left (show ∃ c ∈ xs.filter accept, c.index = i from ⟨c,hc,hi⟩)]
    · have hn : ¬∃ c ∈ xs, c.index = i := by
        rintro ⟨c,hc,hi⟩
        cases h : accept c with
        | false => exact hr ⟨c,by simp [hc,h],hi⟩
        | true => exact ha ⟨c,by simp [hc,h],hi⟩
      rw [ite_eq_right hr, ite_eq_right hn, ite_eq_right ha]

#print axioms speculative_array_restores
#print axioms visits_reference
#print axioms candidate_prefix_order
#print axioms candidate_indices_unique
#print axioms native_enumeration_filter_equivalence
#print axioms decoder_coverage
#print axioms scalar_widths
#print axioms count_le_units
#print axioms reverse_restore_equivalence
#print axioms whole_filter_equivalence
end HyphenScalarFilter
