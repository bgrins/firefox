import StickyPipeline
namespace StickyAbsolute
open StickyNumeric StickyGeometry

structure Box where
  left : Int
  top : Int
  right : Int
  bottom : Int
  deriving Repr, DecidableEq
structure Rect where
  x : Int
  y : Int
  width : Int
  height : Int
  deriving Repr, DecidableEq

def zero : Box := ⟨0,0,0,0⟩
def unbounded : Box := ⟨sentinelLow,sentinelLow,sentinelHigh,sentinelHigh⟩
def Ordered (b : Box) : Prop := b.left ≤ b.right ∧ b.top ≤ b.bottom
def Empty (b : Box) : Prop := b.right ≤ b.left ∨ b.bottom ≤ b.top
instance (b : Box) : Decidable (Empty b) := by unfold Empty; infer_instance

def Enclosed (a b : Box) : Prop := b.left ≤ a.left ∧ a.right ≤ b.right ∧ b.top ≤ a.top ∧ a.bottom ≤ b.bottom

instance (b : Box) : Decidable (Ordered b) := by unfold Ordered; infer_instance

instance (a b : Box) : Decidable (Enclosed a b) := by unfold Enclosed; infer_instance

def fromRect (r : Rect) : Box :=
  if InMachine (r.x+r.width) ∧ InMachine (r.y+r.height) then
    ⟨r.x,r.y,r.x+r.width,r.y+r.height⟩ else zero

def intersect (a b : Box) : Box :=
  let r : Box := ⟨max a.left b.left,max a.top b.top,min a.right b.right,min a.bottom b.bottom⟩
  if r.right < r.left ∨ r.bottom < r.top then ⟨r.left,r.top,r.left+0,r.top+0⟩ else r

def moveClamp (a b : Box) : Box :=
  let l := max b.left a.left
  let t := max b.top a.top
  let w := min (b.right-b.left) (a.right-a.left)
  let h := min (b.bottom-b.top) (a.bottom-a.top)
  let r : Box := ⟨l,t,l+w,t+h⟩
  let nl := min r.right b.right-w
  let nt := min r.bottom b.bottom-h
  let dx := nl-r.left
  let dy := nt-r.top
  ⟨r.left+dx,r.top+dy,r.right+dx,r.bottom+dy⟩

def finish (inner outer : Box) : Box :=
  let clipped := intersect inner outer
  if Empty clipped then moveClamp clipped outer else clipped

def edges (stick contain : Box) (nx ny : Int) : Box × Box :=
  let outer : Box :=
    ⟨if stick.right ≠ sentinelHigh then contain.left-stick.right else sentinelLow,
     if stick.bottom ≠ sentinelHigh then contain.top-stick.bottom else sentinelLow,
     if stick.left ≠ sentinelLow then contain.right-stick.left else sentinelHigh,
     if stick.top ≠ sentinelLow then contain.bottom-stick.top else sentinelHigh⟩
  let inner : Box :=
    ⟨if stick.right ≠ sentinelHigh then nx-stick.right else sentinelLow,
     if stick.bottom ≠ sentinelHigh then ny-stick.bottom else sentinelLow,
     if stick.left ≠ sentinelLow then nx-stick.left else sentinelHigh,
     if stick.top ≠ sentinelLow then ny-stick.top else sentinelHigh⟩
  (outer,inner)

def source (stick contain : Rect) (nx ny : Int) : Box × Box :=
  let p := edges (fromRect stick) (fromRect contain) nx ny
  (p.1,finish p.2 p.1)

def referenceIntersection (a b : Box) : Box :=
  let l := max a.left b.left
  let t := max a.top b.top
  if min a.right b.right < l ∨ min a.bottom b.bottom < t then ⟨l,t,l,t⟩
  else ⟨l,t,min a.right b.right,min a.bottom b.bottom⟩

def referenceMove (a b : Box) : Box :=
  let x := StickyRanges.moveInside ⟨a.left,a.right⟩ ⟨b.left,b.right⟩
  let y := StickyRanges.moveInside ⟨a.top,a.bottom⟩ ⟨b.top,b.bottom⟩
  ⟨x.near,y.near,x.far,y.far⟩

