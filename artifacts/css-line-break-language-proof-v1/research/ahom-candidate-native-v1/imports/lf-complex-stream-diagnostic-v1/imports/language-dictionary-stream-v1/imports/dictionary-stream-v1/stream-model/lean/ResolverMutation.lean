import WordWitness
import SegmentCache

namespace LanguageBreak

def poisonedInvalid (cache : Cache) (id : Nat) (text : String) : Cache :=
  {cache with retained := some (id,text),initialized := true}

def invalidCache : Cache := poisonedInvalid (resolve witnessProviders {} (.atom 1 "ja")).2 3 "bad_tag"

theorem invalid_poisoning_counterexample :
    (resolve witnessProviders invalidCache (.atom 3 "bad_tag")).1 ≠
      reference witnessProviders (.atom 3 "bad_tag") := by decide

def firstOwnerResolution (p : Providers) (cache : Cache) (first _requested : Tag) : Bool :=
  (resolve p cache first).1

theorem first_owner_substitution_counterexample :
    firstOwnerResolution witnessProviders {} (.atom 1 "ja") (.atom 2 "en") ≠
      reference witnessProviders (.atom 2 "en") := by decide

def enState : Cache × WordLanguage := updateLanguage witnessProviders {} {} (.atom 2 "en")

def staleFlush (word : WordLanguage) : WordLanguage := {word with mixed := false}

theorem reset_stale_language_counterexample :
    (updateLanguage witnessProviders enState.1 (staleFlush enState.2) (.atom 1 "ja")).2.script ≠
      (updateLanguage witnessProviders enState.1 (flushLanguage enState.2) (.atom 1 "ja")).2.script := by decide

def cacheWitnessKey (cjk : Bool) : SegmentKey :=
  ⟨[⟨3585,by decide⟩,⟨65,by decide⟩,⟨176,by decide⟩,⟨65,by decide⟩],0,1,cjk⟩

def cacheWitnessProvider (key : SegmentKey) : List BreakKind :=
  if key.cjk then [.normal,.none,.normal,.none] else [.normal,.none,.none,.none]

def omitLanguageMatch (key : SegmentKey) (entry : SegmentEntry) : Option (List BreakKind) :=
  if key.units = entry.key.units ∧ key.wordPolicy = entry.key.wordPolicy ∧ key.linePolicy = entry.key.linePolicy
  then some entry.answer else none

def cachedEnglish : SegmentEntry := ⟨cacheWitnessKey false,cacheWitnessProvider (cacheWitnessKey false)⟩

theorem omitted_cache_language_counterexample :
    omitLanguageMatch (cacheWitnessKey true) cachedEnglish ≠
      some (cacheWitnessProvider (cacheWitnessKey true)) := by decide

end LanguageBreak

def main : IO Unit := do
  let poisoned := (LanguageBreak.resolve LanguageBreak.witnessProviders LanguageBreak.invalidCache (.atom 3 "bad_tag")).1
  let correctPoison := LanguageBreak.reference LanguageBreak.witnessProviders (.atom 3 "bad_tag")
  let correctFirst := LanguageBreak.reference LanguageBreak.witnessProviders (.atom 2 "en")
  let firstOwner := LanguageBreak.firstOwnerResolution LanguageBreak.witnessProviders {} (.atom 1 "ja") (.atom 2 "en")
  let staleReset := (LanguageBreak.updateLanguage LanguageBreak.witnessProviders LanguageBreak.enState.1
    (LanguageBreak.staleFlush LanguageBreak.enState.2) (.atom 1 "ja")).2.script
  let correctReset := (LanguageBreak.updateLanguage LanguageBreak.witnessProviders LanguageBreak.enState.1
    (LanguageBreak.flushLanguage LanguageBreak.enState.2) (.atom 1 "ja")).2.script
  let cache := LanguageBreak.omitLanguageMatch (LanguageBreak.cacheWitnessKey true) LanguageBreak.cachedEnglish
  let correctCache := some (LanguageBreak.cacheWitnessProvider (LanguageBreak.cacheWitnessKey true))
  IO.println s!"invalid-poisoning mutant={poisoned} reference={correctPoison}"
  IO.println s!"first-owner-substitution mutant={firstOwner} reference={correctFirst}"
  IO.println s!"reset-stale-language mutant={staleReset} reference={correctReset}"
  IO.println s!"cache-omits-language mutant={repr cache} reference={repr correctCache}"
  if poisoned == correctPoison || firstOwner == correctFirst || staleReset == correctReset || cache == correctCache then
    throw (IO.userError "mutation survived")
