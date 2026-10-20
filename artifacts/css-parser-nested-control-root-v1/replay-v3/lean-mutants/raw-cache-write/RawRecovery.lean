import WrapperControl
set_option autoImplicit false
namespace RawRecovery
open PublicCache

def clearReference (r : PublicHistory.Reference) : PublicHistory.Reference :=
  {r with cursor := {r.cursor with pending := none}}

def pendingReference (length : Nat) (read : Nat → Lexeme)
    (r : PublicHistory.Reference) : PublicHistory.Reference :=
  let consumed := PublicSourceOnly.pending length read r.cursor
  {r with cursor := consumed.cursor, observations := r.observations ++ consumed.tokens}

theorem cleanup_seen (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (fuel : Nat) (stack : List Block) (s : State) (ht : compatible names s.mode) :
    seen (PublicCleanup.run length read names fuel stack s).state.mode =
      (seen s.mode || (PublicSourceOnly.cleanup length read fuel stack s.cursor).tokens.any (relevant names)) := by
  induction fuel generalizing stack s with
  | zero => simp [PublicCleanup.run, PublicSourceOnly.cleanup]
  | succ fuel ih =>
    by_cases hd : stack = [] ∨ length ≤ s.cursor.position
    · simp [PublicCleanup.run, PublicSourceOnly.cleanup, PublicCleanup.done, hd]
    · simp only [PublicCleanup.run, PublicSourceOnly.cleanup, PublicCleanup.done, hd, ↓reduceIte]
      rw [ih _ _ (track_compatible names _ _ ht)]
      simp [PublicCleanup.clear, fresh, track_seen names _ _ ht, Bool.or_assoc]

theorem pending_seen (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (s : State) (ht : compatible names s.mode) :
    seen (PublicCleanup.pending length read names s).state.mode =
      (seen s.mode || (PublicSourceOnly.pending length read s.cursor).tokens.any (relevant names)) := by
  cases hp : s.cursor.pending with
  | none => simp [PublicCleanup.pending, PublicSourceOnly.pending, hp]
  | some block =>
    simpa [PublicCleanup.pending, PublicSourceOnly.pending, PublicCleanup.clear, hp] using
      cleanup_seen length read names (length-s.cursor.position) [block] (PublicCleanup.clear s) ht

theorem pending_aligned (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (s : State) (r : PublicHistory.Reference) (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (PublicCleanup.pending length read names s).state
      (pendingReference length read r) := by
  refine ⟨?_, ?_, PublicCleanup.pending_coherent _ _ _ _ h.cache_coherent,
    PublicCleanup.pending_compatible _ _ _ _ h.mode_compatible, ?_, ?_⟩
  · simpa [pendingReference, h.cursor_eq] using PublicSourceOnly.pending_cursor length read names s
  · simpa [pendingReference, h.saved_eq] using PublicNext.pending_saved length read names s
  · rw [PublicCleanup.pending_project _ _ _ _ h.mode_compatible]
    exact TrackingEpoch.prefix_inv _ _ h.cache_seen
  · simpa [pendingReference, h.cursor_eq, h.seen_eq, List.any_append] using
      pending_seen length read names s h.mode_compatible

def step (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) : State :=
  (PublicCleanup.pending length read names (fresh read true s)).state

def referenceStep (length : Nat) (read : Nat → Lexeme) (r : PublicHistory.Reference) : PublicHistory.Reference :=
  let value := read r.cursor.position
  pendingReference length read {r with cursor := value.cursor, observations := r.observations ++ [value.token]}

theorem fresh_aligned (read : Nat → Lexeme) (names : List (List Byte))
    (s : State) (r : PublicHistory.Reference) (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (fresh read false s)
      {r with cursor := (read r.cursor.position).cursor, observations := r.observations ++ [(read r.cursor.position).token]} := by
  refine ⟨by simp [fresh, h.cursor_eq], h.saved_eq, fresh_coherent _ _ _ h.cache_coherent,
    track_compatible _ _ _ h.mode_compatible, ?_, ?_⟩
  · rw [fresh_project read names false s h.mode_compatible]
    exact TrackingEpoch.step_inv _ _ h.cache_seen
  · simp [fresh, track_seen names _ _ h.mode_compatible, h.cursor_eq, h.seen_eq]

theorem step_aligned (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (s : State) (r : PublicHistory.Reference) (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (step length read names s) (referenceStep length read r) :=
  pending_aligned _ _ _ _ _ (fresh_aligned _ _ _ _ h)

def stopped (bytes : List Byte) (stops : List Byte) (cursor : Cursor) : Bool :=
  match bytes[cursor.position]? with
  | none => true
  | some byte => stops.contains byte

def run (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (stops : List Byte) :
    Nat → State → State
  | 0, s => s
  | fuel+1, s => if stopped bytes stops s.cursor then s
    else run bytes read names stops fuel (step bytes.length read names s)

def referenceRun (bytes : List Byte) (read : Nat → Lexeme) (stops : List Byte) :
    Nat → PublicHistory.Reference → PublicHistory.Reference
  | 0, r => r
  | fuel+1, r => if stopped bytes stops r.cursor then r
    else referenceRun bytes read stops fuel (referenceStep bytes.length read r)

theorem run_aligned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (fuel : Nat) (s : State) (r : PublicHistory.Reference)
    (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (run bytes read names stops fuel s)
      (referenceRun bytes read stops fuel r) := by
  induction fuel generalizing s r with
  | zero => exact h
  | succ fuel ih =>
    simp only [run, referenceRun, h.cursor_eq]
    split
    · exact h
    · exact ih _ _ (step_aligned _ _ _ _ _ h)

def recover (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (s : State) : State :=
  let skipped := (PublicCleanup.pending bytes.length read names s).state
  run bytes read names stops (bytes.length-skipped.cursor.position) skipped

def referenceRecover (bytes : List Byte) (read : Nat → Lexeme) (stops : List Byte)
    (r : PublicHistory.Reference) : PublicHistory.Reference :=
  let skipped := pendingReference bytes.length read r
  referenceRun bytes read stops (bytes.length-skipped.cursor.position) skipped

theorem recover_aligned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (s : State) (r : PublicHistory.Reference)
    (h : PublicHistory.Aligned read names s r) :
    PublicHistory.Aligned read names (recover bytes read names stops s)
      (referenceRecover bytes read stops r) := by
  have next := pending_aligned bytes.length read names s r h
  simpa [recover, referenceRecover, next.cursor_eq] using
    run_aligned bytes read names stops _ _ _ next

theorem step_cache (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
    (step length read names s).cache = s.cache := by
  simp [step, PublicNext.pending_cache, fresh]

theorem run_cache (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (fuel : Nat) (s : State) :
    (run bytes read names stops fuel s).cache = s.cache := by
  induction fuel generalizing s with
  | zero => rfl
  | succ fuel ih =>
    simp only [run]
    split
    · rfl
    · rw [ih, step_cache]

theorem recover_cache (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (s : State) : (recover bytes read names stops s).cache = s.cache := by
  simp [recover, run_cache, PublicNext.pending_cache]

theorem cleanup_advances (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (fuel : Nat) (stack : List Block) (s : State) (hp : PublicCleanup.Progress length read) :
    s.cursor.position ≤ (PublicCleanup.run length read names fuel stack s).state.cursor.position := by
  induction fuel generalizing stack s with
  | zero => exact Nat.le_refl _
  | succ fuel ih =>
    simp only [PublicCleanup.run]
    split
    · exact Nat.le_refl _
    · rename_i hd
      have pos : s.cursor.position < length := by simp [PublicCleanup.done] at hd; omega
      have advance := hp s.cursor.position pos
      have tail := ih (PublicCleanup.stackAfter stack (read s.cursor.position))
        (PublicCleanup.clear (fresh read false (PublicCleanup.clear s)))
      simp only [PublicCleanup.clear, fresh] at tail ⊢
      omega

theorem pending_advances (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (s : State) (hp : PublicCleanup.Progress length read) :
    s.cursor.position ≤ (PublicCleanup.pending length read names s).state.cursor.position := by
  unfold PublicCleanup.pending
  split
  · exact Nat.le_refl _
  · rename_i block hblock
    simpa [PublicCleanup.clear] using cleanup_advances length read names (length-s.cursor.position) [block] (PublicCleanup.clear s) hp

theorem step_progress (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (s : State) (hp : PublicCleanup.Progress length read) (pos : s.cursor.position < length) :
    s.cursor.position < (step length read names s).cursor.position := by
  have first := hp s.cursor.position pos
  have rest := pending_advances length read names (fresh read false s) hp
  simp only [step, fresh] at *
  omega

theorem run_complete (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (fuel : Nat) (s : State)
    (hp : PublicCleanup.Progress bytes.length read) (hf : bytes.length ≤ s.cursor.position + fuel) :
    stopped bytes stops (run bytes read names stops fuel s).cursor = true := by
  induction fuel generalizing s with
  | zero =>
    have hpos : bytes.length ≤ s.cursor.position := by omega
    simp [run, stopped, List.getElem?_eq_none hpos]
  | succ fuel ih =>
    simp only [run]
    split
    · assumption
    · rename_i hn
      have pos : s.cursor.position < bytes.length := by
        by_cases hpos : s.cursor.position < bytes.length
        · exact hpos
        · have bound : bytes.length ≤ s.cursor.position := by omega
          simp [stopped, List.getElem?_eq_none bound] at hn
      have advance := step_progress bytes.length read names s hp pos
      exact ih _ (by omega)

theorem recover_complete (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (s : State) (hp : PublicCleanup.Progress bytes.length read) :
    stopped bytes stops (recover bytes read names stops s).cursor = true := by
  apply run_complete bytes read names stops _ _ hp
  omega

def stepWrites (length : Nat) (read : Nat → Lexeme) (cursor : Cursor) : List Token :=
  let value := read cursor.position
  value.token :: (PublicSourceOnly.pending length read value.cursor).tokens

def writes (bytes : List Byte) (read : Nat → Lexeme) (stops : List Byte) :
    Nat → Cursor → List Token
  | 0, _ => []
  | fuel+1, cursor => if stopped bytes stops cursor then [] else
      stepWrites bytes.length read cursor ++ writes bytes read stops fuel
        (PublicSourceOnly.pending bytes.length read (read cursor.position).cursor).cursor

theorem step_writes (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
    (step length read names s).urls = PublicAnnotations.applyTokens (stepWrites length read s.cursor) s.urls := by
  simp [step, PublicAnnotations.pending_writes, stepWrites, PublicAnnotations.applyTokens, fresh]

theorem step_cursor (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
    (step length read names s).cursor =
      (PublicSourceOnly.pending length read (read s.cursor.position).cursor).cursor := by
  simp [step, PublicSourceOnly.pending_cursor, fresh]

theorem run_writes (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (fuel : Nat) (s : State) :
    (run bytes read names stops fuel s).urls =
      PublicAnnotations.applyTokens (writes bytes read stops fuel s.cursor) s.urls := by
  induction fuel generalizing s with
  | zero => rfl
  | succ fuel ih =>
    simp only [run, writes]
    split
    · rfl
    · rw [ih, step_cursor, step_writes]
      simp [PublicAnnotations.applyTokens, List.foldl_append]

end RawRecovery