def referenceFinish (a b : Box) : Box :=
  let c := referenceIntersection a b
  if c.left < c.right ∧ c.top < c.bottom then c else referenceMove c b

theorem intersection_refines (a b : Box) : intersect a b = referenceIntersection a b := by
  simp [intersect,referenceIntersection]

theorem move_refines (a b : Box) : moveClamp a b = referenceMove a b := by
  simp only [moveClamp,referenceMove,StickyRanges.moveInside]
  congr 1 <;> omega

theorem finish_refines (a b : Box) : finish a b = referenceFinish a b := by
  simp only [finish,referenceFinish,intersection_refines,move_refines,Empty]
  repeat' split
  all_goals first | rfl | omega

theorem intersection_ordered (a b : Box) : Ordered (intersect a b) := by
  simp only [intersect,Ordered]
  split <;> simp_all <;> omega

theorem finish_contained (a b : Box) (outerOrdered : Ordered b) :
    Ordered (finish a b) ∧ Enclosed (finish a b) b := by
  have ho := intersection_ordered a b
  dsimp only [finish]
  by_cases hc : Empty (intersect a b)
  · simp only [hc,↓reduceIte]
    rw [move_refines]
    have hx := StickyRanges.clamped_inner_contained
      ⟨(intersect a b).left,(intersect a b).right⟩ ⟨b.left,b.right⟩ ho.1 outerOrdered.1
    have hy := StickyRanges.clamped_inner_contained
      ⟨(intersect a b).top,(intersect a b).bottom⟩ ⟨b.top,b.bottom⟩ ho.2 outerOrdered.2
    exact ⟨⟨hx.2.2,hy.2.2⟩,hx.1,hx.2.1,hy.1,hy.2.1⟩
  · simp only [hc,↓reduceIte]
    refine ⟨ho,?_⟩
    simp only [intersect,Enclosed] at *
    split <;> simp_all [Empty] <;> omega

structure EBox where
  left : Expr
  top : Expr
  right : Expr
  bottom : Expr

def evalBox (b : EBox) : Box := ⟨evaluate b.left,evaluate b.top,evaluate b.right,evaluate b.bottom⟩
def machineBox (b : EBox) : Box := ⟨machineEvaluate b.left,machineEvaluate b.top,machineEvaluate b.right,machineEvaluate b.bottom⟩
def BoxSafe (b : EBox) : Prop := Admitted b.left ∧ Admitted b.top ∧ Admitted b.right ∧ Admitted b.bottom
instance (b : EBox) : Decidable (BoxSafe b) := by unfold BoxSafe; infer_instance

def literalBox (b : Box) : EBox := ⟨.literal b.left,.literal b.top,.literal b.right,.literal b.bottom⟩
def choose (a b : Expr) (yes no : EBox) : EBox :=
  ⟨.ifLess a b yes.left no.left,.ifLess a b yes.top no.top,
   .ifLess a b yes.right no.right,.ifLess a b yes.bottom no.bottom⟩
def different (a b yes no : Expr) : Expr := .ifLess a b yes (.ifLess b a yes no)

theorem eval_choose (a b : Expr) (yes no : EBox) :
    evalBox (choose a b yes no) = if evaluate a < evaluate b then evalBox yes else evalBox no := by
  by_cases h : evaluate a < evaluate b <;> simp [choose,evalBox,evaluate,h]

theorem eval_different (a b yes no : Expr) :
    evaluate (different a b yes no) = if evaluate a ≠ evaluate b then evaluate yes else evaluate no := by
  simp only [different,evaluate]
  repeat' split
  all_goals omega

def fromRectE (r : Rect) : EBox :=
  if InMachine (r.x+r.width) ∧ InMachine (r.y+r.height) then
    ⟨.literal r.x,.literal r.y,.add (.literal r.x) (.literal r.width),.add (.literal r.y) (.literal r.height)⟩
  else literalBox zero

