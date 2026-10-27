namespace SvgLengthExtendedPolicy

open CssSemantics.UnitConversion
open SvgLengthFlushPolicy (LengthUnit Tier rank)

inductive FontUnit where
  | ch | rem | ic | cap | lh | rlh | rex | rch | ric | rcap
  deriving DecidableEq, Repr

inductive ViewportUnit where
  | vw | vh | vmin | vmax
  deriving DecidableEq, Repr

inductive Source where
  | legacy (unit : LengthUnit)
  | q
  | font (unit : FontUnit)
  | viewport (unit : ViewportUnit)
  deriving DecidableEq, Repr

def code : Source → Nat
  | .legacy unit => SvgLengthFlushPolicy.code unit
  | .q => 11
  | .font .ch => 12
  | .font .rem => 13
  | .font .ic => 14
  | .font .cap => 15
  | .font .lh => 16
  | .font .rlh => 17
  | .font .rex => 18
  | .font .rch => 19
  | .font .ric => 20
  | .font .rcap => 21
  | .viewport .vw => 22
  | .viewport .vh => 23
  | .viewport .vmin => 24
  | .viewport .vmax => 25

def dependency (viewportTier : Tier) : Source → Tier
  | .legacy unit => SvgLengthFlushPolicy.required unit
  | .q => .none
  | .font _ => .style
  | .viewport _ => viewportTier

def oldSelectorCodes (source target : Nat) : Tier :=
  if SvgLengthFlushPolicy.nativePercentage source || SvgLengthFlushPolicy.nativePercentage target then .layout
  else if SvgLengthFlushPolicy.nativeFont source || SvgLengthFlushPolicy.nativeFont target then .style
  else .none

def nativeAbsolute (unit : Nat) : Bool := unit == 1 || (5 ≤ unit && unit ≤ 11)

def newSelectorCodes (source target : Nat) : Tier :=
  if SvgLengthFlushPolicy.nativePercentage source || SvgLengthFlushPolicy.nativePercentage target then .layout
  else if !nativeAbsolute source || SvgLengthFlushPolicy.nativeFont target then .style
  else .none

def nativeSelected (source : Source) (target : LengthUnit) : Tier :=
  oldSelectorCodes (code source) (SvgLengthFlushPolicy.code target)

def candidateSelected (source : Source) (target : LengthUnit) : Tier :=
  newSelectorCodes (code source) (SvgLengthFlushPolicy.code target)

inductive Access where
  | getter
  | conversion (unit : LengthUnit)
  deriving DecidableEq, Repr

def accessCode : Access → Nat
  | .getter => 0
  | .conversion unit => SvgLengthFlushPolicy.code unit

def sufficient (viewportTier : Tier) (source : Source) (target : LengthUnit) (tier : Tier) : Prop :=
  rank (dependency viewportTier source) ≤ rank tier ∧
  rank (dependency viewportTier (.legacy target)) ≤ rank tier

def selected (viewportTier : Tier) (source : Source) (target : LengthUnit) : Tier :=
  if rank (dependency viewportTier source) ≤ rank (dependency viewportTier (.legacy target)) then
    dependency viewportTier (.legacy target)
  else dependency viewportTier source

def isViewport : Source → Prop
  | .viewport _ => True
  | _ => False

theorem source_code_bounds (source : Source) : 0 < code source ∧ code source ≤ 25 := by
  cases source with
  | legacy unit => cases unit <;> decide
  | q => decide
  | font unit => cases unit <;> decide
  | viewport unit => cases unit <;> decide

theorem same_code_public_identity (source : Source) (target : LengthUnit) :
    code source = code (.legacy target) ↔ source = .legacy target := by
  cases source with
  | legacy unit => cases unit <;> cases target <;> decide
  | q => cases target <;> decide
  | font unit => cases unit <;> cases target <;> decide
  | viewport unit => cases unit <;> cases target <;> decide

theorem public_selector_preserved (source target : LengthUnit) :
    nativeSelected (.legacy source) target = SvgLengthFlushPolicy.selected source target := rfl

