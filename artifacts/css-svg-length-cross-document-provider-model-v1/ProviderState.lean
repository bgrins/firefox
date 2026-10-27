import CssSemantics.ProviderObservation
import CssSemantics.UnitConversion

namespace CrossDocumentViewport

structure Key where
  generation : Nat
  revision : Nat
  deriving DecidableEq, Repr

structure Extent where
  width : Rat
  height : Rat
  deriving DecidableEq, Repr

structure Certificate where
  key : Key
  extent : Extent
  deriving DecidableEq, Repr

inductive Publication where
  | fallback (extent : Extent)
  | layout (certificate : Certificate)
  deriving DecidableEq, Repr

structure State where
  demand : Key
  required : Extent
  requested : Bool
  completed : Option Certificate
  published : Publication
  deriving DecidableEq, Repr

def readExtent (s : State) : Extent :=
  match s.published with
  | .fallback extent => extent
  | .layout certificate => certificate.extent

def Ready (s : State) : Prop :=
  ∃ certificate, s.published = .layout certificate ∧
    certificate.key = s.demand ∧ certificate.extent = s.required

def request (s : State) : State := { s with requested := true }

def completeEmbedder (s : State) : State :=
  { s with completed := some ⟨s.demand, s.required⟩ }

def publish (s : State) : Option State := do
  let certificate ← s.completed
  if certificate.key = s.demand then
    some { s with published := .layout certificate }
  else none

def resize (extent : Extent) (s : State) : State :=
  { s with demand := ⟨s.demand.generation, s.demand.revision + 1⟩, required := extent, completed := none }

def reconstruct (fallback : Extent) (s : State) : State :=
  { s with demand := ⟨s.demand.generation + 1, 0⟩, completed := none, published := .fallback fallback }

inductive Unit where
  | vw | vh | vmin | vmax | px
  deriving DecidableEq, Repr

def factor (extent : Extent) : Unit → Rat
  | .vw => extent.width / 100
  | .vh => extent.height / 100
  | .vmin => min extent.width extent.height / 100
  | .vmax => max extent.width extent.height / 100
  | .px => 1

def requestQuery (s : State) (unit : Unit) : Option (State × Rat) :=
  CssSemantics.ProviderObservation.query (fun _ _ => true)
    (fun world _ => some (request world))
    (fun world target => some (10 * factor (readExtent world) target)) s unit

theorem request_preserves_readiness (s : State) :
    Ready (request s) ↔ Ready s := by
  rfl

theorem completion_then_publication (s : State) :
    ∃ after, publish (completeEmbedder (request s)) = some after ∧
      Ready after ∧ after.required = s.required ∧ after.demand = s.demand := by
  refine ⟨{ request s with completed := some ⟨s.demand, s.required⟩, published := .layout ⟨s.demand, s.required⟩ }, ?_, ?_, rfl, rfl⟩
  · simp [publish, completeEmbedder, request]
  · exact ⟨⟨s.demand, s.required⟩, rfl, rfl, rfl⟩

theorem ready_extent (s : State) (ready : Ready s) : readExtent s = s.required := by
  obtain ⟨certificate, published, _, extent⟩ := ready
  simp [readExtent, published, extent]

theorem ready_conversion (s : State) (ready : Ready s)
    (input output : CssSemantics.UnitConversion.Representation Unit) (target : Unit)
    (converted : CssSemantics.UnitConversion.convert (factor (readExtent s)) input target = some output) :
    CssSemantics.UnitConversion.Preserves (factor s.required) input target output := by
  apply CssSemantics.UnitConversion.ready_preserves _ _ _ _ _ _ _ converted
  · rw [ready_extent s ready]
  · rw [ready_extent s ready]

