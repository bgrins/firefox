import Std

namespace HyphenSpacingValues

inductive Side where
  | before
  | after
  deriving DecidableEq, Repr

structure Write (Value : Type) where
  index : Nat
  side : Side
  value : Value

abbrev Store (Value : Type) := Nat → Side → Value

structure Arithmetic (Value : Type) where
  zero : Value
  add : Value → Value → Value

def write (arithmetic : Arithmetic Value) (store : Store Value) (entry : Write Value) : Store Value :=
  fun index side => if index = entry.index ∧ side = entry.side
    then arithmetic.add (store index side) entry.value else store index side

def execute (arithmetic : Arithmetic Value) (store : Store Value) (entries : List (Write Value)) : Store Value :=
  entries.foldl (write arithmetic) store

def valuesAt (entries : List (Write Value)) (index : Nat) (side : Side) : List Value :=
  entries.filterMap fun entry => if index = entry.index ∧ side = entry.side then some entry.value else none

theorem ordered_values (arithmetic : Arithmetic Value) (store : Store Value)
    (entries : List (Write Value)) (index : Nat) (side : Side) :
    execute arithmetic store entries index side =
      (valuesAt entries index side).foldl arithmetic.add (store index side) := by
  induction entries generalizing store with
  | nil => rfl
  | cons entry rest ih =>
    simp only [execute,List.foldl_cons] at *
    rw [ih]
    by_cases target : index = entry.index ∧ side = entry.side
    · simp [valuesAt,write,target]
    · simp [valuesAt,write,target]

theorem execute_append (arithmetic : Arithmetic Value) (store : Store Value)
    (first later : List (Write Value)) :
    execute arithmetic store (first++later) = execute arithmetic (execute arithmetic store first) later := by
  simp [execute,List.foldl_append]

def Bounded (length : Nat) (entries : List (Write Value)) : Prop :=
  ∀ entry ∈ entries, entry.index < length

theorem bounded_append (length : Nat) (first later : List (Write Value)) :
    Bounded length (first++later) ↔ Bounded length first ∧ Bounded length later := by
  simp [Bounded,List.mem_append,or_imp,forall_and]

theorem writes_leave_outside (arithmetic : Arithmetic Value) (store : Store Value)
    (entries : List (Write Value)) (length index : Nat) (side : Side)
    (bounded : Bounded length entries) (outside : length ≤ index) :
    execute arithmetic store entries index side = store index side := by
  rw [ordered_values]
  have empty : valuesAt entries index side = [] := by
    apply List.filterMap_eq_nil_iff.mpr
    intro entry member
    have bound := bounded entry member
    have different : index ≠ entry.index := by omega
    simp [different]
  rw [empty]
  rfl

structure Classifiers where
  mark : Nat → Bool
  other : Nat → Bool
  shouldSpace : Nat → Nat → Bool
  preceding : Nat

structure Config (Value : Type) where
  arithmetic : Arithmetic Value
  before : Value
  after : Value
  word : Value
  interScript : Value
  beforeEnabled : Bool
  afterEnabled : Bool
  wordEnabled : Bool
  autospaceEnabled : Bool
  classes : Classifiers

structure Unit where
  index : Nat
  wordTarget : Nat
  canBefore : Bool
  canAfter : Bool
  cursive : Bool
  baseCursive : Bool
  wordSpace : Bool
  autospaceChecked : Bool
  charClass : Nat

structure Control where
  atStart : Bool
  previous : Option Nat
  present : Bool
  deriving DecidableEq, Repr

structure NativeState (Value : Type) where
  control : Control
  store : Store Value

def autoChecked (config : Config Value) (unit : Unit) : Bool :=
  config.autospaceEnabled && unit.autospaceChecked && !config.classes.mark unit.charClass

def autoApplied (config : Config Value) (control : Control) (unit : Unit) : Bool :=
  autoChecked config unit && !control.atStart && !config.classes.other unit.charClass &&
    config.classes.shouldSpace (control.previous.getD config.classes.preceding) unit.charClass

def nextControl (config : Config Value) (control : Control) (unit : Unit) : Control :=
  ⟨false, if autoChecked config unit then some unit.charClass else control.previous,
    control.present || (config.wordEnabled && unit.wordSpace) || autoApplied config control unit⟩

def nativeVisit (config : Config Value) (state : NativeState Value) (unit : Unit) : NativeState Value :=
  let store := if !state.control.atStart && config.beforeEnabled && unit.canBefore && !unit.cursive
    then write config.arithmetic state.store ⟨unit.index,.before,config.before⟩ else state.store
  let store := if config.afterEnabled && unit.canAfter && !unit.baseCursive
    then write config.arithmetic store ⟨unit.index,.after,config.after⟩ else store
  let store := if config.wordEnabled && unit.wordSpace
    then write config.arithmetic store ⟨unit.wordTarget,.after,config.word⟩ else store
  let store := if autoApplied config state.control unit
    then write config.arithmetic store ⟨unit.index,.before,config.interScript⟩ else store
  ⟨nextControl config state.control unit,store⟩