theorem native_sufficient_iff (viewportTier : Tier) (source : Source) (target : LengthUnit) :
    sufficient viewportTier source target (nativeSelected source target) ↔
      ¬ isViewport source ∨ rank viewportTier ≤ rank (nativeSelected source target) := by
  unfold sufficient isViewport
  cases viewportTier <;> cases source with
  | legacy unit => cases unit <;> cases target <;> decide
  | q => cases target <;> decide
  | font unit => cases unit <;> cases target <;> decide
  | viewport unit => cases unit <;> cases target <;> decide

theorem layout_profile_characterization (source : Source) (target : LengthUnit) :
    sufficient .layout source target (nativeSelected source target) ↔
      ¬ isViewport source ∨ target = .percentage := by
  unfold sufficient isViewport
  cases source with
  | legacy unit => cases unit <;> cases target <;> decide
  | q => cases target <;> decide
  | font unit => cases unit <;> cases target <;> decide
  | viewport unit => cases unit <;> cases target <;> decide

theorem selected_le_iff (viewportTier : Tier) (source : Source) (target : LengthUnit) (tier : Tier) :
    rank (selected viewportTier source target) ≤ rank tier ↔ sufficient viewportTier source target tier := by
  unfold sufficient
  cases viewportTier <;> cases source with
  | legacy unit => cases unit <;> cases target <;> cases tier <;> decide
  | q => cases target <;> cases tier <;> decide
  | font unit => cases unit <;> cases target <;> cases tier <;> decide
  | viewport unit => cases unit <;> cases target <;> cases tier <;> decide

theorem viewport_style_profile :
    sufficient .style (.viewport .vw) .em .style ∧
    ¬ sufficient .style (.viewport .vw) .px .none ∧
    nativeSelected (.viewport .vw) .em = .style ∧
    nativeSelected (.viewport .vw) .px = .none := by
  unfold sufficient
  decide

theorem candidate_eq_style_join (source : Source) (target : LengthUnit) :
    candidateSelected source target = selected .style source target := by
  cases source with
  | legacy unit => cases unit <;> cases target <;> decide
  | q => cases target <;> decide
  | font unit => cases unit <;> cases target <;> decide
  | viewport unit => cases unit <;> cases target <;> decide

theorem candidate_public_selector_unchanged (source target : LengthUnit) :
    candidateSelected (.legacy source) target = SvgLengthFlushPolicy.selected source target := by
  cases source <;> cases target <;> decide

theorem source_nonviewport_iff (source : Source) :
    code source ≤ 21 ↔ ¬ isViewport source := by
  unfold isViewport
  cases source with
  | legacy unit => cases unit <;> decide
  | q => decide
  | font unit => cases unit <;> decide
  | viewport unit => cases unit <;> decide

theorem access_changes_exactly (source : Source) (access : Access) :
    oldSelectorCodes (code source) (accessCode access) ≠
      newSelectorCodes (code source) (accessCode access) ↔
    isViewport source ∧ oldSelectorCodes (code source) (accessCode access) = .none := by
  unfold isViewport
  cases access with
  | getter =>
    cases source with
    | legacy unit => cases unit <;> decide
    | q => decide
    | font unit => cases unit <;> decide
    | viewport unit => cases unit <;> decide
  | conversion target =>
    cases source with
    | legacy unit => cases unit <;> cases target <;> decide
    | q => cases target <;> decide
    | font unit => cases unit <;> cases target <;> decide
    | viewport unit => cases unit <;> cases target <;> decide

theorem getter_selection (source : Source) :
    newSelectorCodes (code source) 0 = dependency .style source := by
  cases source with
  | legacy unit => cases unit <;> decide
  | q => decide
  | font unit => cases unit <;> decide
  | viewport unit => cases unit <;> decide

theorem invalid_source_zero_outside_domain :
    oldSelectorCodes 0 0 = .none ∧ newSelectorCodes 0 0 = .style ∧
    ∀ source : Source, code source ≠ 0 := by
  refine ⟨by decide, by decide, ?_⟩
  intro source zero
  have positive := (source_code_bounds source).1
  simp [zero] at positive

def ProviderContract (viewportTier : Tier) {State : Type} (force : Tier → State → Option State)
    (sample : State → Source → Rat) (current : Source → Rat) : Prop :=
  ∀ tier before after, SvgLengthFlushPolicy.acquire force tier before = some after →
    ∀ unit, rank (dependency viewportTier unit) ≤ rank tier → sample after unit = current unit

