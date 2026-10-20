import NestedControl
import RawSafety
set_option autoImplicit false
namespace UntilAfter
open PublicCache

def requested (byte : Byte) : Prop :=
  byte = 123 ∨ byte = 59 ∨ byte = 33 ∨ byte = 44

def delimiterToken (byte : Byte) : Token :=
  if byte = 123 then .open .curly else .other

def delimiterLexeme (byte : Byte) (position : Nat) : Lexeme :=
  ⟨delimiterToken byte, ⟨position + 1, if byte = 123 then some .curly else none⟩⟩

def DelimiterLaw (bytes : List Byte) (read : Nat → Lexeme) : Prop :=
  ∀ position byte, bytes[position]? = some byte → requested byte →
    read position = delimiterLexeme byte position

def advance (s : State) : State :=
  {s with cursor := {s.cursor with position := s.cursor.position + 1}}

def readReference (read : Nat → Lexeme) (r : PublicHistory.Reference) : PublicHistory.Reference :=
  let value := read r.cursor.position
  {r with cursor := {value.cursor with pending := none}, observations := r.observations ++ [value.token]}

def takeNative (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (byte : Byte) (s : State) : State :=
  let next := advance s
  if byte = 123 then NestedControl.consume length read names .curly next else next

def takeReference (length : Nat) (read : Nat → Lexeme)
    (r : PublicHistory.Reference) : PublicHistory.Reference :=
  let next := readReference read r
  match (read r.cursor.position).token with
  | .open .curly => NestedControl.referenceConsume length read .curly next
  | _ => next

theorem delimiter_irrelevant (names : List (List Byte)) (byte : Byte) :
    relevant names (delimiterToken byte) = false := by
  by_cases h : byte = 123 <;> simp [delimiterToken, h, relevant]

theorem advance_aligned (read : Nat → Lexeme) (names : List (List Byte))
    (byte : Byte) (s : State) (r : PublicHistory.Reference)
    (h : PublicHistory.Aligned read names s r) (pending : s.cursor.pending = none)
    (provider : read r.cursor.position = delimiterLexeme byte r.cursor.position) :
    PublicHistory.Aligned read names (advance s) (readReference read r) := by
  refine ⟨?_, h.saved_eq, h.cache_coherent, h.mode_compatible, h.cache_seen, ?_⟩
  · have providerNative : read s.cursor.position = delimiterLexeme byte s.cursor.position := by
      simpa [h.cursor_eq] using provider
    simp [advance, readReference, ← h.cursor_eq, providerNative, delimiterLexeme, pending]
  · simp [advance, readReference, provider, delimiterLexeme, List.any_append,
      delimiter_irrelevant, h.seen_eq]

theorem take_aligned (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (byte : Byte) (s : State) (r : PublicHistory.Reference)
    (h : PublicHistory.Aligned read names s r) (pending : s.cursor.pending = none)
    (provider : read r.cursor.position = delimiterLexeme byte r.cursor.position) :
    PublicHistory.Aligned read names (takeNative length read names byte s)
      (takeReference length read r) := by
  have advanced := advance_aligned read names byte s r h pending provider
  by_cases curly : byte = 123
  · simpa [takeNative, takeReference, provider, delimiterLexeme, delimiterToken, curly] using
      NestedControl.consume_aligned length read names .curly _ _ advanced
  · simpa [takeNative, takeReference, provider, delimiterLexeme, delimiterToken, curly] using advanced

theorem take_preserves_cache (length : Nat) (read : Nat → Lexeme)
    (names : List (List Byte)) (byte : Byte) (s : State) :
    (takeNative length read names byte s).cache = s.cache := by
  by_cases h : byte = 123 <;>
    simp [takeNative, h, NestedControl.consume, PublicCleanup.run_cache, advance]

theorem take_preserves_coherent_cache (length : Nat) (read : Nat → Lexeme)
    (names : List (List Byte)) (byte : Byte) (s : State) (h : coherent read s) :
    coherent read (takeNative length read names byte s) := by
  intro cache hc
  exact h cache (by simpa [take_preserves_cache] using hc)

theorem take_pending_none (length : Nat) (read : Nat → Lexeme)
    (names : List (List Byte)) (byte : Byte) (s : State) (h : s.cursor.pending = none) :
    (takeNative length read names byte s).cursor.pending = none := by
  by_cases curly : byte = 123
  · simpa [takeNative, curly, NestedControl.consume, advance] using
      RawSafety.cleanup_pending_none length read names (length-(s.cursor.position+1)) [.curly] (advance s) h
  · simpa [takeNative, curly, advance] using h

def curlyTokens (length : Nat) (read : Nat → Lexeme) (cursor : Cursor) : List Token :=
  (PublicSourceOnly.cleanup length read (length-(cursor.position+1)) [.curly]
    {cursor with position := cursor.position+1}).tokens

theorem take_annotation_writes (length : Nat) (read : Nat → Lexeme)
    (names : List (List Byte)) (byte : Byte) (s : State) :
    (takeNative length read names byte s).urls =
      if byte = 123 then PublicAnnotations.applyTokens (curlyTokens length read s.cursor) s.urls
      else s.urls := by
  by_cases curly : byte = 123
  · simpa [takeNative, curly, NestedControl.consume, curlyTokens, advance] using
      PublicAnnotations.cleanup_writes length read names (length-(s.cursor.position+1)) [.curly] (advance s)
  · simp [takeNative, curly, advance]

theorem take_observations (length : Nat) (read : Nat → Lexeme)
    (names : List (List Byte)) (byte : Byte) (s : State) (h : compatible names s.mode) :
    seen (takeNative length read names byte s).mode =
      (seen s.mode || (if byte = 123 then (curlyTokens length read s.cursor).any (relevant names) else false)) := by
  by_cases curly : byte = 123
  · simpa [takeNative, curly, NestedControl.consume, curlyTokens, advance] using
      RawRecovery.cleanup_seen length read names (length-(s.cursor.position+1)) [.curly] (advance s) h
  · simp [takeNative, curly, advance]

theorem requested_ascii (byte : Byte) (h : requested byte) : byte.val < 128 := by
  rcases h with rfl | rfl | rfl | rfl <;> decide

theorem advance_within_source (bytes : List Byte) (position : Nat) (byte : Byte)
    (h : bytes[position]? = some byte) : position + 1 ≤ bytes.length := by
  by_cases bound : position + 1 ≤ bytes.length
  · exact bound
  · have past : bytes.length ≤ position := by omega
    simp [List.getElem?_eq_none past] at h

def finishNative (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (outer : List Byte) (s : State) : State :=
  match bytes[s.cursor.position]? with
  | none => s
  | some byte => if outer.contains byte then s else takeNative bytes.length read names byte s

def finishReference (bytes : List Byte) (read : Nat → Lexeme)
    (outer extra : List Byte) (r : PublicHistory.Reference) : PublicHistory.Reference :=
  match bytes[r.cursor.position]? with
  | none => r
  | some byte =>
    if outer.contains byte then r
    else if extra.contains byte then takeReference bytes.length read r else r

theorem finish_aligned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (outer extra : List Byte) (s : State) (r : PublicHistory.Reference)
    (h : PublicHistory.Aligned read names s r)
    (pending : s.cursor.pending = none)
    (boundary : RawRecovery.stopped bytes (outer ++ extra) s.cursor = true)
    (mask : ∀ byte, extra.contains byte = true → requested byte)
    (law : DelimiterLaw bytes read) :
    PublicHistory.Aligned read names (finishNative bytes read names outer s)
      (finishReference bytes read outer extra r) := by
  cases hb : bytes[s.cursor.position]? with
  | none => simpa [finishNative, finishReference, ← h.cursor_eq, hb] using h
  | some byte =>
    by_cases owned : outer.contains byte = true
    · have ownedMem : byte ∈ outer := by simpa using owned
      simpa [finishNative, finishReference, ← h.cursor_eq, hb, ownedMem] using h
    · have notOwned : byte ∉ outer := by simpa using owned
      have requestedHere : extra.contains byte = true := by
        simpa [RawRecovery.stopped, hb, List.contains_append, notOwned] using boundary
      have requestedMem : byte ∈ extra := by simpa using requestedHere
      have provider : read r.cursor.position = delimiterLexeme byte r.cursor.position := by
        simpa [h.cursor_eq] using law s.cursor.position byte hb (mask byte requestedHere)
      simpa [finishNative, finishReference, ← h.cursor_eq, hb, notOwned, requestedMem] using
        take_aligned bytes.length read names byte s r h pending provider

theorem finish_preserves_cache (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (outer : List Byte) (s : State) :
    (finishNative bytes read names outer s).cache = s.cache := by
  unfold finishNative
  split
  · rfl
  · split
    · rfl
    · exact take_preserves_cache _ _ _ _ _

theorem outer_owned_unread (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (outer : List Byte) (s : State) (byte : Byte)
    (atByte : bytes[s.cursor.position]? = some byte) (owned : outer.contains byte = true) :
    finishNative bytes read names outer s = s := by
  have ownedMem : byte ∈ outer := by simpa using owned
  simp [finishNative, atByte, ownedMem]

theorem finish_pending_none (bytes : List Byte) (read : Nat → Lexeme)
    (names : List (List Byte)) (outer : List Byte) (s : State) (pending : s.cursor.pending = none) :
    (finishNative bytes read names outer s).cursor.pending = none := by
  unfold finishNative
  split
  · exact pending
  · split
    · exact pending
    · exact take_pending_none _ _ _ _ _ pending

def native (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : NestedControl.State) : Bool × NestedControl.State :=
  let parsed := NestedControl.untilBefore bytes read names extra stopOnError body s
  if stopOnError && !parsed.1 then parsed
  else (parsed.1, {parsed.2 with core := finishNative bytes read names parsed.2.stops parsed.2.core})

def reference (bytes : List Byte) (read : Nat → Lexeme)
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : NestedControl.Reference) : Bool × NestedControl.Reference :=
  let parsed := NestedControl.referenceUntilBefore bytes read extra stopOnError body s
  if stopOnError && !parsed.1 then parsed
  else (parsed.1, {parsed.2 with core := finishReference bytes read parsed.2.stops extra parsed.2.core})

theorem until_ready (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : NestedControl.State) (progress : PublicCleanup.Progress bytes.length read)
    (completed : (stopOnError && !(NestedControl.untilBefore bytes read names extra stopOnError body s).1) = false) :
    let result := (NestedControl.untilBefore bytes read names extra stopOnError body s).2
    RawRecovery.stopped bytes (result.stops ++ extra) result.core.cursor = true ∧
      result.core.cursor.pending = none := by
  simp only [NestedControl.untilBefore] at completed ⊢
  split
  · rename_i early
    simp [early] at completed
  · exact ⟨RawRecovery.recover_complete _ _ _ _ _ progress,
      RawSafety.recover_pending_none _ _ _ _ _⟩

theorem after_refines (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : NestedControl.State) (r : NestedControl.Reference)
    (h : NestedControl.Aligned read names s r)
    (progress : PublicCleanup.Progress bytes.length read)
    (mask : ∀ byte, extra.contains byte = true → requested byte)
    (law : DelimiterLaw bytes read) :
    (native bytes read names extra stopOnError body s).1 =
      (reference bytes read extra stopOnError body r).1 ∧
    NestedControl.Aligned read names (native bytes read names extra stopOnError body s).2
      (reference bytes read extra stopOnError body r).2 := by
  have beforeProof := NestedControl.until_before_refines bytes read names extra stopOnError body s r h
  simp only [native, reference, beforeProof.1]
  split
  · exact ⟨beforeProof.1, beforeProof.2⟩
  · rename_i notEarly
    have completed : (stopOnError && !(NestedControl.untilBefore bytes read names extra stopOnError body s).1) = false := by
      simpa [beforeProof.1] using notEarly
    have ready := until_ready bytes read names extra stopOnError body s progress completed
    refine ⟨rfl, ?_, beforeProof.2.stops, beforeProof.2.depth, beforeProof.2.limit⟩
    simpa [beforeProof.2.stops] using
      finish_aligned bytes read names
        (NestedControl.untilBefore bytes read names extra stopOnError body s).2.stops extra _ _
        beforeProof.2.core ready.2 ready.1 mask law

theorem after_result (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : NestedControl.State) :
    (native bytes read names extra stopOnError body s).1 =
      (NestedControl.untilBefore bytes read names extra stopOnError body s).1 := by
  simp only [native]
  split <;> rfl

theorem stop_error_exact (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (body : List Byte → WrapperControl.Program) (s : NestedControl.State)
    (failed : (NestedControl.untilBefore bytes read names extra true body s).1 = false) :
    native bytes read names extra true body s = NestedControl.untilBefore bytes read names extra true body s := by
  simp [native, failed]

theorem after_controls (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : NestedControl.State) :
    let result := (native bytes read names extra stopOnError body s).2
    result.stops = s.stops ∧ result.depth = s.depth ∧ result.limit = s.limit := by
  simp only [native]
  split <;> simp [NestedControl.untilBefore] <;> split <;> exact ⟨rfl, rfl, rfl⟩

theorem after_pending_none (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : NestedControl.State) (progress : PublicCleanup.Progress bytes.length read)
    (completed : (stopOnError && !(NestedControl.untilBefore bytes read names extra stopOnError body s).1) = false) :
    (native bytes read names extra stopOnError body s).2.core.cursor.pending = none := by
  have ready := until_ready bytes read names extra stopOnError body s progress completed
  simpa [native, completed] using finish_pending_none bytes read names
    (NestedControl.untilBefore bytes read names extra stopOnError body s).2.stops _ ready.2

def continuationWrites (bytes : List Byte) (read : Nat → Lexeme)
    (outer : List Byte) (cursor : Cursor) : List Token :=
  match bytes[cursor.position]? with
  | none => []
  | some byte => if outer.contains byte then []
    else if byte = 123 then curlyTokens bytes.length read cursor else []

theorem finish_writes (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (outer : List Byte) (s : State) :
    (finishNative bytes read names outer s).urls =
      PublicAnnotations.applyTokens (continuationWrites bytes read outer s.cursor) s.urls := by
  unfold finishNative continuationWrites
  split
  · rfl
  · split
    · rfl
    · rw [take_annotation_writes]
      split <;> rfl

theorem curly_completes (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
    (s : State) (progress : PublicCleanup.Progress length read) :
    (PublicCleanup.run length read names (length-(advance s).cursor.position) [.curly] (advance s)).complete = true := by
  apply PublicCleanup.complete_with_byte_fuel _ _ _ _ _ _ progress
  omega

end UntilAfter
