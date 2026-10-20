import WrapperWhitespace
set_option autoImplicit false
namespace WrapperSkip
open PublicCache

theorem cleanup_pending_none (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) (h : s.cursor.pending=none) :
 (PublicCleanup.run length read names fuel stack s).state.cursor.pending=none := by
 induction fuel generalizing stack s with
 | zero => exact h
 | succ fuel ih =>
   simp only [PublicCleanup.run]
   split
   · exact h
   · exact ih _ _ rfl

theorem pending_none (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) : (PublicCleanup.pending length read names s).state.cursor.pending=none := by
 cases hp : s.cursor.pending with
 | none => simp [PublicCleanup.pending,hp]
 | some block =>
   simp only [PublicCleanup.pending,hp]
   exact cleanup_pending_none _ _ _ _ _ _ rfl

def native (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) : PublicCleanup.Output :=
 let pending := PublicCleanup.pending bytes.length read names s
 ⟨WrapperWhitespace.run bytes (bytes.length+1) pending.state,pending.events,pending.complete⟩

structure Reference where
 cursor : Cursor
 observations : List Token
 writes : List Token
 deriving DecidableEq, Repr

def reference (bytes : List Byte) (read : Nat → Lexeme) (cursor : Cursor) : Reference :=
 let pending := PublicSourceOnly.pending bytes.length read cursor
 let scanned := WrapperWhitespace.reference bytes (bytes.length+1) pending.cursor.position
 ⟨{pending.cursor with position:=scanned.position},pending.tokens,
   pending.tokens++scanned.comments.map Token.comment⟩

theorem skip_cursor (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 (native bytes read names s).state.cursor=(reference bytes read s.cursor).cursor := by
 simp only [native,reference,WrapperWhitespace.run_cursor,PublicSourceOnly.pending_cursor]

theorem skip_pending_none (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 (native bytes read names s).state.cursor.pending=none := by
 simp only [native,WrapperWhitespace.run_cursor]
 exact pending_none _ _ _ _

theorem skip_stopped (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 WrapperWhitespace.nativeUnit (bytes.drop (native bytes read names s).state.cursor.position)=none := by
 apply WrapperWhitespace.exhaustion
 omega

theorem skip_cleanup_complete (bytes : List Byte) (read : Nat → Lexeme)
 (names : List (List Byte)) (s : State) (hp : PublicCleanup.Progress bytes.length read) :
 (native bytes read names s).complete=true :=
 PublicCleanup.pending_complete _ _ _ _ hp

theorem skip_cache (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 (native bytes read names s).state.cache=s.cache := by
 simp only [native,WrapperWhitespace.run_cache,PublicNext.pending_cache]

theorem skip_coherent (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : coherent read s) : coherent read (native bytes read names s).state := by
 intro c hc
 exact h c (by simpa [skip_cache] using hc)

theorem skip_saved (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 (native bytes read names s).state.saved=s.saved := by
 simp only [native,WrapperWhitespace.run_saved,PublicNext.pending_saved]

theorem skip_compatible (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : compatible names s.mode) : compatible names (native bytes read names s).state.mode := by
 simpa only [native,WrapperWhitespace.run_mode] using PublicCleanup.pending_compatible bytes.length read names s h

theorem skip_project (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : compatible names s.mode) :
 project names (native bytes read names s).state =
 (native bytes read names s).events.foldl TrackingEpoch.nativeStep (project names s) := by
 simp only [native,WrapperWhitespace.run_project]
 exact PublicCleanup.pending_project _ _ _ _ h

theorem skip_observations (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 TrackingEpoch.reference (cacheRelevant names s) (native bytes read names s).events =
 (reference bytes read s.cursor).observations.map (relevant names) := by
 simp only [native,reference,PublicSourceOnly.pending_events]
 simpa [TrackingEpoch.reference] using PublicNext.raw_reference_append (cacheRelevant names s)
   (PublicSourceOnly.pending bytes.length read s.cursor).tokens names []

theorem skip_inv (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (ht : compatible names s.mode) (hi : TrackingEpoch.Inv (project names s)) :
 TrackingEpoch.Inv (project names (native bytes read names s).state) := by
 rw [skip_project _ _ _ _ ht]
 exact TrackingEpoch.prefix_inv _ _ hi

theorem skip_seen (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (ht : compatible names s.mode) (hi : TrackingEpoch.Inv (project names s)) :
 seen (native bytes read names s).state.mode =
 (seen s.mode || (reference bytes read s.cursor).observations.any (relevant names)) := by
 have h := TrackingEpoch.execution (native bytes read names s).events (project names s) hi
 rw [← skip_project _ _ _ _ ht] at h
 simp only [project] at h
 rw [skip_observations] at h
 simpa [List.any_map] using h

theorem publish_as_tokens (bodies : List (List Byte)) (urls : CommentDirectives.URLs) :
 WrapperWhitespace.publish bodies urls = PublicAnnotations.applyTokens (bodies.map Token.comment) urls := by
 induction bodies generalizing urls with
 | nil => rfl
 | cons b bs ih =>
   simp only [WrapperWhitespace.publish,List.foldl_cons,List.map_cons,PublicAnnotations.applyTokens,annotate]
   rw [← CommentDirectives.update_reference]
   exact ih _

theorem skip_writes (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 (native bytes read names s).state.urls =
 PublicAnnotations.applyTokens (reference bytes read s.cursor).writes s.urls := by
 simp only [native,reference,WrapperWhitespace.run_annotations,PublicSourceOnly.pending_cursor,
   PublicAnnotations.pending_writes,publish_as_tokens,PublicAnnotations.applyTokens,List.foldl_append]

theorem safe_entry_preserved (bytes : List Byte) (read : Nat → Lexeme) (names target : List (List Byte)) (s : State) :
 cacheRelevant target (native bytes read names s).state=cacheRelevant target s := by
 simp [cacheRelevant,skip_cache]

end WrapperSkip