theorem resize_invalidates (s : State) (extent : Extent) (ready : Ready s) :
    ¬ Ready (resize extent s) ∧ publish (resize extent s) = none := by
  constructor
  · intro next
    obtain ⟨old, oldPublished, oldKey, _⟩ := ready
    obtain ⟨fresh, freshPublished, freshKey, _⟩ := next
    have same : old = fresh := by
      have pub : Publication.layout old = Publication.layout fresh := oldPublished.symm.trans freshPublished
      exact Publication.layout.inj pub
    subst fresh
    have impossible : s.demand.revision = s.demand.revision + 1 := by
      have eq := congrArg Key.revision (oldKey.symm.trans freshKey)
      exact eq
    exact Nat.ne_add_one _ impossible
  · simp [publish, resize]

theorem reconstruction_invalidates (s : State) (fallback : Extent) :
    ¬ Ready (reconstruct fallback s) ∧ publish (reconstruct fallback s) = none := by
  constructor
  · rintro ⟨certificate, impossible, _, _⟩
    cases impossible
  · simp [publish, reconstruct]

theorem old_generation_publication_rejected (s : State) (fallback : Extent)
    (old : Certificate) (key : old.key = s.demand) :
    publish { reconstruct fallback s with completed := some old } = none := by
  have different : old.key ≠ (reconstruct fallback s).demand := by
    intro equal
    have impossible : s.demand.generation = s.demand.generation + 1 :=
      congrArg Key.generation (key.symm.trans equal)
    exact Nat.ne_add_one _ impossible
  simp [publish, different]

def initial : State :=
  ⟨⟨0, 0⟩, ⟨240, 120⟩, false, some ⟨⟨0, 0⟩, ⟨240, 120⟩⟩,
    .layout ⟨⟨0, 0⟩, ⟨240, 120⟩⟩⟩

def hiddenOnly : State := request (reconstruct ⟨300, 150⟩ initial)
def hiddenResize : State := request (resize ⟨460, 260⟩ (reconstruct ⟨300, 150⟩ initial))

theorem request_alone_counterexample :
    initial.requested = false ∧ Ready initial ∧
    hiddenOnly.requested = true ∧ ¬ Ready hiddenOnly ∧
    readExtent hiddenOnly ≠ hiddenOnly.required ∧
    10 * factor (readExtent hiddenOnly) .vw = 30 ∧
    10 * factor (readExtent hiddenOnly) .vh = 15 ∧
    10 * factor hiddenOnly.required .vw = 24 ∧
    10 * factor hiddenOnly.required .vh = 12 ∧
    publish hiddenOnly = none ∧
    requestQuery (reconstruct ⟨300,150⟩ initial) .vw = some (hiddenOnly,30) := by
  refine ⟨rfl, ⟨⟨⟨0,0⟩,⟨240,120⟩⟩,rfl,rfl,rfl⟩, rfl, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro ready
    exact (reconstruction_invalidates _ _).1 ((request_preserves_readiness _).mp ready)
  · decide +kernel
  · decide +kernel
  · decide +kernel
  · decide +kernel
  · decide +kernel
  · constructor
    · rfl
    · decide +kernel

theorem resize_counterexample :
    hiddenResize.requested = true ∧
    10 * factor (readExtent hiddenResize) .vw = 30 ∧
    10 * factor (readExtent hiddenResize) .vh = 15 ∧
    10 * factor hiddenResize.required .vw = 46 ∧
    10 * factor hiddenResize.required .vh = 26 ∧
    publish hiddenResize = none := by
  decide +kernel

end CrossDocumentViewport

#print axioms CrossDocumentViewport.request_preserves_readiness
#print axioms CrossDocumentViewport.completion_then_publication
#print axioms CrossDocumentViewport.ready_extent
#print axioms CrossDocumentViewport.ready_conversion
#print axioms CrossDocumentViewport.resize_invalidates
#print axioms CrossDocumentViewport.reconstruction_invalidates
#print axioms CrossDocumentViewport.old_generation_publication_rejected
#print axioms CrossDocumentViewport.request_alone_counterexample
#print axioms CrossDocumentViewport.resize_counterexample
