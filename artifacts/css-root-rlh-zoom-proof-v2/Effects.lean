import Nonvacuity
namespace Rlh.Effects
structure Flags where
  fontRelative : Bool
  selfMetrics : Bool
  inheritedMetrics : Bool
  other : Nat
  deriving DecidableEq, Repr
structure Conditions where
  fontSize : Option Rat
  lineHeight : Option Rat
  other : Nat
  deriving DecidableEq, Repr
structure State where
  flags : Flags
  conditions : Conditions
  deriving DecidableEq, Repr
structure Observation where
  numeric : Rlh.Observation
  after : State
  deriving DecidableEq, Repr

def isNormal : Form → Bool
  | .normal _ _ => true
  | _ => false

def addRelative (s : State) : State :=
  {s with flags := {s.flags with fontRelative := true}}
def addSelf (s : State) : State :=
  {s with flags := {s.flags with selfMetrics := true}}
def addInherited (s : State) : State :=
  {s with flags := {s.flags with inheritedMetrics := true}}

def builder (w : World) (s : State) : State :=
  if w.base = .current then
    if isNormal w.current.form then addSelf s else s
  else if isNormal w.inherited.form then addInherited s else s

def candidateEffects (w : World) (s : State) : State :=
  let s := addRelative s
  if w.role = .root then builder w s
  else if w.role = .media then s else s

def originalEffects (w : World) (s : State) : State :=
  let s := addRelative s
  if w.role = .root then builder w s
  else if w.role = .media then s else s

def intended (w : World) (s : State) : State :=
  { flags := {
      fontRelative := true,
      selfMetrics := s.flags.selfMetrics ||
        (decide (w.role = .root ∧ w.base = .current) && isNormal w.current.form),
      inheritedMetrics := s.flags.inheritedMetrics ||
        (decide (w.role = .root ∧ w.base = .inherited) && isNormal w.inherited.form),
      other := s.flags.other },
    conditions := s.conditions }

def candidate (w : World) (s : State) : Observation :=
  ⟨implementation w, candidateEffects w s⟩
def original (w : World) (s : State) : Observation :=
  ⟨Rlh.original w, originalEffects w s⟩
def reference (w : World) (s : State) : Observation :=
  ⟨Rlh.reference w, intended w s⟩

theorem intended_effect_contract (w : World) (s : State) :
    candidateEffects w s = intended w s := by
  cases hr : w.role <;> cases hb : w.base <;>
    cases hc : isNormal w.current.form <;> cases hp : isNormal w.inherited.form <;>
    simp [candidateEffects, intended, builder, addRelative, addSelf, addInherited, hr, hb, hc, hp]

theorem all_role_effect_preservation (w : World) (s : State) :
    originalEffects w s = candidateEffects w s := rfl

theorem full_nonroot_preservation (w : World) (s : State) (h : w.role ≠ .root) :
    original w s = candidate w s := by
  simp [original, candidate, Rlh.nonroot_preservation w h, all_role_effect_preservation]

theorem full_refinement (w : World) (s : State) (h : Valid w) :
    candidate w s = reference w s := by
  simp [candidate, reference, candidate_refines_reference w h, intended_effect_contract]

theorem adds_font_relative (w : World) (s : State) :
    (candidateEffects w s).flags.fontRelative = true := by
  rw [intended_effect_contract]; rfl

theorem preserves_conditions (w : World) (s : State) :
    (candidateEffects w s).conditions = s.conditions := by
  rw [intended_effect_contract]; rfl

theorem preserves_other_flags (w : World) (s : State) :
    (candidateEffects w s).flags.other = s.flags.other := by
  rw [intended_effect_contract]; rfl

theorem retains_self_flag (w : World) (s : State) (h : s.flags.selfMetrics = true) :
    (candidateEffects w s).flags.selfMetrics = true := by
  rw [intended_effect_contract]; simp [intended, h]

theorem retains_inherited_flag (w : World) (s : State) (h : s.flags.inheritedMetrics = true) :
    (candidateEffects w s).flags.inheritedMetrics = true := by
  rw [intended_effect_contract]; simp [intended, h]

