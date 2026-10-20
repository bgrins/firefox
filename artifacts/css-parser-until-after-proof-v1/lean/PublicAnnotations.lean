import PublicHistory
set_option autoImplicit false
namespace PublicAnnotations
open PublicCache

def applyTokens (tokens : List Token) (urls : CommentDirectives.URLs) : CommentDirectives.URLs :=
 tokens.foldl (fun u t => annotate t u) urls

theorem cleanup_writes (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) :
 (PublicCleanup.run length read names fuel stack s).state.urls =
 applyTokens (PublicSourceOnly.cleanup length read fuel stack s.cursor).tokens s.urls := by
 induction fuel generalizing stack s with
 | zero => rfl
 | succ fuel ih =>
   by_cases hd : stack=[] ∨ length≤s.cursor.position
   · simp [PublicCleanup.run,PublicSourceOnly.cleanup,PublicCleanup.done,hd,applyTokens]
   · simp only [PublicCleanup.run,PublicSourceOnly.cleanup,PublicCleanup.done,hd,↓reduceIte]
     exact ih _ _

theorem pending_writes (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 (PublicCleanup.pending length read names s).state.urls =
 applyTokens (PublicSourceOnly.pending length read s.cursor).tokens s.urls := by
 cases hp : s.cursor.pending with
 | none => simp [PublicCleanup.pending,PublicSourceOnly.pending,hp,applyTokens]
 | some block =>
   simp only [PublicCleanup.pending,PublicSourceOnly.pending,hp]
   exact cleanup_writes _ _ _ _ _ _

def readyWrites (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (cursor : Cursor) (key : Option Nat) : List Token :=
 match bytes[cursor.position]? with
 | none => []
 | some b => if stop b || key==some cursor.position then [] else [(read cursor.position).token]

def key (s : State) : Option Nat := s.cache.map Cache.key

theorem ready_writes (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 (PublicFetch.fetchReady bytes read stop names s).state.urls =
 applyTokens (readyWrites bytes read stop s.cursor (key s)) s.urls := by
 cases hb : bytes[s.cursor.position]? with
 | none => simp [PublicFetch.fetchReady,readyWrites,hb,applyTokens]
 | some b =>
   cases hs : stop b with
   | true => simp [PublicFetch.fetchReady,readyWrites,hb,hs,applyTokens]
   | false =>
     cases hc : s.cache with
     | none => simp [PublicFetch.fetchReady,readyWrites,hb,hs,key,hc,applyTokens,PublicFetch.freshOutput,fresh]
     | some c =>
       by_cases hk : c.key=s.cursor.position
       · simp [PublicFetch.fetchReady,readyWrites,hb,hs,key,hc,hk,applyTokens,hit]
       · simp [PublicFetch.fetchReady,readyWrites,hb,hs,key,hc,hk,applyTokens,PublicFetch.freshOutput,fresh]

def nextWrites (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (cursor : Cursor) (key : Option Nat) : List Token :=
 let skipped := PublicSourceOnly.pending bytes.length read cursor
 skipped.tokens ++ readyWrites bytes read stop skipped.cursor key

theorem next_writes (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 (PublicNext.native bytes read stop names s).state.urls =
 applyTokens (nextWrites bytes read stop s.cursor (key s)) s.urls := by
 simp only [PublicNext.native,ready_writes,nextWrites,applyTokens,List.foldl_append]
 rw [PublicSourceOnly.pending_cursor,show key (PublicCleanup.pending bytes.length read names s).state=key s from
   congrArg (Option.map Cache.key) (PublicNext.pending_cache _ _ _ _),pending_writes]
 rfl

theorem hit_has_no_writes (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (cursor : Cursor) : readyWrites bytes read stop cursor (some cursor.position)=[] := by
 unfold readyWrites
 split
 · rfl
 · simp

theorem reset_has_no_writes (index : Nat) (s : State) :
 (restore index s).urls=s.urls := (restore_preserves_effects index s).2

def readyKey (bytes : List Byte) (stop : Byte → Bool) (cursor : Cursor) (old : Option Nat) : Option Nat :=
 match bytes[cursor.position]? with
 | none => old
 | some b => if stop b then old else some cursor.position

theorem ready_key (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 key (PublicFetch.fetchReady bytes read stop names s).state = readyKey bytes stop s.cursor (key s) := by
 cases hb : bytes[s.cursor.position]? with
 | none => simp [PublicFetch.fetchReady,readyKey,hb]
 | some b =>
   cases hs : stop b with
   | true => simp [PublicFetch.fetchReady,readyKey,hb,hs]
   | false =>
     cases hc : s.cache with
     | none => simp [PublicFetch.fetchReady,readyKey,hb,hs,key,hc,PublicFetch.freshOutput,fresh]
     | some c =>
       by_cases hk : c.key=s.cursor.position
       · simp [PublicFetch.fetchReady,readyKey,hb,hs,key,hc,hk,hit]
       · simp [PublicFetch.fetchReady,readyKey,hb,hs,key,hc,hk,PublicFetch.freshOutput,fresh]

@[ext] structure Reference where
 cursor : Cursor
 key : Option Nat
 saved : List Cursor
 urls : CommentDirectives.URLs
 deriving DecidableEq, Repr

def referenceStep (bytes : List Byte) (read : Nat → Lexeme) (r : Reference) : PublicHistory.Action → Reference
 | .fetch stops =>
   let skipped := PublicSourceOnly.pending bytes.length read r.cursor
   let fetched := PublicSourceOnly.ready bytes read stops.contains skipped.cursor
   ⟨fetched.cursor,readyKey bytes stops.contains skipped.cursor r.key,r.saved,
     applyTokens (nextWrites bytes read stops.contains r.cursor r.key) r.urls⟩
 | .save => {r with saved:=r.cursor::r.saved}
 | .restore index => match r.saved[index]? with
                     | some cursor => {r with cursor:=cursor}
                     | none => r

def projection (s : State) : Reference := ⟨s.cursor,key s,s.saved,s.urls⟩

theorem step_projection (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (action : PublicHistory.Action) (hc : coherent read s) :
 projection (PublicHistory.nativeStep bytes read names s action) = referenceStep bytes read (projection s) action := by
 cases action with
 | fetch stops =>
   apply Reference.ext
   · exact PublicNext.next_cursor bytes read stops.contains names s hc
   · simp only [PublicHistory.nativeStep,PublicNext.native,projection,referenceStep,ready_key]
     rw [PublicSourceOnly.pending_cursor]
     exact congrArg (readyKey bytes stops.contains (PublicSourceOnly.pending bytes.length read s.cursor).cursor)
       (congrArg (Option.map Cache.key) (PublicNext.pending_cache _ _ _ _))
   · exact PublicNext.next_saved _ _ _ _ _
   · exact next_writes _ _ _ _ _
 | save => rfl
 | restore index =>
   cases hs : s.saved[index]? <;> simp [PublicHistory.nativeStep,referenceStep,projection,restore,hs,key]

theorem step_coherent (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (action : PublicHistory.Action) (hc : coherent read s) :
 coherent read (PublicHistory.nativeStep bytes read names s action) := by
 cases action with
 | fetch stops => exact PublicNext.coherent_next _ _ _ _ _ hc
 | save => exact hc
 | restore index => exact restore_coherent _ _ _ hc

theorem history_projection (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (actions : List PublicHistory.Action) (s : State) (hc : coherent read s) :
 projection (actions.foldl (PublicHistory.nativeStep bytes read names) s) =
 actions.foldl (referenceStep bytes read) (projection s) := by
 induction actions generalizing s with
 | nil => rfl
 | cons a actions ih =>
   simp only [List.foldl_cons]
   rw [ih _ (step_coherent _ _ _ _ _ hc),step_projection _ _ _ _ _ hc]

theorem constructor_history (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (actions : List PublicHistory.Action) (urls : CommentDirectives.URLs) :
 projection (actions.foldl (PublicHistory.nativeStep bytes read names) (constructor urls)) =
 actions.foldl (referenceStep bytes read) ⟨⟨0,none⟩,none,[],urls⟩ :=
 history_projection _ _ _ _ _ (constructor_coherent _ _)

end PublicAnnotations
