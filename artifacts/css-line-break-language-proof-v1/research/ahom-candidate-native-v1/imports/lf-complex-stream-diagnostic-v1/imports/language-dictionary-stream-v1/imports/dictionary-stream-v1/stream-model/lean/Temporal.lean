import Std

namespace HyphenTemporal

structure Frame where
  identity : Nat
  policy : Nat
  run : Option Nat
  deriving DecidableEq, Repr

def detach (target : Nat) (frames : List Frame) : List Frame :=
  frames.map fun f => if f.run = some target then {f with run := none} else f

def clearContiguous (target : Nat) : List Frame → List Frame
  | [] => []
  | f :: rest => if f.run = some target then
      {f with run := none} :: clearContiguous target rest else f :: rest

theorem detach_does_not_change_policy (target : Nat) (frames : List Frame) :
    (detach target frames).map (fun f => (f.identity,f.policy)) =
      frames.map (fun f => (f.identity,f.policy)) := by
  simp only [detach, List.map_map]
  apply List.map_congr_left
  intro f hf
  simp only [Function.comp_apply]
  split <;> rfl

theorem detach_absent (target : Nat) (frames : List Frame)
    (absent : ∀ f ∈ frames, f.run ≠ some target) : detach target frames = frames := by
  induction frames with
  | nil => rfl
  | cons f rest ih =>
    have hf := absent f (by simp)
    have hr : ∀ g ∈ rest, g.run ≠ some target := by intro g hg; exact absent g (by simp [hg])
    simp only [detach, List.map_cons, hf, ite_false]
    exact congrArg (List.cons f) (ih hr)

theorem contiguous_unhook_refines (target : Nat) (prefixFrames suffixFrames : List Frame)
    (inside : ∀ f ∈ prefixFrames, f.run = some target)
    (outside : ∀ f ∈ suffixFrames, f.run ≠ some target) :
    clearContiguous target (prefixFrames ++ suffixFrames) =
      detach target (prefixFrames ++ suffixFrames) := by
  induction prefixFrames with
  | nil =>
    rw [List.nil_append, detach_absent target suffixFrames outside]
    cases suffixFrames with
    | nil => rfl
    | cons f rest => simp [clearContiguous, outside f (by simp)]
  | cons f rest ih =>
    have hf := inside f (by simp)
    have hr : ∀ g ∈ rest, g.run = some target := by
      intro g hg; exact inside g (by simp [hg])
    simp only [List.cons_append, clearContiguous, hf, ite_true, detach, List.map_cons]
    exact congrArg (List.cons {f with run := none}) (ih hr)

theorem all_references_removed (target : Nat) (frames : List Frame) :
    ∀ f ∈ detach target frames, f.run ≠ some target := by
  intro f hf
  obtain ⟨g,hg,he⟩ := List.mem_map.mp hf
  subst f
  split <;> simp_all

theorem multi_flow_unhook (target : Nat) (flows : List (List Frame)) :
    (flows.map (detach target)).flatten = detach target flows.flatten := by
  simp [detach, List.map_flatten]
  rfl

def referencedRun (frames : List Frame) : Option Nat :=
  frames.head?.bind Frame.run

theorem changed_frame_cannot_reuse (target : Nat) (f : Frame) (rest : List Frame)
    (old : f.run = some target) :
    referencedRun (detach target (f :: rest)) = none := by
  simp [referencedRun, detach, old]

structure CachedRun where
  identity : Nat
  breaks : List Nat
  deriving DecidableEq, Repr

def finish (reference : Option Nat) (cache : List CachedRun) (fresh : List Nat) : List Nat :=
  match reference with
  | none => fresh
  | some id => match cache.find? (fun r => r.identity == id) with
      | none => fresh
      | some run => run.breaks

theorem invalidation_removes_old_opportunities (target : Nat) (f : Frame)
    (rest : List Frame) (old : f.run = some target)
    (cache : List CachedRun) (fresh : List Nat) :
    finish (referencedRun (detach target (f :: rest))) cache fresh = fresh := by
  rw [changed_frame_cannot_reuse target f rest old]
  rfl

def sinkZero (old : Nat) : Nat := old

theorem zero_write_does_not_invalidate : sinkZero 2 ≠ 0 := by decide

theorem omitted_unhook_counterexample :
    finish (some 7) [⟨7,[0,0,2,0]⟩] [0,0,0,0] ≠ [0,0,0,0] := by decide

#print axioms contiguous_unhook_refines
#print axioms all_references_removed
#print axioms multi_flow_unhook
#print axioms changed_frame_cannot_reuse
#print axioms invalidation_removes_old_opportunities
#print axioms omitted_unhook_counterexample
end HyphenTemporal
