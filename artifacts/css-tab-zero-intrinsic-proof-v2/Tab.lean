import Std
namespace Tab
inductive Token where
  | glyph (advance : Nat)
  | tab
  deriving Repr, BEq, DecidableEq

abbrev Policy := Int → Int
abbrev Event := Nat × Nat × Int
structure Observation where
  advance : Int
  cursor : Nat
  trace : List Event
  deriving Repr, BEq, DecidableEq

def specStep (policy : Policy) (s : Observation) : Token → Observation
  | .glyph n => ⟨s.advance + n, s.cursor + 1, s.trace ++ [(0, s.cursor, (n : Int))]⟩
  | .tab => ⟨policy s.advance, s.cursor + 1, s.trace ++ [(1, s.cursor, 0)]⟩

def specRun (policy : Policy) : List Token → Observation → Observation
  | [], s => s
  | t :: ts, s => specRun policy ts (specStep policy s t)

structure NativeState where
  current : Int
  pending : Int := 0
  pendingCount : Nat := 0
  cursor : Nat := 0
  trace : List Event := []
  atStart : Bool := true
  empty : Bool := true
  metricKnown : Bool := false
  provider : List Event := []
  deriving Repr, BEq, DecidableEq

inductive Mode where | minimum | preferred deriving Repr, BEq, DecidableEq

def commit (mode : Mode) (s : NativeState) : NativeState :=
  { s with current := s.current + s.pending, pending := 0, pendingCount := 0, atStart := if mode == .minimum && s.pendingCount > 0 then false else s.atStart, empty := if mode == .preferred && s.pendingCount > 0 then false else s.empty }

def nativeStep (mode : Mode) (policy : Policy) (s : NativeState) : Token → NativeState
  | .glyph n => { s with pending := s.pending + n, pendingCount := s.pendingCount + 1, cursor := s.cursor + 1, trace := s.trace ++ [(0, s.cursor, (n : Int))] }
  | .tab =>
    let flushed := commit mode s
    { flushed with current := policy flushed.current, cursor := s.cursor + 1, empty := if mode == .preferred then false else flushed.empty, trace := s.trace ++ [(1, s.cursor, 0)], metricKnown := true, provider := if s.metricKnown then s.provider else s.provider ++ [(10,0,0)] }

def nativeLoop (mode : Mode) (policy : Policy) : List Token → NativeState → NativeState
  | [], s => s
  | t :: ts, s => nativeLoop mode policy ts (nativeStep mode policy s t)

def nativeRun (mode : Mode) (policy : Policy) (ts : List Token) (s : NativeState) :=
  commit mode (nativeLoop mode policy ts s)

def view (s : NativeState) : Observation := ⟨s.current + s.pending, s.cursor, s.trace⟩

structure NormalState where
  measured : Int
  offset : Int
  origin : Nat
  cursor : Nat
  trace : List Event := []
  provider : List Event := [(5,0,0)]
  records : List (Nat × Int) := []
  analyzed : Nat := 0
  metricKnown : Bool := false
  cache : Bool := false
  deriving Repr, BEq, DecidableEq

def normalStep (calculate : Bool) (policy : Policy) (s : NormalState) : Token → NormalState
  | .glyph n => { s with measured := s.measured + n, offset := if calculate then s.offset + n else s.offset, cursor := s.cursor + 1, trace := s.trace ++ [(0,s.cursor,(n : Int))], provider := if calculate then s.provider ++ [(11,s.cursor,(s.cursor : Int) + 1)] else s.provider }
  | .tab =>
    if calculate then
      let next := policy s.offset
      { s with measured := s.measured + (next - s.offset), offset := next, cursor := s.cursor + 1, trace := s.trace ++ [(1,s.cursor,0)], records := s.records ++ [(s.cursor - s.origin,next - s.offset)], provider := s.provider ++ (if s.cache then [] else [(4,0,0)]) ++ (if s.metricKnown then [] else [(10,0,0)]), metricKnown := true, cache := true }
    else { s with cursor := s.cursor + 1, trace := s.trace ++ [(1,s.cursor,0)] }

