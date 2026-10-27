import CssSemantics.UnitConversion

namespace SvgLengthFlushPolicy

open CssSemantics.UnitConversion

inductive LengthUnit where
  | number | percentage | em | ex | px | cm | mm | inch | pt | pc
  deriving DecidableEq, Repr

inductive Tier where
  | none | style | layout
  deriving DecidableEq, Repr

def rank : Tier → Nat
  | .none => 0
  | .style => 1
  | .layout => 2

def required : LengthUnit → Tier
  | .percentage => .layout
  | .em | .ex => .style
  | _ => .none

def code : LengthUnit → Nat
  | .number => 1
  | .percentage => 2
  | .em => 3
  | .ex => 4
  | .px => 5
  | .cm => 6
  | .mm => 7
  | .inch => 8
  | .pt => 9
  | .pc => 10

def nativePercentage (unit : Nat) : Bool := unit == 2

def nativeFont (unit : Nat) : Bool :=
  unit == 3 || unit == 4 || (12 ≤ unit && unit ≤ 21)

def selected (source target : LengthUnit) : Tier :=
  if nativePercentage (code source) || nativePercentage (code target) then .layout
  else if nativeFont (code source) || nativeFont (code target) then .style
  else .none

def request (source target : LengthUnit) : Tier :=
  if source = target then .none else selected source target

def Sufficient (source target : LengthUnit) (tier : Tier) : Prop :=
  rank (required source) ≤ rank tier ∧ rank (required target) ≤ rank tier

theorem public_unit_valid (unit : LengthUnit) : 0 < code unit ∧ code unit ≤ 10 := by
  cases unit <;> decide

theorem code_injective (source target : LengthUnit) :
    code source = code target ↔ source = target := by
  cases source <;> cases target <;> decide

theorem selected_le_iff (source target : LengthUnit) (tier : Tier) :
    rank (selected source target) ≤ rank tier ↔ Sufficient source target tier := by
  unfold Sufficient
  cases source <;> cases target <;> cases tier <;> decide

theorem selected_sufficient (source target : LengthUnit) :
    Sufficient source target (selected source target) :=
  (selected_le_iff source target _).mp (Nat.le_refl _)

theorem selected_minimal (source target : LengthUnit) (tier : Tier)
    (enough : Sufficient source target tier) :
    rank (selected source target) ≤ rank tier :=
  (selected_le_iff source target tier).mpr enough

theorem differing_request_minimal (source target : LengthUnit) (tier : Tier)
    (different : source ≠ target) :
    rank (request source target) ≤ rank tier ↔ Sufficient source target tier := by
  simpa [request, different] using selected_le_iff source target tier

theorem distinct_same_tier_still_flushes :
    required .em = required .ex ∧ request .em .ex = .style := by decide

theorem layout_dominates_font :
    request .em .percentage = .layout ∧ request .percentage .ex = .layout := by decide

def acquire {State : Type} (force : Tier → State → Option State)
    (tier : Tier) (before : State) : Option State :=
  match tier with
  | .none => some before
  | _ => force tier before

def ProviderContract {State : Type} (force : Tier → State → Option State)
    (sample : State → LengthUnit → Rat) (current : LengthUnit → Rat) : Prop :=
  ∀ tier before after, acquire force tier before = some after →
    ∀ unit, rank (required unit) ≤ rank tier → sample after unit = current unit

theorem selected_factors_ready {State : Type} (force : Tier → State → Option State)
    (sample : State → LengthUnit → Rat) (current : LengthUnit → Rat)
    (contract : ProviderContract force sample current)
    (source target : LengthUnit) (before after : State)
    (completed : acquire force (selected source target) before = some after) :
    sample after source = current source ∧ sample after target = current target := by
  have enough := selected_sufficient source target
  exact ⟨contract _ _ _ completed source enough.1,
    contract _ _ _ completed target enough.2⟩

def run {State : Type} (force : Tier → State → Option State)
    (sample : State → LengthUnit → Rat) (before : State)
    (input : Representation LengthUnit) (target : LengthUnit) :
    Option (State × Representation LengthUnit) :=
  if input.unit = target then some (before, input)
  else match acquire force (selected input.unit target) before with
    | none => none
    | some after => (convert (sample after) input target).map (fun output => (after, output))

theorem repaired_preserves {State : Type} (force : Tier → State → Option State)
    (sample : State → LengthUnit → Rat) (current : LengthUnit → Rat)
    (contract : ProviderContract force sample current)
    (before after : State) (input output : Representation LengthUnit) (target : LengthUnit)
    (success : run force sample before input target = some (after, output)) :
    Preserves current input target output := by
  unfold run at success
  split at success
  · cases success
    exact ⟨‹_›, rfl⟩
  · cases completed : acquire force (selected input.unit target) before with
    | none => simp [completed] at success
    | some ready =>
      cases converted : convert (sample ready) input target with
      | none => simp [completed, converted] at success
      | some result =>
        simp only [completed, converted, Option.map_some, Option.some.injEq,
          Prod.mk.injEq] at success
        obtain ⟨rfl, rfl⟩ := success
        have factors := selected_factors_ready force sample current contract
          input.unit target before ready completed
        exact ready_preserves _ _ _ _ _ factors.1 factors.2 converted

