import StickyMachineGeometry
import StickyContinuations
import StickyRanges
namespace StickyConsumers
open StickyGeometry StickyRanges StickyNumeric

structure AxisRanges where
  near : Option Range
  far : Option Range
  deriving Repr, DecidableEq

def nativeRanges (g : Raw) (hasOffsets endIsFar : Bool) : AxisRanges :=
  if !hasOffsets then ⟨none,none⟩ else
  if !StickyAxis.active g.insets then ⟨none,none⟩ else
  let limits := nativeLimits g endIsFar true sentinelLow sentinelHigh
  let n := if g.insets.near.isSome then some (nearRange g.normal limits.stickNear limits.containFar) else none
  let f := if g.insets.far.isSome then some (farRange g.normal limits.stickFar limits.containNear) else none
  match n,f with
  | some a,some b => if b.atScroll > a.atScroll then ⟨none,none⟩ else ⟨n,f⟩
  | _,_ => ⟨n,f⟩

def referenceRanges (g : Raw) (hasOffsets endIsFar : Bool) : AxisRanges :=
  let limits := referenceLimits g endIsFar true sentinelLow sentinelHigh
  if hasOffsets then
    ⟨g.insets.near.map (fun _ => nearRange g.normal limits.stickNear limits.containFar),
     g.insets.far.map (fun _ => farRange g.normal limits.stickFar limits.containNear)⟩
  else ⟨none,none⟩

theorem complete_axis_ranges_refine (g : Raw) (hasOffsets endIsFar : Bool)
    (nonnegative : 0 ≤ g.border.size) :
    nativeRanges g hasOffsets endIsFar = referenceRanges g hasOffsets endIsFar := by
  have lim := full_axis_limits_refine g endIsFar true sentinelLow sentinelHigh nonnegative
  unfold nativeRanges referenceRanges
  rw [lim]
  cases hasOffsets
  · rfl
  · cases hn : g.insets.near with
    | none => cases hf : g.insets.far <;> simp [StickyAxis.active,hn,hf]
    | some a =>
      cases hf : g.insets.far with
      | none => simp [StickyAxis.active,hn,hf]
      | some b =>
        have ordered := StickyAxis.both_active_edges_ordered a b g.portSize g.border.size
          (origin g true) endIsFar
        have ei : g.insets = ⟨some a,some b⟩ := by
          calc g.insets = ⟨g.insets.near,g.insets.far⟩ := rfl
               _ = ⟨some a,some b⟩ := by rw [hn,hf]
        simp only [referenceLimits,StickyAxis.movementEdges,ei,Option.map_some,
          Option.getD_some,StickyAxis.active,Option.isSome_some,Bool.or_self,
          Bool.not_true,Bool.false_eq_true,↓reduceIte,nearRange,farRange]
        rw [← StickyAxis.normalization_refines] at *
        split <;> simp_all <;> omega

theorem both_present_limits_ordered (g : Raw) (endIsFar : Bool)
    (nearPresent : g.insets.near.isSome = true) (farPresent : g.insets.far.isSome = true) :
    (nativeLimits g endIsFar true sentinelLow sentinelHigh).stickNear ≤
      (nativeLimits g endIsFar true sentinelLow sentinelHigh).stickFar := by
  have fit := StickyAxis.active_view_fits g.insets g.portSize g.border.size endIsFar
    (by simp [StickyAxis.active,nearPresent,farPresent])
  simp only [nativeLimits,nearPresent,farPresent,↓reduceIte]
  omega

def rangeDisplacement (scroll : Int) (ranges : AxisRanges) : Int :=
  (ranges.near.map (fun r => min (max 0 (scroll-r.atScroll)) r.maxOffset)).getD 0 -
  (ranges.far.map (fun r => min (max 0 (r.atScroll-scroll)) r.maxOffset)).getD 0

theorem actual_range_displacement (g : Raw) (endIsFar : Bool)
    (nonnegative : 0 ≤ g.border.size) :
    rangeDisplacement g.scroll (nativeRanges g true endIsFar) =
      maskedDisplacement g.scroll g.normal
        (nativeLimits g endIsFar true sentinelLow sentinelHigh).stickNear
        (nativeLimits g endIsFar true sentinelLow sentinelHigh).stickFar
        (nativeLimits g endIsFar true sentinelLow sentinelHigh).containNear
        (nativeLimits g endIsFar true sentinelLow sentinelHigh).containFar
        g.insets.near.isSome g.insets.far.isSome := by
  rw [complete_axis_ranges_refine g true endIsFar nonnegative]
  unfold referenceRanges
  rw [← full_axis_limits_refine g endIsFar true sentinelLow sentinelHigh nonnegative]
  cases hn : g.insets.near <;> cases hf : g.insets.far <;>
    simp [rangeDisplacement,maskedDisplacement,hn,hf,nearRange,farRange]

theorem complete_range_position_agreement (g : Raw) (endIsFar : Bool)
    (nonnegative : 0 ≤ g.border.size)
    (normalLow : (nativeContain g).origin ≤ g.normal)
    (normalHigh : g.normal ≤ ending (nativeContain g))
    (finiteLow : sentinelLow ≤ (nativeContain g).origin)
    (finiteHigh : ending (nativeContain g) ≤ sentinelHigh) :
    position g.normal (nativeLimits g endIsFar false sentinelLow sentinelHigh) =
      g.normal + rangeDisplacement g.scroll (nativeRanges g true endIsFar) := by
  rw [actual_range_displacement g endIsFar nonnegative,limits_scroll_relation]
  exact masked_position_range_agreement g.normal _ _ _ _ g.scroll sentinelLow sentinelHigh
    g.insets.near.isSome g.insets.far.isSome normalLow normalHigh finiteLow finiteHigh
    (both_present_limits_ordered g endIsFar)

