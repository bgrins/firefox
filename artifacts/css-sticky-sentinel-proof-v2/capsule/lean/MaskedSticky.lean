import Std
namespace MaskedSticky

structure Limits where
  nearEdge : Int
  farEdge : Int
  containNear : Int
  containFar : Int
  deriving DecidableEq, Repr

structure Offsets where
  nearValue : Int
  farValue : Int
  deriving DecidableEq, Repr

def lower (l : Limits) : Int := min l.nearEdge l.containFar
def upper (l : Limits) : Int := max l.farEdge l.containNear

def original (n : Int) (l : Limits) : Int := min (max n (lower l)) (upper l)

def native (auto : Int) (o : Option Offsets) (n : Int) (l : Limits) : Int :=
  match o with
  | none => n
  | some v =>
    let p := if v.nearValue != auto then max n (lower l) else n
    if v.farValue != auto then min p (upper l) else p

def constraints (auto : Int) (o : Option Offsets) (l : Limits) : Option Int × Option Int :=
  match o with
  | none => (none, none)
  | some v =>
    (if v.nearValue = auto then none else some (lower l),
     if v.farValue = auto then none else some (upper l))

def reference (n : Int) (bounds : Option Int × Option Int) : Int :=
  match bounds with
  | (none, none) => n
  | (some a, none) => max n a
  | (none, some b) => min n b
  | (some a, some b) => if a > b then b else max a (min n b)

theorem reference_refinement (auto n : Int) (o : Option Offsets) (l : Limits) :
    native auto o n l = reference n (constraints auto o l) := by
  cases o with
  | none => rfl
  | some v =>
    simp only [native, constraints]
    by_cases a : v.nearValue = auto <;> by_cases b : v.farValue = auto <;>
      simp [a, b, reference] <;> omega

theorem missing_identity (auto n : Int) (l : Limits) :
    native auto none n l = n := rfl

theorem all_auto_identity (auto n : Int) (l : Limits) :
    native auto (some ⟨auto, auto⟩) n l = n := by simp [native]

theorem near_only_never_decreases (auto a n : Int) (l : Limits) :
    n ≤ native auto (some ⟨a, auto⟩) n l := by
  simp only [native]; split <;> simp_all <;> omega

theorem far_only_never_increases (auto b n : Int) (l : Limits) :
    native auto (some ⟨auto, b⟩) n l ≤ n := by
  simp only [native]; split <;> simp_all <;> omega

theorem absent_far_independent (auto a n far : Int) (l : Limits) :
    native auto (some ⟨a, auto⟩) n {l with farEdge := far} =
      native auto (some ⟨a, auto⟩) n l := by simp [native, lower]

theorem absent_near_independent (auto b n near : Int) (l : Limits) :
    native auto (some ⟨auto, b⟩) n {l with nearEdge := near} =
      native auto (some ⟨auto, b⟩) n l := by simp [native, upper]

theorem both_active_unchanged (auto a b n : Int) (l : Limits)
    (ha : a ≠ auto) (hb : b ≠ auto) :
    native auto (some ⟨a,b⟩) n l = original n l := by
  simp [native, original, ha, hb]

theorem containment_preserved (auto n : Int) (o : Option Offsets) (l : Limits)
    (hn : l.containNear ≤ n) (hf : n ≤ l.containFar) :
    l.containNear ≤ native auto o n l ∧ native auto o n l ≤ l.containFar := by
  cases o with
  | none => exact ⟨hn,hf⟩
  | some v =>
    simp only [native,lower,upper]
    split <;> split <;> omega

def Feasible (bounds : Option Int × Option Int) (x : Int) : Prop :=
  (∀ a, bounds.1 = some a → a ≤ x) ∧ (∀ b, bounds.2 = some b → x ≤ b)

def Compatible (bounds : Option Int × Option Int) : Prop :=
  ∀ a b, bounds = (some a, some b) → a ≤ b

theorem reference_feasible (n : Int) (bounds : Option Int × Option Int)
    (h : Compatible bounds) : Feasible bounds (reference n bounds) := by
  rcases bounds with ⟨a,b⟩
  cases a <;> cases b <;> simp_all [Feasible,Compatible,reference] <;> omega