theorem sufficient_conversion_preserves (viewportTier : Tier) {State : Type}
    (force : Tier → State → Option State) (sample : State → Source → Rat)
    (current : Source → Rat) (contract : ProviderContract viewportTier force sample current)
    (input output : Representation Source) (target : LengthUnit)
    (tier : Tier) (before after : State)
    (enough : sufficient viewportTier input.unit target tier)
    (completed : SvgLengthFlushPolicy.acquire force tier before = some after)
    (converted : convert (sample after) input (.legacy target) = some output) :
    Preserves current input (.legacy target) output := by
  exact ready_preserves _ _ _ _ _
    (contract _ _ _ completed input.unit enough.1)
    (contract _ _ _ completed (.legacy target) enough.2) converted

theorem native_preserves_when_covered (viewportTier : Tier) {State : Type}
    (force : Tier → State → Option State) (sample : State → Source → Rat)
    (current : Source → Rat) (contract : ProviderContract viewportTier force sample current)
    (input output : Representation Source) (target : LengthUnit) (before after : State)
    (covered : ¬ isViewport input.unit ∨ rank viewportTier ≤ rank (nativeSelected input.unit target))
    (completed : SvgLengthFlushPolicy.acquire force (nativeSelected input.unit target) before = some after)
    (converted : convert (sample after) input (.legacy target) = some output) :
    Preserves current input (.legacy target) output :=
  sufficient_conversion_preserves viewportTier force sample current contract input output target _ before after
    ((native_sufficient_iff _ _ _).mpr covered) completed converted

theorem joined_preserves (viewportTier : Tier) {State : Type}
    (force : Tier → State → Option State) (sample : State → Source → Rat)
    (current : Source → Rat) (contract : ProviderContract viewportTier force sample current)
    (input output : Representation Source) (target : LengthUnit) (before after : State)
    (completed : SvgLengthFlushPolicy.acquire force (selected viewportTier input.unit target) before = some after)
    (converted : convert (sample after) input (.legacy target) = some output) :
    Preserves current input (.legacy target) output :=
  sufficient_conversion_preserves viewportTier force sample current contract input output target _ before after
    ((selected_le_iff _ _ _ _).mp (Nat.le_refl _)) completed converted

theorem candidate_preserves_with_style_provider {State : Type}
    (force : Tier → State → Option State) (sample : State → Source → Rat)
    (current : Source → Rat) (contract : ProviderContract .style force sample current)
    (input output : Representation Source) (target : LengthUnit) (before after : State)
    (completed : SvgLengthFlushPolicy.acquire force (candidateSelected input.unit target) before = some after)
    (converted : convert (sample after) input (.legacy target) = some output) :
    Preserves current input (.legacy target) output := by
  rw [candidate_eq_style_join] at completed
  exact joined_preserves .style force sample current contract input output target before after completed converted

theorem getter_factor_ready_with_style_provider {State : Type}
    (force : Tier → State → Option State) (sample : State → Source → Rat)
    (current : Source → Rat) (contract : ProviderContract .style force sample current)
    (source : Source) (before after : State)
    (completed : SvgLengthFlushPolicy.acquire force (newSelectorCodes (code source) 0) before = some after) :
    sample after source = current source := by
  rw [getter_selection] at completed
  exact contract _ _ _ completed source (Nat.le_refl _)

structure Snapshot where
  cssWidth : Rat
  cssHeight : Rat
  svgAxis : Rat
  deriving DecidableEq, Repr

def basis (s : Snapshot) : Source → Rat
  | .viewport .vw => s.cssWidth / 100
  | .viewport .vh => s.cssHeight / 100
  | .viewport .vmin => min s.cssWidth s.cssHeight / 100
  | .viewport .vmax => max s.cssWidth s.cssHeight / 100
  | .legacy .percentage => s.svgAxis / 100
  | .q => 120 / 127
  | .legacy .cm => 4800 / 127
  | .legacy .mm => 480 / 127
  | .legacy .inch => 96
  | .legacy .pt => 4 / 3
  | .legacy .pc => 16
  | _ => 1

