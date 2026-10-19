import PublicCleanup
set_option autoImplicit false
namespace PublicSourceOnly
open PublicCache
structure Skipped where
 cursor : Cursor
 tokens : List Token
 deriving DecidableEq, Repr

def cleanup (length : Nat) (read : Nat → Lexeme) : Nat → List Block → Cursor → Skipped
 | 0,_,cursor => ⟨cursor,[]⟩
 | fuel+1,stack,cursor =>
   if stack=[] ∨ length≤cursor.position then ⟨cursor,[]⟩ else
   let value := read cursor.position
   let rest := cleanup length read fuel (PublicCleanup.stackAfter stack value)
     { value.cursor with pending := none }
   ⟨rest.cursor,value.token::rest.tokens⟩

def pending (length : Nat) (read : Nat → Lexeme) (cursor : Cursor) : Skipped :=
 match cursor.pending with
 | none => ⟨cursor,[]⟩
 | some block => cleanup length read (length-cursor.position) [block] {cursor with pending:=none}

structure Fetched where
 cursor : Cursor
 token : Option Token
 deriving DecidableEq, Repr

def ready (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool) (cursor : Cursor) : Fetched :=
 match bytes[cursor.position]? with
 | none => ⟨cursor,none⟩
 | some b => if stop b then ⟨cursor,none⟩ else
             let value := read cursor.position
             ⟨value.cursor,some value.token⟩

theorem cleanup_cursor (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) :
 (PublicCleanup.run length read names fuel stack s).state.cursor =
   (cleanup length read fuel stack s.cursor).cursor := by
 induction fuel generalizing stack s with
 | zero => rfl
 | succ fuel ih =>
   by_cases hd : stack=[] ∨ length≤s.cursor.position
   · simp [PublicCleanup.run,cleanup,PublicCleanup.done,hd]
   · simp only [PublicCleanup.run,cleanup,PublicCleanup.done,hd,↓reduceIte]
     exact ih _ _

theorem cleanup_events (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) :
 (PublicCleanup.run length read names fuel stack s).events =
   (cleanup length read fuel stack s.cursor).tokens.map (fun t => .raw (relevant names t)) := by
 induction fuel generalizing stack s with
 | zero => rfl
 | succ fuel ih =>
   by_cases hd : stack=[] ∨ length≤s.cursor.position
   · simp [PublicCleanup.run,cleanup,PublicCleanup.done,hd]
   · simp only [PublicCleanup.run,cleanup,PublicCleanup.done,hd,↓reduceIte,List.map_cons]
     congr 1
     exact ih _ _

theorem pending_cursor (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) :
 (PublicCleanup.pending length read names s).state.cursor = (pending length read s.cursor).cursor := by
 cases hp : s.cursor.pending with
 | none => simp [PublicCleanup.pending,pending,hp]
 | some block =>
   simp only [PublicCleanup.pending,pending,hp]
   exact cleanup_cursor _ _ _ _ _ _

theorem pending_events (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) :
 (PublicCleanup.pending length read names s).events =
   (pending length read s.cursor).tokens.map (fun t => .raw (relevant names t)) := by
 cases hp : s.cursor.pending with
 | none => simp [PublicCleanup.pending,pending,hp]
 | some block =>
   simp only [PublicCleanup.pending,pending,hp]
   exact cleanup_events _ _ _ _ _ _

theorem ready_token (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 (PublicFetch.fetchReady bytes read stop names s).token = (ready bytes read stop s.cursor).token := by
 cases hb : bytes[s.cursor.position]? with
 | none => simp [PublicFetch.fetchReady,ready,hb]
 | some b =>
   cases hs : stop b with
   | true => simp [PublicFetch.fetchReady,ready,hb,hs]
   | false =>
     simpa [ready,hb,hs] using PublicFetch.fetch_fresh_token bytes read stop names s h b hb hs

theorem ready_cursor (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 (PublicFetch.fetchReady bytes read stop names s).state.cursor = (ready bytes read stop s.cursor).cursor := by
 cases hb : bytes[s.cursor.position]? with
 | none => simp [PublicFetch.fetchReady,ready,hb]
 | some b =>
   cases hs : stop b with
   | true => simp [PublicFetch.fetchReady,ready,hb,hs]
   | false =>
     cases hc : s.cache with
     | none => simp [PublicFetch.fetchReady,ready,hb,hs,hc,PublicFetch.freshOutput,fresh]
     | some c =>
       by_cases hk : c.key=s.cursor.position
       · simp [PublicFetch.fetchReady,ready,hb,hs,hc,hk,hit,matching_cache_fresh read s c h hc hk]
       · simp [PublicFetch.fetchReady,ready,hb,hs,hc,hk,PublicFetch.freshOutput,fresh]

end PublicSourceOnly
