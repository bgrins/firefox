import WideGeometry
import StickyAbsolute

namespace WideCallers
open StickyNumeric StickyGeometry StickyWritingMode StickyAbsolute

structure Frame where
  axes : StickyPipeline.TwoAxes
  modern : Bool
  deriving Repr, DecidableEq

def sourceEnd (f : Frame) (a : Axis) : Bool :=
  if f.modern then StickyPipeline.sourceEnd f.axes a
  else match a with | .x => !f.axes.rtl | .y => true

def specEnd (f : Frame) (a : Axis) : Bool :=
  if f.modern then StickyPipeline.specEnd f.axes a
  else match a with | .x => !f.axes.rtl | .y => true

theorem mode_mapping (f : Frame) (a : Axis) : sourceEnd f a = specEnd f a := by
  unfold sourceEnd specEnd StickyPipeline.sourceEnd StickyPipeline.specEnd
  rw [end_selection_refines]

def raw (f : Frame) : Axis → Raw | .x => f.axes.x | .y => f.axes.y

def selected (f : Frame) (a : Axis) (ignore : Bool) : Limits :=
  if f.axes.hasOffsets then WideGeometry.sourceLimits (raw f a) f.modern (sourceEnd f a) ignore
  else missingOffsets sentinelLow sentinelHigh

def specified (f : Frame) (a : Axis) (ignore : Bool) : Limits :=
  if f.axes.hasOffsets then WideGeometry.referenceLimits (raw f a) f.modern (specEnd f a) ignore
  else missingOffsets sentinelLow sentinelHigh

def machineSelected (f : Frame) (a : Axis) (ignore : Bool) : Limits :=
  if f.axes.hasOffsets then
    WideGeometry.machineFields (WideGeometry.machineConstruct (raw f a) f.modern (sourceEnd f a) ignore)
  else missingOffsets sentinelLow sentinelHigh

def CoreSafe (f : Frame) (ignore : Bool) : Prop :=
  if f.axes.hasOffsets then
    WideGeometry.Safe f.axes.x f.modern (sourceEnd f .x) ignore ∧
    WideGeometry.Safe f.axes.y f.modern (sourceEnd f .y) ignore
  else True

instance (f : Frame) (i : Bool) : Decidable (CoreSafe f i) := by unfold CoreSafe; infer_instance

theorem selected_refines (f : Frame) (a : Axis) (i : Bool)
    (valid : 0 ≤ (raw f a).border.size) : selected f a i = specified f a i := by
  unfold selected specified
  rw [WideGeometry.source_reference _ _ _ _ valid,mode_mapping]

theorem machine_selected_refines (f : Frame) (a : Axis) (i : Bool)
    (safe : CoreSafe f i) (valid : 0 ≤ (raw f a).border.size) :
    machineSelected f a i = specified f a i := by
  unfold machineSelected specified
  split
  · rename_i h
    simp only [CoreSafe,h,↓reduceIte] at safe
    have s : WideGeometry.Safe (raw f a) f.modern (sourceEnd f a) i := by
      cases a
      · exact safe.1
      · exact safe.2
    rw [WideGeometry.complete_machine_limits _ _ _ _ s valid,mode_mapping]
  · rfl

def positionE (n : Int) (l : Limits) (near far : Bool) : Expr :=
  let p := if near then Expr.greater (.literal n) (.lesser (.literal l.stickNear) (.literal l.containFar)) else .literal n
  if far then .lesser p (.greater (.literal l.stickFar) (.literal l.containNear)) else p

def positionReference (n : Int) (l : Limits) (near far : Bool) : Int :=
  let a := min l.stickNear l.containFar
  let b := max l.stickFar l.containNear
  match near,far with
  | false,false => n
  | true,false => max n a
  | false,true => min n b
  | true,true => if b < a then b else max a (min n b)

theorem position_expression (n : Int) (l : Limits) (near far : Bool) :
    evaluate (positionE n l near far) = positionReference n l near far := by
  cases near <;> cases far <;> simp [positionE,positionReference,evaluate] <;> omega

