import RawRecovery
set_option autoImplicit false
namespace NestedControl
open PublicCache

structure State where
  core : PublicCache.State
  stops : List Byte
  depth : Fin 256
  limit : Fin 256
  deriving DecidableEq, Repr

structure Reference where
  core : PublicHistory.Reference
  stops : List Byte
  depth : Fin 256
  limit : Fin 256
  deriving DecidableEq, Repr

structure Aligned (read : Nat → Lexeme) (names : List (List Byte)) (s : State) (r : Reference) : Prop where
  core : PublicHistory.Aligned read names s.core r.core
  stops : s.stops = r.stops
  depth : s.depth = r.depth
  limit : s.limit = r.limit

def closing : Block → Byte
  | .parenthesis => 41
  | .square => 93
  | .curly => 125

def increment (depth : Fin 256) : Fin 256 := depth + 1
def decrement (depth : Fin 256) : Fin 256 := depth - 1

inductive Outcome where
  | noOpening
  | depthLimit
  | parsed (success : Bool)
  deriving DecidableEq, Repr

def consume (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (block : Block) (s : PublicCache.State) : PublicCache.State :=
  (PublicCleanup.run length read names (length-s.cursor.position) [block] s).state

def referenceConsume (length : Nat) (read : Nat → Lexeme) (block : Block)
    (r : PublicHistory.Reference) : PublicHistory.Reference :=
  let consumed := PublicSourceOnly.cleanup length read (length-r.cursor.position) [block] r.cursor
  {r with cursor := consumed.cursor, observations := r.observations ++ consumed.tokens}

theorem consume_aligned (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (block : Block) (s : PublicCache.State) (r : PublicHistory.Reference)
    (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (consume length read names block s)
      (referenceConsume length read block r) := by
  refine ⟨?_, ?_, PublicCleanup.run_coherent _ _ _ _ _ _ h.cache_coherent,
    PublicCleanup.run_compatible _ _ _ _ _ _ h.mode_compatible, ?_, ?_⟩
  · simpa [consume, referenceConsume, h.cursor_eq] using
      PublicSourceOnly.cleanup_cursor length read names (length-s.cursor.position) [block] s
  · simpa [consume, referenceConsume, h.saved_eq] using
      PublicNext.cleanup_saved length read names (length-s.cursor.position) [block] s
  · rw [consume, PublicCleanup.run_project _ _ _ _ _ _ h.mode_compatible]
    exact TrackingEpoch.prefix_inv _ _ h.cache_seen
  · simpa [consume, referenceConsume, h.cursor_eq, h.seen_eq, List.any_append] using
      RawRecovery.cleanup_seen length read names (length-s.cursor.position) [block] s h.mode_compatible

def finish (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (block : Block) (s : PublicCache.State) : PublicCache.State :=
  consume bytes.length read names block (PublicCleanup.pending bytes.length read names s).state

def referenceFinish (bytes : List Byte) (read : Nat → Lexeme) (block : Block)
    (r : PublicHistory.Reference) : PublicHistory.Reference :=
  referenceConsume bytes.length read block (RawRecovery.pendingReference bytes.length read r)

theorem finish_aligned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (block : Block) (s : PublicCache.State) (r : PublicHistory.Reference)
    (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (finish bytes read names block s)
      (referenceFinish bytes read block r) :=
  consume_aligned _ _ _ _ _ _ (RawRecovery.pending_aligned _ _ _ _ _ h)

def native (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (body : List Byte → WrapperControl.Program) (s : State) : Outcome × State :=
  match s.core.cursor.pending with
  | none => (.noOpening,s)
  | some block =>
    let taken := PublicCleanup.clear s.core
    if s.depth.val ≥ s.limit.val && s.limit.val != 0 then
      (.depthLimit, {s with core := consume bytes.length read names block taken})
    else
      let entered := {s with core := taken, stops := [closing block], depth := increment s.depth}
      let parsed := WrapperControl.native bytes read names (.entirely (body entered.stops) entered.stops) entered.core
      (.parsed parsed.1, {entered with core := finish bytes read names block parsed.2, stops := entered.stops, depth := decrement entered.depth})

def reference (bytes : List Byte) (read : Nat → Lexeme)
    (body : List Byte → WrapperControl.Program) (r : Reference) : Outcome × Reference :=
  match r.core.cursor.pending with
  | none => (.noOpening,r)
  | some block =>
    let taken := RawRecovery.clearReference r.core
    if r.depth.val ≥ r.limit.val && r.limit.val != 0 then
      (.depthLimit, {r with core := referenceConsume bytes.length read block taken})
    else
      let entered := {r with core := taken, stops := [closing block], depth := increment r.depth}
      let parsed := WrapperControl.reference bytes read (.entirely (body entered.stops) entered.stops) entered.core
      (.parsed parsed.1, {entered with core := referenceFinish bytes read block parsed.2, stops := r.stops, depth := decrement entered.depth})

theorem clear_aligned (read : Nat → Lexeme) (names : List (List Byte))
    (s : PublicCache.State) (r : PublicHistory.Reference) (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (PublicCleanup.clear s) (RawRecovery.clearReference r) :=
  ⟨by simp [PublicCleanup.clear, RawRecovery.clearReference, h.cursor_eq],
    h.saved_eq, h.cache_coherent, h.mode_compatible, h.cache_seen, h.seen_eq⟩

theorem nested_refines (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (body : List Byte → WrapperControl.Program) (s : State) (r : Reference)
    (h : Aligned read names s r) :
    (native bytes read names body s).1 = (reference bytes read body r).1 ∧
    Aligned read names (native bytes read names body s).2 (reference bytes read body r).2 := by
  have hc := h.core.cursor_eq
  cases hp : r.core.cursor.pending with
  | none => simp [native, reference, hc, hp, h]
  | some block =>
    have cleared := clear_aligned read names s.core r.core h.core
    simp only [native, reference, hc, hp, h.depth, h.limit]
    split
    · exact ⟨rfl, consume_aligned _ _ _ _ _ _ cleared, h.stops, rfl, rfl⟩
    · have parsed := WrapperControl.program_refines bytes read names
        (.entirely (body [closing block]) [closing block]) _ _ cleared
      exact ⟨congrArg Outcome.parsed parsed.1,
        finish_aligned _ _ _ _ _ _ parsed.2, h.stops, rfl, rfl⟩

theorem nested_restores_stop_depth (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (body : List Byte → WrapperControl.Program) (s : State) :
    (native bytes read names body s).2.stops = s.stops ∧
    (native bytes read names body s).2.depth = s.depth := by
  unfold native
  split
  · exact ⟨rfl,rfl⟩
  · split
    · exact ⟨rfl,rfl⟩
    · refine ⟨rfl, ?_⟩
      apply Fin.ext
      simp [decrement, increment, Fin.add_def, Fin.sub_def]
      omega

def untilBefore (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : State) : Bool × State :=
  let combined := s.stops ++ extra
  let parsed := WrapperControl.native bytes read names (.entirely (body combined) combined) s.core
  if stopOnError && !parsed.1 then (parsed.1,{s with core := parsed.2})
  else (parsed.1,{s with core := RawRecovery.recover bytes read names combined parsed.2})

def referenceUntilBefore (bytes : List Byte) (read : Nat → Lexeme)
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (r : Reference) : Bool × Reference :=
  let combined := r.stops ++ extra
  let parsed := WrapperControl.reference bytes read (.entirely (body combined) combined) r.core
  if stopOnError && !parsed.1 then (parsed.1,{r with core := parsed.2})
  else (parsed.1,{r with core := RawRecovery.referenceRecover bytes read combined parsed.2})

theorem until_before_refines (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : State) (r : Reference) (h : Aligned read names s r) :
    (untilBefore bytes read names extra stopOnError body s).1 =
      (referenceUntilBefore bytes read extra stopOnError body r).1 ∧
    Aligned read names (untilBefore bytes read names extra stopOnError body s).2
      (referenceUntilBefore bytes read extra stopOnError body r).2 := by
  have parsed := WrapperControl.program_refines bytes read names
    (.entirely (body (r.stops++extra)) (r.stops++extra)) _ _ h.core
  simp only [untilBefore, referenceUntilBefore, h.stops, parsed.1]
  split
  · exact ⟨rfl, parsed.2, rfl, h.depth, h.limit⟩
  · exact ⟨rfl, RawRecovery.recover_aligned _ _ _ _ _ _ parsed.2, rfl, h.depth, h.limit⟩

end NestedControl
