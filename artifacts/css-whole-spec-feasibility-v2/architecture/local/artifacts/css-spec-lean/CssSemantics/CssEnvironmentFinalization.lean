import CssSemantics.CssEnvironmentRefinement
import CssSemantics.CssFinalizedSource

namespace CssSemantics.CssEnvironmentFinalization

open CssNumericFinalization
open CssFinalizedSource (Result Attempt assemble assess Assessed assess_iff)

def parseSource (mode : CssCalcSource.Mode) (types : CssCalculationType.Context) (environment : CssNumericEnvironment.Environment) (stage : Stage)
    (availability : Availability) (source : String) : Option Attempt :=
  (CssEnvironmentSource.parseSource mode types environment source).map (assemble types stage availability)

def Attempted (mode : CssCalcSource.Mode) (types : CssCalculationType.Context) (environment : CssNumericEnvironment.Environment) (stage : Stage)
    (availability : Availability) (source : String) (attempt : Attempt) : Prop :=
  CssEnvironmentSource.Attempted mode types environment source attempt.original ∧
    attempt.result = attempt.original.result.map (assess types stage availability)

theorem parseSource_iff (mode types environment stage availability source attempt) :
    parseSource mode types environment stage availability source = some attempt ↔ Attempted mode types environment stage availability source attempt := by
  constructor
  · intro equal
    obtain ⟨original, known, same⟩ := Option.map_eq_some_iff.mp equal
    cases same
    exact ⟨(CssEnvironmentSource.parseSource_iff _ _ _ _ _).mp known, rfl⟩
  · rintro ⟨parsed, equal⟩
    unfold parseSource
    rw [(CssEnvironmentSource.parseSource_iff _ _ _ _ _).mpr parsed]
    cases attempt
    simp_all [assemble]

theorem parseSource_total (mode types environment stage availability source) :
    ∃ attempt, parseSource mode types environment stage availability source = some attempt := by
  obtain ⟨original, equal⟩ := CssEnvironmentSource.parseSource_total mode types environment source
  exact ⟨assemble types stage availability original, by simp [parseSource, equal]⟩

def parseRaw (mode : CssCalcSource.Mode) (types : CssCalculationType.Context) (environment : CssNumericEnvironment.Environment) (stage : Stage)
    (availability : Availability) (source : String) : Option Result :=
  (CssEnvironmentSource.parseRaw mode types environment source).map (assess types stage availability)

def Parsed (mode : CssCalcSource.Mode) (types : CssCalculationType.Context) (environment : CssNumericEnvironment.Environment) (stage : Stage)
    (availability : Availability) (source : String) (result : Result) : Prop :=
  ∃ original, CssEnvironmentSource.Parsed mode types environment source original ∧ Assessed types stage availability original result

theorem parseRaw_iff (mode types environment stage availability source result) :
    parseRaw mode types environment stage availability source = some result ↔ Parsed mode types environment stage availability source result := by
  constructor
  · intro equal
    obtain ⟨original, known, same⟩ := Option.map_eq_some_iff.mp equal
    exact ⟨original, (CssEnvironmentSource.parseRaw_iff _ _ _ _ _).mp known, (assess_iff _ _ _ _ _).mp same⟩
  · rintro ⟨original, parsed, assessed⟩
    simp [parseRaw, (CssEnvironmentSource.parseRaw_iff _ _ _ _ _).mpr parsed, (assess_iff _ _ _ _ _).mpr assessed]

theorem parseRaw_source (mode types environment stage availability source) :
    parseRaw mode types environment stage availability source = (parseSource mode types environment stage availability source).bind (·.result) := by
  obtain ⟨original, equal⟩ := CssEnvironmentSource.parseSource_total mode types environment source
  simp [parseRaw, parseSource, CssEnvironmentSource.parseRaw, equal, assemble]

theorem parseSource_original (mode types environment stage availability source) :
    (parseSource mode types environment stage availability source).map (·.original) =
      CssEnvironmentSource.parseSource mode types environment source := by
  simp [parseSource, assemble, Option.map_map, Function.comp_def]

theorem parseRaw_none_iff (mode types environment stage availability source) :
    parseRaw mode types environment stage availability source = none ↔ CssEnvironmentSource.parseRaw mode types environment source = none := by
  simp [parseRaw]

theorem Parsed.provenance {mode types environment stage availability source output}
    (parsed : Parsed mode types environment stage availability source (.finalized output)) :
    ∃ type value context, CssEnvironmentSource.Parsed mode types environment source (.supported type value) ∧
      Ready stage availability context ∧ context.Valid ∧
      CssCalculationType.Matches types context.production type ∧ Finished context value output := by
  obtain ⟨original, sourceParsed, assessed⟩ := parsed
  obtain ⟨type, value, context, equal, ready, valid, admitted, finished⟩ := assessed.provenance
  exact ⟨type, value, context, equal ▸ sourceParsed, ready, valid, admitted, finished⟩

theorem Parsed.bounded {mode types environment stage availability source output}
    (parsed : Parsed mode types environment stage availability source (.finalized output)) :
    ∃ context, Ready stage availability context ∧ context.Valid ∧
      context.bounds.lower ≤ output.value ∧ output.value ≤ context.bounds.upper := by
  obtain ⟨_, _, context, _, ready, valid, _, finished⟩ := parsed.provenance
  exact ⟨context, ready, valid, finished.bounded valid⟩

theorem Parsed.at_used {mode types environment availability source output}
    (parsed : Parsed mode types environment .computed availability source (.finalized output)) :
    Parsed mode types environment .used availability source (.finalized output) := by
  obtain ⟨type, value, context, sourceParsed, ready, valid, admitted, finished⟩ := parsed.provenance
  exact ⟨.supported type value, sourceParsed, .finalized ready.at_used valid admitted finished⟩

theorem parsed_preserved {mode types stage availability source output} (environment)
    (parsed : CssFinalizedSource.Parsed mode types stage availability source (.finalized output)) :
    Parsed mode types environment stage availability source (.finalized output) := by
  obtain ⟨type, value, context, sourceParsed, ready, valid, admitted, finished⟩ := parsed.provenance
  exact ⟨.supported type value, CssEnvironmentRefinement.parsed_preserved environment sourceParsed,
    .finalized ready valid admitted finished⟩

theorem parseRaw_preserved {mode types stage availability source output} (environment)
    (parsed : CssFinalizedSource.parseRaw mode types stage availability source = some (.finalized output)) :
    parseRaw mode types environment stage availability source = some (.finalized output) :=
  (parseRaw_iff _ _ _ _ _ _ _).mpr
    (parsed_preserved environment ((CssFinalizedSource.parseRaw_iff _ _ _ _ _ _).mp parsed))

theorem parseSource_empty (mode types stage availability source) :
    parseSource mode types CssNumericEnvironment.empty stage availability source =
      CssFinalizedSource.parseSource mode types stage availability source := by
  simp [parseSource, CssFinalizedSource.parseSource, CssEnvironmentRefinement.parseSource_empty]

theorem parseRaw_empty (mode types stage availability source) :
    parseRaw mode types CssNumericEnvironment.empty stage availability source =
      CssFinalizedSource.parseRaw mode types stage availability source := by
  simp [parseRaw, CssFinalizedSource.parseRaw, CssEnvironmentRefinement.parseRaw_empty]

end CssSemantics.CssEnvironmentFinalization
