import StickyEndpointCaller
namespace FullEntryMutant
open StickyNumeric StickyGeometry StickyConsumers StickyRanges StickyEndpoints StickyEndpointCaller

def eligible2 (f : Frame2) : Bool := f.sticky && f.sameContainer

def choose (xAxis : Bool) (p : α × α) : α := if xAxis then p.1 else p.2

def selectedRaw (xAxis : Bool) (f : Frame2) : Raw := if xAxis then f.x else f.y
def selectedEnd (xAxis : Bool) (f : Frame2) : Bool := if xAxis then f.xEndFar else f.yEndFar

def entersCore (xAxis : Bool) (f : Frame2) : Bool :=
  f.hasOffsets && StickyAxis.active (selectedRaw xAxis f).insets

def coreCodes (f : Frame2) :=
  (StickyMachineGeometry.construct f.x f.xEndFar true,
   StickyMachineGeometry.construct f.y f.yEndFar true)

def CoreSafe (f : Frame2) : Prop :=
  StickyMachineGeometry.ArithmeticSafe (coreCodes f).1 ∧
  StickyMachineGeometry.ArithmeticSafe (coreCodes f).2

instance (f : Frame2) : Decidable (CoreSafe f) := by unfold CoreSafe; infer_instance

def machineCore (f : Frame2) : Limits × Limits :=
  (StickyMachineGeometry.machineFields (coreCodes f).1,
   StickyMachineGeometry.machineFields (coreCodes f).2)

def mathCore (f : Frame2) : Limits × Limits :=
  (nativeLimits f.x f.xEndFar true sentinelLow sentinelHigh,
   nativeLimits f.y f.yEndFar true sentinelLow sentinelHigh)

def shiftCodes (f : Frame2) : Expr × Expr :=
  (.subtract (.literal f.currentX) (.literal f.normalX),
   .subtract (.literal f.currentY) (.literal f.normalY))

def ShiftSafe (f : Frame2) : Prop := Admitted (shiftCodes f).1 ∧ Admitted (shiftCodes f).2
instance (f : Frame2) : Decidable (ShiftSafe f) := by unfold ShiftSafe; infer_instance

def machineShift (f : Frame2) : Int × Int :=
  (machineEvaluate (shiftCodes f).1,machineEvaluate (shiftCodes f).2)
def mathShift (f : Frame2) : Int × Int := (f.currentX-f.normalX,f.currentY-f.normalY)

def hasRange (r : AxisRanges) : Bool := r.near.isSome || r.far.isSome

def ranges (xAxis : Bool) (f : Frame2) : AxisRanges :=
  nativeRanges (selectedRaw xAxis f) f.hasOffsets (selectedEnd xAxis f)

def rangesFromCore (g : Raw) (l : Limits) : AxisRanges :=
  let code := fun near => StickyMachineGeometry.rangeExpr (.literal g.normal)
    (.literal (if near then l.stickNear else l.stickFar))
    (.literal (if near then l.containFar else l.containNear)) near
  let n := if g.insets.near.isSome then some (evalRange (code true)) else none
  let f := if g.insets.far.isSome then some (evalRange (code false)) else none
  match n,f with
  | some a,some b => if b.atScroll > a.atScroll then ⟨none,none⟩ else ⟨n,f⟩
  | _,_ => ⟨n,f⟩

def machineSelectedRanges (xAxis : Bool) (f : Frame2) : AxisRanges :=
  rangesFromCore (selectedRaw xAxis f) (choose xAxis (machineCore f))

structure Observation where
  core : Option (Limits × Limits)
  shift : Option (Int × Int)
  displacement : Option Displacement
  deriving Repr, DecidableEq

def absent : Observation := ⟨none,none,none⟩

def withRanges (xAxis : Bool) (f : Frame2) (c : Limits × Limits)
    (r : AxisRanges) (s : Unit → Int × Int) : Observation :=
  if hasRange r then
    ⟨some c,some (s ()),some ⟨f.identity,choose xAxis (s ()),r.near.getD ⟨0,0⟩,r.far.getD ⟨0,0⟩⟩⟩
  else ⟨some c,none,none⟩

def machineSelected (xAxis : Bool) (f : Frame2) : Observation :=
  if entersCore xAxis f then
    withRanges xAxis f (machineCore f) (machineSelectedRanges xAxis f) (fun _ => machineShift f)
  else absent

def mathSelected (xAxis : Bool) (f : Frame2) : Observation :=
  if entersCore xAxis f then
    withRanges xAxis f (mathCore f) (ranges xAxis f) (fun _ => mathShift f)
  else absent

def SelectedSafe (xAxis : Bool) (f : Frame2) : Prop :=
  entersCore xAxis f = true →
    CoreSafe f ∧ RangeSafe (selectedRaw xAxis f) f.hasOffsets (selectedEnd xAxis f) ∧
    (hasRange (ranges xAxis f) = true → ShiftSafe f)
instance (a : Bool) (f : Frame2) : Decidable (SelectedSafe a f) := by
  unfold SelectedSafe; infer_instance

def machineEntry (container xAxis : Bool) (frames : List Frame2) : Observation :=
  if container then
    match nativeScan eligible2 none frames with
    | .one f => machineSelected xAxis f
    | _ => absent
  else absent

def mathEntry (container xAxis : Bool) (frames : List Frame2) : Observation :=
  if container then
    match nativeScan eligible2 none frames with
    | .one f => mathSelected xAxis f
    | _ => absent
  else absent

def EntrySafe2 (container xAxis : Bool) (frames : List Frame2) : Prop :=
  if container then
    match nativeScan eligible2 none frames with
    | .one f => SelectedSafe xAxis f
    | _ => True
  else True
instance (c a : Bool) (fs : List Frame2) : Decidable (EntrySafe2 c a fs) := by
  unfold EntrySafe2
  cases c
  · exact isTrue trivial
  · cases nativeScan eligible2 none fs <;> infer_instance

def selectionMap (f : α → β) : Selection α → Selection β
  | .absent => .absent
  | .multiple => .multiple
  | .one x => .one (f x)

def fullCaller2 (container xAxis early : Bool) (offset : Int) (frames : List Frame2) : Expr :=
  caller early offset (machineEntry container xAxis frames).displacement

end FullEntryMutant