def referenceEntries (config : Config Value) (control : Control) (unit : Unit) : List (Write Value) :=
  (if !control.atStart && config.beforeEnabled && unit.canBefore && !unit.cursive
    then [⟨unit.index,.before,config.before⟩] else []) ++
  (if config.afterEnabled && unit.canAfter && !unit.baseCursive
    then [⟨unit.index,.after,config.after⟩] else []) ++
  (if config.wordEnabled && unit.wordSpace
    then [⟨unit.wordTarget,.after,config.word⟩] else []) ++
  (if autoApplied config control unit
    then [⟨unit.index,.before,config.interScript⟩] else [])

theorem visit_reference (config : Config Value) (state : NativeState Value) (unit : Unit) :
    nativeVisit config state unit =
      ⟨nextControl config state.control unit,
       execute config.arithmetic state.store (referenceEntries config state.control unit)⟩ := by
  simp only [referenceEntries,execute_append]
  unfold nativeVisit
  split <;> split <;> split <;> split <;> simp_all [execute]

def nativeLoop (config : Config Value) (state : NativeState Value) : List Unit → NativeState Value
  | [] => state
  | unit::rest => nativeLoop config (nativeVisit config state unit) rest

def referenceControl (config : Config Value) (control : Control) : List Unit → Control
  | [] => control
  | unit::rest => referenceControl config (nextControl config control unit) rest

def referenceTrace (config : Config Value) (control : Control) : List Unit → List (Write Value)
  | [] => []
  | unit::rest => referenceEntries config control unit ++
      referenceTrace config (nextControl config control unit) rest

theorem whole_loop_reference (config : Config Value) (state : NativeState Value) (units : List Unit) :
    nativeLoop config state units =
      ⟨referenceControl config state.control units,
       execute config.arithmetic state.store (referenceTrace config state.control units)⟩ := by
  induction units generalizing state with
  | nil => rfl
  | cons unit rest ih =>
    rw [nativeLoop,visit_reference,ih]
    simp only [referenceControl,referenceTrace,execute_append]

theorem whole_loop_pointwise (config : Config Value) (state : NativeState Value) (units : List Unit)
    (index : Nat) (side : Side) :
    (nativeLoop config state units).store index side =
      (valuesAt (referenceTrace config state.control units) index side).foldl config.arithmetic.add
        (state.store index side) := by
  rw [whole_loop_reference]
  exact ordered_values _ _ _ _ _

theorem entry_bounds (config : Config Value) (control : Control) (unit : Unit) (length : Nat)
    (unitBound : unit.index < length) (wordBound : unit.wordTarget < length) :
    Bounded length (referenceEntries config control unit) := by
  unfold referenceEntries
  simp only [bounded_append]
  repeat' constructor
  all_goals split <;> simp_all [Bounded]

theorem trace_bounds (config : Config Value) (control : Control) (units : List Unit) (length : Nat)
    (bounds : ∀ unit ∈ units, unit.index < length ∧ unit.wordTarget < length) :
    Bounded length (referenceTrace config control units) := by
  induction units generalizing control with
  | nil => simp [referenceTrace,Bounded]
  | cons unit rest ih =>
    rw [referenceTrace,bounded_append]
    exact ⟨entry_bounds config control unit length (bounds unit (by simp)).1 (bounds unit (by simp)).2,
      ih _ (by intro u hu; exact bounds u (by simp [hu]))⟩

def queriedPredecessor (config : Config Value) (control : Control) (unit : Unit) : Bool :=
  autoChecked config unit && !control.atStart && !config.classes.other unit.charClass && control.previous.isNone

def predecessorRequests (config : Config Value) (control : Control) : List Unit → Nat
  | [] => 0
  | unit::rest => (if queriedPredecessor config control unit then 1 else 0) +
      predecessorRequests config (nextControl config control unit) rest

theorem previous_stays_set (config : Config Value) (control : Control) (unit : Unit)
    (set : control.previous.isSome = true) :
    (nextControl config control unit).previous.isSome = true := by
  simp only [nextControl]
  split <;> simp_all

theorem no_repeated_predecessor (config : Config Value) (control : Control) (units : List Unit)
    (set : control.previous.isSome = true) : predecessorRequests config control units = 0 := by
  induction units generalizing control with
  | nil => rfl
  | cons unit rest ih =>
    have notNone : control.previous.isNone = false := by cases h : control.previous <;> simp_all
    simp [predecessorRequests,queriedPredecessor,notNone,ih _ (previous_stays_set _ _ _ set)]

theorem at_most_one_predecessor (config : Config Value) (control : Control) (units : List Unit) :
    predecessorRequests config control units ≤ 1 := by
  induction units generalizing control with
  | nil => simp [predecessorRequests]
  | cons unit rest ih =>
    rw [predecessorRequests]
    by_cases queried : queriedPredecessor config control unit = true
    · have checked : autoChecked config unit = true := by
        simp only [queriedPredecessor,Bool.and_eq_true] at queried
        exact queried.1.1.1
      have set : (nextControl config control unit).previous.isSome = true := by simp [nextControl,checked]
      simp [queried,no_repeated_predecessor _ _ _ set]
    · simpa [queried] using ih (nextControl config control unit)

end HyphenSpacingValues
