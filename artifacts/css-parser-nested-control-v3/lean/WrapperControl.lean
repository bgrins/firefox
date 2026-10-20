import WrapperEntry
set_option autoImplicit false
namespace WrapperControl
open PublicCache

def rewind (cursor : Cursor) (s : State) : State := {s with cursor := cursor}

theorem rewind_aligned (read : Nat → Lexeme) (names : List (List Byte))
    (s : State) (r : PublicHistory.Reference) (cursor : Cursor)
    (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (rewind cursor s) {r with cursor := cursor} :=
  ⟨rfl, h.saved_eq, h.cache_coherent, h.mode_compatible, h.cache_seen, h.seen_eq⟩

def expectExhausted (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (stops : List Byte) (s : State) : Bool × State :=
  let fetched := WrapperNext.native bytes read stops.contains names s
  (fetched.token.isNone, rewind s.cursor fetched.state)

def referenceExhausted (bytes : List Byte) (read : Nat → Lexeme)
    (stops : List Byte) (r : PublicHistory.Reference) : Bool × PublicHistory.Reference :=
  let fetched := WrapperNext.reference bytes read stops.contains r.cursor
  (fetched.token.isNone, {r with observations := r.observations ++ fetched.observations})

theorem exhaustion_refines (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (stops : List Byte) (s : State)
    (r : PublicHistory.Reference) (h : PublicHistory.Aligned read names s r) :
    (expectExhausted bytes read names stops s).1 = (referenceExhausted bytes read stops r).1 ∧
    PublicHistory.Aligned read names (expectExhausted bytes read names stops s).2
      (referenceExhausted bytes read stops r).2 := by
  constructor
  · simp only [expectExhausted, referenceExhausted]
    rw [WrapperNext.next_token _ _ _ _ _ h.cache_coherent, h.cursor_eq]
  · have step := WrapperHistory.step_aligned bytes read names s r (.next stops) h
    have reset := rewind_aligned read names _ _ s.cursor step
    simpa [expectExhausted, referenceExhausted, WrapperHistory.nativeStep,
      WrapperHistory.referenceStep, h.cursor_eq] using reset

theorem exhaustion_restores_cursor (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (stops : List Byte) (s : State) :
    (expectExhausted bytes read names stops s).2.cursor = s.cursor := rfl

theorem exhaustion_retains_effects (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (stops : List Byte) (s : State) :
    (expectExhausted bytes read names stops s).2.mode =
      (WrapperNext.native bytes read stops.contains names s).state.mode ∧
    (expectExhausted bytes read names stops s).2.cache =
      (WrapperNext.native bytes read stops.contains names s).state.cache ∧
    (expectExhausted bytes read names stops s).2.urls =
      PublicAnnotations.applyTokens
        (WrapperNext.writes bytes read stops.contains s.cursor (PublicAnnotations.key s)) s.urls := by
  exact ⟨rfl, rfl, WrapperNext.next_writes _ _ _ _ _⟩

inductive Program where
  | callback (actions : List WrapperHistory.Action) (accept : List (Option Token) → Bool)
  | entirely (body : Program) (stops : List Byte)
  | attempt (body : Program)
  | andThen (first second : Program)

def native (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) :
    Program → State → Bool × State
  | .callback actions accept, s =>
    (accept (WrapperHistory.nativeReturns bytes read names actions s),
      actions.foldl (WrapperHistory.nativeStep bytes read names) s)
  | .entirely body stops, s =>
    let result := native bytes read names body s
    if result.1 then expectExhausted bytes read names stops result.2 else result
  | .attempt body, s =>
    let result := native bytes read names body s
    (result.1, if result.1 then result.2 else rewind s.cursor result.2)
  | .andThen first second, s =>
    let result := native bytes read names first s
    if result.1 then native bytes read names second result.2 else result

def reference (bytes : List Byte) (read : Nat → Lexeme) :
    Program → PublicHistory.Reference → Bool × PublicHistory.Reference
  | .callback actions accept, r =>
    (accept (WrapperHistory.referenceReturns bytes read actions r),
      actions.foldl (WrapperHistory.referenceStep bytes read) r)
  | .entirely body stops, r =>
    let result := reference bytes read body r
    if result.1 then referenceExhausted bytes read stops result.2 else result
  | .attempt body, r =>
    let result := reference bytes read body r
    (result.1, if result.1 then result.2 else {result.2 with cursor := r.cursor})
  | .andThen first second, r =>
    let result := reference bytes read first r
    if result.1 then reference bytes read second result.2 else result

theorem program_refines (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (program : Program) (s : State)
    (r : PublicHistory.Reference) (h : PublicHistory.Aligned read names s r) :
    (native bytes read names program s).1 = (reference bytes read program r).1 ∧
    PublicHistory.Aligned read names (native bytes read names program s).2
      (reference bytes read program r).2 := by
  induction program generalizing s r with
  | callback actions accept =>
    exact ⟨congrArg accept (WrapperHistory.histories_return _ _ _ _ _ _ h),
      WrapperHistory.histories_aligned _ _ _ _ _ _ h⟩
  | entirely body stops ih =>
    obtain ⟨result, aligned⟩ := ih s r h
    simp only [native, reference, result]
    cases hr : (reference bytes read body r).1 with
    | false => simpa [hr] using And.intro result aligned
    | true => simpa [hr] using exhaustion_refines bytes read names stops _ _ aligned
  | attempt body ih =>
    obtain ⟨result, aligned⟩ := ih s r h
    simp only [native, reference, result]
    cases hr : (reference bytes read body r).1 with
    | true => simpa [hr] using aligned
    | false =>
      simpa [hr, h.cursor_eq] using rewind_aligned read names _ _ s.cursor aligned
  | andThen first second first_ih second_ih =>
    obtain ⟨result, aligned⟩ := first_ih s r h
    simp only [native, reference, result]
    cases hr : (reference bytes read first r).1 with
    | false => simpa [hr] using And.intro result aligned
    | true => simpa [hr] using second_ih _ _ aligned

theorem constructor_program_query (provider : ByteLex.Family → List Byte → Nat)
    (bytes : List Byte) (names : List (List Byte)) (program : Program)
    (urls : CommentDirectives.URLs) :
    (PublicHistory.query
      (native bytes (ByteLex.read provider bytes) names program
        (PublicHistory.begin names (constructor urls))).2).1 =
    (reference bytes (ByteLex.read provider bytes) program
      (PublicHistory.initialReference (constructor urls))).2.observations.any (relevant names) :=
  (program_refines _ _ _ _ _ _ (PublicHistory.constructor_begin _ _ _)).2.seen_eq

theorem attempt_failure_retains_effects (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (body : Program) (s : State)
    (failed : (native bytes read names body s).1 = false) :
    (native bytes read names (.attempt body) s).2.cursor = s.cursor ∧
    (native bytes read names (.attempt body) s).2.mode = (native bytes read names body s).2.mode ∧
    (native bytes read names (.attempt body) s).2.cache = (native bytes read names body s).2.cache ∧
    (native bytes read names (.attempt body) s).2.urls = (native bytes read names body s).2.urls := by
  simp [native, failed, rewind]

end WrapperControl