theorem no_nondirect_metric_flags (w : World) (s : State) (h : w.role ≠ .root) :
    candidateEffects w s = addRelative s := by
  simp [candidateEffects, h]

theorem direct_current_normal (w : World) (s : State)
    (hr : w.role = .root) (hb : w.base = .current) (hn : isNormal w.current.form = true) :
    candidateEffects w s = addSelf (addRelative s) := by
  simp [candidateEffects, builder, hr, hb, hn]

theorem direct_inherited_normal (w : World) (s : State)
    (hr : w.role = .root) (hb : w.base = .inherited) (hn : isNormal w.inherited.form = true) :
    candidateEffects w s = addInherited (addRelative s) := by
  simp [candidateEffects, builder, hr, hb, hn]

theorem direct_ordinary (w : World) (s : State)
    (hc : isNormal w.current.form = false) (hp : isNormal w.inherited.form = false) :
    candidateEffects w s = addRelative s := by
  cases hr : w.role <;> cases hb : w.base <;>
    simp [candidateEffects, builder, hr, hb, hc, hp]

theorem cache_independent (w : World) (s : State) (value : Rat) :
    candidateEffects {w with cache := ⟨value⟩} s = candidateEffects w s := rfl

def readCandidate (state : Rlh.State) (q : Request) (seed : State) : Observation :=
  ⟨readNative state q, candidateEffects (actualWorld state q) seed⟩
def readReference (state : Rlh.State) (q : Request) (seed : State) : Observation :=
  ⟨Rlh.readReference state q, intended q.world seed⟩

theorem admitted_read_full_refinement (state : Rlh.State) (q : Request) (seed : State)
    (hi : invariant state) (ha : requestAdmitted state q) :
    readCandidate state q seed = readReference state q seed := by
  simp [readCandidate, readReference, read_refinement state q hi ha,
    actualWorld, intended_effect_contract, intended]

def mutateEffects (kind : Nat) (w : World) (s : State) : State :=
  if kind = 1 then
    if w.role = .root then builder w s else s
  else if kind = 2 then addRelative s
  else if kind = 3 then candidateEffects w {s with flags := ⟨false,false,false,0⟩}
  else candidateEffects w s

def mutated (kind : Nat) (w : World) (s : State) : Observation :=
  ⟨implementation w, mutateEffects kind w s⟩

theorem mutants_keep_numerics (kind : Nat) (w : World) (s : State) :
    (mutated kind w s).numeric = (candidate w s).numeric := rfl

def seeded : State := ⟨⟨false,false,true,8⟩,⟨some 13,some 29,7⟩⟩
def normalSample (b : Base) : World :=
  let w := sample .root b (.normal 18 ⟨1,0,1⟩) 1
  {w with inherited := ⟨20,.normal 21 ⟨2,0,1⟩,⟨21⟩⟩}

theorem normal_sample_valid (b : Base) : Valid (normalSample b) := by
  refine ⟨rfl,?_,?_,rfl,rfl,?_,rfl,rfl,rfl⟩
  · simp [normalSample, Provider.Valid, sample, semanticLine, zOne, Rat.mul_one]
  · simp [normalSample, sample, zOne, zTwo, Rat.one_mul]
  · intro _; rfl

theorem seeded_nonempty : seeded.flags.other ≠ 0 ∧
    seeded.conditions.fontSize = some 13 ∧ seeded.conditions.lineHeight = some 29 := by decide

theorem current_normal_witness :
    candidateEffects (normalSample .current) seeded =
      ⟨⟨true,true,true,8⟩,⟨some 13,some 29,7⟩⟩ := by decide

theorem inherited_normal_witness :
    candidateEffects (normalSample .inherited) {seeded with flags := ⟨false,true,false,8⟩} =
      ⟨⟨true,true,true,8⟩,⟨some 13,some 29,7⟩⟩ := by decide

