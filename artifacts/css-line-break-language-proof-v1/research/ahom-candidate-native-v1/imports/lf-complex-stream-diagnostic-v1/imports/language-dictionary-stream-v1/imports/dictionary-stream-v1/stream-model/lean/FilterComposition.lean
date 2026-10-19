import CapturedOwnership
import RecordedFilter
import Ownership

namespace LanguageBreak

def breakNumber : BreakKind → Nat
  | .none => 0 | .normal => 1 | .hyphen => 2 | .emergency => 3

def numberBreak : Nat → BreakKind
  | 1 => .normal | 2 => .hyphen | 3 => .emergency | _ => .none

def oldBreaks (old : List BreakKind) (index : Nat) : Nat :=
  breakNumber (old[index]?.getD .none)

def nativeFiltered (category : Nat → HyphenScalarFilter.Category) (mask : Nat → Bool)
    (units : List CodeUnit) (limits : AuxLimits) (old : List BreakKind) : List BreakKind :=
  let filtered := HyphenRecordedFilter.nativeFilter category (units.map Fin.val)
    limits.word.val limits.start.val limits.finish.val mask (oldBreaks old)
  (List.range units.length).map fun i => numberBreak (filtered i)

def referenceFiltered (category : Nat → HyphenScalarFilter.Category) (mask : Nat → Bool)
    (units : List CodeUnit) (limits : AuxLimits) (old : List BreakKind) : List BreakKind :=
  let candidates := HyphenRecordedFilter.referenceCandidates category (units.map Fin.val)
    limits.word.val limits.start.val limits.finish.val mask (oldBreaks old)
  let filtered := HyphenScalarFilter.writes candidates (fun _ => 2) (oldBreaks old)
  (List.range units.length).map fun i => numberBreak (filtered i)

theorem native_filtered_reference (category : Nat → HyphenScalarFilter.Category)
    (mask : Nat → Bool) (units : List CodeUnit) (limits : AuxLimits) (old : List BreakKind) :
    nativeFiltered category mask units limits old = referenceFiltered category mask units limits old := by
  unfold nativeFiltered referenceFiltered
  rw [HyphenRecordedFilter.complete_filter_reference]

theorem native_filtered_length (category : Nat → HyphenScalarFilter.Category)
    (mask : Nat → Bool) (units : List CodeUnit) (limits : AuxLimits) (old : List BreakKind) :
    (nativeFiltered category mask units limits old).length = units.length := by
  simp [nativeFiltered]

theorem changed_filter_position_is_eligible (category : Nat → HyphenScalarFilter.Category)
    (mask : Nat → Bool) (units : List Nat) (minimum pre after : Nat) (old : Nat → Nat) (i : Nat)
    (changed : HyphenRecordedFilter.nativeFilter category units minimum pre after mask old i ≠ old i) :
    ∃ visit ∈ HyphenScalarFilter.referenceVisits category (HyphenScalarFilter.decode units) 0 0,
      visit.index + 1 = i ∧ mask visit.index = true ∧
      pre ≤ visit.countBefore ∧ visit.index + 1 < units.length ∧
      minimum ≤ HyphenScalarFilter.count category (HyphenScalarFilter.decode units) ∧
      after ≤ HyphenScalarFilter.count category (HyphenScalarFilter.decode units) - visit.countBefore := by
  rw [HyphenRecordedFilter.complete_filter_reference,HyphenScalarFilter.writes_at] at changed
  split at changed
  next selected =>
    obtain ⟨candidate,member,index⟩ := selected
    unfold HyphenRecordedFilter.referenceCandidates at member
    obtain ⟨visit,hvisit,heq⟩ := List.mem_map.mp member
    subst candidate
    have eligible := (List.mem_filter.mp hvisit).2
    simp only [HyphenScalarFilter.declarativeEligible,Bool.and_eq_true,decide_eq_true_eq] at eligible
    exact ⟨visit,(List.mem_filter.mp hvisit).1,index,eligible.1.1.1.1,
      eligible.1.1.1.2,eligible.1.1.2,eligible.1.2,eligible.2⟩
  next _ => exact False.elim (changed rfl)

theorem constructed_uniform_filter_reference (providers : StreamProviders) (ops : List Operation)
    (category : Nat → HyphenScalarFilter.Category) (mask : Nat → Bool)
    (limits : AuxLimits) (old : List BreakKind)
    (pending : (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces ≠ [])
    (uniform : ∀ piece ∈ (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces,
      piece.2 = limits) :
    nativeFiltered category mask
      (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.buffer.units
      (runStream providers ⟨initialStream {},[]⟩ ops).state.capturedLimits old =
    referenceFiltered category mask
      (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.buffer.units limits old := by
  rw [constructed_uniform_word_limits providers ops limits pending uniform,native_filtered_reference]

def byteLimit (n : Nat) : Fin 256 := ⟨min 255 n,by omega⟩
def styleLimits (word before after : Option Nat) : AuxLimits :=
  let limits := HyphenOwnership.resolve word before after
  ⟨byteLimit limits.word,byteLimit limits.before,byteLimit limits.after⟩
def externalLimits (limits : AuxLimits) : HyphenOwnership.Limits :=
  ⟨limits.word.val,limits.start.val,limits.finish.val⟩

theorem style_limits_exact_byte_saturation (word before after : Option Nat) :
    externalLimits (styleLimits word before after) =
      HyphenOwnership.saturate (HyphenOwnership.resolve word before after) := rfl

theorem admitted_css_minima_preserved (word before after : Option Nat)
    (w : (HyphenOwnership.resolve word before after).word ≤ 255)
    (b : (HyphenOwnership.resolve word before after).before ≤ 255)
    (a : (HyphenOwnership.resolve word before after).after ≤ 255) :
    externalLimits (styleLimits word before after) = HyphenOwnership.resolve word before after := by
  rw [style_limits_exact_byte_saturation,HyphenOwnership.saturation_exact _ w b a]

def withNativeFilter (providers : StreamProviders)
    (category : Nat → HyphenScalarFilter.Category)
    (mask : Tag → List CodeUnit → Nat → Bool) : StreamProviders :=
  {providers with breaks := {providers.breaks with hyphenate := fun tag units limits old => nativeFiltered category (mask tag units) units limits old}}

def withReferenceFilter (providers : StreamProviders)
    (category : Nat → HyphenScalarFilter.Category)
    (mask : Tag → List CodeUnit → Nat → Bool) : StreamProviders :=
  {providers with breaks := {providers.breaks with hyphenate := fun tag units limits old => referenceFiltered category (mask tag units) units limits old}}

theorem filter_provider_refinement (providers : StreamProviders)
    (category : Nat → HyphenScalarFilter.Category)
    (mask : Tag → List CodeUnit → Nat → Bool) :
    withNativeFilter providers category mask = withReferenceFilter providers category mask := by
  have equality : (fun tag units limits old => nativeFiltered category (mask tag units) units limits old) =
      (fun tag units limits old => referenceFiltered category (mask tag units) units limits old) := by
    funext tag units limits old
    exact native_filtered_reference category (mask tag units) units limits old
  unfold withNativeFilter withReferenceFilter
  rw [equality]

theorem complete_stream_filter_refinement (providers : StreamProviders)
    (category : Nat → HyphenScalarFilter.Category)
    (mask : Tag → List CodeUnit → Nat → Bool) (input : StreamResult) (ops : List Operation) :
    runStream (withNativeFilter providers category mask) input ops =
      runStream (withReferenceFilter providers category mask) input ops := by
  rw [filter_provider_refinement]

end LanguageBreak
