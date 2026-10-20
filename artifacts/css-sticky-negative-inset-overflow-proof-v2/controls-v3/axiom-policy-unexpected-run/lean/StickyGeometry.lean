import StickyWritingMode
import StickyPosition
namespace StickyGeometry
structure Interval where
  origin : Int
  size : Int
  deriving Repr, DecidableEq

def ending (r : Interval) : Int := r.origin + r.size

def deflate (r : Interval) (near far : Int) : Interval :=
  ⟨r.origin + near, max 0 (r.size - (near + far))⟩

def move (r : Interval) (d : Int) : Interval := ⟨r.origin+d,r.size⟩

structure Raw where
  border : Interval
  margin : Interval
  containing : Interval
  framePosition : Int
  normal : Int
  portSize : Int
  padding : Int
  parentToScroll : Int
  scroll : Int
  insets : StickyAxis.Insets
  deriving Repr, DecidableEq

def nativeContain (g : Raw) : Interval :=
  let marginNear := g.border.origin - g.margin.origin
  let marginFar := ending g.margin - ending g.border
  let first := deflate g.containing marginNear marginFar
  let second := deflate first 0 g.border.size
  move second (g.framePosition - g.border.origin)

def referenceContain (g : Raw) : Interval :=
  ⟨g.containing.origin + g.framePosition - g.margin.origin,
   max 0 (g.containing.size - g.margin.size)⟩

theorem containment_geometry_refines (g : Raw) (borderNonnegative : 0 ≤ g.border.size) :
    nativeContain g = referenceContain g := by
  simp only [nativeContain, referenceContain, deflate, move, ending]
  congr 1 <;> omega

theorem containment_size_nonnegative (g : Raw) : 0 ≤ (nativeContain g).size := by
  simp only [nativeContain, deflate, move]; omega

def origin (g : Raw) (ignoreScroll : Bool) : Int :=
  (if ignoreScroll then 0 else g.scroll) + g.padding - g.parentToScroll +
    (g.framePosition - g.border.origin)

structure Limits where
  stickNear : Int
  stickFar : Int
  containNear : Int
  containFar : Int
  deriving Repr, DecidableEq

def nativeLimits (g : Raw) (endIsFar ignoreScroll : Bool) (low high : Int) : Limits :=
  let e := StickyAxis.nativeNormalize g.insets g.portSize g.border.size endIsFar
  let c := nativeContain g
  ⟨if g.insets.near.isSome then origin g ignoreScroll + e.near else low,
   if g.insets.far.isSome then origin g ignoreScroll + g.portSize - e.far - g.border.size else high,
   c.origin, ending c⟩

theorem limits_scroll_relation (g : Raw) (endIsFar : Bool) (low high : Int) :
    nativeLimits g endIsFar false low high =
      {nativeLimits g endIsFar true low high with
       stickNear := if g.insets.near.isSome then (nativeLimits g endIsFar true low high).stickNear+g.scroll else low,
       stickFar := if g.insets.far.isSome then (nativeLimits g endIsFar true low high).stickFar+g.scroll else high} := by
  by_cases n : g.insets.near.isSome = true <;> by_cases f : g.insets.far.isSome = true <;>
    simp [nativeLimits,origin,n,f]
  all_goals omega

def referenceLimits (g : Raw) (endIsFar ignoreScroll : Bool) (low high : Int) : Limits :=
  let e := StickyAxis.referenceNormalize g.insets g.portSize g.border.size endIsFar
  let c := referenceContain g
  let constraints := StickyAxis.movementEdges g.insets e (origin g ignoreScroll) g.portSize g.border.size
  ⟨constraints.1.getD low, constraints.2.getD high, c.origin, ending c⟩

theorem full_axis_limits_refine (g : Raw) (endIsFar ignoreScroll : Bool) (low high : Int)
    (borderNonnegative : 0 ≤ g.border.size) :
    nativeLimits g endIsFar ignoreScroll low high = referenceLimits g endIsFar ignoreScroll low high := by
  simp only [nativeLimits,referenceLimits,StickyAxis.normalization_refines,
    containment_geometry_refines g borderNonnegative,StickyAxis.movementEdges]
  cases h : g.insets.near <;> cases j : g.insets.far <;> simp

def position (normal : Int) (limits : Limits) : Int :=
  StickyPosition.native normal limits.stickNear limits.stickFar limits.containNear limits.containFar

theorem position_pipeline_refines (g : Raw) (endIsFar ignoreScroll : Bool) (low high : Int)
    (borderNonnegative : 0 ≤ g.border.size) :
    position g.normal (nativeLimits g endIsFar ignoreScroll low high) =
      position g.normal (referenceLimits g endIsFar ignoreScroll low high) := by
  rw [full_axis_limits_refine g endIsFar ignoreScroll low high borderNonnegative]

def missingOffsets (low high : Int) : Limits := ⟨low,high,low,high⟩

theorem missing_offsets_identity (normal low high : Int)
    (lo : low ≤ normal) (hi : normal ≤ high) :
    position normal (missingOffsets low high) = normal := by
  exact StickyPosition.inactive_identity normal low high low high lo hi

def continuationPositions (storedNormal : Option Int) (_firstCurrent target : Int)
    (continuations : List (Int × Int)) : List Int :=
  match storedNormal with
  | none => continuations.map Prod.snd
  | some n => continuations.map (fun c => c.1 + (target - n))

theorem missing_normal_no_movement (current target : Int) (xs : List (Int × Int)) :
    continuationPositions none current target xs = xs.map Prod.snd := rfl

theorem all_continuations_same_translation (normal current target : Int)
    (xs : List (Int × Int)) :
    continuationPositions (some normal) current target xs =
      xs.map (fun c => c.1 + (target-normal)) := rfl

theorem continuation_pairwise_distance (a b normal target : Int) :
    (a + (target-normal)) - (b + (target-normal)) = a - b := by omega

theorem oversize_margin_clamps (g : Raw) (borderNonnegative : 0 ≤ g.border.size)
    (oversize : g.containing.size ≤ g.margin.size) :
    (nativeContain g).size = 0 := by
  rw [containment_geometry_refines g borderNonnegative]
  simp only [referenceContain]; omega
def reposition (g : Raw) (d : Int) : Raw :=
  {g with border := move g.border d, margin := move g.margin d,
          framePosition := g.framePosition+d}

theorem reposition_containment_invariant (g : Raw) (d : Int) :
    nativeContain (reposition g d) = nativeContain g := by
  simp only [nativeContain,reposition,move,deflate,ending]
  congr 1 <;> omega

theorem reposition_origin_invariant (g : Raw) (d : Int) (ignoreScroll : Bool) :
    origin (reposition g d) ignoreScroll = origin g ignoreScroll := by
  simp only [origin,reposition,move]; omega

theorem reposition_limits_invariant (g : Raw) (d : Int)
    (endIsFar ignoreScroll : Bool) (low high : Int) :
    nativeLimits (reposition g d) endIsFar ignoreScroll low high =
      nativeLimits g endIsFar ignoreScroll low high := by
  unfold nativeLimits
  rw [reposition_containment_invariant,reposition_origin_invariant]
  rfl
end StickyGeometry
