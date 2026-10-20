import Std
namespace StickyAxis
structure Insets where
  near : Option Int
  far : Option Int
  deriving Repr, DecidableEq

def active (i : Insets) : Bool := i.near.isSome || i.far.isSome

def value (i : Option Int) : Int := i.getD 0

structure Edges where
  near : Int
  far : Int
  deriving Repr, DecidableEq

def nativeEnd (port box start ending : Int) : Int :=
  let view := port - (start + ending)
  if box > view then ending - (box - view) else ending

def referenceEnd (port box start ending : Int) : Int :=
  min ending (port - start - box)

theorem end_refinement (port box start ending : Int) :
    nativeEnd port box start ending = referenceEnd port box start ending := by
  simp only [nativeEnd, referenceEnd]
  split <;> omega

theorem end_fits (port box start ending : Int) :
    box ≤ port - (start + nativeEnd port box start ending) := by
  rw [end_refinement]; unfold referenceEnd; omega

theorem end_not_increased (port box start ending : Int) :
    nativeEnd port box start ending ≤ ending := by
  rw [end_refinement]; unfold referenceEnd; omega

theorem sufficient_unchanged (port box start ending : Int)
    (fit : box ≤ port - (start + ending)) :
    nativeEnd port box start ending = ending := by
  simp only [nativeEnd]; split <;> omega

theorem insufficient_exact (port box start ending : Int)
    (small : port - (start + ending) < box) :
    port - (start + nativeEnd port box start ending) = box := by
  simp only [nativeEnd]; split <;> omega

theorem minimal_reduction (port box start ending candidate : Int)
    (reduced : candidate ≤ ending) (fit : box ≤ port - (start + candidate)) :
    candidate ≤ nativeEnd port box start ending := by
  rw [end_refinement]; unfold referenceEnd; omega

theorem normalization_idempotent (port box start ending : Int) :
    nativeEnd port box start (nativeEnd port box start ending) =
      nativeEnd port box start ending :=
  sufficient_unchanged _ _ _ _ (end_fits _ _ _ _)

def nativeNormalize (i : Insets) (port box : Int) (endIsFar : Bool) : Edges :=
  let a := value i.near
  let b := value i.far
  if active i then
    if endIsFar then ⟨a, nativeEnd port box a b⟩
    else ⟨nativeEnd port box b a, b⟩
  else ⟨a,b⟩

def referenceNormalize (i : Insets) (port box : Int) (endIsFar : Bool) : Edges :=
  if active i then
    if endIsFar then ⟨value i.near, min (value i.far) (port - value i.near - box)⟩
    else ⟨min (value i.near) (port - value i.far - box), value i.far⟩
  else ⟨0,0⟩

theorem normalization_refines (i : Insets) (port box : Int) (endIsFar : Bool) :
    nativeNormalize i port box endIsFar = referenceNormalize i port box endIsFar := by
  cases i with
  | mk a b =>
    cases a <;> cases b <;> cases endIsFar <;>
      simp [nativeNormalize, referenceNormalize, active, value, end_refinement, referenceEnd]

theorem active_view_fits (i : Insets) (port box : Int) (endIsFar : Bool)
    (h : active i = true) :
    box ≤ port - ((nativeNormalize i port box endIsFar).near +
                   (nativeNormalize i port box endIsFar).far) := by
  cases endIsFar <;> simp [nativeNormalize,h]
  · have := end_fits port box (value i.far) (value i.near); omega
  · exact end_fits _ _ _ _

theorem logical_start_preserved (i : Insets) (port box : Int) (endIsFar : Bool) :
    (if endIsFar then (nativeNormalize i port box endIsFar).near
     else (nativeNormalize i port box endIsFar).far) =
    (if endIsFar then value i.near else value i.far) := by
  cases endIsFar <;> simp only [nativeNormalize, Bool.false_eq_true, ↓reduceIte]
  all_goals split <;> rfl

theorem both_absent (port box : Int) (endIsFar : Bool) :
    nativeNormalize ⟨none,none⟩ port box endIsFar = ⟨0,0⟩ := by
  simp [nativeNormalize,active,value]

def movementEdges (i : Insets) (normalized : Edges) (origin port box : Int) :
    Option Int × Option Int :=
  (i.near.map (fun _ => origin + normalized.near),
   i.far.map (fun _ => origin + port - normalized.far - box))

theorem absent_near_never_constrains (far : Option Int) (e : Edges) (o p b : Int) :
    (movementEdges ⟨none,far⟩ e o p b).1 = none := rfl

theorem absent_far_never_constrains (near : Option Int) (e : Edges) (o p b : Int) :
    (movementEdges ⟨near,none⟩ e o p b).2 = none := rfl

theorem both_active_edges_ordered (a b port box origin : Int) (endIsFar : Bool) :
    let e := nativeNormalize ⟨some a,some b⟩ port box endIsFar
    origin + e.near ≤ origin + port - e.far - box := by
  have h := active_view_fits ⟨some a,some b⟩ port box endIsFar (by rfl)
  dsimp; omega

theorem h1_counterexample : nativeNormalize ⟨none,some 20⟩ 100 200 true = ⟨0,-100⟩ := by
  decide +kernel
end StickyAxis
