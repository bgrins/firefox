import Std

namespace Destruction

abbrev Address := Nat

inductive Role where
  | itemCache | fragment | shared | linesBuffer | itemsBuffer | propertiesBuffer | unrelated
  deriving DecidableEq, Repr

structure Release where
  address : Address
  role : Role
  deriving DecidableEq, Repr

structure LinePayload where
  buffer : Option Address
  frames : List Address
  deriving DecidableEq, Repr

inductive Property where
  | itemCache (root : Address)
  | fragment (root : Address)
  | shared (root : Address) (linesBuffer : Option Address) (lines : List LinePayload)
  | foreign (root : Address)
  deriving DecidableEq, Repr

def optional (role : Role) (a : Option Address) : List Release :=
  a.toList.map (fun address => ⟨address, role⟩)

def footprint : Property → Option (List Release)
  | .itemCache root => some [⟨root, .itemCache⟩]
  | .fragment root => some [⟨root, .fragment⟩]
  | .shared root buffer lines =>
      some (lines.flatMap (fun line => optional .itemsBuffer line.buffer) ++
        optional .linesBuffer buffer ++ [⟨root, .shared⟩])
  | .foreign _ => none

def plan : List Property → Option (List Release)
  | [] => some []
  | p :: ps => (footprint p).bind fun first => (plan ps).map (first ++ ·)

structure PropertyTable where
  buffer : Option Address
  entries : List Property
  deriving DecidableEq, Repr

def emptyTable : PropertyTable := ⟨none, []⟩

def tablePlan (table : PropertyTable) : Option (List Release) :=
  (plan table.entries).map (· ++ optional .propertiesBuffer table.buffer)

inductive Cell where
  | frame (content : Address) (primaryBit : Bool) (properties : PropertyTable)
  | content (primary : Option Address)
  | allocation (role : Role)
  deriving DecidableEq, Repr

abbrev Heap := Address → Option Cell

def write (h : Heap) (address : Address) (value : Option Cell) : Heap :=
  fun x => if x = address then value else h x

def freeOne (h : Heap) (release : Release) : Option Heap :=
  match h release.address with
  | some (.allocation actual) =>
      if actual = release.role then some (write h release.address none) else none
  | _ => none

def freeMany : Heap → List Release → Option Heap
  | h, [] => some h
  | h, a :: rest => (freeOne h a).bind (fun next => freeMany next rest)

def referenceErase (h : Heap) (releases : List Release) : Heap :=
  fun x => if x ∈ releases.map Release.address then none else h x

def Allocation (h : Heap) (release : Release) : Prop :=
  h release.address = some (.allocation release.role)

def Allocated (h : Heap) (releases : List Release) : Prop :=
  ∀ release ∈ releases, Allocation h release

theorem freeOne_eq (h next : Heap) (a : Release)
    (success : freeOne h a = some next) : next = write h a.address none := by
  unfold freeOne at success
  split at success <;> try contradiction
  split at success <;> simp_all

theorem freeOne_requires_role (h next : Heap) (release : Release)
    (success : freeOne h release = some next) : Allocation h release := by
  unfold freeOne at success
  split at success <;> try contradiction
  next actual found =>
    split at success
    next same => simpa [Allocation, same] using found
    next different => contradiction

theorem erase_cons (h : Heap) (a : Release) (rest : List Release) :
    referenceErase (write h a.address none) rest = referenceErase h (a :: rest) := by
  funext x
  by_cases first : x = a.address <;> by_cases later : x ∈ rest.map Release.address <;>
    simp [referenceErase, write, first, later]

theorem freeMany_reference (h next : Heap) (addresses : List Release)
    (success : freeMany h addresses = some next) :
    next = referenceErase h addresses := by
  induction addresses generalizing h with
  | nil =>
      have same : next = h := by simpa [freeMany] using success.symm
      rw [same]
      funext x
      simp [referenceErase]
  | cons a rest ih =>
      cases step : freeOne h a with
      | none => simp [freeMany, step] at success
      | some mid =>
          have later : freeMany mid rest = some next := by
            simpa [freeMany, step] using success
          rw [ih mid later, freeOne_eq h mid a step]
          exact erase_cons h a rest

