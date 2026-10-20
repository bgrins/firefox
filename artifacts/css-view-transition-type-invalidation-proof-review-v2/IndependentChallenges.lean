import Boundaries
namespace IndependentChallenges
open TypeInvalidation

def splitDelivery : State :=
  flush fixture (flush fixture addAlpha [.root]) [.descendant 0, .pseudo 0]

example : splitDelivery.cache .root = 100 ∧
    splitDelivery.cache (.descendant 0) = 43 ∧
    splitDelivery.cache (.pseudo 0) = 71 ∧ splitDelivery.pending = true := by
  decide +kernel

def changedBetween : State :=
  mutate fixture (flush fixture addAlpha [.root]) 7 (.delete 0) true

example : changedBetween.cache .root = 100 ∧
    expected fixture changedBetween .root = 10 ∧ changedBetween.pending = true := by
  decide +kernel

example : (flush fixture changedBetween fixture.subjects).cache .root = 10 ∧
    (flush fixture changedBetween fixture.subjects).cache (.descendant 0) = 17 ∧
    (flush fixture changedBetween fixture.subjects).pending = false := by
  decide +kernel

example : (flush fixture missingAdd fixture.subjects).cache .root = 10 ∧
    expected fixture missingAdd .root = 100 ∧
    (flush fixture missingAdd fixture.subjects).pending = false := by
  decide +kernel

def ownedState := freshState fixture (fun id => if id = 7 then [0] else [])
def handedOff := { fixture with owner := some 8 }

example : ownedState.cache .root = 100 ∧ expected handedOff ownedState .root = 10 ∧
    ownedState.pending = false := by decide +kernel

example : evaluate false [0] (.negated (.activeType 0)) = true ∧
    resolve false [0] .root 10 [⟨.root, .negated (.activeType 0), 99⟩] = 99 := by
  decide +kernel

example (e : Environment) (s : State) (visited : List Subject) (subject : Subject)
    (pending : s.pending = true) (member : subject ∈ visited) :
    (flush e s visited).cache subject = expected e s subject := by
  simp [flush, pending, member]

example : (flush { fixture with subjects := [] } missingAdd []).pending = false ∧
    (flush { fixture with subjects := [] } missingAdd []).cache .root = 10 := by
  decide +kernel

end IndependentChallenges
