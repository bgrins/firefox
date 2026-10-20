import WrapperSkip
set_option autoImplicit false
namespace WrapperNext
open PublicCache

def native (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) : PublicFetch.Output :=
 let skipped := WrapperSkip.native bytes read names s
 let fetched := PublicNext.native bytes read stop names skipped.state
 ⟨fetched.state,skipped.events++fetched.events,fetched.token⟩

def reference (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (cursor : Cursor) : PublicNext.Reference :=
 let skipped := WrapperSkip.reference bytes read cursor
 let fetched := PublicNext.reference bytes read stop skipped.cursor
 ⟨fetched.cursor,fetched.token,skipped.observations++fetched.observations⟩

theorem second_cleanup_empty (bytes : List Byte) (read : Nat → Lexeme)
 (names : List (List Byte)) (s : State) :
 PublicCleanup.pending bytes.length read names (WrapperSkip.native bytes read names s).state =
 ⟨(WrapperSkip.native bytes read names s).state,[],true⟩ := by
 simp [PublicCleanup.pending,WrapperSkip.skip_pending_none]

theorem actual_fetch_join (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 native bytes read stop names s =
 let skipped := WrapperSkip.native bytes read names s
 let fetched := PublicFetch.fetchReady bytes read stop names skipped.state
 ⟨fetched.state,skipped.events++fetched.events,fetched.token⟩ := by
 simp [native,PublicNext.native,second_cleanup_empty]

theorem next_coherent (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 coherent read (native bytes read stop names s).state :=
 PublicNext.coherent_next _ _ _ _ _ (WrapperSkip.skip_coherent _ _ _ _ h)

theorem next_compatible (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : compatible names s.mode) :
 compatible names (native bytes read stop names s).state.mode :=
 PublicNext.compatible_next _ _ _ _ _ (WrapperSkip.skip_compatible _ _ _ _ h)

theorem next_cursor (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 (native bytes read stop names s).state.cursor=(reference bytes read stop s.cursor).cursor := by
 simp only [native,reference]
 rw [PublicNext.next_cursor _ _ _ _ _ (WrapperSkip.skip_coherent _ _ _ _ h),WrapperSkip.skip_cursor]

theorem next_token (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 (native bytes read stop names s).token=(reference bytes read stop s.cursor).token := by
 simp only [native,reference]
 rw [PublicNext.next_token _ _ _ _ _ (WrapperSkip.skip_coherent _ _ _ _ h),WrapperSkip.skip_cursor]

theorem next_saved (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 (native bytes read stop names s).state.saved=s.saved := by
 simp only [native,PublicNext.next_saved,WrapperSkip.skip_saved]

theorem next_seen (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (hc : coherent read s)
 (ht : compatible names s.mode) (hi : TrackingEpoch.Inv (project names s)) :
 seen (native bytes read stop names s).state.mode =
 (seen s.mode || (reference bytes read stop s.cursor).observations.any (relevant names)) := by
 have h := PublicNext.next_seen bytes read stop names (WrapperSkip.native bytes read names s).state
   (WrapperSkip.skip_coherent _ _ _ _ hc) (WrapperSkip.skip_compatible _ _ _ _ ht)
   (WrapperSkip.skip_inv _ _ _ _ ht hi)
 simpa [native,reference,WrapperSkip.skip_seen _ _ _ _ ht hi,WrapperSkip.skip_cursor,
   List.any_append,Bool.or_assoc] using h

theorem next_inv (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (ht : compatible names s.mode)
 (hi : TrackingEpoch.Inv (project names s)) :
 TrackingEpoch.Inv (project names (native bytes read stop names s).state) :=
 PublicNext.next_inv _ _ _ _ _ (WrapperSkip.skip_compatible _ _ _ _ ht)
   (WrapperSkip.skip_inv _ _ _ _ ht hi)

theorem returned_cache (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (token : Token)
 (h : (native bytes read stop names s).token=some token) :
 cacheRelevant names (native bytes read stop names s).state=relevant names token :=
 PublicEntry.returned_cache _ _ _ _ _ _ h

theorem colon_safe_entry (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State)
 (h : (native bytes read stop names s).token=some .colon) :
 cacheRelevant names (native bytes read stop names s).state=false := returned_cache _ _ _ _ _ _ h

def writes (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (cursor : Cursor) (key : Option Nat) : List Token :=
 let skipped := WrapperSkip.reference bytes read cursor
 skipped.writes++PublicAnnotations.nextWrites bytes read stop skipped.cursor key

theorem next_writes (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 (native bytes read stop names s).state.urls =
 PublicAnnotations.applyTokens (writes bytes read stop s.cursor (PublicAnnotations.key s)) s.urls := by
 simp only [native,PublicAnnotations.next_writes,writes,PublicAnnotations.applyTokens,List.foldl_append]
 rw [WrapperSkip.skip_cursor,WrapperSkip.skip_writes]
 simp only [PublicAnnotations.key,WrapperSkip.skip_cache,PublicAnnotations.applyTokens]

end WrapperNext
