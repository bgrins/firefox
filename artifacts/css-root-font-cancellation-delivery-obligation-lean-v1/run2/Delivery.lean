import Admission
import Provider

namespace CancellationDelivery

structure Key where
  host : Nat
  pseudo : Bool
  deriving DecidableEq, Repr

structure Hop where
  normalVisited : Bool
  fontChanged : Bool
  deriving DecidableEq, Repr

def reached (route : List Hop) : Bool := route.all (·.normalVisited)

structure State where
  hint : Bool
  provider : RootFontProvider.State
  queued : Option Nat := none
  delivered : Option Key := none
  result : Option (Key × RootFontProvider.Observation) := none
  deriving DecidableEq, Repr

def enqueue (ownerOf : Nat → Nat) (registry : FontUnitAdmission.State)
    (node : Nat) (normal : Bool) (route : List Hop) (s : State) : State :=
  if normal && reached route &&
      FontUnitAdmission.admits ownerOf normal s.hint false registry node then
    { s with queued := some node }
  else s

def deliver (normalize : Nat → Key) (s : State) : State :=
  match s.queued with
  | none => s
  | some node => { s with queued := none, delivered := some (normalize node) }

def rebuild (key : Key) (s : State) : State :=
  if s.delivered = some key then
    { s with result := (RootFontProvider.provider s.provider).map
      (fun metrics => (key, RootFontProvider.observe metrics .rem)) }
  else s

theorem fixed_fonts_do_not_shorten_route (route : List Hop) :
    reached (route.map fun hop => { hop with fontChanged := false }) = reached route := by
  simp [reached, Function.comp_def]

theorem animation_only_does_not_enqueue (ownerOf : Nat → Nat)
    (registry : FontUnitAdmission.State) (node : Nat) (route : List Hop) (s : State) :
    enqueue ownerOf registry node false route s = s := by simp [enqueue]

theorem unreached_route_does_not_enqueue (ownerOf : Nat → Nat)
    (registry : FontUnitAdmission.State) (node : Nat) (normal : Bool)
    (route : List Hop) (s : State) (missed : reached route = false) :
    enqueue ownerOf registry node normal route s = s := by simp [enqueue, missed]

theorem queued_normalizes (normalize : Nat → Key) (s : State) (node : Nat)
    (queued : s.queued = some node) :
    (deliver normalize s).delivered = some (normalize node) := by simp [deliver, queued]

theorem rebuild_uses_current_provider (s : State) (key : Key)
    (valid : RootFontProvider.Valid s.provider) (delivered : s.delivered = some key)
    (value : RootFontProvider.Observation)
    (got : (rebuild key s).result = some (key, value)) :
    value = RootFontProvider.observe s.provider.desired .rem := by
  simp only [rebuild, delivered, ite_true] at got
  obtain ⟨metrics, current, eq⟩ := Option.map_eq_some_iff.mp got
  have same := RootFontProvider.provider_current valid current
  simp only [Prod.mk.injEq, true_and] at eq
  simpa [same] using eq.symm

theorem complete_route_delivery (ownerOf : Nat → Nat)
    (events : List FontUnitAdmission.Event) (id : Nat) (entry : AttributeWatches.Entry)
    (member : (id, entry) ∈ (FontUnitAdmission.run ownerOf events).registry.active)
    (route : List Hop) (allVisited : reached route = true) (s : State)
    (hint : s.hint = true) (normalize : Nat → Key) (key : Key)
    (identity : normalize entry.target = key) (metrics : RootFontProvider.Metrics)
    (current : RootFontProvider.provider s.provider = some metrics) :
    (rebuild key (deliver normalize
      (enqueue ownerOf (FontUnitAdmission.run ownerOf events) entry.target true route s))).result
      = some (key, RootFontProvider.observe metrics .rem) := by
  have admitted := FontUnitAdmission.registered_normal_hint_admitted ownerOf events id entry false member
  simp [enqueue, allVisited, hint, admitted, deliver, identity, rebuild, current]

def pseudoKey : Key := ⟨1, true⟩
def normalize : Nat → Key := fun node => if node = 7 then pseudoKey else ⟨node, false⟩
def fixedRoute : List Hop := [⟨true, false⟩, ⟨true, false⟩]
def stoppedRoute : List Hop := [⟨true, false⟩, ⟨false, false⟩]
def fresh : State := { hint := true, provider := RootFontProvider.finish (RootFontProvider.begin RootFontProvider.dirty) }
def stale : State := { hint := true, provider := RootFontProvider.dirty }
def queue (route : List Hop) (s : State) : State :=
  enqueue FontUnitAdmission.idOwner FontUnitAdmission.shared 7 true route s
def good : State := rebuild pseudoKey (deliver normalize (queue fixedRoute fresh))
def noReach : State := rebuild pseudoKey (deliver normalize (queue stoppedRoute fresh))
def staleRead : State := rebuild pseudoKey (deliver normalize (queue fixedRoute stale))
def wrongHost : State := rebuild pseudoKey
  (deliver (fun node => ⟨node, false⟩) (queue fixedRoute fresh))

theorem retained_hint_counterexample : noReach.hint = true ∧ noReach.result = none := by decide +kernel
theorem admission_not_delivery :
    FontUnitAdmission.admits FontUnitAdmission.idOwner true true false FontUnitAdmission.shared 7 = true ∧
    (queue fixedRoute fresh).queued = some 7 ∧ (queue fixedRoute fresh).result = none := by decide +kernel
theorem delivered_not_fresh : staleRead.delivered = some pseudoKey ∧ staleRead.result = none := by decide +kernel
theorem pseudo_mapping_is_required : wrongHost.result = none ∧ (normalize 7).host ≠ 7 := by decide +kernel
theorem fixed_route_can_complete : good.result = some (pseudoKey, .font (.size 23)) := by decide +kernel

end CancellationDelivery