def normalLoop (calculate : Bool) (policy : Policy) : List Token → NormalState → NormalState
  | [], s => s
  | t :: ts, s => normalLoop calculate policy ts (normalStep calculate policy s t)

def normalView (s : NormalState) : Observation := ⟨s.measured,s.cursor,s.trace⟩

def legacy (width minimum x : Int) : Int :=
  if width > 0 then ((x + minimum + width - 1) / width) * width else x + minimum

def candidate (width minimum x : Int) : Int :=
  if width = 0 then x else legacy width minimum x

def removeTabs : List Token → List Token
  | [] => []
  | .glyph n :: ts => .glyph n :: removeTabs ts
  | .tab :: ts => removeTabs ts

def scalar (policy : Policy) : List Token → Int → Int
  | [], x => x
  | .glyph n :: ts, x => scalar policy ts (x + n)
  | .tab :: ts, x => scalar policy ts (policy x)

@[simp] theorem zero_identity (minimum x : Int) : candidate 0 minimum x = x := by
  simp [candidate]

theorem nonzero_preservation (w m x : Int) (h : w ≠ 0) :
    candidate w m x = legacy w m x := by simp [candidate,h]

@[simp] theorem view_commit (mode : Mode) (s : NativeState) :
    view (commit mode s) = view s := by simp [view,commit]

theorem step_agreement (mode : Mode) (policy : Policy) (s : NativeState) (t : Token) :
    view (nativeStep mode policy s t) = specStep policy (view s) t := by
  cases t <;> simp [nativeStep,view,specStep,commit,Int.add_assoc]

theorem loop_agreement (mode : Mode) (policy : Policy) (ts : List Token) (s : NativeState) :
    view (nativeLoop mode policy ts s) = specRun policy ts (view s) := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih => simp only [nativeLoop,specRun,ih,step_agreement]

theorem run_agreement (mode : Mode) (policy : Policy) (ts : List Token) (s : NativeState) :
    view (nativeRun mode policy ts s) = specRun policy ts (view s) := by
  simp [nativeRun,loop_agreement]

theorem spec_scalar (policy : Policy) (ts : List Token) (s : Observation) :
    (specRun policy ts s).advance = scalar policy ts s.advance := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih => cases t <;> simp [specRun,specStep,scalar,ih]

theorem zero_delete (ts : List Token) (x : Int) :
    scalar id ts x = scalar id (removeTabs ts) x := by
  induction ts generalizing x with
  | nil => rfl
  | cons t ts ih => cases t <;> simp [scalar,removeTabs,ih]

theorem scalar_append (policy : Policy) (a b : List Token) (x : Int) :
    scalar policy (a ++ b) x = scalar policy b (scalar policy a x) := by
  induction a generalizing x with
  | nil => rfl
  | cons t ts ih => cases t <;> simp [scalar,ih]

theorem scalar_policy_congr (f g : Policy) (h : ∀ x, f x = g x) (ts : List Token) (x : Int) :
    scalar f ts x = scalar g ts x := by
  have heq : f = g := funext h
  rw [heq]

theorem native_policy_congr (mode : Mode) (f g : Policy) (h : ∀ x, f x = g x)
    (ts : List Token) (s : NativeState) : nativeRun mode f ts s = nativeRun mode g ts s := by
  have heq : f = g := funext h
  rw [heq]

theorem nonzero_native_preservation (mode : Mode) (w m : Int) (h : w ≠ 0)
    (ts : List Token) (s : NativeState) :
    nativeRun mode (candidate w m) ts s = nativeRun mode (legacy w m) ts s := by
  apply native_policy_congr
  intro x
  exact nonzero_preservation w m x h

theorem zero_native_advance (mode : Mode) (m : Int) (ts : List Token) (s : NativeState) :
    (view (nativeRun mode (candidate 0 m) ts s)).advance =
      scalar id (removeTabs ts) (view s).advance := by
  rw [run_agreement,spec_scalar]
  have h : candidate 0 m = id := funext (zero_identity m)
  rw [h,zero_delete]

theorem normal_zero_step (policy : Policy) (s : NormalState) (t : Token) :
    normalView (normalStep false policy s t) = specStep id (normalView s) t := by
  cases t <;> rfl

