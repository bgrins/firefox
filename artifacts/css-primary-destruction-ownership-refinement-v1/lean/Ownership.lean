import Representation

namespace Destruction.Ownership

theorem other_frame_survives (h next : Heap) (owner content : Address)
    (bit : Bool) (table : PropertyTable)
    (selected : h owner = some (.frame content bit table))
    (success : removeAll h owner = some next)
    (other c : Address) (b : Bool) (p : PropertyTable)
    (present : h other = some (.frame c b p)) (different : other ≠ owner) :
    next other = some (.frame c b p) := by
  obtain ⟨xs, _, execution⟩ :=
    phase_execution h next owner content bit table selected success
  exact protected_cell _ next xs other (.frame c b p)
    (by simpa [detached, write, different] using present) rfl execution

theorem other_frame_was_present (h next : Heap) (owner content : Address)
    (bit : Bool) (table : PropertyTable)
    (selected : h owner = some (.frame content bit table))
    (success : removeAll h owner = some next)
    (other c : Address) (b : Bool) (p : PropertyTable)
    (present : next other = some (.frame c b p)) (different : other ≠ owner) :
    h other = some (.frame c b p) := by
  obtain ⟨xs, _, execution⟩ :=
    phase_execution h next owner content bit table selected success
  rw [freeMany_reference _ _ _ execution] at present
  by_cases erased : other ∈ xs.map Release.address
  · simp [referenceErase, erased] at present
  · simpa [referenceErase, erased, detached, write, different] using present

theorem selected_frame_empty (h next : Heap) (owner content : Address)
    (bit : Bool) (table : PropertyTable)
    (selected : h owner = some (.frame content bit table))
    (success : removeAll h owner = some next) :
    next owner = some (.frame content bit emptyTable) := by
  obtain ⟨xs, _, execution⟩ :=
    phase_execution h next owner content bit table selected success
  exact protected_cell _ next xs owner (.frame content bit emptyTable)
    (by simp [detached, write]) rfl execution

theorem other_allocations_survive (h next : Heap) (owner content : Address)
    (bit : Bool) (table : PropertyTable) (xs ys : List Release)
    (selected : h owner = some (.frame content bit table))
    (planned : tablePlan table = some xs)
    (success : removeAll h owner = some next)
    (separate : SeparatePlans xs ys) (allocated : Allocated h ys) :
    Allocated next ys := by
  obtain ⟨actual, planActual, execution⟩ :=
    phase_execution h next owner content bit table selected success
  have same : actual = xs := Option.some.inj (planActual.symm.trans planned)
  subst actual
  intro release member
  have ready := allocation_survives_detach h owner content bit table selected
    release (allocated release member)
  have outside := separate_no_address xs ys separate release member
  rw [freeMany_reference _ _ _ execution]
  simpa [Allocation, referenceErase, outside] using ready

theorem represented_after_cleanup (h next : Heap) (capacity : Capacity)
    (owner content : Address) (bit : Bool) (table : PropertyTable)
    (selected : h owner = some (.frame content bit table))
    (world : World h capacity) (success : removeAll h owner = some next) :
    AllRepresented next capacity := by
  obtain ⟨xs, planned, _⟩ :=
    phase_execution h next owner content bit table selected success
  intro other c b p present
  by_cases same : other = owner
  · subst other
    rw [selected_frame_empty h next owner content bit table selected success] at present
    have equality : emptyTable = p := by
      simpa using congrArg
        (fun value : Option Cell => match value with
          | some (.frame _ _ props) => props
          | _ => emptyTable) present
    rw [← equality]
    exact represented_empty next capacity
  · have earlier := other_frame_was_present h next owner content bit table
      selected success other c b p present same
    obtain ⟨shape, ys, otherPlan, unique, ready⟩ :=
      world.represented other c b p earlier
    refine ⟨shape, ys, otherPlan, unique, ?_⟩
    exact other_allocations_survive h next owner content bit table xs ys
      selected planned success
      (world.separated owner other content c bit b table p xs ys
        selected earlier (Ne.symm same) planned otherPlan) ready

theorem separation_after_cleanup (h next : Heap) (capacity : Capacity)
    (owner content : Address) (bit : Bool) (table : PropertyTable)
    (selected : h owner = some (.frame content bit table))
    (world : World h capacity) (success : removeAll h owner = some next) :
    OwnersSeparated next := by
  intro first second c d b e p q xs ys firstLive secondLive different firstPlan secondPlan
  have emptyPlan (p : PropertyTable) (c : Address) (b : Bool) (rs : List Release)
      (live : next owner = some (.frame c b p)) (planP : tablePlan p = some rs) :
      rs = [] := by
    rw [selected_frame_empty h next owner content bit table selected success] at live
    have equality : emptyTable = p := by
      simpa using congrArg
        (fun value : Option Cell => match value with
          | some (.frame _ _ props) => props
          | _ => emptyTable) live
    rw [← equality] at planP
    simpa [tablePlan, emptyTable, plan, optional] using planP.symm
  by_cases firstIsOwner : first = owner
  · subst first
    rw [emptyPlan p c b xs firstLive firstPlan]
    intro x member; simp at member
  · by_cases secondIsOwner : second = owner
    · subst second
      rw [emptyPlan q d e ys secondLive secondPlan]
      intro x memberX y memberY; simp at memberY
    · exact world.separated first second c d b e p q xs ys
        (other_frame_was_present h next owner content bit table selected success
          first c b p firstLive firstIsOwner)
        (other_frame_was_present h next owner content bit table selected success
          second d e q secondLive secondIsOwner)
        different firstPlan secondPlan

theorem world_after_cleanup (h next : Heap) (capacity : Capacity)
    (owner content : Address) (bit : Bool) (table : PropertyTable)
    (selected : h owner = some (.frame content bit table))
    (world : World h capacity) (success : removeAll h owner = some next) :
    World next capacity :=
  ⟨represented_after_cleanup h next capacity owner content bit table selected world success,
   separation_after_cleanup h next capacity owner content bit table selected world success⟩

theorem represented_cleanup_executes (h : Heap) (capacity : Capacity)
    (owner content : Address) (bit : Bool) (table : PropertyTable)
    (selected : h owner = some (.frame content bit table))
    (world : World h capacity) :
    ∃ next, removeAll h owner = some next ∧ World next capacity := by
  obtain ⟨_, xs, planned, unique, ready⟩ :=
    world.represented owner content bit table selected
  have success := phase_complete h owner content bit table xs selected planned unique ready
  exact ⟨_, success, world_after_cleanup h _ capacity owner content bit table
    selected world success⟩

theorem untouched_owner_cleanup_remains_executable (h next : Heap) (capacity : Capacity)
    (owner content : Address) (bit : Bool) (table : PropertyTable)
    (selected : h owner = some (.frame content bit table))
    (world : World h capacity) (success : removeAll h owner = some next)
    (other c : Address) (b : Bool) (p : PropertyTable)
    (present : h other = some (.frame c b p)) (different : other ≠ owner) :
    ∃ after, removeAll next other = some after ∧ World after capacity :=
  represented_cleanup_executes next capacity other c b p
    (other_frame_survives h next owner content bit table selected success
      other c b p present different)
    (world_after_cleanup h next capacity owner content bit table selected world success)

end Destruction.Ownership