theorem drop_relative_witness :
    mutated 1 (sample .descendant .current (.absolute 20) 1) seeded ≠
      candidate (sample .descendant .current (.absolute 20) 1) seeded := by
  intro h
  have bad := congrArg (fun o => o.after.flags.fontRelative) h
  change false = true at bad
  cases bad

theorem drop_normal_witness :
    mutated 2 (normalSample .current) seeded ≠ candidate (normalSample .current) seeded := by
  intro h
  have bad := congrArg (fun o => o.after.flags.selfMetrics) h
  change false = true at bad
  cases bad

theorem clear_incoming_witness :
    mutated 3 (sample .media .inherited (.numeric (5/4)) 1) seeded ≠
      candidate (sample .media .inherited (.numeric (5/4)) 1) seeded := by
  intro h
  have bad := congrArg (fun o => o.after.flags.other) h
  change 0 = 8 at bad
  cases bad
theorem seeded_ordinary_root (f : Form) :
    candidate (sample .root .inherited f 1) seeded =
      reference (sample .root .inherited f 1) seeded :=
  full_refinement _ _ (sample_valid _ _ _ _)

theorem seeded_media (b : Base) (f : Form) :
    candidate (sample .media b f 1) seeded = reference (sample .media b f 1) seeded :=
  full_refinement _ _ (sample_valid _ _ _ _)

theorem seeded_descendant (b : Base) (f : Form) :
    candidate (sample .descendant b f 1) seeded = reference (sample .descendant b f 1) seeded :=
  full_refinement _ _ (sample_valid _ _ _ _)

theorem seeded_normal_root (b : Base) :
    candidate (normalSample b) seeded = reference (normalSample b) seeded :=
  full_refinement _ _ (normal_sample_valid b)

def stepCandidate (state : Rlh.State) (input : Event × State) : Rlh.State × Option Observation :=
  ((stepNative state input.1).1,
    match input.1 with
    | .read q => some (readCandidate state q input.2)
    | _ => none)

def stepReference (state : Rlh.State) (input : Event × State) : Rlh.State × Option Observation :=
  ((Rlh.stepReference state input.1).1,
    match input.1 with
    | .read q => some (readReference state q input.2)
    | _ => none)

theorem full_step_refinement (state : Rlh.State) (input : Event × State)
    (hi : invariant state) (ha : admitted state input.1) :
    stepCandidate state input = stepReference state input := by
  obtain ⟨event, seed⟩ := input
  cases event with
  | read q =>
    simp only [admitted] at ha
    simp [stepCandidate, stepReference, step_refinement state (.read q) hi ha,
      admitted_read_full_refinement state q seed hi ha]
  | update r => rfl
  | publish => simp [stepCandidate, stepReference, Rlh.stepNative, Rlh.stepReference, publication_refinement]
  | foreignUpdate o => rfl

def runCandidate (state : Rlh.State) : List (Event × State) → Rlh.State × List (Option Observation)
  | [] => (state, [])
  | input :: rest =>
    let next := stepCandidate state input
    let result := runCandidate next.1 rest
    (result.1, next.2 :: result.2)

def runReference (state : Rlh.State) : List (Event × State) → Rlh.State × List (Option Observation)
  | [] => (state, [])
  | input :: rest =>
    let next := stepReference state input
    let result := runReference next.1 rest
    (result.1, next.2 :: result.2)

theorem finite_full_observation_refinement (inputs : List (Event × State)) (state : Rlh.State)
    (hi : invariant state) (ha : admittedTrace state (inputs.map Prod.fst)) :
    runCandidate state inputs = runReference state inputs := by
  induction inputs generalizing state with
  | nil => rfl
  | cons input rest ih =>
    have hstep := full_step_refinement state input hi ha.1
    have hnext : invariant (stepReference state input).1 := by
      have h := step_invariant state input.1 hi
      rw [step_refinement state input.1 hi ha.1] at h
      exact h
    simp only [runCandidate, runReference, hstep]
    rw [ih (stepReference state input).1 hnext ha.2]
end Rlh.Effects