theorem reference_closest (n x : Int) (bounds : Option Int × Option Int)
    (h : Compatible bounds) (hx : Feasible bounds x) :
    (reference n bounds - n).natAbs ≤ (x - n).natAbs := by
  rcases bounds with ⟨a,b⟩
  cases a <;> cases b <;> simp_all [Feasible,Compatible,reference] <;> omega

theorem native_closest_contained (auto n : Int) (o : Option Offsets) (l : Limits)
    (hn : l.containNear ≤ n) (hf : n ≤ l.containFar)
    (hc : Compatible (constraints auto o l)) :
    Feasible (constraints auto o l) (native auto o n l) ∧
    l.containNear ≤ native auto o n l ∧ native auto o n l ≤ l.containFar ∧
    ∀ x, Feasible (constraints auto o l) x → l.containNear ≤ x → x ≤ l.containFar →
      (native auto o n l - n).natAbs ≤ (x - n).natAbs := by
  obtain ⟨hlo,hhi⟩ := containment_preserved auto n o l hn hf
  refine ⟨?_,hlo,hhi,?_⟩
  · rw [reference_refinement]
    exact reference_feasible n _ hc
  · intro x hx _ _
    rw [reference_refinement]
    exact reference_closest n x _ hc hx

theorem contradiction_far_priority (auto a b n : Int) (l : Limits)
    (ha : a ≠ auto) (hb : b ≠ auto) (bad : upper l < lower l) :
    native auto (some ⟨a,b⟩) n l = upper l := by
  rw [both_active_unchanged auto a b n l ha hb]
  unfold original; omega

theorem old_new_coincide (auto n : Int) (v : Offsets) (l : Limits)
    (ha : v.nearValue = auto → lower l ≤ n)
    (hb : v.farValue = auto → max n (lower l) ≤ upper l) :
    native auto (some v) n l = original n l := by
  by_cases a : v.nearValue = auto <;> by_cases b : v.farValue = auto <;>
    simp_all [native,original] <;> omega

def sentinelLimits : Limits := ⟨-536870911,536870912,0,1020000000⟩

theorem concrete_original_failure :
    original 700000000 sentinelLimits = 536870912 ∧
    native 1073741823 (some ⟨1073741823,1073741823⟩) 700000000 sentinelLimits = 700000000 := by
  decide +kernel

theorem concrete_one_side_failure :
    original 700000000 {sentinelLimits with nearEdge := 0} = 536870912 ∧
    native 1073741823 (some ⟨0,1073741823⟩) 700000000 {sentinelLimits with nearEdge := 0} = 700000000 := by
  decide +kernel

def Representable (x : Int) : Prop := -2147483648 ≤ x ∧ x ≤ 2147483647

def signed32 (x : Int) : Int := (x + 2147483648) % 4294967296 - 2147483648

theorem signed32_identity (x : Int) (h : Representable x) : signed32 x = x := by
  unfold Representable signed32 at *
  omega

theorem min_max_representable (a b : Int) (ha : Representable a) (hb : Representable b) :
    Representable (min a b) ∧ Representable (max a b) := by
  unfold Representable at *
  omega

theorem signed_minmax_exact (a b : Int) (ha : Representable a) (hb : Representable b) :
    signed32 (min (signed32 a) (signed32 b)) = min a b ∧
    signed32 (max (signed32 a) (signed32 b)) = max a b := by
  rw [signed32_identity a ha, signed32_identity b hb]
  exact ⟨signed32_identity _ (min_max_representable a b ha hb).1,
         signed32_identity _ (min_max_representable a b ha hb).2⟩

theorem native_result_representable (auto n : Int) (o : Option Offsets) (l : Limits)
    (hn : Representable n) (ha : Representable l.nearEdge) (hb : Representable l.farEdge)
    (hc : Representable l.containNear) (hd : Representable l.containFar) :
    Representable (native auto o n l) := by
  cases o with
  | none => exact hn
  | some v =>
    simp only [native]
    unfold lower upper Representable at *
    split <;> split <;> omega

theorem masked_near_collision_retains_constraint :
    native 1073741823 (some ⟨0,1073741823⟩) (-700000000)
      ⟨-536870911,536870912,-1020000000,1020000000⟩ = -536870911 := by
  decide +kernel

theorem masked_far_collision_retains_constraint :
    native 1073741823 (some ⟨1073741823,0⟩) 700000000 sentinelLimits = 536870912 := by
  decide +kernel

end MaskedSticky
