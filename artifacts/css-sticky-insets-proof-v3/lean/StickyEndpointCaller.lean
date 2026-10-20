import StickyEndpoints
namespace StickyEndpointCaller
open StickyNumeric StickyGeometry StickyConsumers StickyRanges StickyEndpoints

def rangeCode (g : Raw) (endIsFar near : Bool) : Expr × Expr :=
  let l := nativeLimits g endIsFar true sentinelLow sentinelHigh
  StickyMachineGeometry.rangeExpr (.literal g.normal)
    (.literal (if near then l.stickNear else l.stickFar))
    (.literal (if near then l.containFar else l.containNear)) near

def RangeSafe (g : Raw) (has endIsFar : Bool) : Prop :=
  has = true →
    (StickyAxis.active g.insets = true → StickyMachineGeometry.ArithmeticSafe (StickyMachineGeometry.construct g endIsFar true)) ∧
    (g.insets.near.isSome = true → Admitted (rangeCode g endIsFar true).1 ∧ Admitted (rangeCode g endIsFar true).2) ∧
    (g.insets.far.isSome = true → Admitted (rangeCode g endIsFar false).1 ∧ Admitted (rangeCode g endIsFar false).2)

instance (g : Raw) (has endIsFar : Bool) : Decidable (RangeSafe g has endIsFar) := by unfold RangeSafe; infer_instance

def evalRange (code : Expr × Expr) : Range := ⟨machineEvaluate code.1,machineEvaluate code.2⟩

def machineRangeCode (g : Raw) (endIsFar near : Bool) : Expr × Expr :=
  let l := StickyMachineGeometry.machineFields (StickyMachineGeometry.construct g endIsFar true)
  StickyMachineGeometry.rangeExpr (.literal g.normal)
    (.literal (if near then l.stickNear else l.stickFar))
    (.literal (if near then l.containFar else l.containNear)) near

theorem range_core_join (g : Raw) (endIsFar near : Bool)
    (safe : StickyMachineGeometry.ArithmeticSafe (StickyMachineGeometry.construct g endIsFar true)) :
    machineRangeCode g endIsFar near = rangeCode g endIsFar near := by
  unfold machineRangeCode rangeCode
  rw [StickyMachineGeometry.machine_fields_refine _ safe,StickyMachineGeometry.complete_expression_limits]

def machineRanges (g : Raw) (has endIsFar : Bool) : AxisRanges :=
  if !has then ⟨none,none⟩ else
  if !StickyAxis.active g.insets then ⟨none,none⟩ else
  let n := if g.insets.near.isSome then some (evalRange (machineRangeCode g endIsFar true)) else none
  let f := if g.insets.far.isSome then some (evalRange (machineRangeCode g endIsFar false)) else none
  match n,f with
  | some a,some b => if b.atScroll > a.atScroll then ⟨none,none⟩ else ⟨n,f⟩
  | _,_ => ⟨n,f⟩

theorem range_code_refines (g : Raw) (endIsFar near : Bool)
    (safe : Admitted (rangeCode g endIsFar near).1 ∧ Admitted (rangeCode g endIsFar near).2) :
    evalRange (rangeCode g endIsFar near) =
      let l := nativeLimits g endIsFar true sentinelLow sentinelHigh
      if near then nearRange g.normal l.stickNear l.containFar else farRange g.normal l.stickFar l.containNear := by
  have h := StickyMachineGeometry.machine_range_refines (.literal g.normal)
    (.literal (if near then (nativeLimits g endIsFar true sentinelLow sentinelHigh).stickNear else (nativeLimits g endIsFar true sentinelLow sentinelHigh).stickFar))
    (.literal (if near then (nativeLimits g endIsFar true sentinelLow sentinelHigh).containFar else (nativeLimits g endIsFar true sentinelLow sentinelHigh).containNear)) near safe.1 safe.2
  have h1 := congrArg Prod.fst h
  have h2 := congrArg Prod.snd h
  dsimp only at h1 h2
  unfold evalRange rangeCode
  rw [h1,h2]
  cases near <;> rfl

