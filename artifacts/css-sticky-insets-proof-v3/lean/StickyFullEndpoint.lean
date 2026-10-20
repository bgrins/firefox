import StickyEndpointCaller
namespace StickyFullEndpoint
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

theorem core_pair_refines (f : Frame2) (h : CoreSafe f) : machineCore f = mathCore f := by
  unfold machineCore mathCore
  rw [StickyMachineGeometry.machine_fields_refine _ h.1,
    StickyMachineGeometry.machine_fields_refine _ h.2]
  simp only [coreCodes,StickyMachineGeometry.complete_expression_limits]

def shiftCodes (f : Frame2) : Expr × Expr :=
  (.subtract (.literal f.currentX) (.literal f.normalX),
   .subtract (.literal f.currentY) (.literal f.normalY))

def ShiftSafe (f : Frame2) : Prop := Admitted (shiftCodes f).1 ∧ Admitted (shiftCodes f).2
instance (f : Frame2) : Decidable (ShiftSafe f) := by unfold ShiftSafe; infer_instance

def machineShift (f : Frame2) : Int × Int :=
  (machineEvaluate (shiftCodes f).1,machineEvaluate (shiftCodes f).2)
def mathShift (f : Frame2) : Int × Int := (f.currentX-f.normalX,f.currentY-f.normalY)

theorem shift_pair_refines (f : Frame2) (h : ShiftSafe f) : machineShift f = mathShift f := by
  unfold machineShift
  rw [admitted_arithmetic_refines _ h.1,admitted_arithmetic_refines _ h.2]
  rfl

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

theorem range_from_full_core (xAxis : Bool) (f : Frame2)
    (h : entersCore xAxis f = true) :
    machineSelectedRanges xAxis f =
      machineRanges (selectedRaw xAxis f) f.hasOffsets (selectedEnd xAxis f) := by
  have pair : f.hasOffsets = true ∧ StickyAxis.active (selectedRaw xAxis f).insets = true := by simpa [entersCore] using h
  have hh := pair.1
  have ha := pair.2
  unfold machineSelectedRanges machineRanges
  simp only [hh,ha,Bool.not_true,Bool.false_eq_true,↓reduceIte]
  cases xAxis <;> rfl

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

theorem selected_pair_refines (xAxis : Bool) (f : Frame2) (h : SelectedSafe xAxis f) :
    machineSelected xAxis f = mathSelected xAxis f := by
  unfold machineSelected mathSelected
  split
  · rename_i active
    obtain ⟨hc,hr,hs⟩ := h active
    rw [core_pair_refines f hc]
    have rangesEqual : machineSelectedRanges xAxis f = ranges xAxis f := by
      rw [range_from_full_core _ _ active]
      exact ranges_machine_refine _ _ _ hr
    rw [rangesEqual]
    unfold withRanges
    split
    · rename_i live
      rw [shift_pair_refines f (hs live)]
    · rfl
  · rfl

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

theorem complete_entry_refines (container xAxis : Bool) (frames : List Frame2)
    (safe : EntrySafe2 container xAxis frames) :
    machineEntry container xAxis frames = mathEntry container xAxis frames := by
  cases hc : container
  · rfl
  · unfold machineEntry mathEntry
    simp only [↓reduceIte]
    unfold EntrySafe2 at safe
    cases hs : nativeScan eligible2 none frames with
    | absent => rfl
    | multiple => rfl
    | one f => exact selected_pair_refines xAxis f (by simpa [hc,hs] using safe)

def selectionMap (f : α → β) : Selection α → Selection β
  | .absent => .absent
  | .multiple => .multiple
  | .one x => .one (f x)

theorem scan_projects (xAxis : Bool) (frames : List Frame2) (found : Option Frame2) :
    nativeScan eligible (found.map (project xAxis)) (frames.map (project xAxis)) =
      selectionMap (project xAxis) (nativeScan eligible2 found frames) := by
  induction frames generalizing found with
  | nil => cases found <;> rfl
  | cons f fs ih =>
    have he : eligible (project xAxis f) = eligible2 f := rfl
    simp only [List.map_cons,nativeScan,he]
    split
    · cases found <;> simp only [Option.map_none,Option.map_some]
      · exact ih (some f)
      · rfl
    · exact ih found

theorem absent_selected_ranges (xAxis : Bool) (f : Frame2)
    (h : entersCore xAxis f = false) : ranges xAxis f = ⟨none,none⟩ := by
  unfold entersCore at h
  unfold ranges nativeRanges
  cases hh : f.hasOffsets <;> cases ha : StickyAxis.active (selectedRaw xAxis f).insets <;>
    simp_all

theorem selected_displacement (xAxis : Bool) (f : Frame2) :
    (mathSelected xAxis f).displacement = pack (project xAxis f) (ranges xAxis f) := by
  unfold mathSelected
  split
  · unfold withRanges pack hasRange
    cases hn : (ranges xAxis f).near <;> cases hf : (ranges xAxis f).far <;>
      cases xAxis <;> rfl
  · rename_i h
    have no : entersCore xAxis f = false := by simpa using h
    rw [absent_selected_ranges _ _ no]
    rfl

theorem full_displacement_projection (container xAxis : Bool) (frames : List Frame2) :
    (mathEntry container xAxis frames).displacement =
      nativeTimeline container (frames.map (project xAxis)) := by
  cases container
  · rfl
  · unfold mathEntry nativeTimeline
    simp only [Bool.not_true,Bool.false_eq_true,↓reduceIte]
    have mapped := scan_projects xAxis frames none
    simp only [Option.map_none] at mapped
    rw [mapped]
    cases hs : nativeScan eligible2 none frames with
    | absent => rfl
    | multiple => rfl
    | one f => exact selected_displacement xAxis f

def fullCaller2 (container xAxis early : Bool) (offset : Int) (frames : List Frame2) : Expr :=
  caller early offset (machineEntry container xAxis frames).displacement

theorem complete_two_axis_caller (container xAxis early : Bool) (offset : Int) (frames : List Frame2)
    (geometry : ∀ f ∈ frames, 0 ≤ f.x.border.size ∧ 0 ≤ f.y.border.size)
    (entry : EntrySafe2 container xAxis frames)
    (endpoint : CallerSafe early offset (nativeTimeline container (frames.map (project xAxis)))) :
    machineEntry container xAxis frames = mathEntry container xAxis frames ∧
    machineEvaluate (fullCaller2 container xAxis early offset frames) =
      expected container xAxis early offset frames := by
  refine ⟨complete_entry_refines container xAxis frames entry,?_⟩
  unfold fullCaller2
  rw [complete_entry_refines container xAxis frames entry,full_displacement_projection]
  exact complete_axis_caller container xAxis early offset frames geometry endpoint

end StickyFullEndpoint
