import StickyConsumers
namespace StickyPipeline
open StickyGeometry StickyWritingMode StickyNumeric

structure TwoAxes where
  x : Raw
  y : Raw
  hasOffsets : Bool
  mode : Mode
  rtl : Bool
  orientation : Orientation
  deriving Repr, DecidableEq

def sourceEnd (g : TwoAxes) (a : Axis) : Bool :=
  isFar (selectedEnd (flags g.mode g.rtl g.orientation) a)
def specEnd (g : TwoAxes) (a : Axis) : Bool :=
  isFar (referenceEnd g.mode g.rtl g.orientation a)

def geometricChoice (n : Int) (l : Limits) : Int :=
  if l.containNear ≤ n ∧ n ≤ l.containFar ∧
      max l.stickNear l.containNear ≤ min l.stickFar l.containFar then
    StickyPosition.project n (max l.stickNear l.containNear) (min l.stickFar l.containFar)
  else StickyPosition.native n l.stickNear l.stickFar l.containNear l.containFar

theorem choice_refines (n : Int) (l : Limits) : position n l = geometricChoice n l := by
  unfold geometricChoice
  split
  · rename_i h
    exact StickyPosition.feasible_intersection_projection n l.stickNear l.stickFar l.containNear l.containFar h.1 h.2.1 h.2.2
  · rfl

def nativePositions (g : TwoAxes) (ignoreScroll : Bool) : Int × Int :=
  (position g.x.normal (StickyConsumers.selectedLimits g.x g.hasOffsets (sourceEnd g .x) ignoreScroll),
   position g.y.normal (StickyConsumers.selectedLimits g.y g.hasOffsets (sourceEnd g .y) ignoreScroll))

def referencePositions (g : TwoAxes) (ignoreScroll : Bool) : Int × Int :=
  (geometricChoice g.x.normal (StickyConsumers.specifiedLimits g.x g.hasOffsets (specEnd g .x) ignoreScroll),
   geometricChoice g.y.normal (StickyConsumers.specifiedLimits g.y g.hasOffsets (specEnd g .y) ignoreScroll))

theorem complete_two_axis_refinement (g : TwoAxes) (ignoreScroll : Bool)
    (xNonnegative : 0 ≤ g.x.border.size) (yNonnegative : 0 ≤ g.y.border.size) :
    nativePositions g ignoreScroll = referencePositions g ignoreScroll := by
  unfold nativePositions referencePositions sourceEnd specEnd
  rw [end_selection_refines,end_selection_refines,
    StickyConsumers.optional_limits_refine g.x g.hasOffsets _ ignoreScroll xNonnegative,
    StickyConsumers.optional_limits_refine g.y g.hasOffsets _ ignoreScroll yNonnegative,
    choice_refines,choice_refines]

theorem absent_offsets_normal (g : TwoAxes) (ignoreScroll : Bool)
    (absent : g.hasOffsets = false)
    (xl : sentinelLow ≤ g.x.normal) (xh : g.x.normal ≤ sentinelHigh)
    (yl : sentinelLow ≤ g.y.normal) (yh : g.y.normal ≤ sentinelHigh) :
    nativePositions g ignoreScroll = (g.x.normal,g.y.normal) := by
  simp only [nativePositions,StickyConsumers.selectedLimits,absent,Bool.false_eq_true,↓reduceIte]
  rw [missing_offsets_identity g.x.normal sentinelLow sentinelHigh xl xh,
      missing_offsets_identity g.y.normal sentinelLow sentinelHigh yl yh]

theorem both_auto_normal (g : Raw) (endIsFar ignoreScroll : Bool)
    (nearAbsent : g.insets.near = none) (farAbsent : g.insets.far = none)
    (lo : sentinelLow ≤ g.normal) (hi : g.normal ≤ sentinelHigh) :
    position g.normal (nativeLimits g endIsFar ignoreScroll sentinelLow sentinelHigh) = g.normal := by
  simp only [nativeLimits,nearAbsent,farAbsent,Option.isSome_none,Bool.false_eq_true,↓reduceIte,position]
  exact StickyPosition.inactive_identity g.normal _ _ sentinelLow sentinelHigh lo hi

theorem first_frame_dispatch_with_modes (g : TwoAxes) (xFrames yFrames : List StickyContinuations.Frame)
    (_sameFrames : xFrames.map StickyContinuations.Frame.identity = yFrames.map StickyContinuations.Frame.identity)
    (xNonnegative : 0 ≤ g.x.border.size) (yNonnegative : 0 ≤ g.y.border.size) :
    StickyContinuations.nativeDispatch (nativePositions g false).1 xFrames =
      StickyContinuations.referenceDispatch (referencePositions g false).1 xFrames ∧
    StickyContinuations.nativeDispatch (nativePositions g false).2 yFrames =
      StickyContinuations.referenceDispatch (referencePositions g false).2 yFrames := by
  rw [complete_two_axis_refinement g false xNonnegative yNonnegative,
      StickyContinuations.complete_dispatch_refines,
      StickyContinuations.complete_dispatch_refines]
  exact ⟨rfl,rfl⟩

end StickyPipeline
