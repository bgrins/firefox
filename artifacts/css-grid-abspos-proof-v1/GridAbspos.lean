import Std.Tactic

set_option linter.unusedSimpArgs false

namespace GridAbspos

def cap (lo hi x : Int) : Int := if x < lo then lo else if hi < x then hi else x

def project (lo hi x : Int) : Option Int :=
  if lo ≤ x ∧ x ≤ hi then some x else none

def normalize (hi : Int) (a b : Int) : Int × Int :=
  if a > b then (b, a)
  else if a = b then
    let start := if a = hi then hi - 1 else a
    (start, start + 1)
  else (a, b)

def finish (lo hi : Int) (p : Int × Int) : Int × Int :=
  normalize hi (cap lo hi p.1) (cap lo hi p.2)

def projectPair (lo hi : Int) (p : Int × Int) : Option Int × Option Int :=
  (project lo hi p.1, project lo hi p.2)

def specPair (lo hi : Int) (p : Int × Int) : Option Int × Option Int :=
  projectPair lo hi (min p.1 p.2, max p.1 p.2)

def abspos (ulo uhi lo hi : Int) (p : Int × Int) :=
  projectPair lo hi (finish ulo uhi p)

theorem cap_lower_absorb (lo hi x : Int) (h : lo ≤ hi) :
    cap lo hi (max x lo) = cap lo hi x := by
  simp only [cap, Int.max_def]
  repeat' split
  all_goals omega

theorem cap_upper_absorb (lo hi x : Int) (h : lo ≤ hi) :
    cap lo hi (min x hi) = cap lo hi x := by
  simp only [cap, Int.min_def]
  repeat' split
  all_goals omega

theorem finish_lower_absorb (lo hi a b : Int) (h : lo ≤ hi) :
    finish lo hi (max a lo, b) = finish lo hi (a, b) := by
  simp only [finish, cap_lower_absorb lo hi a h]

theorem finish_upper_absorb (lo hi a b : Int) (h : lo ≤ hi) :
    finish lo hi (a, min b hi) = finish lo hi (a, b) := by
  simp only [finish, cap_upper_absorb lo hi b h]

theorem cap_identity (lo hi x : Int) (a : lo ≤ x) (b : x ≤ hi) :
    cap lo hi x = x := by
  simp only [cap]
  repeat' split
  all_goals omega

theorem projection_inside (lo hi x : Int) (h : lo ≤ x ∧ x ≤ hi) :
    project lo hi x = some x := by simp [project, h]

theorem projection_outside (lo hi x : Int) (h : x < lo ∨ hi < x) :
    project lo hi x = none := by
  simp only [project]
  split <;> simp_all
  omega

theorem projection_preserves_iff (lo hi x y : Int) :
    project lo hi x = some y ↔ lo ≤ x ∧ x ≤ hi ∧ y = x := by
  simp only [project]
  split
  · simp_all [eq_comm]
  · simp_all
    intro h1 h2
    omega

theorem cap_bounded (lo hi x : Int) (h : lo ≤ hi) :
    lo ≤ cap lo hi x ∧ cap lo hi x ≤ hi := by
  simp only [cap]
  repeat' split
  all_goals omega

theorem normalize_bounded (lo hi a b : Int) (h : lo < hi)
    (ha : lo ≤ a ∧ a ≤ hi) (hb : lo ≤ b ∧ b ≤ hi) :
    lo ≤ (normalize hi a b).1 ∧
    (normalize hi a b).1 < (normalize hi a b).2 ∧
    (normalize hi a b).2 ≤ hi := by
  simp only [normalize]
  repeat' split
  all_goals simp only [Prod.fst, Prod.snd]
  all_goals omega

theorem finish_bounded (lo hi a b : Int) (h : lo < hi) :
    lo ≤ (finish lo hi (a,b)).1 ∧
    (finish lo hi (a,b)).1 < (finish lo hi (a,b)).2 ∧
    (finish lo hi (a,b)).2 ≤ hi := by
  exact normalize_bounded lo hi _ _ h (cap_bounded lo hi a (by omega))
    (cap_bounded lo hi b (by omega))

theorem finish_distinct_identity (lo hi a b : Int)
    (ha : lo ≤ a ∧ a ≤ hi) (hb : lo ≤ b ∧ b ≤ hi) (hne : a ≠ b) :
    finish lo hi (a,b) = (min a b, max a b) := by
  simp only [finish, cap_identity lo hi a ha.1 ha.2,
    cap_identity lo hi b hb.1 hb.2, normalize, Int.min_def, Int.max_def]
  repeat' split
  all_goals simp_all
  all_goals omega

theorem abspos_refinement (ulo uhi lo hi a b : Int)
    (ha : ulo ≤ a ∧ a ≤ uhi) (hb : ulo ≤ b ∧ b ≤ uhi) (hne : a ≠ b) :
    abspos ulo uhi lo hi (a,b) = specPair lo hi (a,b) := by
  simp only [abspos, specPair, finish_distinct_identity ulo uhi a b ha hb hne]

theorem old_counterexample :
    projectPair 1 3 (finish 1 3 (4,5)) ≠ specPair 1 3 (4,5) := by decide

theorem fixed_counterexample :
    abspos (-10000) 10000 1 3 (4,5) = specPair 1 3 (4,5) := by decide

theorem equal_endpoint_limitation :
    abspos (-10000) 10000 1 3 (1,1) ≠ (some 1, none) := by decide

theorem ua_boundary_limitation :
    abspos (-10000) 10000 1 10000 (10001,10002) ≠
      specPair 1 10000 (10001,10002) := by decide

