import WrapperNext
set_option autoImplicit false
namespace WrapperHistory
open PublicCache

inductive Action where
 | skip
 | next (stops : List Byte)
 | primary (stops : List Byte)
 | save
 | restore (index : Nat)
 deriving DecidableEq, Repr

def nativeStep (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) : Action → State
 | .skip => (WrapperSkip.native bytes read names s).state
 | .next stops => (WrapperNext.native bytes read stops.contains names s).state
 | .primary stops => (PublicNext.native bytes read stops.contains names s).state
 | .save => save s
 | .restore index => restore index s

def referenceStep (bytes : List Byte) (read : Nat → Lexeme)
 (r : PublicHistory.Reference) : Action → PublicHistory.Reference
 | .skip => let skipped := WrapperSkip.reference bytes read r.cursor
            {r with cursor:=skipped.cursor,observations:=r.observations++skipped.observations}
 | .next stops => let fetched := WrapperNext.reference bytes read stops.contains r.cursor
                  {r with cursor:=fetched.cursor,observations:=r.observations++fetched.observations}
 | .primary stops => PublicHistory.referenceStep bytes read r (.fetch stops)
 | .save => PublicHistory.referenceStep bytes read r .save
 | .restore index => PublicHistory.referenceStep bytes read r (.restore index)

theorem step_aligned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (r : PublicHistory.Reference) (a : Action) (h : PublicHistory.Aligned read names s r) :
 PublicHistory.Aligned read names (nativeStep bytes read names s a) (referenceStep bytes read r a) := by
 cases a with
 | skip =>
   refine ⟨?_,?_,WrapperSkip.skip_coherent _ _ _ _ h.cache_coherent,
     WrapperSkip.skip_compatible _ _ _ _ h.mode_compatible,
     WrapperSkip.skip_inv _ _ _ _ h.mode_compatible h.cache_seen,?_⟩
   · simpa [nativeStep,referenceStep,h.cursor_eq] using WrapperSkip.skip_cursor bytes read names s
   · simpa [nativeStep,referenceStep,h.saved_eq] using WrapperSkip.skip_saved bytes read names s
   · simpa [nativeStep,referenceStep,h.cursor_eq,h.seen_eq,List.any_append] using
       WrapperSkip.skip_seen bytes read names s h.mode_compatible h.cache_seen
 | next stops =>
   refine ⟨?_,?_,WrapperNext.next_coherent _ _ _ _ _ h.cache_coherent,
     WrapperNext.next_compatible _ _ _ _ _ h.mode_compatible,
     WrapperNext.next_inv _ _ _ _ _ h.mode_compatible h.cache_seen,?_⟩
   · simpa [nativeStep,referenceStep,h.cursor_eq] using
       WrapperNext.next_cursor bytes read stops.contains names s h.cache_coherent
   · simpa [nativeStep,referenceStep,h.saved_eq] using WrapperNext.next_saved bytes read stops.contains names s
   · simpa [nativeStep,referenceStep,h.cursor_eq,h.seen_eq,List.any_append] using
       WrapperNext.next_seen bytes read stops.contains names s h.cache_coherent h.mode_compatible h.cache_seen
 | primary stops => exact PublicHistory.step_aligned _ _ _ _ _ (.fetch stops) h
 | save => exact PublicHistory.step_aligned bytes read names s r .save h
 | restore index => exact PublicHistory.step_aligned bytes read names s r (.restore index) h

theorem histories_aligned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (actions : List Action) (s : State) (r : PublicHistory.Reference) (h : PublicHistory.Aligned read names s r) :
 PublicHistory.Aligned read names (actions.foldl (nativeStep bytes read names) s)
   (actions.foldl (referenceStep bytes read) r) := by
 induction actions generalizing s r with
 | nil => exact h
 | cons a rest ih => exact ih _ _ (step_aligned _ _ _ _ _ _ h)

def returned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) : Action → List (Option Token)
 | .next stops => [(WrapperNext.native bytes read stops.contains names s).token]
 | .primary stops => [(PublicNext.native bytes read stops.contains names s).token]
 | _ => []

def referenceReturned (bytes : List Byte) (read : Nat → Lexeme)
 (cursor : Cursor) : Action → List (Option Token)
 | .next stops => [(WrapperNext.reference bytes read stops.contains cursor).token]
 | .primary stops => [(PublicNext.reference bytes read stops.contains cursor).token]
 | _ => []

theorem step_returns (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (a : Action) (h : coherent read s) :
 returned bytes read names s a=referenceReturned bytes read s.cursor a := by
 cases a with
 | next stops => exact congrArg List.singleton (WrapperNext.next_token _ _ _ _ _ h)
 | primary stops => exact congrArg List.singleton (PublicNext.next_token _ _ _ _ _ h)
 | skip => rfl
 | save => rfl
 | restore _ => rfl

def nativeReturns (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) :
 List Action → State → List (Option Token)
 | [],_ => []
 | a::rest,s => returned bytes read names s a++nativeReturns bytes read names rest (nativeStep bytes read names s a)

def referenceReturns (bytes : List Byte) (read : Nat → Lexeme) :
 List Action → PublicHistory.Reference → List (Option Token)
 | [],_ => []
 | a::rest,r => referenceReturned bytes read r.cursor a++referenceReturns bytes read rest (referenceStep bytes read r a)

theorem histories_return (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (actions : List Action) (s : State) (r : PublicHistory.Reference) (h : PublicHistory.Aligned read names s r) :
 nativeReturns bytes read names actions s=referenceReturns bytes read actions r := by
 induction actions generalizing s r with
 | nil => rfl
 | cons a rest ih =>
   simp only [nativeReturns,referenceReturns]
   rw [step_returns _ _ _ _ _ h.cache_coherent,h.cursor_eq,ih _ _ (step_aligned _ _ _ _ _ _ h)]

theorem query_after_wrappers (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (actions : List Action) (s : State) (hc : coherent read s) (safe : cacheRelevant names s=false) :
 let final := actions.foldl (nativeStep bytes read names) (PublicHistory.begin names s)
 (PublicHistory.query final).1 =
   (actions.foldl (referenceStep bytes read) (PublicHistory.initialReference s)).observations.any (relevant names) ∧
 (PublicHistory.query final).2.mode=.off := by
 have h := histories_aligned bytes read names actions _ _ (PublicHistory.begin_aligned read names s hc safe)
 exact ⟨h.seen_eq,rfl⟩

theorem byte_constructor_returns (provider : ByteLex.Family → List Byte → Nat)
 (bytes : List Byte) (names : List (List Byte)) (actions : List Action) (urls : CommentDirectives.URLs) :
 nativeReturns bytes (ByteLex.read provider bytes) names actions (PublicHistory.begin names (constructor urls)) =
 referenceReturns bytes (ByteLex.read provider bytes) actions (PublicHistory.initialReference (constructor urls)) :=
 histories_return _ _ _ _ _ _ (PublicHistory.constructor_begin _ _ _)

end WrapperHistory
