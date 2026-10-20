import StickyAbsolute
namespace StickyEndpoints
open StickyNumeric StickyConsumers StickyRanges

def nonzero (x yes no : Expr) : Expr := .ifLess x (.literal 0) yes (.ifLess (.literal 0) x yes no)

theorem nonzero_evaluate (x yes no : Expr) :
    evaluate (nonzero x yes no) = if evaluate x ≠ 0 then evaluate yes else evaluate no := by
  simp only [nonzero,evaluate]
  repeat' split
  all_goals omega

def construct (early : Bool) (offset : Int) (d : Displacement) : Expr :=
  let x := Expr.literal offset
  let endMax := Expr.literal d.far.maxOffset
  let startMax := Expr.literal d.near.maxOffset
  let add := Expr.add x startMax
  let sub := Expr.subtract x endMax
  let startBranch := if early then Expr.ifLess (.literal d.near.atScroll) x add x
    else Expr.ifLess (.literal d.near.atScroll) x add x
  let rest := nonzero startMax startBranch x
  let endBranch := if early then Expr.ifLess (.literal d.far.atScroll) x rest sub
    else Expr.ifLess x (.literal d.far.atScroll) sub rest
  nonzero endMax endBranch rest

def reference (early : Bool) (offset : Int) (d : Displacement) : Int :=
  if early then earliest offset d.far.atScroll d.far.maxOffset d.near.atScroll d.near.maxOffset
  else latest offset d.far.atScroll d.far.maxOffset d.near.atScroll d.near.maxOffset

theorem endpoint_expression (early : Bool) (offset : Int) (d : Displacement) :
    evaluate (construct early offset d) = reference early offset d := by
  cases early <;> simp only [construct,reference,nonzero_evaluate,evaluate,earliest,latest,Bool.false_eq_true,↓reduceIte]
  all_goals repeat' split
  all_goals first | rfl | omega

def Safe (early : Bool) (offset : Int) (d : Displacement) : Prop := Admitted (construct early offset d)
instance (e : Bool) (o : Int) (d : Displacement) : Decidable (Safe e o d) := by unfold Safe; infer_instance

theorem endpoint_machine (early : Bool) (offset : Int) (d : Displacement)
    (safe : Safe early offset d) : machineEvaluate (construct early offset d) = reference early offset d := by
  rw [admitted_arithmetic_refines _ safe,endpoint_expression]

def zeroDisplacement : Displacement := ⟨0,0,⟨0,0⟩,⟨0,0⟩⟩

def caller (early : Bool) (offset : Int) (found : Option Displacement) : Expr :=
  construct early offset (found.getD zeroDisplacement)

def CallerSafe (early : Bool) (offset : Int) (found : Option Displacement) : Prop :=
  Safe early offset (found.getD zeroDisplacement)

instance (e : Bool) (o : Int) (d : Option Displacement) : Decidable (CallerSafe e o d) := by unfold CallerSafe; infer_instance

theorem absent_default_identity (early : Bool) (offset : Int) :
    evaluate (caller early offset none) = offset := by
  rw [show caller early offset none = construct early offset zeroDisplacement from rfl,endpoint_expression]
  cases early <;> simp [reference,zeroDisplacement,earliest,latest]

theorem absent_default_safe (early : Bool) (offset : Int) (safe : InMachine offset) :
    CallerSafe early offset none := by
  cases early <;> simp [CallerSafe,Safe,construct,zeroDisplacement,nonzero,Admitted,evaluate,InMachine,machineMin,machineMax] at * <;> omega

structure Frame2 where
  identity : Nat
  sticky : Bool
  sameContainer : Bool
  x : StickyGeometry.Raw
  y : StickyGeometry.Raw
  hasOffsets : Bool
  xEndFar : Bool
  yEndFar : Bool
  currentX : Int
  currentY : Int
  normalX : Int
  normalY : Int
  deriving Repr, DecidableEq

def project (xAxis : Bool) (f : Frame2) : Ancestor :=
  ⟨f.identity,f.sticky,f.sameContainer,if xAxis then f.x else f.y,f.hasOffsets,
   if xAxis then f.xEndFar else f.yEndFar,if xAxis then f.currentX else f.currentY,
   if xAxis then f.normalX else f.normalY⟩

def scheduled (hasContainer xAxis early : Bool) (offset : Int) (frames : List Frame2) : Expr :=
  caller early offset (nativeTimeline hasContainer (frames.map (project xAxis)))

