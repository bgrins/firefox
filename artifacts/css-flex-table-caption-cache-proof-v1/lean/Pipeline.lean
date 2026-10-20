import CaptionKey
namespace CaptionCache

structure Gates where
  optimization : Bool
  previousOrNextInFlow : Bool
  fragmented : Bool
  dirty : Bool
  finalPresent : Bool
  cachedFinalSize : Int
  paddingChanged : Bool
  indefiniteChanged : Bool
  relativeDependency : Bool
  deriving Repr

structure Measurement where
  planned : Int
  hadMeasuringReflow : Bool
  deriving DecidableEq, Repr

def measure (cachedPresent dirty accepted : Bool) (cachedSize freshSize : Int) : Measurement :=
  if reuse cachedPresent dirty accepted then ⟨cachedSize,false⟩ else ⟨freshSize,true⟩

def needsFinal (g : Gates) (m : Measurement) (liveContent : Int) : Bool :=
  if !g.optimization || g.previousOrNextInFlow || g.fragmented then true
  else if m.hadMeasuringReflow then
    decide (m.planned ≠ liveContent) || g.relativeDependency
  else g.dirty || !g.finalPresent || decide (g.cachedFinalSize ≠ m.planned) ||
    g.paddingChanged || (g.indefiniteChanged && g.relativeDependency)

def observe (g : Gates) (m : Measurement) (oldLive freshLive : Int) : Int :=
  let live := if m.hadMeasuringReflow then freshLive else oldLive
  if needsFinal g m live then freshLive else live

theorem accepted_measurement_leaves_measured_false (present dirty accepted : Bool)
    (cached fresh : Int) (hit : reuse present dirty accepted = true) :
    measure present dirty accepted cached fresh = ⟨cached,false⟩ := by
  simp [measure,hit]

theorem rejected_measurement_sets_measured_true (present dirty accepted : Bool)
    (cached fresh : Int) (miss : reuse present dirty accepted = false) :
    measure present dirty accepted cached fresh = ⟨fresh,true⟩ := by
  simp [measure,miss]

theorem fresh_measurement_observation (g : Gates) (fresh old : Int) :
    observe g ⟨fresh,true⟩ old fresh = fresh := by
  simp [observe]

theorem changed_basis_forces_measurement [DecidableEq P] (a b : Input P)
    (present dirty : Bool) (cached fresh : Int)
    (changed : a.containingBlock ≠ b.containingBlock) :
    measure present dirty (candidate a b) cached fresh = ⟨fresh,true⟩ := by
  simp [measure,reuse,changed_basis_rejected a b changed]

theorem changed_basis_delivers_supplied_fresh_observation [DecidableEq P]
    (a b : Input P) (present dirty : Bool) (cached fresh oldLive : Int) (g : Gates)
    (changed : a.containingBlock ≠ b.containingBlock) :
    observe g (measure present dirty (candidate a b) cached fresh) oldLive fresh = fresh := by
  rw [changed_basis_forces_measurement a b present dirty cached fresh changed]
  exact fresh_measurement_observation g fresh oldLive

def reusableFinal (size : Int) : Gates :=
  ⟨true,false,false,false,true,size,false,false,true⟩

theorem stale_plan_allows_final_reuse (size live : Int) :
    needsFinal (reusableFinal size) ⟨size,false⟩ live = false := by
  simp [needsFinal,reusableFinal]

theorem relative_dependency_alone_does_not_reject_nonmeasuring_hit (size : Int) :
    (reusableFinal size).relativeDependency = true ∧
    needsFinal (reusableFinal size) ⟨size,false⟩ size = false := by
  simp [reusableFinal,needsFinal]

theorem two_hits_retain_old_observation (old fresh : Int) :
    observe (reusableFinal old) (measure true false true old fresh) old fresh = old := by
  simp [observe,measure,reuse,reusableFinal,needsFinal]

end CaptionCache