inductive Selection (α : Type) where
  | absent
  | one (value : α)
  | multiple
  deriving Repr, DecidableEq

def referenceSelect (xs : List α) : Selection α :=
  match xs with
  | [] => .absent
  | [x] => .one x
  | _ => .multiple

def nativeScan (eligible : α → Bool) (found : Option α) : List α → Selection α
  | [] => match found with | none => .absent | some x => .one x
  | x::xs =>
    if eligible x then
      match found with
      | none => nativeScan eligible (some x) xs
      | some _ => .multiple
    else nativeScan eligible found xs

theorem scan_one (eligible : α → Bool) (found : α) (xs : List α) :
    nativeScan eligible (some found) xs = referenceSelect (found :: xs.filter eligible) := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    by_cases h : eligible x = true
    · simp [nativeScan,h,List.filter,referenceSelect]
    · simp [nativeScan,h,List.filter,ih]

theorem scan_refines (eligible : α → Bool) (xs : List α) :
    nativeScan eligible none xs = referenceSelect (xs.filter eligible) := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    by_cases h : eligible x = true
    · simp [nativeScan,h,List.filter,scan_one]
    · simp [nativeScan,h,List.filter,ih]

structure Ancestor where
  identity : Nat
  sticky : Bool
  sameScrollContainer : Bool
  firstGeometry : Raw
  hasOffsets : Bool
  endIsFar : Bool
  current : Int
  normal : Int
  deriving Repr, DecidableEq

def eligible (f : Ancestor) : Bool := f.sticky && f.sameScrollContainer

structure Displacement where
  identity : Nat
  shift : Int
  near : Range
  far : Range
  deriving Repr, DecidableEq

def pack (f : Ancestor) (ranges : AxisRanges) : Option Displacement :=
  if ranges.near.isNone && ranges.far.isNone then none
  else some ⟨f.identity,f.current-f.normal,ranges.near.getD ⟨0,0⟩,ranges.far.getD ⟨0,0⟩⟩

def nativeTimeline (containerExists : Bool) (ancestors : List Ancestor) : Option Displacement :=
  if !containerExists then none else
  match nativeScan eligible none ancestors with
  | .one f => pack f (nativeRanges f.firstGeometry f.hasOffsets f.endIsFar)
  | _ => none

def referenceTimeline (containerExists : Bool) (ancestors : List Ancestor) : Option Displacement :=
  if containerExists then
    match ancestors.filter eligible with
    | [f] => pack f (referenceRanges f.firstGeometry f.hasOffsets f.endIsFar)
    | _ => none
  else none

theorem complete_timeline_refines (containerExists : Bool) (ancestors : List Ancestor)
    (valid : ∀ f ∈ ancestors, 0 ≤ f.firstGeometry.border.size) :
    nativeTimeline containerExists ancestors = referenceTimeline containerExists ancestors := by
  unfold nativeTimeline referenceTimeline
  rw [scan_refines]
  cases containerExists
  · rfl
  · simp only [Bool.not_true,Bool.false_eq_true,↓reduceIte]
    generalize he : ancestors.filter eligible = chosen
    cases chosen with
    | nil => rfl
    | cons f fs =>
      cases fs with
      | cons x xs => rfl
      | nil =>
        have member : f ∈ ancestors := (List.mem_filter.mp (show f ∈ ancestors.filter eligible from by rw [he]; simp)).1
        simp only [referenceSelect]
        rw [complete_axis_ranges_refine f.firstGeometry f.hasOffsets f.endIsFar (valid f member)]

def selectedLimits (g : Raw) (hasOffsets endIsFar ignoreScroll : Bool) : Limits :=
  if hasOffsets then nativeLimits g endIsFar ignoreScroll sentinelLow sentinelHigh
  else missingOffsets sentinelLow sentinelHigh

def specifiedLimits (g : Raw) (hasOffsets endIsFar ignoreScroll : Bool) : Limits :=
  if hasOffsets then referenceLimits g endIsFar ignoreScroll sentinelLow sentinelHigh
  else missingOffsets sentinelLow sentinelHigh

theorem optional_limits_refine (g : Raw) (hasOffsets endIsFar ignoreScroll : Bool)
    (valid : 0 ≤ g.border.size) :
    selectedLimits g hasOffsets endIsFar ignoreScroll = specifiedLimits g hasOffsets endIsFar ignoreScroll := by
  cases hasOffsets <;> simp [selectedLimits,specifiedLimits,full_axis_limits_refine g endIsFar ignoreScroll sentinelLow sentinelHigh valid]

theorem complete_position_continuations (g : Raw) (hasOffsets endIsFar : Bool)
    (frames : List StickyContinuations.Frame) (valid : 0 ≤ g.border.size) :
    StickyContinuations.nativeDispatch (position g.normal (selectedLimits g hasOffsets endIsFar false)) frames =
    StickyContinuations.referenceDispatch (position g.normal (specifiedLimits g hasOffsets endIsFar false)) frames := by
  rw [optional_limits_refine g hasOffsets endIsFar false valid,
      StickyContinuations.complete_dispatch_refines]

end StickyConsumers