def expected (hasContainer xAxis early : Bool) (offset : Int) (frames : List Frame2) : Int :=
  reference early offset ((referenceTimeline hasContainer (frames.map (project xAxis))).getD zeroDisplacement)

theorem complete_axis_caller (hasContainer xAxis early : Bool) (offset : Int) (frames : List Frame2)
    (geometry : ∀ f ∈ frames, 0 ≤ f.x.border.size ∧ 0 ≤ f.y.border.size)
    (safe : CallerSafe early offset (nativeTimeline hasContainer (frames.map (project xAxis)))) :
    machineEvaluate (scheduled hasContainer xAxis early offset frames) = expected hasContainer xAxis early offset frames := by
  have valid : ∀ f ∈ frames.map (project xAxis), 0 ≤ f.firstGeometry.border.size := by
    intro f hf
    obtain ⟨p,hp,rfl⟩ := List.mem_map.mp hf
    cases xAxis
    · exact (geometry p hp).2
    · exact (geometry p hp).1
  unfold scheduled caller expected
  rw [endpoint_machine _ _ _ safe,complete_timeline_refines hasContainer _ valid]

theorem selected_identity (xAxis : Bool) (f : Frame2) : (project xAxis f).identity = f.identity := rfl

theorem no_container_identity (xAxis early : Bool) (offset : Int) (frames : List Frame2)
    (safe : InMachine offset) : machineEvaluate (scheduled false xAxis early offset frames) = offset := by
  change machineEvaluate (caller early offset none) = offset
  calc
    _ = evaluate (caller early offset none) := admitted_arithmetic_refines _ (absent_default_safe early offset safe)
    _ = offset := absent_default_identity early offset

theorem raw_negative_max_is_truthy :
    reference true 0 ⟨0,0,⟨0,0⟩,⟨0,-5⟩⟩ = 5 := by decide +kernel

def exampleDisplacement : Displacement := ⟨7,0,⟨20,4⟩,⟨10,3⟩⟩
theorem boundary_domain_inhabited :
    ∀ early ∈ [false,true], ∀ offset ∈ [9,10,11,19,20,21], Safe early offset exampleDisplacement := by
  decide +kernel

theorem strict_boundaries :
    reference true 10 exampleDisplacement = 7 ∧ reference false 10 exampleDisplacement = 10 ∧
    reference true 20 exampleDisplacement = 20 ∧ reference false 20 exampleDisplacement = 24 := by decide +kernel

theorem absent_addition_not_required :
    Safe true machineMax ⟨0,0,⟨machineMax,1⟩,⟨0,0⟩⟩ ∧
    ¬ InMachine (machineMax+1) := by decide +kernel

theorem selected_addition_requires_bound :
    ¬ Safe false machineMax ⟨0,0,⟨0,1⟩,⟨0,0⟩⟩ ∧
    machineEvaluate (construct false machineMax ⟨0,0,⟨0,1⟩,⟨0,0⟩⟩) ≠
      reference false machineMax ⟨0,0,⟨0,1⟩,⟨0,0⟩⟩ := by decide +kernel

theorem selected_subtraction_requires_bound :
    ¬ Safe true machineMin ⟨0,0,⟨0,0⟩,⟨0,1⟩⟩ ∧
    machineEvaluate (construct true machineMin ⟨0,0,⟨0,0⟩,⟨0,1⟩⟩) ≠
      reference true machineMin ⟨0,0,⟨0,0⟩,⟨0,1⟩⟩ := by decide +kernel

def sampleGeometry : StickyGeometry.Raw :=
  ⟨⟨50,10⟩,⟨50,10⟩,⟨0,500⟩,50,50,100,0,0,0,⟨some 0,some 0⟩⟩
def sampleFrame : Frame2 :=
  ⟨7,true,true,sampleGeometry,{sampleGeometry with insets := ⟨none,none⟩},true,true,true,60,50,50,50⟩

theorem selected_axis_default_cases :
    expected true true true 50 [sampleFrame] = 50 ∧
    expected true true false 50 [sampleFrame] = 490 ∧
    expected true false false 50 [sampleFrame] = 50 ∧
    CallerSafe false 50 (nativeTimeline true ([sampleFrame].map (project true))) ∧
    CallerSafe false 50 (nativeTimeline true ([sampleFrame].map (project false))) := by
  decide +kernel

end StickyEndpoints
