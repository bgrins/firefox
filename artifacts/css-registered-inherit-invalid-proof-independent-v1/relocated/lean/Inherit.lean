namespace RegisteredInherit

abbrev Store (Key Value : Type) := Bool → Key → Option Value

structure Context (Key Value : Type) where
  name : Key
  inherited : Bool
  root : Bool
  initial : Option Value
  parent : Store Key Value

structure State (Key Value Flags : Type) where
  values : Store Key Value
  inheritsResetStyle : Bool
  otherFlags : Flags

def selected (c : Context K V) (s : State K V F) : Option V :=
  s.values c.inherited c.name

def seed (c : Context K V) : Option V :=
  if c.root then c.initial
  else if c.inherited then c.parent true c.name else c.initial

def Ready (c : Context K V) (s : State K V F) : Prop :=
  selected c s = seed c ∧ (c.root = true → c.parent false c.name = none)

def expected (c : Context K V) : Option V :=
  if c.root then c.initial else c.parent c.inherited c.name

def put [DecidableEq K] (c : Context K V) (s : State K V F) (value : Option V) : State K V F :=
  { s with values := fun bucket key =>
      if bucket = c.inherited ∧ key = c.name then value else s.values bucket key }

def gate (fixed : Bool) (c : Context K V) (s : State K V F) : Bool :=
  if c.inherited then false
  else match selected c s with
    | none => true
    | some _ => if fixed then !c.root else (c.parent false c.name).isSome

def update [DecidableEq K] (fixed : Bool) (c : Context K V) (s : State K V F) : State K V F :=
  let s := { s with inheritsResetStyle := true }
  match c.parent false c.name with
  | some value => put c s (some value)
  | none => if fixed then put c s none else s

def run [DecidableEq K] (gateFixed updateFixed : Bool) (c : Context K V) (s : State K V F) : State K V F :=
  if gate gateFixed c s then update updateFixed c s else s

theorem put_selected [DecidableEq K] (c : Context K V) (s : State K V F) (v : Option V) :
    selected c (put c s v) = v := by
  simp [selected, put]