theorem from_rect_expression (r : Rect) : evalBox (fromRectE r) = fromRect r := by
  simp only [fromRectE,fromRect]
  split <;> rfl

def intersectE (a b : EBox) : EBox :=
  let r : EBox := ⟨.greater a.left b.left,.greater a.top b.top,.lesser a.right b.right,.lesser a.bottom b.bottom⟩
  let z : EBox := ⟨r.left,r.top,.add r.left (.literal 0),.add r.top (.literal 0)⟩
  choose r.right r.left z (choose r.bottom r.top z r)

theorem intersection_expression (a b : EBox) :
    evalBox (intersectE a b) = intersect (evalBox a) (evalBox b) := by
  dsimp only [intersectE]
  rw [eval_choose,eval_choose]
  simp only [evalBox,evaluate,intersect]
  by_cases hx : min (evaluate a.right) (evaluate b.right) < max (evaluate a.left) (evaluate b.left)
  all_goals by_cases hy : min (evaluate a.bottom) (evaluate b.bottom) < max (evaluate a.top) (evaluate b.top)
  all_goals simp [hx,hy]

def moveE (a b : EBox) : EBox :=
  let l := Expr.greater b.left a.left
  let t := Expr.greater b.top a.top
  let w := Expr.lesser (.subtract b.right b.left) (.subtract a.right a.left)
  let h := Expr.lesser (.subtract b.bottom b.top) (.subtract a.bottom a.top)
  let r := Expr.add l w
  let bot := Expr.add t h
  let nl := Expr.subtract (.lesser r b.right) w
  let nt := Expr.subtract (.lesser bot b.bottom) h
  let dx := Expr.subtract nl l
  let dy := Expr.subtract nt t
  ⟨.add l dx,.add t dy,.add r dx,.add bot dy⟩

theorem move_expression (a b : EBox) : evalBox (moveE a b) = moveClamp (evalBox a) (evalBox b) := rfl

def finishE (a b : EBox) : EBox :=
  let c := intersectE a b
  choose c.left c.right (choose c.top c.bottom c (moveE c b)) (moveE c b)

theorem finish_expression (a b : EBox) : evalBox (finishE a b) = finish (evalBox a) (evalBox b) := by
  dsimp only [finishE]
  rw [eval_choose,eval_choose,move_expression]
  change (if (evalBox (intersectE a b)).left < (evalBox (intersectE a b)).right then
      if (evalBox (intersectE a b)).top < (evalBox (intersectE a b)).bottom then
        evalBox (intersectE a b) else moveClamp (evalBox (intersectE a b)) (evalBox b)
      else moveClamp (evalBox (intersectE a b)) (evalBox b)) = _
  rw [intersection_expression]
  simp only [finish,Empty]
  repeat' split
  all_goals try simp_all
  all_goals first | rfl | omega

def edgesE (s c : EBox) (nx ny : Int) : EBox × EBox :=
  let low := Expr.literal sentinelLow
  let high := Expr.literal sentinelHigh
  let outer : EBox :=
    ⟨different s.right high (.subtract c.left s.right) low,
     different s.bottom high (.subtract c.top s.bottom) low,
     different s.left low (.subtract c.right s.left) high,
     different s.top low (.subtract c.bottom s.top) high⟩
  let inner : EBox :=
    ⟨different s.right high (.subtract (.literal nx) s.right) low,
     different s.bottom high (.subtract (.literal ny) s.bottom) low,
     different s.left low (.subtract (.literal nx) s.left) high,
     different s.top low (.subtract (.literal ny) s.top) high⟩
  (outer,inner)

theorem edges_expression (s c : EBox) (nx ny : Int) :
    (evalBox (edgesE s c nx ny).1,evalBox (edgesE s c nx ny).2) = edges (evalBox s) (evalBox c) nx ny := by
  simp only [edgesE,evalBox,eval_different,evaluate,edges]
  rfl

