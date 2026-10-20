import WideWitnesses
import Lean.Data.Json
open StickyNumeric StickyGeometry StickyWritingMode WideCallers Lean

def jint (n : Int) : Json := toJson n
def jlist (n : List Int) : Json := toJson n
def jbool (b : Bool) : Json := toJson b
def jbox (b : StickyAbsolute.Box) : Json := jlist [b.left,b.top,b.right,b.bottom]
def jranges (r : StickyConsumers.AxisRanges) : Json :=
  let item := fun (r : Option StickyRanges.Range) => match r with
    | none => Json.null | some r => jlist [r.atScroll,r.maxOffset]
  Json.arr #[item r.near,item r.far]
def jlimits (f : Frame) (i : Bool) : Json :=
  let x := specified f .x i
  let y := specified f .y i
  let c := containRect f
  Json.arr #[jlist [x.stickNear,y.stickNear,x.stickFar,y.stickFar],jlist [c.x,c.y,c.width,c.height]]

def oldAxisSafe (f : Frame) (a : Axis) (i : Bool) : Prop :=
  if f.axes.hasOffsets then
    let g := raw f a
    let n := WideNormalization.rawValue f.modern g.insets.near
    let e := WideNormalization.rawValue f.modern g.insets.far
    (if WideNormalization.active f.modern g.insets then
      Admitted (if sourceEnd f a then WideNormalization.oldEndExpression g.portSize g.border.size n e
       else WideNormalization.oldEndExpression g.portSize g.border.size e n) else True) ∧
    WideGeometry.LegacyStorageSafe g.insets.near.isSome g.insets.far.isSome
      (selected f a i).stickNear (selected f a i).stickFar
  else True
instance (f : Frame) (a : Axis) (i : Bool) : Decidable (oldAxisSafe f a i) := by
  unfold oldAxisSafe; infer_instance

def row (id : Nat) (f : Frame) (p : WideProviders.Preparation) : Json :=
  let ranges := rangeReference (stickBox (specified f .x false) (specified f .y false))
    (containRect f) f.axes.x.normal f.axes.y.normal
  let common := decide (PositionSafe f false ∧ PositionSafe f true ∧ TranslationSafe f ∧
    AbsoluteSafe f ∧ WideAxisRanges.Safe f .x ∧ WideAxisRanges.Safe f .y)
  let debug := decide (WideAxisRanges.DebugSafe f .x ∧ WideAxisRanges.DebugSafe f .y)
  let old := decide (oldAxisSafe f .x false ∧ oldAxisSafe f .y false ∧ oldAxisSafe f .x true ∧ oldAxisSafe f .y true)
  Json.mkObj [
    ("preparation_safe",jbool (decide (WideProviders.EnteredPaddingSafe p f))),
    ("preparation_match",jbool (decide (WideProviders.prepared p f = f))),
    ("sizes_valid",jbool (decide (0 ≤ f.axes.x.border.size ∧ 0 ≤ f.axes.y.border.size))),
    ("id",toJson id),("safe",jbool common),("debug",jbool debug),("old_safe",jbool old),
    ("current",jlimits f false),("ignoring",jlimits f true),
    ("position",jlist [referencePosition f .x false,referencePosition f .y false]),
    ("zero",jlist [referencePosition f .x true,referencePosition f .y true]),
    ("translation",jlist [referencePosition f .x true-f.axes.x.normal,referencePosition f .y true-f.axes.y.normal]),
    ("range_x",jranges (WideAxisRanges.referenceWith f .x (specified f .x true))),
    ("range_y",jranges (WideAxisRanges.referenceWith f .y (specified f .y true))),
    ("outer",jbox ranges.1),("inner",jbox ranges.2)]