theorem put_other [DecidableEq K] (c : Context K V) (s : State K V F) (v : Option V)
    (bucket : Bool) (key : K) (h : bucket ≠ c.inherited ∨ key ≠ c.name) :
    (put c s v).values bucket key = s.values bucket key := by
  simp only [put]
  split
  next h' => exact False.elim (h.elim (fun x => x h'.1) (fun x => x h'.2))
  next => rfl

theorem update_selected [DecidableEq K] (c : Context K V) (s : State K V F) :
    selected c (update true c s) = c.parent false c.name := by
  cases hp : c.parent false c.name <;> simp [update, hp, put_selected]

theorem corrected_selected [DecidableEq K] (c : Context K V) (s : State K V F)
    (ready : Ready c s) : selected c (run true true c s) = expected c := by
  rcases ready with ⟨seeded, rootEmpty⟩
  cases hi : c.inherited <;> cases hr : c.root
  · cases hs : selected c s <;>
      simpa [run, gate, hi, hr, hs, expected] using update_selected c s
  · have empty := rootEmpty hr
    have seeded' : selected c s = c.initial := by simpa [seed, hr] using seeded
    cases hs : selected c s with
    | none =>
      have initialNone : c.initial = none := seeded'.symm.trans hs
      simp [run, gate, hi, hr, hs, update_selected, expected, empty, initialNone]
    | some value => simp [run, gate, hi, hr, hs, expected, ← seeded']
  · simpa [run, gate, hi, hr, expected, seed] using seeded
  · simpa [run, gate, hi, hr, expected, seed] using seeded

theorem run_other [DecidableEq K] (a b : Bool) (c : Context K V) (s : State K V F)
    (bucket : Bool) (key : K) (h : bucket ≠ c.inherited ∨ key ≠ c.name) :
    (run a b c s).values bucket key = s.values bucket key := by
  simp only [run]
  split
  · simp only [update]
    split
    · exact put_other _ _ _ _ _ h
    · split
      · exact put_other _ _ _ _ _ h
      · rfl
  · rfl

theorem corrected_store [DecidableEq K] (c : Context K V) (s : State K V F)
    (ready : Ready c s) (bucket : Bool) (key : K) :
    (run true true c s).values bucket key =
      if bucket = c.inherited ∧ key = c.name then expected c else s.values bucket key := by
  split
  next h => rcases h with ⟨rfl, rfl⟩; exact corrected_selected c s ready
  next h =>
    apply run_other
    by_cases hb : bucket = c.inherited
    · exact Or.inr (fun hk => h ⟨hb, hk⟩)
    · exact Or.inl hb

theorem other_flags [DecidableEq K] (a b : Bool) (c : Context K V) (s : State K V F) :
    (run a b c s).otherFlags = s.otherFlags := by
  simp only [run]
  split
  · simp only [update]
    split
    · rfl
    · split <;> rfl
  · rfl

theorem exact_reset_flag [DecidableEq K] (a b : Bool) (c : Context K V) (s : State K V F) :
    (run a b c s).inheritsResetStyle = (gate a c s || s.inheritsResetStyle) := by
  cases hg : gate a c s <;> cases hp : c.parent false c.name <;> cases b <;>
    simp [run, hg, update, hp, put]

theorem corrected_gate (c : Context K V) (s : State K V F) (ready : Ready c s) :
    gate true c s = (!c.inherited && (!c.root || c.initial.isNone)) := by
  rcases ready with ⟨seeded, _⟩
  cases hi : c.inherited <;> cases hr : c.root <;> cases hs : selected c s <;> cases hn : c.initial <;>
    simp_all [gate, seed]

theorem corrected_reset_flag [DecidableEq K] (c : Context K V) (s : State K V F)
    (ready : Ready c s) :
    (run true true c s).inheritsResetStyle =
      ((!c.inherited && (!c.root || c.initial.isNone)) || s.inheritsResetStyle) := by
  rw [exact_reset_flag, corrected_gate c s ready]

theorem incoming_reset_flag [DecidableEq K] (a b : Bool) (c : Context K V) (s : State K V F)
    (h : s.inheritsResetStyle = true) : (run a b c s).inheritsResetStyle = true := by
  rw [exact_reset_flag, h]
  simp

theorem nonroot_reset_dependency [DecidableEq K] (c : Context K V) (s : State K V F)
    (hi : c.inherited = false) (hr : c.root = false) :
    (run true true c s).inheritsResetStyle = true := by
  rw [exact_reset_flag]
  cases hs : selected c s <;> simp [gate, hi, hr, hs]

def witness (root := false) : Context Nat Nat :=
  ⟨0, false, root, some 7, fun _ _ => none⟩

def start : State Nat Nat Nat :=
  ⟨fun bucket key => if bucket = false ∧ key = 0 then some 7 else some 99, false, 13⟩

theorem witness_ready : Ready (witness false) start ∧ Ready (witness true) start := by
  simp [Ready, witness, start, selected, seed]

theorem original_counterexample :
    selected (witness false) (run false false (witness false) start) = some 7 ∧
    expected (witness false) = none := by decide

theorem both_sites_necessary :
    selected (witness false) (run false true (witness false) start) = some 7 ∧
    selected (witness false) (run true false (witness false) start) = some 7 ∧
    selected (witness false) (run true true (witness false) start) = none := by decide

theorem root_guard_necessary :
    selected (witness true) (update true (witness true) start) = none ∧
    selected (witness true) (run true true (witness true) start) = some 7 := by decide

theorem absent_root_initial :
    let c : Context Nat Nat := ⟨0, false, true, none, fun _ _ => none⟩
    let s : State Nat Nat Nat := ⟨fun _ _ => none, false, 13⟩
    Ready c s ∧ selected c (run true true c s) = none ∧
      (run true true c s).inheritsResetStyle = true := by
  simp [Ready, selected, seed, run, gate, update, put]

end RegisteredInherit
