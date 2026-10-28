import Independence

namespace ProviderDemand
open SelectedIndependence

inductive Requirements where
  | unknown
  | known (keys : List Nat)
  deriving DecidableEq, Repr

def RequirementsComplete (v : Value) : Requirements → Prop
  | .unknown => False
  | .known keys => ∀ a b : Nat → Nat, (∀ k ∈ keys, a k = b k) → compute a v = compute b v

def CanCompute (r : Requirements) (ready : Nat → Prop) : Prop :=
  match r with
  | .unknown => False
  | .known keys => ∀ k ∈ keys, ready k

theorem unknown_blocks (ready : Nat → Prop) : ¬ CanCompute .unknown ready := id

theorem complete_ready_context_matches_final (v : Value) (r : Requirements)
    (ready : Nat → Prop) (now final : Nat → Nat)
    (complete : RequirementsComplete v r) (available : CanCompute r ready)
    (coherent : ∀ k, ready k → now k = final k) : compute now v = compute final v := by
  cases r with
  | unknown => exact False.elim available
  | known keys => exact complete now final (fun k hk => coherent k (available k hk))

theorem actual_dependencies_complete (v : Value) :
    RequirementsComplete v (.known (dependencies v)) := agreement_suffices v

inductive Phase where
  | pending | applying | ready
  deriving DecidableEq, Repr

structure State where
  owner : Nat
  stack : List Nat
  phase : Phase
  generation : Nat
  committed : Nat
  provisional : Nat
  published : Option Nat
  deriving DecidableEq, Repr

def begin (s : State) : Option State :=
  if s.owner ∈ s.stack ∧ s.phase = .pending then
    some {s with phase := .applying, provisional := 0}
  else none

def suspend (s : State) : Option State :=
  if s.owner ∈ s.stack ∧ s.phase = .applying then
    some {s with phase := .pending, provisional := 0}
  else none

def publish (generation value : Nat) (s : State) : Option State :=
  if s.owner ∈ s.stack ∧ s.phase = .applying ∧ s.generation = generation then
    some {s with phase := .ready, committed := s.committed + s.provisional, provisional := 0, published := some value}
  else none

theorem suspend_retains_frame_and_committed_effects (s t : State)
    (h : suspend s = some t) :
    t.stack = s.stack ∧ t.owner ∈ t.stack ∧ t.committed = s.committed ∧
      t.provisional = 0 ∧ t.published = s.published ∧ t.phase = .pending := by
  unfold suspend at h
  split at h
  next guard => cases h; simp_all
  next => contradiction

theorem closed_frame_cannot_suspend (s : State) (closed : s.owner ∉ s.stack) :
    suspend s = none := by simp [suspend, closed]

theorem published_once (g v : Nat) (s t : State) (h : publish g v s = some t) :
    t.committed = s.committed + s.provisional ∧
    ∀ next, publish g next t = none := by
  unfold publish at h
  split at h
  next guard => cases h; simp [publish]
  next => contradiction

theorem stale_generation_cannot_publish (g v : Nat) (s : State)
    (stale : s.generation ≠ g) : publish g v s = none := by simp [publish, stale]

inductive Provider where
  | pending (staleCache : Nat)
  | applying (staleCache : Nat)
  | ready (generation value : Nat)
  deriving DecidableEq, Repr

def lookup (generation : Nat) : Provider → Option Nat
  | .ready g v => if g = generation then some v else none
  | _ => none

theorem applying_masks_cached_value (g stale : Nat) : lookup g (.applying stale) = none := rfl

theorem consumer_matches_finalized_provider (g value : Nat) :
    lookup g (.ready g value) = some value := by simp [lookup]

def frame : State := ⟨7, [7, 4], .applying, 1, 0, 1, none⟩
def popped : State := {frame with stack := [4]}
def enumOnlySuspend (s : State) : State := {s with phase := .pending}

theorem enum_reset_loses_owner :
    (enumOnlySuspend popped).phase = .pending ∧
    (enumOnlySuspend popped).owner ∉ (enumOnlySuspend popped).stack ∧
    begin (enumOnlySuspend popped) = none := by decide +kernel

def badRetryEffects : Nat := frame.provisional + frame.provisional

theorem retried_effects_must_not_accumulate :
    (suspend frame).map State.committed = some 0 ∧ badRetryEffects = 2 := by decide +kernel

def semanticEdge (a b : Nat) : Bool := a == 0 && b == 1
def demandEdge (a b : Nat) : Bool := a == 1 && b == 0

theorem scheduling_edge_creates_spurious_two_cycle :
    semanticEdge 0 1 = true ∧ semanticEdge 1 0 = false ∧ demandEdge 1 0 = true := by
  decide +kernel

theorem empty_requirements_can_be_incomplete :
    ¬ RequirementsComplete (.contextual 0) (.known []) := by
  intro complete
  have bad := complete (fun _ => 800) (fun _ => 200) (by simp)
  have : Computed.literal 800 = Computed.literal 200 := bad
  contradiction

end ProviderDemand
