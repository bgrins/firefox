import Watches

namespace AttributeWatches

def absentEntry : Entry := ⟨7, 5, [⟨11, none⟩]⟩
def oldEntry : Entry := ⟨7, 5, [⟨11, some 5⟩]⟩
def equalEntry : Entry := ⟨7, 5, [⟨12, some 5⟩]⟩
def one := install empty 1 oldEntry
def shared := install one 2 oldEntry

def dropAbsent (s : State) (id : Nat) (e : Entry) : State :=
  let names := (e.queries.filter fun q => q.value.isSome).map Query.name
  let watches := (id, (⟨e.target, names⟩ : Watch)) :: eraseId id s.published
  { install s id e with published := watches }

def equalSkip (s : State) (id : Nat) (e : Entry) : State :=
  if (entryAt s id).any (fun old => old.endpoint == e.endpoint) then
    { install s id e with published := s.published }
  else install s id e

def removeTargetWatches (s : State) (id : Nat) : State :=
  match entryAt s id with
  | none => remove s id
  | some e =>
    let watches := s.published.filter fun pair => pair.2.target != e.target
    { remove s id with published := watches }

theorem absent_read_admitted : 7 ∈ (change (install empty 1 absentEntry) 7 11).pending := by decide +kernel

theorem equal_value_new_query_admitted : 7 ∈ (change (install one 1 equalEntry) 7 12).pending := by decide +kernel

theorem cancelled_one_survivor_admitted : 7 ∈ (change (remove shared 1) 7 11).pending := by decide +kernel

theorem retarget_drops_old_watch :
    watching (install one 1 { oldEntry with target := 8 }) 7 11 = false ∧
    watching (install one 1 { oldEntry with target := 8 }) 8 11 = true := by decide +kernel

theorem absent_mutant_misses : (change (dropAbsent empty 1 absentEntry) 7 11).pending = [] := by decide +kernel

theorem equal_mutant_misses : (change (equalSkip one 1 equalEntry) 7 12).pending = [] := by decide +kernel

theorem removal_mutant_misses : (change (removeTargetWatches shared 1) 7 11).pending = [] := by decide +kernel

end AttributeWatches
