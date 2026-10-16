/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import RelativeProofs

open Aeneas Aeneas.Std Relative RelativeProofs

namespace CacheProofs
noncomputable section

abbrev Key := relative_filter.Key
abbrev Entry := relative_filter.Entry
abbrev Map := std.collections.hash.map.HashMap Key Entry std.hash.random.RandomState Global
abbrev Handle := std.collections.hash.map.Entry Key Entry Global
abbrev View := Key → Option Entry

noncomputable def write (view : View) (key : Key) (entry : Entry) : View := by
  classical
  exact fun query => if query = key then some entry else view query

def entryValue (entry : Entry) : Option Filter :=
  match entry with
  | .Lookup => none
  | .HasFilter filter => some filter

def access (map : Map) (key : Key) :=
  std.collections.hash.map.HashMap.entry relative_filter.Key.Insts.CoreCmpEq
    relative_filter.Key.Insts.CoreHashHash
    std.hash.random.RandomState.Insts.CoreHashBuildHasherDefaultHasher map key

def AccessContract (view : Map → View) (map : Map) (key : Key)
    (handle : Handle) (back : Handle → Map) : Prop :=
  match handle with
  | .Vacant handle =>
    view map key = none ∧
    std.collections.hash.map.VacantEntry.insert handle relative_filter.Entry.Lookup ⦃ result =>
      result.1 = relative_filter.Entry.Lookup ∧ ∀ entry,
      view (back (.Vacant (result.2 entry))) = write (view map) key entry ⦄
  | .Occupied handle =>
    ∃ previous, view map key = some previous ∧
    std.collections.hash.map.OccupiedEntry.get_mut handle ⦃ result =>
      result.1 = previous ∧ ∀ entry,
      std.collections.hash.map.OccupiedEntry.into_mut (result.2.1 entry) ⦃ result' =>
        result'.1 = entry ∧ ∀ written,
        view (back (.Occupied (result.2.2 (result'.2 written)))) = write (view map) key written ⦄ ⦄

structure MapContract (view : Map → View) where
  entry_spec : ∀ map key, access map key ⦃ result => AccessContract view map key result.1 result.2 ⦄
  borrow_filter : ∀ filter : Filter, Box.Insts.CoreConvertAsRef.as_ref Global filter = .ok filter

inductive LookupStep (update : Entry → Entry → Prop) : Option Entry → Option Filter → Entry → Prop where
  | first : LookupStep update none none .Lookup
  | occupied (previous next : Entry) (transition : update previous next) :
      LookupStep update (some previous) (entryValue next) next

theorem get_filter_spec {E : Type} (ops : tree.Element E) (element : E) (identity : Usize)
    (hidentity : ops.«opaque» element = .ok identity) (kind : Kind)
    (view : Map → View) (contract : MapContract view)
    (update : Entry → Entry → Prop)
    (hupdate : ∀ previous, relative_filter.Entry.update ops previous element kind ⦃ next =>
      update previous next ⦄)
    (map : relative_filter.RelativeSelectorFilterMap) :
    relative_filter.RelativeSelectorFilterMap.get_filter ops map element kind ⦃ result =>
      ∃ next, LookupStep update (view map.map (identity, kind)) result.1 next ∧
        view result.2.map = write (view map.map) (identity, kind) next ⦄ := by
  unfold relative_filter.RelativeSelectorFilterMap.get_filter
  simp only [hidentity]
  have hentry := contract.entry_spec map.map (identity, kind)
  unfold access at hentry
  step with hentry as ⟨handle, back, haccess⟩
  cases handle with
  | Vacant handle =>
    rcases haccess with ⟨hmissing, hinsert⟩
    step with hinsert as ⟨result, heq, hwrite⟩
    rcases result with ⟨value, insert_back⟩
    dsimp at heq hwrite
    subst value
    simp
    exact ⟨.Lookup, by simpa [hmissing] using LookupStep.first (update := update), hwrite .Lookup⟩
  | Occupied handle =>
    obtain ⟨previous, hpresent, hget⟩ := haccess
    step with hget as ⟨result, heq, hinto⟩
    rcases result with ⟨value, get_back, get_back1⟩
    dsimp at heq hinto
    subst value
    step with hupdate previous as ⟨next, htransition⟩
    step with hinto next as ⟨result, heq, hwrite⟩
    rcases result with ⟨value, into_back⟩
    dsimp at heq hwrite
    subst value
    cases next with
    | Lookup =>
      simp
      exact ⟨.Lookup, by simpa [hpresent, entryValue] using LookupStep.occupied previous .Lookup htransition,
        hwrite .Lookup⟩
    | HasFilter filter =>
      simp [contract.borrow_filter]
      exact ⟨.HasFilter filter,
        by simpa [hpresent, entryValue] using LookupStep.occupied previous (.HasFilter filter) htransition,
        hwrite (.HasFilter filter)⟩

def EntrySound (covers : Key → Filter → Prop) (key : Key) (entry : Entry) : Prop :=
  match entry with
  | .Lookup => True
  | .HasFilter filter => covers key filter

def EpochSound (view : Map → View) (covers : Key → Filter → Prop) (map : Map) : Prop :=
  ∀ key entry, view map key = some entry → EntrySound covers key entry

theorem first_lookup_without_build {E : Type} (ops : tree.Element E) (element : E) (identity : Usize)
    (hidentity : ops.«opaque» element = .ok identity) (kind : Kind)
    (view : Map → View) (contract : MapContract view)
    (map : relative_filter.RelativeSelectorFilterMap)
    (hmissing : view map.map (identity, kind) = none) :
    relative_filter.RelativeSelectorFilterMap.get_filter ops map element kind ⦃ result =>
      result.1 = none ∧ view result.2.map = write (view map.map) (identity, kind) .Lookup ⦄ := by
  unfold relative_filter.RelativeSelectorFilterMap.get_filter
  simp only [hidentity]
  have hentry := contract.entry_spec map.map (identity, kind)
  unfold access at hentry
  step with hentry as ⟨handle, back, haccess⟩
  cases handle with
  | Vacant handle =>
    rcases haccess with ⟨_, hinsert⟩
    step with hinsert as ⟨result, heq, hwrite⟩
    rcases result with ⟨value, insert_back⟩
    dsimp at heq hwrite
    subst value
    simpa using hwrite .Lookup
  | Occupied handle =>
    obtain ⟨previous, hpresent, _⟩ := haccess
    rw [hmissing] at hpresent
    cases hpresent

theorem update_preserves_coverage {E : Type} (ops : tree.Element E) (element : E) (kind : Kind)
    (covers : Key → Filter → Prop) (key : Key)
    (hbuild : relative_filter.add_to_filter ops element empty kind ⦃ result =>
      result.1 = true → covers key result.2 ⦄)
    (previous : Entry) :
    relative_filter.Entry.update ops previous element kind ⦃ next =>
      EntrySound covers key previous → EntrySound covers key next ⦄ := by
  cases previous with
  | HasFilter filter => simp [reuse_filter]
  | Lookup =>
    unfold relative_filter.Entry.update
    simp [new_eq_empty]
    step with hbuild as ⟨success, filter, hcoverage⟩
    cases success <;> simp_all [EntrySound]

theorem get_filter_preserves_epoch {E : Type} (ops : tree.Element E) (element : E) (identity : Usize)
    (hidentity : ops.«opaque» element = .ok identity) (kind : Kind)
    (view : Map → View) (contract : MapContract view) (covers : Key → Filter → Prop)
    (hbuild : relative_filter.add_to_filter ops element empty kind ⦃ result =>
      result.1 = true → covers (identity, kind) result.2 ⦄)
    (map : relative_filter.RelativeSelectorFilterMap) (hepoch : EpochSound view covers map.map) :
    relative_filter.RelativeSelectorFilterMap.get_filter ops map element kind ⦃ result =>
      EpochSound view covers result.2.map ∧
      ∀ filter, result.1 = some filter → covers (identity, kind) filter ⦄ := by
  classical
  have hget := get_filter_spec ops element identity hidentity kind view contract
    (fun previous next => EntrySound covers (identity, kind) previous → EntrySound covers (identity, kind) next)
    (update_preserves_coverage ops element kind covers (identity, kind) hbuild) map
  apply WP.spec_mono hget
  intro result hresult
  obtain ⟨next, hstep, hview⟩ := hresult
  generalize hprevious : view map.map (identity, kind) = previous at hstep
  generalize hreturned : result.1 = returned at hstep
  have hsound : EntrySound covers (identity, kind) next := by
    cases hstep with
    | first => trivial
    | occupied previous next transition =>
      apply transition
      apply hepoch
      assumption
  constructor
  · intro key entry hentry
    rw [hview] at hentry
    by_cases heq : key = (identity, kind)
    · subst key
      simp [write] at hentry
      split at hentry
      · have he := Option.some.inj hentry
        subst next
        exact hsound
      · rename_i hne
        exact False.elim (hne rfl)
    · have hprior : view map.map key = some entry := by
        simpa [write, heq] using hentry
      exact hepoch key entry hprior
  · intro filter hfilter
    cases hstep with
    | first => cases hfilter
    | occupied previous next transition =>
      cases next with
      | Lookup => cases hfilter
      | HasFilter stored =>
        have heq : stored = filter := Option.some.inj hfilter
        subst filter
        exact hsound

#print axioms get_filter_spec
#print axioms first_lookup_without_build
#print axioms update_preserves_coverage
#print axioms get_filter_preserves_epoch

end
end CacheProofs
