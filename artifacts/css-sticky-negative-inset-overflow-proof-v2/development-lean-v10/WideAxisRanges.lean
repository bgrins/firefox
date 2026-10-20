import WideCallers
namespace WideAxisRanges
open StickyNumeric StickyGeometry StickyWritingMode WideCallers

structure ERange where
  threshold : Expr
  amount : Expr

def nearE (n : Int) (l : Limits) : ERange :=
  ⟨.subtract (.literal n) (.literal l.stickNear),
   .greater (.literal 0) (.subtract (.literal l.containFar) (.literal n))⟩
def farE (n : Int) (l : Limits) : ERange :=
  ⟨.subtract (.literal n) (.literal l.stickFar),
   .greater (.literal 0) (.subtract (.literal n) (.literal l.containNear))⟩
def RangeSafe (r : ERange) : Prop := Admitted r.threshold ∧ Admitted r.amount
instance (r : ERange) : Decidable (RangeSafe r) := by unfold RangeSafe; infer_instance

def eval (r : ERange) : StickyRanges.Range := ⟨evaluate r.threshold,evaluate r.amount⟩
def machine (r : ERange) : StickyRanges.Range := ⟨machineEvaluate r.threshold,machineEvaluate r.amount⟩
theorem range_machine (r : ERange) (h : RangeSafe r) : machine r = eval r := by
  simp only [machine,eval,admitted_arithmetic_refines _ h.1,admitted_arithmetic_refines _ h.2]

def entered (f : Frame) (a : Axis) : Bool :=
  f.axes.hasOffsets && ((raw f a).insets.near.isSome || (raw f a).insets.far.isSome)

def finish (near far : Option StickyRanges.Range) : StickyConsumers.AxisRanges :=
  match near,far with
  | some x,some y => if x.atScroll < y.atScroll then ⟨none,none⟩ else ⟨near,far⟩
  | _,_ => ⟨near,far⟩

def sourceWith (f : Frame) (a : Axis) (l : Limits) : StickyConsumers.AxisRanges :=
  if entered f a then
    finish (if (raw f a).insets.near.isSome then some (eval (nearE (raw f a).normal l)) else none)
      (if (raw f a).insets.far.isSome then some (eval (farE (raw f a).normal l)) else none)
  else ⟨none,none⟩

def referenceWith (f : Frame) (a : Axis) (l : Limits) : StickyConsumers.AxisRanges :=
  if f.axes.hasOffsets then
    let n := (raw f a).insets.near.map (fun _ => StickyRanges.nearRange (raw f a).normal l.stickNear l.containFar)
    let e := (raw f a).insets.far.map (fun _ => StickyRanges.farRange (raw f a).normal l.stickFar l.containNear)
    finish n e
  else ⟨none,none⟩

theorem range_reference (f : Frame) (a : Axis) (l : Limits) : sourceWith f a l = referenceWith f a l := by
  unfold sourceWith referenceWith entered
  cases hh : f.axes.hasOffsets <;>
    cases hn : (raw f a).insets.near <;> cases hf : (raw f a).insets.far <;>
    simp [hh,hn,hf,finish,eval,nearE,farE,evaluate,StickyRanges.nearRange,StickyRanges.farRange]

def machineWith (f : Frame) (a : Axis) (l : Limits) : StickyConsumers.AxisRanges :=
  if entered f a then
    finish (if (raw f a).insets.near.isSome then some (machine (nearE (raw f a).normal l)) else none)
      (if (raw f a).insets.far.isSome then some (machine (farE (raw f a).normal l)) else none)
  else ⟨none,none⟩

def SafeWith (f : Frame) (a : Axis) (l : Limits) : Prop :=
  (if (raw f a).insets.near.isSome then RangeSafe (nearE (raw f a).normal l) else True) ∧
  (if (raw f a).insets.far.isSome then RangeSafe (farE (raw f a).normal l) else True)
instance (f : Frame) (a : Axis) (l : Limits) : Decidable (SafeWith f a l) := by
  unfold SafeWith; infer_instance

def Safe (f : Frame) (a : Axis) : Prop :=
  if entered f a then CoreSafe f true ∧ SafeWith f a (selected f a true) else True
instance (f : Frame) (a : Axis) : Decidable (Safe f a) := by unfold Safe; infer_instance

def DebugSafe (f : Frame) (a : Axis) : Prop :=
  if entered f a then
    ((raw f a).insets.near.isSome = true → (selected f a true).stickNear ≠ sentinelLow) ∧
    ((raw f a).insets.far.isSome = true → (selected f a true).stickFar ≠ sentinelHigh) ∧
    ((raw f a).insets.near.isSome = true → (raw f a).insets.far.isSome = true →
      (selected f a true).stickNear ≤ (selected f a true).stickFar)
  else True
instance (f : Frame) (a : Axis) : Decidable (DebugSafe f a) := by unfold DebugSafe; infer_instance

theorem machine_with_refines (f : Frame) (a : Axis) (l : Limits) (h : SafeWith f a l) :
    machineWith f a l = sourceWith f a l := by
  unfold machineWith sourceWith
  split
  · by_cases n : (raw f a).insets.near.isSome = true <;>
      by_cases e : (raw f a).insets.far.isSome = true <;>
      simp only [SafeWith,n,e,Bool.false_eq_true,↓reduceIte] at h ⊢
    · rw [range_machine _ h.1,range_machine _ h.2]
    · rw [range_machine _ h.1]
    · rw [range_machine _ h.2]
    · rfl
  · rfl

def caller (f : Frame) (a : Axis) : StickyConsumers.AxisRanges :=
  if entered f a then machineWith f a (machineSelected f a true) else ⟨none,none⟩

theorem complete_axis_caller (f : Frame) (a : Axis) (h : Safe f a)
    (valid : 0 ≤ (raw f a).border.size) :
    caller f a = referenceWith f a (specified f a true) := by
  unfold caller
  split
  · rename_i enabled
    simp only [Safe,enabled,↓reduceIte] at h
    have hc := machine_selected_refines f a true h.1 valid
    rw [← selected_refines f a true valid] at hc
    rw [hc,machine_with_refines _ _ _ h.2,range_reference,selected_refines f a true valid]
  · rename_i disabled
    rw [← range_reference]
    simp [sourceWith,disabled]

theorem both_active_ordered (m e : Bool) (v : StickyAxis.Insets) (p b origin : Int)
    (near : v.near.isSome = true) (far : v.far.isSome = true) :
    origin + (WideNormalization.source m v p b e).1 ≤
    origin+p-(WideNormalization.source m v p b e).2-b := by
  cases m <;> cases e <;>
    simp [WideNormalization.source,WideNormalization.active,near,far,
      WidenedInsets.end_refines,WidenedInsets.referenceEnd] <;> omega

end WideAxisRanges