def masks (f : Frame) (a : Axis) : Bool × Bool :=
  if f.modern then
    (f.axes.hasOffsets && (raw f a).insets.near.isSome,
     f.axes.hasOffsets && (raw f a).insets.far.isSome)
  else (true,true)

def position (f : Frame) (a : Axis) (i : Bool) : Expr :=
  positionE (raw f a).normal (selected f a i) (masks f a).1 (masks f a).2

def PositionSafe (f : Frame) (i : Bool) : Prop :=
  CoreSafe f i ∧ Admitted (position f .x i) ∧ Admitted (position f .y i)
instance (f : Frame) (i : Bool) : Decidable (PositionSafe f i) := by unfold PositionSafe; infer_instance

def referencePosition (f : Frame) (a : Axis) (i : Bool) : Int :=
  positionReference (raw f a).normal (specified f a i) (masks f a).1 (masks f a).2

def machinePosition (f : Frame) (a : Axis) (i : Bool) : Int :=
  machineEvaluate (positionE (raw f a).normal (machineSelected f a i) (masks f a).1 (masks f a).2)

theorem complete_position (f : Frame) (a : Axis) (i : Bool)
    (safe : PositionSafe f i) (valid : 0 ≤ (raw f a).border.size) :
    machinePosition f a i = referencePosition f a i := by
  have sa : Admitted (position f a i) := by cases a; exact safe.2.1; exact safe.2.2
  have limits := machine_selected_refines f a i safe.1 valid
  rw [← selected_refines f a i valid] at limits
  unfold machinePosition
  rw [limits]
  change machineEvaluate (position f a i) = _
  rw [admitted_arithmetic_refines _ sa]
  unfold position referencePosition
  rw [position_expression,selected_refines f a i valid]

theorem both_positions (f : Frame) (i : Bool) (safe : PositionSafe f i)
    (x : 0 ≤ f.axes.x.border.size) (y : 0 ≤ f.axes.y.border.size) :
    (machinePosition f .x i,machinePosition f .y i) =
      (referencePosition f .x i,referencePosition f .y i) := by
  rw [complete_position f .x i safe x,complete_position f .y i safe y]

def translation (f : Frame) (a : Axis) : Expr := .subtract (position f a true) (.literal (raw f a).normal)
def TranslationSafe (f : Frame) : Prop :=
  PositionSafe f true ∧ Admitted (translation f .x) ∧ Admitted (translation f .y)
instance (f : Frame) : Decidable (TranslationSafe f) := by unfold TranslationSafe; infer_instance

theorem both_translation_components (f : Frame) (safe : TranslationSafe f)
    (x : 0 ≤ f.axes.x.border.size) (y : 0 ≤ f.axes.y.border.size) :
    (machineEvaluate (translation f .x),machineEvaluate (translation f .y)) =
      (referencePosition f .x true-f.axes.x.normal,referencePosition f .y true-f.axes.y.normal) := by
  rw [admitted_arithmetic_refines _ safe.2.1,admitted_arithmetic_refines _ safe.2.2]
  unfold translation
  simp only [evaluate,position,position_expression,referencePosition,
    selected_refines f .x true x,selected_refines f .y true y]
  rfl

def stickBox (x y : Limits) : Box := ⟨x.stickNear,y.stickNear,x.stickFar,y.stickFar⟩
def containRect (f : Frame) : Rect :=
  if f.axes.hasOffsets then
    let x := nativeContain f.axes.x
    let y := nativeContain f.axes.y
    ⟨x.origin,y.origin,x.size,y.size⟩
  else ⟨sentinelLow,sentinelLow,coordMax,coordMax⟩

def rangeConstruct (s : Box) (c : Rect) (nx ny : Int) : EBox × EBox :=
  let p := edgesE (literalBox s) (fromRectE c) nx ny
  (p.1,finishE p.2 p.1)

