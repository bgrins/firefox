import WideAxisRanges
namespace WideProviders
open StickyNumeric StickyGeometry WideCallers StickyWritingMode

structure Preparation where
  scrolled : Bool
  overflowX : Interval
  overflowY : Interval
  padLeft : Int
  padRight : Int
  padTop : Int
  padBottom : Int
  transformedX : Interval
  transformedY : Interval
  unionX : Interval
  unionY : Interval

def prepared (p : Preparation) (f : Frame) : Frame :=
  {f with axes := {f.axes with
    x := {f.axes.x with containing := if p.scrolled then p.transformedX else p.unionX},
    y := {f.axes.y with containing := if p.scrolled then p.transformedY else p.unionY}}}

def PaddingSafe (p : Preparation) : Prop :=
  WideGeometry.PreparationSafe p.scrolled p.overflowX p.padLeft p.padRight ∧
  WideGeometry.PreparationSafe p.scrolled p.overflowY p.padTop p.padBottom
instance (p : Preparation) : Decidable (PaddingSafe p) := by unfold PaddingSafe; infer_instance

def EnteredPaddingSafe (p : Preparation) (f : Frame) : Prop :=
  if f.axes.hasOffsets then PaddingSafe p else True
instance (p : Preparation) (f : Frame) : Decidable (EnteredPaddingSafe p f) := by
  unfold EnteredPaddingSafe; infer_instance

theorem both_padding_components (p : Preparation) (h : PaddingSafe p) (enabled : p.scrolled = true) :
    (machineEvaluate (.add (.literal p.overflowX.origin) (.literal p.padLeft)),
     machineEvaluate (.greater (.literal 0) (.subtract (.literal p.overflowX.size)
       (.add (.literal p.padLeft) (.literal p.padRight))))) =
      ((deflate p.overflowX p.padLeft p.padRight).origin,(deflate p.overflowX p.padLeft p.padRight).size) ∧
    (machineEvaluate (.add (.literal p.overflowY.origin) (.literal p.padTop)),
     machineEvaluate (.greater (.literal 0) (.subtract (.literal p.overflowY.size)
       (.add (.literal p.padTop) (.literal p.padBottom))))) =
      ((deflate p.overflowY p.padTop p.padBottom).origin,(deflate p.overflowY p.padTop p.padBottom).size) := by
  simp only [PaddingSafe,enabled] at h
  exact ⟨WideGeometry.local_padding_deflate_exact _ _ _ h.1,
    WideGeometry.local_padding_deflate_exact _ _ _ h.2⟩

structure CallDomain (p : Preparation) (f : Frame) : Prop where
  padding : EnteredPaddingSafe p f
  current : PositionSafe (prepared p f) false
  ignoring : PositionSafe (prepared p f) true
  translation : TranslationSafe (prepared p f)
  absolute : AbsoluteSafe (prepared p f)
  horizontal : WideAxisRanges.Safe (prepared p f) .x
  vertical : WideAxisRanges.Safe (prepared p f) .y
  xSize : 0 ≤ f.axes.x.border.size
  ySize : 0 ≤ f.axes.y.border.size

theorem prepared_positions (p : Preparation) (f : Frame) (h : CallDomain p f) :
    (machinePosition (prepared p f) .x false,machinePosition (prepared p f) .y false) =
      (referencePosition (prepared p f) .x false,referencePosition (prepared p f) .y false) ∧
    (machinePosition (prepared p f) .x true,machinePosition (prepared p f) .y true) =
      (referencePosition (prepared p f) .x true,referencePosition (prepared p f) .y true) :=
  ⟨both_positions _ false h.current h.xSize h.ySize,
    both_positions _ true h.ignoring h.xSize h.ySize⟩

theorem prepared_absolute (p : Preparation) (f : Frame) (h : CallDomain p f) :
    machineRanges (prepared p f) = rangeReference
      (stickBox (specified (prepared p f) .x false) (specified (prepared p f) .y false))
      (containRect (prepared p f)) f.axes.x.normal f.axes.y.normal :=
  complete_absolute_caller _ h.absolute h.xSize h.ySize

theorem prepared_axis_callers (p : Preparation) (f : Frame) (h : CallDomain p f) :
    WideAxisRanges.caller (prepared p f) .x =
      WideAxisRanges.referenceWith (prepared p f) .x (specified (prepared p f) .x true) ∧
    WideAxisRanges.caller (prepared p f) .y =
      WideAxisRanges.referenceWith (prepared p f) .y (specified (prepared p f) .y true) :=
  ⟨WideAxisRanges.complete_axis_caller _ .x h.horizontal h.xSize,
   WideAxisRanges.complete_axis_caller _ .y h.vertical h.ySize⟩

end WideProviders
