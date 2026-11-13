import FlexViolationCaller.Target

namespace FlexViolationCaller

def emptyPass : Pass :=
  ⟨⟨[], 0⟩, ⟨[], 0, 0, 0, false⟩, ⟨[], 0, 0, 0, false⟩, ⟨[], 0⟩⟩

def firstPass : Pass :=
  (runPass 0 (start twoSeeds true false).line [-1,5]).getD emptyPass

def middleState : LoopState := advance (start twoSeeds true false) firstPass

def secondPass : Pass := (runPass middleState.iteration middleState.line [123,5]).getD emptyPass

def finalState : LoopState := advance middleState secondPass

theorem two_seed_domain : SeedsValid twoSeeds := by
  unfold SeedsValid SeedValid FieldsValid
  decide

theorem two_pass_history : History twoSeeds true false finalState := by
  have hfirst : History twoSeeds true false middleState := by
    apply History.step History.initial
    · decide
    · decide
    · unfold ProviderValid
      decide
    · decide
  apply History.step hfirst
  · decide
  · decide
  · unfold ProviderValid
    decide
  · decide

theorem two_pass_joint : SeedsValid twoSeeds ∧ History twoSeeds true false finalState ∧
    twoPassControl = some (firstPass, secondPass, finalState) ∧
    finalState.finished = true ∧ finalState.iteration = 2 ∧ finalState.line.frozenCount = 2 ∧
    finalState.line.items.map (fun item => (item.fields.identity, item.current)) = [(9,0),(9,5)] ∧
    firstPass.helper.fallback = false ∧ secondPass.helper.fallback = false ∧
    remaining firstPass.after = 1 ∧ Fresh firstPass.after.items := by
  refine ⟨two_seed_domain, two_pass_history, ?_⟩
  unfold Fresh
  decide

end FlexViolationCaller
