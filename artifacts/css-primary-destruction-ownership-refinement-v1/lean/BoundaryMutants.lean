import NestedWitness

namespace Destruction.Ownership

def omitLength (capacity : Capacity) (buffer : Option Address) (length : Nat) : Bool :=
  match buffer with
  | none => true
  | some a => decide (length ≤ capacity a)

def compareAddressAndRole (xs ys : List Release) : Bool :=
  xs.all fun x => ys.all fun y => !(x.address == y.address && x.role == y.role)

def aliasTable : PropertyTable := ⟨some 91, [.itemCache 30]⟩

def aliasOwners : Heap :=
  write twoOwners 2 (some (.frame 3 true aliasTable))

theorem omitted_length_accepts_missing_buffer : omitLength roomy none 1 = true := rfl

theorem role_sensitive_separation_accepts_address_alias :
    compareAddressAndRole [⟨30, .itemCache⟩] [⟨30, .itemsBuffer⟩] = true := rfl

theorem alias_owner_individually_represented : Represented aliasOwners roomy aliasTable := by
  refine ⟨?_, [⟨30, .itemCache⟩, ⟨91, .propertiesBuffer⟩], rfl, by decide, ?_⟩
  · simp [TableShape, ArrayShape, PropertyShape, aliasTable, roomy]
  · intro x member
    simp only [List.mem_cons, List.not_mem_nil, or_false] at member
    rcases member with rfl | rfl <;> unfold Allocation <;> decide

theorem alias_world_rejected : ¬ World aliasOwners roomy := by
  intro world
  have separation := world.separated 0 2 1 3 true true oneTable aliasTable
    [⟨30, .itemCache⟩, ⟨90, .propertiesBuffer⟩]
    [⟨30, .itemCache⟩, ⟨91, .propertiesBuffer⟩]
    (by decide) (by decide) (by decide) rfl rfl
  exact cross_owner_same_root_rejected separation

def aliasAfter : Heap := referenceErase (detached aliasOwners 0 1 true)
  [⟨30, .itemCache⟩, ⟨90, .propertiesBuffer⟩]

theorem alias_execution : removeAll aliasOwners 0 = some aliasAfter := by
  apply phase_complete aliasOwners 0 1 true oneTable
    [⟨30, .itemCache⟩, ⟨90, .propertiesBuffer⟩] (by decide) rfl (by decide)
  intro x member
  simp only [List.mem_cons, List.not_mem_nil, or_false] at member
  rcases member with rfl | rfl <;> unfold Allocation <;> decide

theorem local_ownership_does_not_protect_other_owner :
    aliasAfter 2 = some (.frame 3 true aliasTable) ∧ aliasAfter 30 = none ∧
      (removeAll aliasAfter 2).isNone = true := by decide

def noDetach : Heap := referenceErase nestedOwners nestedReleases

theorem no_detach_retains_stale_table :
    noDetach 0 = some (.frame 1 true nestedTable) ∧ noDetach 30 = none := by decide

theorem no_detach_not_represented : ¬ World noDetach roomy := by
  intro world
  obtain ⟨_, xs, plan, _, live⟩ := world.represented 0 1 true nestedTable (by decide)
  have same : xs = nestedReleases := Option.some.inj (plan.symm.trans nested_plan)
  subst xs
  have wrong := live ⟨30, .itemCache⟩ (by simp [nestedReleases])
  have empty : noDetach 30 = none := by decide
  simp [Allocation, empty] at wrong

theorem captured_pointer_claim_is_false :
    nestedAfter 30 ≠ some (.allocation .itemCache) := by decide

end Destruction.Ownership
