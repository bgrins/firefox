import DictionaryManager

namespace HyphenDictionaryFallback

open HyphenDictionaryManager

def trimWildcard (key : Key) : Key :=
  match key.reverse with
  | 42::45::rest => rest.reverse
  | _ => key

def dashIndices (key : Key) : List Nat :=
  (List.range key.length).filter fun index => key[index]?.getD 0 == 45

def fallback (key : Key) : Option Key :=
  let stem := trimWildcard key
  match (dashIndices stem).getLast? with
  | none => none
  | some index => if index > 1 then some (stem.take index ++ [45,42]) else none

theorem trim_generated_wildcard (stem : Key) : trimWildcard (stem++[45,42]) = stem := by
  simp [trimWildcard,List.reverse_append]

theorem fallback_decreases (key next : Key) (found : fallback key = some next) :
    (trimWildcard next).length < (trimWildcard key).length := by
  dsimp only [fallback] at found
  split at found
  · cases found
  next index present =>
    split at found
    next positive =>
      cases found
      rw [trim_generated_wildcard,List.length_take]
      have bound := List.mem_range.mp (List.mem_filter.mp (List.mem_of_getLast? present)).1
      omega
    · cases found

theorem fallback_selected_prefix (key next : Key) (found : fallback key = some next) :
    ∃ index, 1 < index ∧ index < (trimWildcard key).length ∧
      (trimWildcard key)[index]?.getD 0 = 45 ∧
      (dashIndices (trimWildcard key)).getLast? = some index ∧
      next = (trimWildcard key).take index ++ [45,42] := by
  dsimp only [fallback] at found
  split at found
  · cases found
  next index present =>
    split at found
    next positive =>
      cases found
      have member := List.mem_filter.mp (List.mem_of_getLast? present)
      exact ⟨index,positive,List.mem_range.mp member.1,by simpa using member.2,present,rfl⟩
    · cases found

def allKeys (key : Key) : List Key :=
  key :: (match _found : fallback key with
    | none => []
    | some next => allKeys next)
termination_by (trimWildcard key).length
decreasing_by exact fallback_decreases key next _found

theorem complete_candidate_keys (fuel : Nat) (key : Key)
    (enough : (trimWildcard key).length < fuel) :
    candidateKeys fallback fuel key = allKeys key := by
  induction fuel generalizing key with
  | zero => omega
  | succ fuel ih =>
    rw [candidateKeys,allKeys]
    cases found : fallback key with
    | none => simp only [found]
    | some next =>
      simp only [found]
      rw [ih next (by have bound := fallback_decreases key next found;omega)]

theorem no_fuel_cutoff (valid : Resource → Bool) (state : State) (key : Key) :
    nativeGet valid fallback ((trimWildcard key).length+1) state key =
      referenceGet valid state (allKeys key) := by
  rw [all_candidates_exact,complete_candidate_keys _ _ (by omega)]

theorem wildcard_strictly_shortens_stem (stem next : Key)
    (found : fallback (stem++[45,42]) = some next) :
    (trimWildcard next).length < stem.length := by
  have result := fallback_decreases _ next found
  simpa only [trim_generated_wildcard] using result

theorem no_fallback_for_no_dash (key : Key) (empty : dashIndices (trimWildcard key) = []) :
    fallback key = none := by simp [fallback,empty]

end HyphenDictionaryFallback