theorem allocated_after_distinct_free (h : Heap) (a : Release) (rest : List Release)
    (fresh : a.address ∉ rest.map Release.address) (ready : Allocated h (a :: rest)) :
    Allocated (write h a.address none) rest := by
  intro x member
  have different : x.address ≠ a.address := by
    intro same
    exact fresh (by simpa [same] using List.mem_map_of_mem (f := Release.address) member)
  simpa [Allocation, write, different] using ready x (by simp [member])

theorem freeMany_complete (h : Heap) (addresses : List Release)
    (unique : (addresses.map Release.address).Nodup) (ready : Allocated h addresses) :
    freeMany h addresses = some (referenceErase h addresses) := by
  induction addresses generalizing h with
  | nil => rfl
  | cons a rest ih =>
      have atA := ready a (by simp)
      obtain ⟨fresh, restUnique⟩ := List.nodup_cons.mp unique
      have restReady := allocated_after_distinct_free h a rest fresh ready
      calc
        freeMany h (a :: rest) = freeMany (write h a.address none) rest := by
          change h a.address = some (.allocation a.role) at atA
          simp [freeMany, freeOne, atA]
        _ = some (referenceErase (write h a.address none) rest) :=
          ih (write h a.address none) restUnique restReady
        _ = some (referenceErase h (a :: rest)) := congrArg some (erase_cons h a rest)

def IsAllocation : Cell → Bool
  | .allocation _ => true
  | _ => false

theorem protected_cell (h next : Heap) (addresses : List Release) (x : Address)
    (cell : Cell) (present : h x = some cell) (notAllocation : IsAllocation cell = false)
    (success : freeMany h addresses = some next) : next x = some cell := by
  induction addresses generalizing h with
  | nil => simp [freeMany] at success; cases success; exact present
  | cons a rest ih =>
      cases step : freeOne h a with
      | none => simp [freeMany, step] at success
      | some mid =>
          have different : x ≠ a.address := by
            intro same
            rw [same] at present
            cases cell <;> simp [IsAllocation] at notAllocation <;>
              simp [freeOne, present] at step
          apply ih mid
          · rw [freeOne_eq h mid a step]
            simpa [write, different] using present
          · simpa [freeMany, step] using success

def primary (h : Heap) (content : Address) : Option Address :=
  match h content with
  | some (.content pointer) => pointer
  | _ => none

def Coherent (h : Heap) : Prop :=
  ∀ frame content bit props, h frame = some (.frame content bit props) →
    bit = decide (primary h content = some frame)

theorem primary_preserved (h next : Heap) (addresses : List Release)
    (success : freeMany h addresses = some next) : primary next = primary h := by
  funext content
  rw [freeMany_reference h next addresses success]
  by_cases erased : content ∈ addresses.map Release.address
  · cases atContent : h content with
    | none => simp [primary, referenceErase, erased, atContent]
    | some cell =>
        cases cell with
        | content pointer =>
            have same := protected_cell h next addresses content (.content pointer)
              atContent rfl success
            rw [freeMany_reference h next addresses success] at same
            simp [referenceErase, erased] at same
        | frame owner bit props => simp [primary, referenceErase, erased, atContent]
        | allocation kind => simp [primary, referenceErase, erased, atContent]
  · simp [primary, referenceErase, erased]

theorem coherent_after_free (h next : Heap) (addresses : List Release)
    (coherent : Coherent h) (success : freeMany h addresses = some next) :
    Coherent next := by
  intro frame content bit props present
  have earlier : h frame = some (.frame content bit props) := by
    rw [freeMany_reference h next addresses success] at present
    by_cases erased : frame ∈ addresses.map Release.address
    · simp [referenceErase, erased] at present
    · simpa [referenceErase, erased] using present
  rw [primary_preserved h next addresses success]
  exact coherent frame content bit props earlier

theorem freed_allocation (h next : Heap) (addresses : List Release) (a : Release)
    (member : a ∈ addresses) (success : freeMany h addresses = some next) :
    next a.address = none := by
  rw [freeMany_reference h next addresses success]
  simp [referenceErase, List.mem_map_of_mem (f := Release.address) member]

end Destruction
