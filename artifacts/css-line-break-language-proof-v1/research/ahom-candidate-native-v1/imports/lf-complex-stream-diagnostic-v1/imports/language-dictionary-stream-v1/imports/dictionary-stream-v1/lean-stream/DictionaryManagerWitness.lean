import DictionaryManagerSequence

namespace HyphenDictionaryWitness

open HyphenDictionaryManager HyphenDictionaryFallback

def requested : Key := [100,101,45,68,69]
def alias : Key := [100,101,45,97,108,105,97,115]
def fuzzy : Key := [100,101,45,42]

def fixture : State :=
  { HyphenDictionarySequence.initial with
    patterns := replace (replace (fun _ => none) fuzzy (some 1)) alias (some 0)
    aliases := replace (fun _ => none) requested (some alias)
    capitalized := fun key => key = alias }

def get (state : State) (key : Key) : Result :=
  nativeGet (fun resource => resource == 1) fallback ((trimWildcard key).length+1) state key

theorem invalid_alias_stops_then_later_fallback :
    (get fixture requested).answer = none ∧
    (get fixture requested).events = [.load alias 0 true,.remove alias] ∧
    (get (get fixture requested).state requested).answer = some ⟨1,false⟩ ∧
    (get (get fixture requested).state requested).events = [.load fuzzy 1 false] := by decide

def cached : State := (get (get fixture requested).state requested).state

def preferenceChanged : State := {cached with capitalized := fun _ => true}

theorem cached_preference_and_pressure :
    (get preferenceChanged requested).answer = some ⟨1,false⟩ ∧
    (get preferenceChanged requested).events = [] ∧
    (get (pressure preferenceChanged) requested).answer = some ⟨1,true⟩ ∧
    (get (pressure preferenceChanged) requested).events = [.load fuzzy 1 true] := by decide

def aliasChain : State :=
  { HyphenDictionarySequence.initial with
    patterns := replace (fun _ => none) [99,99] (some 1)
    aliases := replace (replace (fun _ => none) [98,98] (some [99,99])) [97,97] (some [98,98]) }

theorem aliases_are_not_recursively_chased :
    (get aliasChain [97,97]).answer = none ∧ (get aliasChain [97,97]).events = [] := by decide

theorem wildcard_and_one_byte_parent :
    allKeys [100,101,45,68,69,45,49,57,57,54] =
      [[100,101,45,68,69,45,49,57,57,54],[100,101,45,68,69,45,42],[100,101,45,42]] ∧
    allKeys [120,45,85,83] = [[120,45,85,83]] := by
  rw [←complete_candidate_keys 11 [100,101,45,68,69,45,49,57,57,54] (by decide),
    ←complete_candidate_keys 5 [120,45,85,83] (by decide)]
  decide

end HyphenDictionaryWitness