def RangeSafe (s : Box) (c : Rect) (nx ny : Int) : Prop :=
  let p := edgesE (literalBox s) (fromRectE c) nx ny
  BoxSafe (literalBox s) ∧ RectInputs c ∧ InMachine nx ∧ InMachine ny ∧
    BoxSafe p.1 ∧ BoxSafe p.2 ∧ BoxSafe (intersectE p.2 p.1) ∧ BoxSafe (finishE p.2 p.1)
instance (s : Box) (c : Rect) (nx ny : Int) : Decidable (RangeSafe s c nx ny) := by
  unfold RangeSafe; infer_instance

def rangeReference (s : Box) (c : Rect) (nx ny : Int) : Box × Box :=
  let p := edges s (fromRect c) nx ny
  (p.1,referenceFinish p.2 p.1)

theorem direct_absolute_expression (s : Box) (c : Rect) (nx ny : Int) :
    (evalBox (rangeConstruct s c nx ny).1,evalBox (rangeConstruct s c nx ny).2) =
    rangeReference s c nx ny := by
  have h := edges_expression (literalBox s) (fromRectE c) nx ny
  rw [from_rect_expression] at h
  have hs : evalBox (literalBox s) = s := by cases s; rfl
  rw [hs] at h
  have h1 := congrArg Prod.fst h
  have h2 := congrArg Prod.snd h
  dsimp only at h1 h2
  simp only [rangeConstruct,finish_expression,rangeReference,h1,h2,finish_refines]

theorem direct_absolute_machine (s : Box) (c : Rect) (nx ny : Int)
    (safe : RangeSafe s c nx ny) :
    (machineBox (rangeConstruct s c nx ny).1,machineBox (rangeConstruct s c nx ny).2) =
    rangeReference s c nx ny := by
  have ho : BoxSafe (rangeConstruct s c nx ny).1 := safe.2.2.2.2.1
  have hi : BoxSafe (rangeConstruct s c nx ny).2 := safe.2.2.2.2.2.2.2
  rw [box_machine _ ho,box_machine _ hi,direct_absolute_expression]

def AbsoluteSafe (f : Frame) : Prop :=
  CoreSafe f false ∧ RangeSafe (stickBox (selected f .x false) (selected f .y false))
    (containRect f) f.axes.x.normal f.axes.y.normal
instance (f : Frame) : Decidable (AbsoluteSafe f) := by unfold AbsoluteSafe; infer_instance

def machineRanges (f : Frame) : Box × Box :=
  let s := stickBox (machineSelected f .x false) (machineSelected f .y false)
  let p := rangeConstruct s (containRect f) f.axes.x.normal f.axes.y.normal
  (machineBox p.1,machineBox p.2)

theorem complete_absolute_caller (f : Frame) (safe : AbsoluteSafe f)
    (x : 0 ≤ f.axes.x.border.size) (y : 0 ≤ f.axes.y.border.size) :
    machineRanges f = rangeReference
      (stickBox (specified f .x false) (specified f .y false)) (containRect f)
      f.axes.x.normal f.axes.y.normal := by
  have hx := machine_selected_refines f .x false safe.1 x
  have hy := machine_selected_refines f .y false safe.1 y
  rw [← selected_refines f .x false x] at hx
  rw [← selected_refines f .y false y] at hy
  unfold machineRanges
  rw [hx,hy,direct_absolute_machine _ _ _ _ safe.2,
      selected_refines f .x false x,selected_refines f .y false y]

def clampStick : Box := ⟨0,-1073741823,0,1073740223⟩
def clampContain : Rect := ⟨0,0,6000,59400⟩
theorem retained_clamp_overflow_rejected :
    ¬ RangeSafe clampStick clampContain 0 12000 ∧
    (edges clampStick (fromRect clampContain) 0 12000).1.bottom -
      (edges clampStick (fromRect clampContain) 0 12000).1.top = 2147541446 := by decide +kernel

theorem wide_extent_requires_no_subtraction :
    RangeSafe ⟨sentinelLow,-1073741823,sentinelHigh,1073747223⟩
      ⟨0,0,6000,59400⟩ 0 12000 ∧
    ¬ InMachine (1073747223-(-1073741823)) := by decide +kernel

end WideCallers