theorem normal_zero_agreement (policy : Policy) (ts : List Token) (s : NormalState) :
    normalView (normalLoop false policy ts s) = specRun id ts (normalView s) := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih => simp only [normalLoop,specRun,ih,normal_zero_step]

theorem normal_zero_delete (policy : Policy) (ts : List Token) (s : NormalState) :
    (normalView (normalLoop false policy ts s)).advance = scalar id (removeTabs ts) s.measured := by
  rw [normal_zero_agreement,spec_scalar,zero_delete]
  rfl

theorem normal_policy_congr (calculate : Bool) (f g : Policy) (h : ∀ x, f x = g x)
    (ts : List Token) (s : NormalState) : normalLoop calculate f ts s = normalLoop calculate g ts s := by
  have heq : f = g := funext h
  rw [heq]

theorem nonzero_normal_preservation (calculate : Bool) (w m : Int) (h : w ≠ 0)
    (ts : List Token) (s : NormalState) :
    normalLoop calculate (candidate w m) ts s = normalLoop calculate (legacy w m) ts s := by
  apply normal_policy_congr
  intro x
  exact nonzero_preservation w m x h

theorem zero_caller_agreement (mode : Mode) (m : Int) (ts : List Token)
    (s : NativeState) (n : NormalState) (h : view s = normalView n) :
    view (nativeRun mode (candidate 0 m) ts s) = normalView (normalLoop false (candidate 0 m) ts n) := by
  rw [run_agreement,normal_zero_agreement,h]
  have hp : candidate 0 m = id := funext (zero_identity m)
  rw [hp]

theorem native_empty (mode : Mode) (policy : Policy) (s : NativeState) :
    nativeRun mode policy [] s = commit mode s := rfl

theorem zero_tab_only (n : Nat) (x : Int) : scalar id (List.replicate n .tab) x = x := by
  induction n with
  | zero => rfl
  | succ n ih => simpa [List.replicate_succ,scalar] using ih


theorem spec_append (policy : Policy) (a b : List Token) (s : Observation) :
    specRun policy (a ++ b) s = specRun policy b (specRun policy a s) := by
  induction a generalizing s with
  | nil => rfl
  | cons t ts ih => simp [specRun,ih]

theorem native_sequential (mode : Mode) (policy : Policy) (a b : List Token) (s : NativeState) :
    view (nativeRun mode policy b (nativeRun mode policy a s)) =
      view (nativeRun mode policy (a ++ b) s) := by
  simp only [run_agreement,spec_append]

theorem minimum_empty_preserved (policy : Policy) (ts : List Token) (s : NativeState) :
    (nativeLoop .minimum policy ts s).empty = s.empty := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih => cases t <;> simp only [nativeLoop,ih] <;> rfl

theorem preferred_start_preserved (policy : Policy) (ts : List Token) (s : NativeState) :
    (nativeLoop .preferred policy ts s).atStart = s.atStart := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih => cases t <;> simp only [nativeLoop,ih] <;> rfl

theorem normal_zero_cache_preserved (policy : Policy) (ts : List Token) (s : NormalState) :
    (normalLoop false policy ts s).records = s.records := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih => cases t <;> simp [normalLoop,ih,normalStep]

theorem normal_zero_offset_preserved (policy : Policy) (ts : List Token) (s : NormalState) :
    (normalLoop false policy ts s).offset = s.offset := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih => cases t <;> simp [normalLoop,ih,normalStep]

theorem normal_zero_provider_preserved (policy : Policy) (ts : List Token) (s : NormalState) :
    (normalLoop false policy ts s).provider = s.provider := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih => cases t <;> simp [normalLoop,ih,normalStep]


theorem preferred_tab_nonempty (policy : Policy) (s : NativeState) :
    (nativeStep .preferred policy s .tab).empty = false := by rfl

theorem normal_positive_record (policy : Policy) (s : NormalState) :
    (normalStep true policy s .tab).records = s.records ++ [(s.cursor-s.origin,policy s.offset-s.offset)] := by rfl

end Tab
