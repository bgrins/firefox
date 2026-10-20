import PublicSourceOnly
set_option autoImplicit false
namespace PublicNext
open PublicCache

def native (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) : PublicFetch.Output :=
 let skipped := PublicCleanup.pending bytes.length read names s
 let fetched := PublicFetch.fetchReady bytes read stop names skipped.state
 ⟨fetched.state,skipped.events++fetched.events,fetched.token⟩

structure Reference where
 cursor : Cursor
 token : Option Token
 observations : List Token
 deriving DecidableEq, Repr

def reference (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (cursor : Cursor) : Reference :=
 let skipped := PublicSourceOnly.pending bytes.length read cursor
 let fetched := PublicSourceOnly.ready bytes read stop skipped.cursor
 ⟨fetched.cursor,fetched.token,skipped.tokens++fetched.token.toList⟩

theorem coherent_next (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 coherent read (native bytes read stop names s).state :=
 PublicFetch.fetch_coherent _ _ _ _ _ (PublicCleanup.pending_coherent _ _ _ _ h)

theorem compatible_next (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : compatible names s.mode) :
 compatible names (native bytes read stop names s).state.mode :=
 PublicFetch.fetch_compatible _ _ _ _ _ (PublicCleanup.pending_compatible _ _ _ _ h)

theorem next_project (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : compatible names s.mode) :
 project names (native bytes read stop names s).state =
 (native bytes read stop names s).events.foldl TrackingEpoch.nativeStep (project names s) := by
 simp only [native,List.foldl_append]
 rw [PublicFetch.fetch_project _ _ _ _ _ (PublicCleanup.pending_compatible _ _ _ _ h),
   PublicCleanup.pending_project _ _ _ _ h]

theorem next_cursor (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 (native bytes read stop names s).state.cursor = (reference bytes read stop s.cursor).cursor := by
 simp only [native,reference]
 rw [PublicSourceOnly.ready_cursor _ _ _ _ _ (PublicCleanup.pending_coherent _ _ _ _ h),
   PublicSourceOnly.pending_cursor]

theorem next_token (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 (native bytes read stop names s).token = (reference bytes read stop s.cursor).token := by
 simp only [native,reference]
 rw [PublicSourceOnly.ready_token _ _ _ _ _ (PublicCleanup.pending_coherent _ _ _ _ h),
   PublicSourceOnly.pending_cursor]

theorem raw_reference_append (cache : Bool) (tokens : List Token) (names : List (List Byte))
 (events : List TrackingEpoch.Event) :
 TrackingEpoch.reference cache (tokens.map (fun t => .raw (relevant names t))++events) =
 tokens.map (relevant names) ++ TrackingEpoch.reference cache events := by
 induction tokens with
 | nil => simp
 | cons t ts ih => simp [TrackingEpoch.reference,TrackingEpoch.emitted,TrackingEpoch.nextCache,ih]

theorem pending_cache (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 (PublicCleanup.pending length read names s).state.cache=s.cache := by
 unfold PublicCleanup.pending
 split
 · rfl
 · exact PublicCleanup.run_cache _ _ _ _ _ _

theorem ready_logical (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 PublicFetch.logical bytes read stop names s =
 ((PublicSourceOnly.ready bytes read stop s.cursor).token.toList).map (relevant names) := by
 cases hb : bytes[s.cursor.position]? with
 | none => simp [PublicFetch.logical,PublicSourceOnly.ready,hb]
 | some b =>
   cases hs : stop b <;> simp [PublicFetch.logical,PublicSourceOnly.ready,hb,hs]

theorem next_observations (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 TrackingEpoch.reference (cacheRelevant names s) (native bytes read stop names s).events =
 (reference bytes read stop s.cursor).observations.map (relevant names) := by
 simp only [native,reference,PublicSourceOnly.pending_events,raw_reference_append,List.map_append]
 have eqcache : cacheRelevant names (PublicCleanup.pending bytes.length read names s).state =
     cacheRelevant names s := by simp only [cacheRelevant,pending_cache]
 rw [← eqcache,PublicFetch.fetch_emissions _ _ _ _ _ (PublicCleanup.pending_coherent _ _ _ _ h),
   ready_logical,PublicSourceOnly.pending_cursor]

theorem next_seen (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (hc : coherent read s)
 (ht : compatible names s.mode) (hi : TrackingEpoch.Inv (project names s)) :
 seen (native bytes read stop names s).state.mode =
 (seen s.mode || (reference bytes read stop s.cursor).observations.any (relevant names)) := by
 have h := TrackingEpoch.execution (native bytes read stop names s).events (project names s) hi
 rw [← next_project _ _ _ _ _ ht] at h
 simp only [project] at h
 rw [next_observations _ _ _ _ _ hc] at h
 simpa [List.any_map] using h

theorem next_inv (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (ht : compatible names s.mode)
 (hi : TrackingEpoch.Inv (project names s)) :
 TrackingEpoch.Inv (project names (native bytes read stop names s).state) := by
 rw [next_project _ _ _ _ _ ht]
 exact TrackingEpoch.prefix_inv _ _ hi

theorem cleanup_saved (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) :
 (PublicCleanup.run length read names fuel stack s).state.saved=s.saved := by
 induction fuel generalizing stack s with
 | zero => rfl
 | succ fuel ih =>
   simp only [PublicCleanup.run]
   split
   · rfl
   · exact ih _ _

theorem pending_saved (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
 (PublicCleanup.pending length read names s).state.saved=s.saved := by
 unfold PublicCleanup.pending
 split
 · rfl
 · exact cleanup_saved _ _ _ _ _ _

theorem ready_saved (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 (PublicFetch.fetchReady bytes read stop names s).state.saved=s.saved := by
 unfold PublicFetch.fetchReady
 split
 · rfl
 · split
   · rfl
   · split
     · rfl
     · split <;> rfl

theorem next_saved (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) :
 (native bytes read stop names s).state.saved=s.saved := by
 simp only [native,ready_saved,pending_saved]

end PublicNext