theorem ranges_machine_refine (g : Raw) (has endIsFar : Bool) (safe : RangeSafe g has endIsFar) :
    machineRanges g has endIsFar = nativeRanges g has endIsFar := by
  cases hh : has
  · simp [machineRanges,nativeRanges,hh]
  · have hn := (safe hh).2.1
    have hf := (safe hh).2.2
    unfold machineRanges nativeRanges
    simp only [Bool.not_true,Bool.false_eq_true,↓reduceIte]
    split
    · rfl
    · rename_i active
      have ha : StickyAxis.active g.insets = true := by simpa using active
      rw [range_core_join g endIsFar true ((safe hh).1 ha),range_core_join g endIsFar false ((safe hh).1 ha)]
      by_cases n : g.insets.near.isSome = true <;> by_cases f : g.insets.far.isSome = true
      all_goals simp only [n,f,↓reduceIte]
      · rw [range_code_refines g endIsFar true (hn n),range_code_refines g endIsFar false (hf f)]
        rfl
      · rw [range_code_refines g endIsFar true (hn n)]
        rfl
      · rw [range_code_refines g endIsFar false (hf f)]
        rfl
      · rfl

def shiftCode (f : Ancestor) : Expr := .subtract (.literal f.current) (.literal f.normal)
def machinePack (f : Ancestor) (ranges : AxisRanges) : Option Displacement :=
  if ranges.near.isNone && ranges.far.isNone then none
  else some ⟨f.identity,machineEvaluate (shiftCode f),ranges.near.getD ⟨0,0⟩,ranges.far.getD ⟨0,0⟩⟩

def machineTimeline (container : Bool) (ancestors : List Ancestor) : Option Displacement :=
  if !container then none else
  match nativeScan eligible none ancestors with
  | .one f => machinePack f (machineRanges f.firstGeometry f.hasOffsets f.endIsFar)
  | _ => none

def EntrySafe (container : Bool) (ancestors : List Ancestor) : Prop :=
  if container then
    match nativeScan eligible none ancestors with
    | .one f => RangeSafe f.firstGeometry f.hasOffsets f.endIsFar ∧
        ((nativeRanges f.firstGeometry f.hasOffsets f.endIsFar).near.isSome = true ∨
         (nativeRanges f.firstGeometry f.hasOffsets f.endIsFar).far.isSome = true → Admitted (shiftCode f))
    | _ => True
  else True

instance (c : Bool) (a : List Ancestor) : Decidable (EntrySafe c a) := by
  unfold EntrySafe
  cases c
  · exact isTrue trivial
  · cases nativeScan eligible none a <;> infer_instance

theorem pack_machine (f : Ancestor) (ranges : AxisRanges)
    (safe : ranges.near.isSome = true ∨ ranges.far.isSome = true → Admitted (shiftCode f)) :
    machinePack f ranges = pack f ranges := by
  unfold machinePack pack
  split
  · rfl
  · rename_i h
    have live : ranges.near.isSome = true ∨ ranges.far.isSome = true := by
      cases hn : ranges.near <;> cases hf : ranges.far <;> simp_all
    rw [admitted_arithmetic_refines _ (safe live)]
    rfl

theorem selected_machine_refines (container : Bool) (ancestors : List Ancestor)
    (safe : EntrySafe container ancestors) : machineTimeline container ancestors = nativeTimeline container ancestors := by
  cases hc : container
  · simp [machineTimeline,nativeTimeline,hc]
  · simp only [EntrySafe,hc,↓reduceIte] at safe
    unfold machineTimeline nativeTimeline
    simp only [Bool.not_true,Bool.false_eq_true,↓reduceIte]
    cases hs : nativeScan eligible none ancestors with
    | absent => rfl
    | multiple => rfl
    | one f =>
      simp only [hs] at safe
      dsimp only
      rw [ranges_machine_refine _ _ _ safe.1,pack_machine _ _ safe.2]

def fullCaller (container xAxis early : Bool) (offset : Int) (frames : List Frame2) : Expr :=
  caller early offset (machineTimeline container (frames.map (project xAxis)))

theorem complete_machine_axis_caller (container xAxis early : Bool) (offset : Int) (frames : List Frame2)
    (geometry : ∀ f ∈ frames, 0 ≤ f.x.border.size ∧ 0 ≤ f.y.border.size)
    (entry : EntrySafe container (frames.map (project xAxis)))
    (endpoint : CallerSafe early offset (nativeTimeline container (frames.map (project xAxis)))) :
    machineEvaluate (fullCaller container xAxis early offset frames) = expected container xAxis early offset frames := by
  unfold fullCaller
  rw [selected_machine_refines _ _ entry]
  exact complete_axis_caller container xAxis early offset frames geometry endpoint

theorem entry_domain_inhabited :
    EntrySafe true ([sampleFrame].map (project true)) ∧
    EntrySafe true ([sampleFrame].map (project false)) := by
  decide +kernel

end StickyEndpointCaller
