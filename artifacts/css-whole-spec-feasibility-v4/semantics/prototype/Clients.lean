import Protocol

namespace CssProtocol

def sizingClient (key : SizeKey) : Plan Nat :=
  .ask (.size key) fun basis => .done (match basis with
    | .initial => 20
    | .definite px => 20 + px / 2)

inductive EffectObservation where
  | inactive
  | position (progress translated : Nat)
  deriving DecidableEq, Repr

def animationClient (sample : SampleKey) (usedBasis : SizeKey) : Plan EffectObservation :=
  .ask (.sample sample) fun progress => match progress with
    | none => .done .inactive
    | some fraction => .ask (.size usedBasis) fun basis =>
      .done (.position fraction (match basis with
        | .initial => 0
        | .definite px => fraction * px / 100))

def intrinsicKey : SizeKey := ⟨7, 3, 8, .intrinsic⟩
def usedKey : SizeKey := ⟨7, 3, 8, .used⟩
def sampledKey : SampleKey := ⟨2, 5⟩

def fixture : Provider
  | _, .size key => match key.phase with
    | .intrinsic => .initial
    | .used => .definite 100
  | _, .sample key => if key.epoch = 5 then some 25 else some 75

def phaseErased : Provider
  | _, .size _ => .initial
  | _, .sample key => fixture (.sample key)

def latestOnly : Provider
  | _, .size key => fixture (.size key)
  | _, .sample key => fixture (.sample { key with epoch := 8 })

def inactive : Provider
  | _, .size key => fixture (.size key)
  | _, .sample _ => none

def demo : Plan (Nat × EffectObservation) :=
  bind (sizingClient intrinsicKey) fun contribution =>
    bind (animationClient sampledKey usedKey) fun effect => .done (contribution, effect)

theorem sizing_substitution (left right : Provider) (key : SizeKey)
    (agree : AgreesOn left right (run left (sizingClient key)).2) :
    run left (sizingClient key) = run right (sizingClient key) :=
  actual_footprint_sufficient _ _ _ agree

theorem animation_substitution (left right : Provider) (sample : SampleKey) (used : SizeKey)
    (agree : AgreesOn left right (run left (animationClient sample used)).2) :
    run left (animationClient sample used) = run right (animationClient sample used) :=
  actual_footprint_sufficient _ _ _ agree

theorem joint_substitution (left right : Provider)
    (agree : AgreesOn left right (run left demo).2) :
    run left demo = run right demo := actual_footprint_sufficient _ _ _ agree

theorem demo_nonvacuous : (run fixture demo).1 = (20, .position 25 25) := by decide

theorem phase_erasure_changes_result : (run fixture demo).1 ≠ (run phaseErased demo).1 := by decide

theorem epoch_erasure_changes_result : (run fixture demo).1 ≠ (run latestOnly demo).1 := by decide

theorem unsuccessful_request_remains_dependency :
    (⟨Option Nat, .sample sampledKey⟩ : PackedRequest) ∈
      (run inactive (animationClient sampledKey usedKey)).2 := by
  simp [run, animationClient]

theorem inactive_avoids_size_request :
    (run inactive (animationClient sampledKey usedKey)).2 = [⟨Option Nat, .sample sampledKey⟩] := rfl

theorem inactive_change_is_observable :
    (run inactive (animationClient sampledKey usedKey)).1 ≠
      (run fixture (animationClient sampledKey usedKey)).1 := by decide

def repeatSample (key : SampleKey) : Plan (Option Nat × Option Nat) :=
  .ask (.sample key) fun first => .ask (.sample key) fun second => .done (first, second)

theorem same_key_same_episode (provider : Provider) (key : SampleKey) :
    (run provider (repeatSample key)).1.1 = (run provider (repeatSample key)).1.2 := rfl

theorem changing_reply_not_one_episode :
    ¬ ∃ provider : Provider,
      (run provider (repeatSample sampledKey)).1 = (some 25, some 75) := by
  rintro ⟨provider, result⟩
  have same := same_key_same_episode provider sampledKey
  rw [result] at same
  contradiction

def requestName : PackedRequest → String
  | ⟨_, .size key⟩ => s!"size({key.subject},{key.owner},epoch={key.epoch},{repr key.phase})"
  | ⟨_, .sample key⟩ => s!"sample({key.timeline},epoch={key.epoch})"

def showResult (label : String) (provider : Provider) : IO Unit := do
  let (result, trace) := run provider demo
  IO.println s!"{label}: {repr result}; requests={trace.map requestName}"

def main : IO Unit := do
  showResult "fixture" fixture
  showResult "phase-erased" phaseErased
  showResult "latest-only" latestOnly
  showResult "inactive" inactive

#print axioms actual_footprint_sufficient
#print axioms run_bind
#print axioms sizing_substitution
#print axioms animation_substitution
#print axioms joint_substitution
#print axioms demo_nonvacuous
#print axioms phase_erasure_changes_result
#print axioms epoch_erasure_changes_result
#print axioms unsuccessful_request_remains_dependency
#print axioms inactive_avoids_size_request
#print axioms same_key_same_episode
#print axioms changing_reply_not_one_episode
#print axioms inactive_change_is_observable

end CssProtocol

def main := CssProtocol.main