inductive Branch where
  | unchanged
  | lowerStart
  | upperEnd
  deriving DecidableEq, Repr

inductive Resolved where
  | span (length : Int)
  | pair (branch : Branch) (start finish : Int)
  deriving DecidableEq, Repr

def preClamp (lo hi : Int) : Branch → Int → Int → Int × Int
  | .unchanged, a, b => (a,b)
  | .lowerStart, a, b => (max a lo,b)
  | .upperEnd, a, b => (a,min b hi)

def finalizer (lo hi : Int) : Resolved → Resolved
  | .span n => .span (min n (hi - 1))
  | .pair branch a b =>
    let p := finish lo hi (preClamp lo hi branch a b)
    .pair .unchanged p.1 p.2

def rawFinalizer (lo hi : Int) : Resolved → Resolved
  | .span n => .span (min n (hi - 1))
  | .pair _ a b =>
    let p := finish lo hi (a,b)
    .pair .unchanged p.1 p.2

def absProjection (lo hi : Int) : Resolved → Option Int × Option Int
  | .span _ => (none,none)
  | .pair _ a b => projectPair lo hi (a,b)

def selectBounds (abs : Bool) (ulo uhi maplo maphi : Int) : Int × Int :=
  if abs then (ulo,uhi) else (maplo,maphi)

def candidate (abs : Bool) (ulo uhi maplo maphi : Int) (r : Resolved) : Resolved :=
  let limits := selectBounds abs ulo uhi maplo maphi
  finalizer limits.1 limits.2 r

theorem preclamp_absorption (lo hi : Int) (h : lo ≤ hi)
    (branch : Branch) (a b : Int) :
    finish lo hi (preClamp lo hi branch a b) = finish lo hi (a,b) := by
  cases branch
  · rfl
  · exact finish_lower_absorb lo hi a b h
  · exact finish_upper_absorb lo hi a b h

theorem all_helper_branches (lo hi : Int) (h : lo ≤ hi) (r : Resolved) :
    finalizer lo hi r = rawFinalizer lo hi r := by
  cases r with
  | span n => rfl
  | pair branch a b => simp only [finalizer, rawFinalizer, preclamp_absorption lo hi h]

theorem normal_flow_unchanged (ulo uhi maplo maphi : Int) (r : Resolved) :
    candidate false ulo uhi maplo maphi r = finalizer maplo maphi r := by rfl

theorem abspos_independent_of_map_bounds (ulo uhi mlo mhi nlo nhi : Int) (r : Resolved) :
    candidate true ulo uhi mlo mhi r = candidate true ulo uhi nlo nhi r := by rfl

theorem complete_pair_refinement (ulo uhi lo hi maplo maphi a b : Int)
    (branch : Branch) (h : ulo ≤ uhi)
    (ha : ulo ≤ a ∧ a ≤ uhi) (hb : ulo ≤ b ∧ b ≤ uhi) (hne : a ≠ b) :
    absProjection lo hi (candidate true ulo uhi maplo maphi (.pair branch a b)) =
    specPair lo hi (a,b) := by
  simp only [candidate, selectBounds, Bool.true_eq, ↓reduceIte]
  rw [all_helper_branches ulo uhi h]
  simp only [rawFinalizer, absProjection]
  exact abspos_refinement ulo uhi lo hi a b ha hb hne

theorem span_only_is_auto (ulo uhi maplo maphi lo hi n : Int) :
    absProjection lo hi (candidate true ulo uhi maplo maphi (.span n)) = (none,none) := by rfl

theorem preclamp_max_not_sentinel (x hi sentinel : Int) (h : hi < sentinel) :
    min x hi ≠ sentinel := by
  simp only [Int.min_def]
  split <;> omega

theorem finalizer_not_sentinel (lo hi a b sentinel : Int)
    (h : lo < hi) (hs : hi < sentinel) :
    (finish lo hi (a,b)).1 ≠ sentinel ∧ (finish lo hi (a,b)).2 ≠ sentinel := by
  have bounds := finish_bounded lo hi a b h
  omega

theorem strict_interior_is_not_enough :
    abspos (-10000) 10000 1 9999 (10001,10002) ≠
      specPair 1 9999 (10001,10002) := by decide

end GridAbspos

#print axioms GridAbspos.cap_lower_absorb
#print axioms GridAbspos.cap_upper_absorb
#print axioms GridAbspos.finish_lower_absorb
#print axioms GridAbspos.finish_upper_absorb
#print axioms GridAbspos.cap_identity
#print axioms GridAbspos.projection_inside
#print axioms GridAbspos.projection_outside
#print axioms GridAbspos.projection_preserves_iff
#print axioms GridAbspos.cap_bounded
#print axioms GridAbspos.normalize_bounded
#print axioms GridAbspos.finish_bounded
#print axioms GridAbspos.finish_distinct_identity
#print axioms GridAbspos.abspos_refinement
#print axioms GridAbspos.old_counterexample
#print axioms GridAbspos.fixed_counterexample
#print axioms GridAbspos.equal_endpoint_limitation
#print axioms GridAbspos.ua_boundary_limitation
#print axioms GridAbspos.preclamp_absorption
#print axioms GridAbspos.all_helper_branches
#print axioms GridAbspos.normal_flow_unchanged
#print axioms GridAbspos.abspos_independent_of_map_bounds
#print axioms GridAbspos.complete_pair_refinement
#print axioms GridAbspos.span_only_is_auto
#print axioms GridAbspos.preclamp_max_not_sentinel
#print axioms GridAbspos.finalizer_not_sentinel
#print axioms GridAbspos.strict_interior_is_not_enough