theorem same_unit_no_force {State : Type} (force : Tier → State → Option State)
    (sample : State → LengthUnit → Rat) (before : State) (input : Representation LengthUnit) :
    request input.unit input.unit = .none ∧
    run force sample before input input.unit = some (before, input) := by
  simp [request, run]

theorem same_unit_preserves_without_contract {State : Type}
    (force : Tier → State → Option State) (sample : State → LengthUnit → Rat)
    (current : LengthUnit → Rat) (before : State) (input : Representation LengthUnit) :
    run force sample before input input.unit = some (before, input) ∧
    Preserves current input input.unit input := by
  exact ⟨(same_unit_no_force force sample before input).2,
    sound current input input input.unit (identity current input)⟩

theorem failed_provider_no_conversion {State : Type} (force : Tier → State → Option State)
    (sample : State → LengthUnit → Rat) (before : State)
    (input : Representation LengthUnit) (target : LengthUnit)
    (different : input.unit ≠ target)
    (failed : acquire force (selected input.unit target) before = none) :
    run force sample before input target = none := by
  simp [run, different, failed]

structure Snapshot where
  viewport : Rat
  font : Rat
  deriving DecidableEq, Repr

def basis (snapshot : Snapshot) : LengthUnit → Rat
  | .percentage => snapshot.viewport / 100
  | .em => snapshot.font
  | .ex => snapshot.font / 2
  | .cm => 4800 / 127
  | .mm => 480 / 127
  | .inch => 96
  | .pt => 4 / 3
  | .pc => 16
  | _ => 1

def fresh : Snapshot := ⟨400, 40⟩
def stale : Snapshot := ⟨200, 20⟩

def refresh : Tier → Snapshot → Option Snapshot
  | .none, snapshot => some snapshot
  | .style, snapshot => some { snapshot with font := fresh.font }
  | .layout, _ => some fresh

theorem refresh_contract : ProviderContract refresh basis (basis fresh) := by
  intro tier before after completed unit enough
  cases tier <;> cases unit <;>
    simp_all [acquire, refresh, required, rank, basis]
  all_goals cases completed; rfl

def sourceOnly (source : LengthUnit) : Tier :=
  if nativePercentage (code source) then .layout
  else if nativeFont (code source) then .style else .none

theorem source_only_target_percentage_counterexample :
    sourceOnly .px = .none ∧
    acquire refresh (sourceOnly .px) stale = some stale ∧
    basis stale .px = basis fresh .px ∧
    convert (basis stale) ⟨.px, 100⟩ .percentage = some ⟨.percentage, 50⟩ ∧
    ¬ Preserves (basis fresh) ⟨.px, 100⟩ .percentage ⟨.percentage, 50⟩ ∧
    run refresh basis stale ⟨.px, 100⟩ .percentage = some (fresh, ⟨.percentage, 25⟩) := by
  unfold Preserves
  decide +kernel

theorem source_only_target_font_counterexample :
    sourceOnly .px = .none ∧
    acquire refresh (sourceOnly .px) stale = some stale ∧
    basis stale .px = basis fresh .px ∧
    convert (basis stale) ⟨.px, 40⟩ .em = some ⟨.em, 2⟩ ∧
    ¬ Preserves (basis fresh) ⟨.px, 40⟩ .em ⟨.em, 2⟩ ∧
    run refresh basis stale ⟨.px, 40⟩ .em = some (⟨200, 40⟩, ⟨.em, 1⟩) := by
  unfold Preserves
  decide +kernel

theorem same_unit_stale_basis_identity :
    basis stale .percentage ≠ basis fresh .percentage ∧
    run refresh basis stale ⟨.percentage, 50⟩ .percentage = some (stale, ⟨.percentage, 50⟩) ∧
    Preserves (basis fresh) ⟨.percentage, 50⟩ .percentage ⟨.percentage, 50⟩ := by
  unfold Preserves
  decide +kernel

def incompleteForce (_ : Tier) (snapshot : Snapshot) : Option Snapshot := some snapshot

theorem tier_selection_without_provider_completion_counterexample :
    request .px .percentage = .layout ∧
    run incompleteForce basis stale ⟨.px, 100⟩ .percentage = some (stale, ⟨.percentage, 50⟩) ∧
    ¬ Preserves (basis fresh) ⟨.px, 100⟩ .percentage ⟨.percentage, 50⟩ ∧
    ¬ ProviderContract incompleteForce basis (basis fresh) := by
  refine ⟨by decide, by decide +kernel, ?_, ?_⟩
  · unfold Preserves
    decide +kernel
  · intro contract
    have equality := contract .layout stale stale rfl .percentage (by decide)
    exact (by decide +kernel : basis stale .percentage ≠ basis fresh .percentage) equality

#print axioms public_unit_valid
#print axioms code_injective
#print axioms selected_le_iff
#print axioms selected_sufficient
#print axioms selected_minimal
#print axioms differing_request_minimal
#print axioms distinct_same_tier_still_flushes
#print axioms layout_dominates_font
#print axioms selected_factors_ready
#print axioms repaired_preserves
#print axioms same_unit_no_force
#print axioms same_unit_preserves_without_contract
#print axioms failed_provider_no_conversion
#print axioms refresh_contract
#print axioms source_only_target_percentage_counterexample
#print axioms source_only_target_font_counterexample
#print axioms same_unit_stale_basis_identity
#print axioms tier_selection_without_provider_completion_counterexample

end SvgLengthFlushPolicy