def construct (s c : Rect) (nx ny : Int) : EBox × EBox :=
  let p := edgesE (fromRectE s) (fromRectE c) nx ny
  (p.1,finishE p.2 p.1)

def RectInputs (r : Rect) : Prop := InMachine r.x ∧ InMachine r.y ∧ InMachine r.width ∧ InMachine r.height
instance (r : Rect) : Decidable (RectInputs r) := by unfold RectInputs; infer_instance

def PreludeSafe (s c : Rect) (nx ny : Int) : Prop :=
  let sp := fromRectE s
  let cp := fromRectE c
  let p := edgesE sp cp nx ny
  BoxSafe sp ∧ BoxSafe cp ∧ BoxSafe p.2 ∧ BoxSafe (intersectE p.2 p.1)
instance (s c : Rect) (nx ny : Int) : Decidable (PreludeSafe s c nx ny) := by
  unfold PreludeSafe; infer_instance

def ObserverSafe (s c : Rect) (nx ny : Int) : Prop :=
  let p := construct s c nx ny
  RectInputs s ∧ RectInputs c ∧ InMachine nx ∧ InMachine ny ∧ PreludeSafe s c nx ny ∧ BoxSafe p.1 ∧ BoxSafe p.2

instance (s c : Rect) (nx ny : Int) : Decidable (ObserverSafe s c nx ny) := by
  unfold ObserverSafe; infer_instance

theorem complete_expression (s c : Rect) (nx ny : Int) :
    (evalBox (construct s c nx ny).1,evalBox (construct s c nx ny).2) = source s c nx ny := by
  have h := edges_expression (fromRectE s) (fromRectE c) nx ny
  rw [from_rect_expression,from_rect_expression] at h
  have h1 := congrArg Prod.fst h
  have h2 := congrArg Prod.snd h
  simp only [Prod.fst,Prod.snd] at h1 h2
  simp only [construct,finish_expression,source,h1,h2]

theorem box_machine (b : EBox) (safe : BoxSafe b) : machineBox b = evalBox b := by
  simp only [machineBox,evalBox,admitted_arithmetic_refines b.left safe.1,
    admitted_arithmetic_refines b.top safe.2.1,admitted_arithmetic_refines b.right safe.2.2.1,
    admitted_arithmetic_refines b.bottom safe.2.2.2]

theorem complete_machine (s c : Rect) (nx ny : Int) (safe : ObserverSafe s c nx ny) :
    (machineBox (construct s c nx ny).1,machineBox (construct s c nx ny).2) = source s c nx ny := by
  rw [box_machine _ safe.2.2.2.2.2.1,box_machine _ safe.2.2.2.2.2.2,complete_expression]

theorem checked_sum_64_safe (x width : Int) (hx : InMachine x) (hw : InMachine width) :
    -9223372036854775808 ≤ x+width ∧ x+width ≤ 9223372036854775807 := by
  unfold InMachine machineMin machineMax at *; omega

theorem from_rect_safe (r : Rect) (inputs : RectInputs r) : BoxSafe (fromRectE r) := by
  simp only [fromRectE]
  split
  · rename_i h
    exact ⟨inputs.1,inputs.2.1,⟨inputs.1,inputs.2.2.1,h.1⟩,⟨inputs.2.1,inputs.2.2.2,h.2⟩⟩
  · decide +kernel

def reference (s c : Rect) (nx ny : Int) : Box × Box :=
  let p := edges (fromRect s) (fromRect c) nx ny
  (p.1,referenceFinish p.2 p.1)

theorem complete_reference (s c : Rect) (nx ny : Int) : source s c nx ny = reference s c nx ny := by
  simp only [source,reference,finish_refines]

theorem complete_observer (s c : Rect) (nx ny : Int) (safe : ObserverSafe s c nx ny) :
    (machineBox (construct s c nx ny).1,machineBox (construct s c nx ny).2) = reference s c nx ny := by
  rw [complete_machine _ _ _ _ safe,complete_reference]

