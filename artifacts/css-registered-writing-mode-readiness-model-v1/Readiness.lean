namespace WritingModeReadiness

inductive Mode where
  | horizontal | vertical
  deriving DecidableEq, Repr

inductive Raw where
  | bogus | keyword (mode : Mode)
  deriving DecidableEq, Repr

inductive Provider where
  | pending (raw : Raw) | ready (mode : Mode)
  deriving DecidableEq, Repr

def admit : Raw → Mode
  | .bogus => .vertical
  | .keyword mode => mode

def consume : Provider → Mode
  | .pending .bogus => .horizontal
  | .pending (.keyword mode) | .ready mode => mode

structure State where
  provider : Provider
  writingMode : Option Mode := none
  lineHeightApplied : Bool := false
  length : Option Nat := none
  deriving DecidableEq, Repr

def admitProvider (s : State) : State :=
  match s.provider with
  | .pending raw => {s with provider := .ready (admit raw)}
  | .ready _ => s

def ensureWritingMode (s : State) : State :=
  match s.writingMode with
  | some _ => s
  | none => {s with writingMode := some (consume s.provider)}

def ensureLineHeight (s : State) : State :=
  {ensureWritingMode s with lineHeightApplied := true}

def inlineSize : Mode → Nat
  | .horizontal => 320
  | .vertical => 180

def computeLength (s : State) : State :=
  let ready := ensureWritingMode (ensureLineHeight s)
  {ready with length := ready.writingMode.map (fun mode => 40 + inlineSize mode)}

inductive Action where
  | admitProvider | ensureWritingMode | computeLength
  deriving DecidableEq, Repr

def step : Action → State → State
  | .admitProvider => admitProvider
  | .ensureWritingMode => ensureWritingMode
  | .computeLength => computeLength

def run (actions : List Action) (s : State) : State :=
  actions.foldl (fun state action => step action state) s

def initial : State := ⟨.pending .bogus, none, false, none⟩
def badOrder : List Action := [.computeLength, .admitProvider, .ensureWritingMode]
def goodOrder : List Action := [.admitProvider, .computeLength]

inductive Node where
  | raw | provider | writingMode | lineHeight | font | length
  deriving DecidableEq, Repr

def edges : Node → Node → Bool
  | .provider, .raw | .writingMode, .provider
  | .length, .writingMode | .length, .lineHeight | .length, .font => true
  | _, _ => false

def rank : Node → Nat
  | .raw | .lineHeight | .font => 0
  | .provider => 1
  | .writingMode => 2
  | .length => 3

inductive Reaches : Node → Node → Prop where
  | edge {a b} : edges a b = true → Reaches a b
  | trans {a b c} : Reaches a b → Reaches b c → Reaches a c

theorem edge_rank : ∀ a b, edges a b = true → rank b < rank a := by
  intro a b
  cases a <;> cases b <;> decide

theorem path_rank {a b : Node} (h : Reaches a b) : rank b < rank a := by
  induction h with
  | edge h => exact edge_rank _ _ h
  | trans _ _ first second => exact Nat.lt_trans second first

theorem acyclic (node : Node) : ¬ Reaches node node := by
  intro path
  exact (Nat.lt_irrefl _) (path_rank path)

theorem invalid_provider_defaults : admit .bogus = .vertical := rfl

theorem bad_order :
    run badOrder initial = ⟨.ready .vertical, some .horizontal, true, some 360⟩ := by
  decide +kernel

theorem good_order :
    run goodOrder initial = ⟨.ready .vertical, some .vertical, true, some 220⟩ := by
  decide +kernel

theorem ready_and_coherent_suffices (s : State) (mode : Mode)
    (ready : s.provider = .ready mode)
    (coherent : s.writingMode = none ∨ s.writingMode = some mode) :
    (ensureWritingMode s).writingMode = some mode := by
  rcases coherent with empty | correct
  · simp [ensureWritingMode, empty, consume, ready]
  · simp [ensureWritingMode, correct]

theorem acyclicity_does_not_force_readiness :
    (∀ node, ¬ Reaches node node) ∧
    (run badOrder initial).writingMode ≠ some .vertical := by
  exact ⟨acyclic, by decide +kernel⟩

def guardedWritingMode (s : State) : Option State :=
  match s.provider with
  | .pending _ => none
  | .ready _ => some (ensureWritingMode s)

theorem guarded_pending_does_not_publish (raw : Raw) (mode : Option Mode)
    (lh : Bool) (length : Option Nat) :
    guardedWritingMode ⟨.pending raw, mode, lh, length⟩ = none := rfl

theorem guarded_fresh_ready_correct (mode : Mode) (lh : Bool) (length : Option Nat) :
    guardedWritingMode ⟨.ready mode, none, lh, length⟩ =
      some ⟨.ready mode, some mode, lh, length⟩ := rfl

def nodes : List Node := [.raw, .provider, .writingMode, .lineHeight, .font, .length]
def ranked : Bool := nodes.all (fun a => nodes.all (fun b => !edges a b || rank b < rank a))

theorem finite_rank_certificate : ranked = true := by decide +kernel

end WritingModeReadiness
