import FlexViolationCaller.Model

namespace FlexViolationCaller

def InitialTarget : Prop :=
  ∀ seeds grow wantsInfo, SeedsValid seeds →
    CountAgrees (initialLine seeds) ∧
    (initialLine seeds).items = seeds.map seedItem ∧
    (earlyWalk grow ((initialLine seeds).items.length - (initialLine seeds).frozenCount)
      (initialLine seeds).items).left = 0 ∧
    (start seeds grow wantsInfo).line.items = (seeds.map seedItem).map (earlyItem grow) ∧
    LineValid (start seeds grow wantsInfo).line

def HistoryTarget : Prop :=
  ∀ seeds grow wantsInfo state, SeedsValid seeds → History seeds grow wantsInfo state →
    LineValid state.line ∧
    state.line.items.map ItemState.fields = seeds.map Seed.fields ∧
    state.line.items.length = seeds.length ∧
    state.line.items.length - state.line.frozenCount = remaining state.line ∧
    remaining state.line ≤ seeds.length - state.iteration ∧
    state.iteration ≤ seeds.length ∧
    (state.finished = false → state.iteration < seeds.length) ∧
    (state.finished = true → remaining state.line = 0)

def PassTarget : Prop :=
  ∀ seeds grow wantsInfo state values,
    SeedsValid seeds → History seeds grow wantsInfo state → state.finished = false →
    ProviderValid state.line values →
    ∃ pass, runPass state.iteration state.line values = some pass ∧
      FlexViolation.Acquired ((active pass.prepared.items).map asItem) ∧
      pass.clamped.left = 0 ∧ pass.helper.left = 0 ∧
      ClampedFrom pass.prepared.items pass.clamped.items ∧
      FlexViolation.wideFold ((active pass.prepared.items).map asItem) = some pass.clamped.violation ∧
      pass.clamped.violation = FlexViolation.total ((active pass.prepared.items).map asItem) ∧
      FrozenPreserved state.line.items pass.after.items ∧
      LineValid pass.after ∧
      state.line.frozenCount ≤ pass.after.frozenCount ∧
      (0 < remaining state.line → remaining pass.after < remaining state.line)

def SelectionTarget : Prop :=
  ∀ seeds grow wantsInfo state values pass,
    SeedsValid seeds → History seeds grow wantsInfo state → state.finished = false →
    ProviderValid state.line values → runPass state.iteration state.line values = some pass →
    newlySelected pass.prepared.items pass.after.items =
      FlexViolation.frozen ((active pass.prepared.items).map asItem)

def FallbackTarget : Prop :=
  ∀ seeds grow wantsInfo state values pass,
    SeedsValid seeds → History seeds grow wantsInfo state → state.finished = false →
    ProviderValid state.line values → runPass state.iteration state.line values = some pass →
    pass.helper.fallback = false ∧
    (state.iteration + 1 = seeds.length → remaining state.line ≤ 1 ∧ remaining pass.after = 0)

def CompletionTarget : Prop :=
  ∀ seeds grow wantsInfo state, SeedsValid seeds → History seeds grow wantsInfo state →
    state.iteration = seeds.length → state.finished = true ∧ remaining state.line = 0

def preferredMax : Int := 2 ^ 30 - 1
def boundedDelta (delta : Int) : Int := max (-preferredMax) (min preferredMax delta)

def DeltaAdmissionTarget : Prop :=
  ∀ base delta minimum maximum : Int,
    0 ≤ base → base ≤ preferredMax →
    0 ≤ minimum → minimum ≤ maximum → maximum ≤ preferredMax →
    FlexViolation.Fits32 (base + boundedDelta delta) ∧
    FlexViolation.clamped ⟨0, base + boundedDelta delta, minimum, maximum⟩ =
      FlexViolation.clamped ⟨0, base + delta, minimum, maximum⟩

def normalSeed (identity : Nat) (base minimum maximum : Int)
    (growZero shrinkZero : Bool := false) : Seed :=
  ⟨⟨identity, base, minimum, maximum, growZero, shrinkZero⟩, none⟩

def strutSeed (identity : Nat) : Seed :=
  ⟨⟨identity, 0, 0, 0, true, true⟩, some (0, false, false)⟩

def twoSeeds : List Seed := [normalSeed 9 5 0 10, normalSeed 9 5 0 10]

def earlySeeds : List Seed :=
  [strutSeed 0, normalSeed 1 5 7 10, normalSeed 2 8 0 6,
    normalSeed 3 4 0 10 false true]

def twoPassControl : Option (Pass × Pass × LoopState) := do
  let initial := start twoSeeds true false
  let first ← runPass initial.iteration initial.line [-1, 5]
  let middle := advance initial first
  let second ← runPass middle.iteration middle.line [123, 5]
  return (first, second, advance middle second)

def JointTarget : Prop :=
  (SeedsValid twoSeeds ∧ ∃ first second final,
    twoPassControl = some (first, second, final) ∧
    History twoSeeds true false final ∧
    final.finished = true ∧ final.iteration = 2 ∧ final.line.frozenCount = 2 ∧
    final.line.items.map (fun item => (item.fields.identity, item.current)) = [(9,0),(9,5)] ∧
    first.helper.fallback = false ∧ second.helper.fallback = false ∧
    remaining first.after = 1 ∧ Fresh first.after.items) ∧
  (SeedsValid earlySeeds ∧ (initialLine earlySeeds).frozenCount = 1 ∧
    (start earlySeeds false false).line.frozenCount = 3 ∧
    (start earlySeeds false false).line.items.map (·.frozen) = [true,true,false,true] ∧
    (start earlySeeds true false).line.frozenCount = 2 ∧
    (start earlySeeds true false).line.items.map (·.frozen) = [true,false,true,false]) ∧
  (SeedsValid [strutSeed 0] ∧
    (start [strutSeed 0] true false).finished = true ∧
    (start [strutSeed 0] true true).finished = false ∧
    ∃ pass, runPass 0 (start [strutSeed 0] true true).line [123] = some pass ∧
      pass.after = (start [strutSeed 0] true true).line ∧
      pass.helper.fallback = false ∧
      (advance (start [strutSeed 0] true true) pass).finished = true) ∧
  ((start [] false false).finished = true ∧ (start [] false true).finished = true)

def UniversalTarget : Prop :=
  InitialTarget ∧ HistoryTarget ∧ PassTarget ∧ SelectionTarget ∧
  FallbackTarget ∧ CompletionTarget ∧ DeltaAdmissionTarget ∧ JointTarget

end FlexViolationCaller
