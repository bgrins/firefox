import RawRecovery
set_option autoImplicit false
namespace RawSafety
open PublicCache

theorem cleanup_pending_none (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (fuel : Nat) (stack : List Block) (s : State) (h : s.cursor.pending = none) :
    (PublicCleanup.run length read names fuel stack s).state.cursor.pending = none := by
  induction fuel generalizing stack s with
  | zero => exact h
  | succ fuel ih =>
    simp only [PublicCleanup.run]
    split
    · exact h
    · exact ih _ _ rfl

theorem pending_none (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
    (PublicCleanup.pending length read names s).state.cursor.pending = none := by
  cases h : s.cursor.pending with
  | none => simp [PublicCleanup.pending,h]
  | some block =>
    simpa [PublicCleanup.pending,h] using
      cleanup_pending_none length read names (length-s.cursor.position) [block] (PublicCleanup.clear s) rfl

theorem step_pending_none (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) :
    (RawRecovery.step length read names s).cursor.pending = none :=
  pending_none length read names (fresh read false s)

theorem run_pending_none (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (fuel : Nat) (s : State) (h : s.cursor.pending = none) :
    (RawRecovery.run bytes read names stops fuel s).cursor.pending = none := by
  induction fuel generalizing s with
  | zero => exact h
  | succ fuel ih =>
    simp only [RawRecovery.run]
    split
    · exact h
    · exact ih _ (step_pending_none _ _ _ _)

theorem recover_pending_none (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (s : State) :
    (RawRecovery.recover bytes read names stops s).cursor.pending = none :=
  run_pending_none _ _ _ _ _ _ (pending_none _ _ _ _)

def recoveryWrites (bytes : List Byte) (read : Nat → Lexeme) (stops : List Byte)
    (cursor : Cursor) : List Token :=
  let skipped := PublicSourceOnly.pending bytes.length read cursor
  skipped.tokens ++ RawRecovery.writes bytes read stops (bytes.length-skipped.cursor.position) skipped.cursor

theorem recovery_writes (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (stops : List Byte) (s : State) :
    (RawRecovery.recover bytes read names stops s).urls =
      PublicAnnotations.applyTokens (recoveryWrites bytes read stops s.cursor) s.urls := by
  simp [RawRecovery.recover,RawRecovery.run_writes,PublicAnnotations.pending_writes,
    PublicSourceOnly.pending_cursor,recoveryWrites,PublicAnnotations.applyTokens,List.foldl_append]

end RawSafety