def stale : Snapshot := ⟨200, 100, 200⟩
def fresh : Snapshot := ⟨400, 100, 400⟩
def refresh : Tier → Snapshot → Option Snapshot
  | .layout, _ => some fresh
  | .style, state => some { state with cssWidth := fresh.cssWidth, cssHeight := fresh.cssHeight }
  | .none, state => some state

theorem refresh_contract : ProviderContract .style refresh basis (basis fresh) := by
  intro tier before after completed unit enough
  cases tier <;>
    simp only [SvgLengthFlushPolicy.acquire, refresh, Option.some.injEq] at completed <;>
    subst after <;> cases unit with
  | legacy unit => cases unit <;>
      simp_all [dependency, SvgLengthFlushPolicy.required, rank, basis]
  | q => rfl
  | font unit => rfl
  | viewport unit => cases unit <;> simp_all [dependency, rank, basis]

theorem viewport_source_stale_counterexample :
    nativeSelected (.viewport .vw) .px = .none ∧
    SvgLengthFlushPolicy.acquire refresh (nativeSelected (.viewport .vw) .px) stale = some stale ∧
    convert (basis stale) ⟨.viewport .vw, 10⟩ (.legacy .px) = some ⟨.legacy .px, 20⟩ ∧
    ¬ Preserves (basis fresh) ⟨.viewport .vw, 10⟩ (.legacy .px) ⟨.legacy .px, 20⟩ ∧
    convert (basis fresh) ⟨.viewport .vw, 10⟩ (.legacy .px) = some ⟨.legacy .px, 40⟩ := by
  unfold Preserves
  decide +kernel

theorem percentage_target_requests_layout :
    nativeSelected (.viewport .vw) .percentage = .layout ∧
    SvgLengthFlushPolicy.acquire refresh (nativeSelected (.viewport .vw) .percentage) stale = some fresh ∧
    convert (basis fresh) ⟨.viewport .vw, 10⟩ (.legacy .percentage) = some ⟨.legacy .percentage, 10⟩ := by
  decide +kernel

theorem stale_ratio_can_cancel :
    basis stale (.viewport .vw) ≠ basis fresh (.viewport .vw) ∧
    basis stale (.legacy .percentage) ≠ basis fresh (.legacy .percentage) ∧
    convert (basis stale) ⟨.viewport .vw, 10⟩ (.legacy .percentage) = some ⟨.legacy .percentage, 10⟩ ∧
    Preserves (basis fresh) ⟨.viewport .vw, 10⟩ (.legacy .percentage) ⟨.legacy .percentage, 10⟩ := by
  unfold Preserves
  decide +kernel

theorem candidate_viewport_refresh_witness :
    candidateSelected (.viewport .vw) .px = .style ∧
    SvgLengthFlushPolicy.acquire refresh (candidateSelected (.viewport .vw) .px) stale =
      some ⟨400, 100, 200⟩ ∧
    convert (basis ⟨400, 100, 200⟩) ⟨.viewport .vw, 10⟩ (.legacy .px) = some ⟨.legacy .px, 40⟩ ∧
    Preserves (basis fresh) ⟨.viewport .vw, 10⟩ (.legacy .px) ⟨.legacy .px, 40⟩ := by
  unfold Preserves
  decide +kernel

#print axioms source_code_bounds
#print axioms same_code_public_identity
#print axioms public_selector_preserved
#print axioms native_sufficient_iff
#print axioms layout_profile_characterization
#print axioms selected_le_iff
#print axioms viewport_style_profile
#print axioms sufficient_conversion_preserves
#print axioms native_preserves_when_covered
#print axioms joined_preserves
#print axioms source_nonviewport_iff
#print axioms access_changes_exactly
#print axioms getter_selection
#print axioms invalid_source_zero_outside_domain
#print axioms getter_factor_ready_with_style_provider
#print axioms candidate_eq_style_join
#print axioms candidate_public_selector_unchanged
#print axioms candidate_preserves_with_style_provider
#print axioms candidate_viewport_refresh_witness
#print axioms refresh_contract
#print axioms viewport_source_stale_counterexample
#print axioms percentage_target_requests_layout
#print axioms stale_ratio_can_cancel

end SvgLengthExtendedPolicy