def rectangles (x y : Limits) : Rect × Rect :=
  (⟨x.stickNear,y.stickNear,x.stickFar-x.stickNear,y.stickFar-y.stickNear⟩,
   ⟨x.containNear,y.containNear,x.containFar-x.containNear,y.containFar-y.containNear⟩)

def selected (g : StickyPipeline.TwoAxes) : Rect × Rect :=
  rectangles (StickyConsumers.selectedLimits g.x g.hasOffsets (StickyPipeline.sourceEnd g .x) false)
    (StickyConsumers.selectedLimits g.y g.hasOffsets (StickyPipeline.sourceEnd g .y) false)

def specified (g : StickyPipeline.TwoAxes) : Rect × Rect :=
  rectangles (StickyConsumers.specifiedLimits g.x g.hasOffsets (StickyPipeline.specEnd g .x) false)
    (StickyConsumers.specifiedLimits g.y g.hasOffsets (StickyPipeline.specEnd g .y) false)

theorem selected_rectangles_refine (g : StickyPipeline.TwoAxes)
    (hx : 0 ≤ g.x.border.size) (hy : 0 ≤ g.y.border.size) : selected g = specified g := by
  unfold selected specified StickyPipeline.sourceEnd StickyPipeline.specEnd
  rw [StickyWritingMode.end_selection_refines,StickyWritingMode.end_selection_refines,
    StickyConsumers.optional_limits_refine _ _ _ _ hx,StickyConsumers.optional_limits_refine _ _ _ _ hy]

def pipeline (g : StickyPipeline.TwoAxes) : Box × Box :=
  let r := selected g
  let p := construct r.1 r.2 g.x.normal g.y.normal
  (machineBox p.1,machineBox p.2)

theorem complete_get_scroll_ranges (g : StickyPipeline.TwoAxes)
    (hx : 0 ≤ g.x.border.size) (hy : 0 ≤ g.y.border.size)
    (safe : ObserverSafe (selected g).1 (selected g).2 g.x.normal g.y.normal) :
    pipeline g = reference (specified g).1 (specified g).2 g.x.normal g.y.normal := by
  unfold pipeline
  rw [complete_observer _ _ _ _ safe,selected_rectangles_refine g hx hy]

theorem complete_observer_containment (s c : Rect) (nx ny : Int)
    (safe : ObserverSafe s c nx ny) (ordered : Ordered (edges (fromRect s) (fromRect c) nx ny).1) :
    Ordered (machineBox (construct s c nx ny).2) ∧
    Enclosed (machineBox (construct s c nx ny).2) (machineBox (construct s c nx ny).1) := by
  have h := complete_machine s c nx ny safe
  have h1 := congrArg Prod.fst h
  have h2 := congrArg Prod.snd h
  dsimp only at h1 h2
  rw [h1,h2]
  exact finish_contained _ _ ordered

theorem cross_axis_reset_witness :
    intersect ⟨5,2,8,6⟩ ⟨0,0,3,10⟩ = ⟨5,2,5,2⟩ ∧
    finish ⟨5,2,8,6⟩ ⟨0,0,3,10⟩ = ⟨3,2,3,2⟩ := by decide +kernel

theorem empty_width_keeps_other_extent :
    intersect ⟨3,2,8,6⟩ ⟨0,0,3,10⟩ = ⟨3,2,3,6⟩ ∧
    finish ⟨3,2,8,6⟩ ⟨0,0,3,10⟩ = ⟨3,2,3,6⟩ := by decide +kernel

theorem reversed_outer_excludes_ordered_result :
    ¬ Ordered (finish ⟨0,0,0,0⟩ ⟨5,0,3,10⟩) := by decide +kernel

theorem overflow_returns_zero :
    fromRect ⟨machineMax,0,1,1⟩ = zero ∧ RectInputs ⟨machineMax,0,1,1⟩ := by decide +kernel

theorem sentinel_collision_uses_source_encoding :
    (edges ⟨0,0,sentinelHigh,10⟩ ⟨0,0,900000000,100⟩ 700000000 0).1.left = sentinelLow := by decide +kernel

