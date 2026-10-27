namespace QuoteAppend

inductive Op where
  | openQuote | noOpen | closeQuote | noClose
  deriving DecidableEq, Repr

def after (depth : Nat) : Op → Nat
  | .openQuote | .noOpen => depth + 1
  | .closeQuote | .noClose => depth - 1

def finish : Nat → List Op → Nat
  | depth, [] => depth
  | depth, op :: rest => finish (after depth op) rest

abbrev Provider := Bool → Nat → String

structure Cell where
  before : Nat
  text : String
  deriving DecidableEq, Repr

def cell (provider : Provider) (depth : Nat) (op : Op) : Cell :=
  ⟨depth, match op with
    | .openQuote => provider true depth
    | .closeQuote => if depth = 0 then "" else provider false (depth - 1)
    | .noOpen | .noClose => ""⟩

def scan (provider : Provider) : Nat → List Op → List Cell
  | _, [] => []
  | depth, op :: rest => cell provider depth op :: scan provider (after depth op) rest

theorem finish_append (depth : Nat) (ops : List Op) (op : Op) :
    finish depth (ops ++ [op]) = after (finish depth ops) op := by
  induction ops generalizing depth with
  | nil => rfl
  | cons first rest ih => simpa [finish] using ih (after depth first)

theorem scan_append (p : Provider) (depth : Nat) (ops : List Op) (op : Op) :
    scan p depth (ops ++ [op]) = scan p depth ops ++ [cell p (finish depth ops) op] := by
  induction ops generalizing depth with
  | nil => rfl
  | cons first rest ih => simp [scan, finish, ih]

structure State where
  seed : Nat
  parents : List Op
  parentEnd : Nat
  parentCache : List Cell
  child : Option (List Op)
  childCache : List Cell
  dirty : Bool
  deriving DecidableEq, Repr

def childReference (p : Provider) (s : State) : List Cell :=
  match s.child with
  | none => []
  | some ops => scan p (finish s.seed s.parents) ops

def Fresh (p : Provider) (s : State) : Prop :=
  s.parentEnd = finish s.seed s.parents ∧
  s.parentCache = scan p s.seed s.parents ∧ s.childCache = childReference p s

def Conserved (p : Provider) (s : State) : Prop :=
  s.parentEnd = finish s.seed s.parents ∧
  s.parentCache = scan p s.seed s.parents ∧
  (s.dirty = true ∨ s.childCache = childReference p s)

def append (p : Provider) (s : State) (op : Op) : State :=
  { s with
    parents := s.parents ++ [op]
    parentEnd := after s.parentEnd op
    parentCache := s.parentCache ++ [cell p s.parentEnd op]
    dirty := s.dirty || s.child.isSome }

def legacyAppend (p : Provider) (s : State) (op : Op) : State :=
  { append p s op with dirty := s.dirty }

def deliver (p : Provider) (s : State) : State :=
  if s.dirty then
    { s with
      parentEnd := finish s.seed s.parents
      parentCache := scan p s.seed s.parents
      childCache := childReference p s
      dirty := false }
  else s

theorem fresh_conserved (p : Provider) (s : State) (h : Fresh p s) : Conserved p s :=
  ⟨h.1, h.2.1, Or.inr h.2.2⟩

theorem append_conserves (p : Provider) (s : State) (op : Op)
    (h : Conserved p s) : Conserved p (append p s op) := by
  refine ⟨?_, ?_, ?_⟩
  · simpa [append, finish_append] using congrArg (fun d => after d op) h.1
  · simp [append, scan_append, h.1, h.2.1]
  · cases hc : s.child with
    | some ops => exact Or.inl (by simp [append, hc])
    | none =>
      rcases h.2.2 with hd | hv
      · exact Or.inl (by simp [append, hd])
      · exact Or.inr (by simpa [childReference, append, hc] using hv)

theorem delivery_fresh (p : Provider) (s : State) (h : Conserved p s) :
    Fresh p (deliver p s) := by
  cases hd : s.dirty with
  | true => simp [deliver, hd, Fresh, childReference]
  | false =>
    simp only [deliver, hd, Bool.false_eq_true, ↓reduceIte]
    exact ⟨h.1, h.2.1, h.2.2.resolve_left (by simp [hd])⟩

theorem leaf_append_unchanged (p : Provider) (s : State) (op : Op)
    (h : s.child = none) : append p s op = legacyAppend p s op := by
  simp [append, legacyAppend, h]

theorem leaf_append_fresh (p : Provider) (s : State) (op : Op)
    (h : Fresh p s) (hc : s.child = none) : Fresh p (append p s op) := by
  refine ⟨?_, ?_, ?_⟩
  · simp [append, finish_append, h.1]
  · simp [append, scan_append, h.1, h.2.1]
  · simpa [childReference, append, hc] using h.2.2

inductive Event where
  | append (op : Op)
  | flush

def step (p : Provider) (s : State) : Event → State
  | .append op => append p s op
  | .flush => deliver p s

def run (p : Provider) : State → List Event → State
  | s, [] => s
  | s, event :: rest => run p (step p s event) rest

theorem histories_conserve (p : Provider) (events : List Event) (s : State)
    (h : Conserved p s) : Conserved p (run p s events) := by
  induction events generalizing s with
  | nil => exact h
  | cons event rest ih =>
    apply ih
    cases event with
    | append op => exact append_conserves p s op h
    | flush => exact fresh_conserved p _ (delivery_fresh p s h)

theorem delivered_history_fresh (p : Provider) (events : List Event) (s : State)
    (h : Conserved p s) : Fresh p (deliver p (run p s events)) :=
  delivery_fresh p _ (histories_conserve p events s h)

def explicitPairs : Provider := fun _ depth => if depth = 0 then "A" else "AAA"
def initial : State :=
  ⟨0, [], 0, [], some [.openQuote, .closeQuote],
    [⟨0, "A"⟩, ⟨1, "A"⟩], false⟩

theorem initial_fresh : Fresh explicitPairs initial := by
  unfold Fresh
  decide +kernel
theorem original_misses_delivery :
    (deliver explicitPairs (legacyAppend explicitPairs initial .noOpen)).childCache ≠
      childReference explicitPairs (legacyAppend explicitPairs initial .noOpen) := by decide +kernel

theorem dirty_is_not_delivery :
    (append explicitPairs initial .noOpen).childCache ≠
      childReference explicitPairs (append explicitPairs initial .noOpen) := by decide +kernel

theorem delivered_text_witness :
    (deliver explicitPairs (append explicitPairs initial .noOpen)).childCache =
      [⟨1, "AAA"⟩, ⟨2, "AAA"⟩] := by decide +kernel

example : after 0 .closeQuote = 0 ∧ after 0 .noClose = 0 := by decide +kernel
example : (cell explicitPairs 0 .closeQuote).text = "" := by decide +kernel
example : (append explicitPairs { initial with child := some [], childCache := [] } .noOpen).dirty = true := by decide +kernel
example : (run explicitPairs initial [.append .noOpen, .append .noClose]).dirty = true := by decide +kernel
example : (deliver explicitPairs (run explicitPairs initial [.append .noOpen, .append .noClose])).childCache = initial.childCache := by decide +kernel

end QuoteAppend