theorem observer_domain_inhabited :
    ObserverSafe ⟨0,0,100,100⟩ ⟨0,0,500,500⟩ 40 40 ∧
    ObserverSafe ⟨sentinelLow,sentinelLow,coordMax,coordMax⟩
      ⟨sentinelLow,sentinelLow,coordMax,coordMax⟩ 0 0 ∧
    ObserverSafe ⟨0,0,10,10⟩ ⟨20,20,100,100⟩ 0 50 := by decide +kernel

theorem final_clamp_is_necessary :
    ¬ Enclosed (intersect ⟨5,2,8,6⟩ ⟨0,0,3,10⟩) ⟨0,0,3,10⟩ := by decide +kernel

theorem temporary_move_bound_is_necessary :
    ¬ BoxSafe (moveE (literalBox ⟨machineMax,0,machineMax,1⟩)
      (literalBox ⟨machineMin,0,machineMin+1,1⟩)) := by decide +kernel

theorem discarded_assignment_still_requires_bound :
    BoxSafe (construct ⟨0,-1,10,10⟩ ⟨20,0,100,100⟩ 0 machineMax).2 ∧
    ¬ ObserverSafe ⟨0,-1,10,10⟩ ⟨20,0,100,100⟩ 0 machineMax := by decide +kernel

def CoreSafe (g : StickyPipeline.TwoAxes) : Prop :=
  if g.hasOffsets then
    StickyMachineGeometry.ArithmeticSafe (StickyMachineGeometry.construct g.x (StickyPipeline.sourceEnd g .x) false) ∧
    StickyMachineGeometry.ArithmeticSafe (StickyMachineGeometry.construct g.y (StickyPipeline.sourceEnd g .y) false)
  else True

def machineSelected (g : StickyPipeline.TwoAxes) : Rect × Rect :=
  if g.hasOffsets then
    rectangles (StickyMachineGeometry.machineFields (StickyMachineGeometry.construct g.x (StickyPipeline.sourceEnd g .x) false))
      (StickyMachineGeometry.machineFields (StickyMachineGeometry.construct g.y (StickyPipeline.sourceEnd g .y) false))
  else rectangles (missingOffsets sentinelLow sentinelHigh) (missingOffsets sentinelLow sentinelHigh)

theorem core_machine_join (g : StickyPipeline.TwoAxes) (safe : CoreSafe g) : machineSelected g = selected g := by
  unfold CoreSafe at safe
  unfold machineSelected selected StickyConsumers.selectedLimits
  split
  · rename_i h
    simp only [h,↓reduceIte] at safe ⊢
    rw [StickyMachineGeometry.machine_fields_refine _ safe.1,StickyMachineGeometry.machine_fields_refine _ safe.2,
      StickyMachineGeometry.complete_expression_limits,StickyMachineGeometry.complete_expression_limits]
  · rename_i h
    simp only [h,↓reduceIte]

def fullMachinePipeline (g : StickyPipeline.TwoAxes) : Box × Box :=
  let r := machineSelected g
  let p := construct r.1 r.2 g.x.normal g.y.normal
  (machineBox p.1,machineBox p.2)

theorem complete_machine_get_scroll_ranges (g : StickyPipeline.TwoAxes)
    (hx : 0 ≤ g.x.border.size) (hy : 0 ≤ g.y.border.size)
    (core : CoreSafe g)
    (observer : ObserverSafe (selected g).1 (selected g).2 g.x.normal g.y.normal) :
    fullMachinePipeline g = reference (specified g).1 (specified g).2 g.x.normal g.y.normal := by
  unfold fullMachinePipeline
  rw [core_machine_join g core]
  exact complete_get_scroll_ranges g hx hy observer

theorem intersection_clipping_is_necessary :
    finish ⟨-2,2,4,6⟩ ⟨0,0,3,10⟩ = ⟨0,2,3,6⟩ ∧
    ¬ Enclosed ⟨-2,2,4,6⟩ ⟨0,0,3,10⟩ := by decide +kernel

end StickyAbsolute
