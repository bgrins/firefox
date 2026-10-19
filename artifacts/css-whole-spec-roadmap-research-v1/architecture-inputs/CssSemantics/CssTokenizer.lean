import CssSemantics.CssTokenCore

namespace CssSemantics.CssTokenizer

open CssToken

def combine (comments : CssComments.Result) (token : CssToken.Result) : CssToken.Result :=
  ⟨token.token, token.rest, comments.parseError || token.parseError⟩

def consumeToken (rangesAllowed : Bool) (source : List Char) : CssToken.Result :=
  let comments := CssComments.consume source
  combine comments (consumeCore rangesAllowed comments.rest)

def Consumed (rangesAllowed : Bool) (source : List Char) (result : CssToken.Result) : Prop :=
  ∃ comments token, CssComments.Consumed source comments ∧ Core rangesAllowed comments.rest token ∧
    result = combine comments token

theorem consumeToken_sound (mode : Bool) (source : List Char) :
    Consumed mode source (consumeToken mode source) :=
  ⟨_, _, CssComments.consume_sound source, consumeCore_sound mode _, rfl⟩

theorem Consumed.result {mode source result} (parsed : Consumed mode source result) :
    consumeToken mode source = result := by
  obtain ⟨comments, token, consumed, core, equal⟩ := parsed
  simp [consumeToken, consumed.result, core.result, equal]

theorem consumeToken_iff (mode : Bool) (source : List Char) (result : CssToken.Result) :
    consumeToken mode source = result ↔ Consumed mode source result :=
  ⟨fun equal => equal ▸ consumeToken_sound mode source, Consumed.result⟩

theorem Consumed.unique {mode source left right} (hl : Consumed mode source left)
    (hr : Consumed mode source right) : left = right := hl.result.symm.trans hr.result

theorem Consumed.progress {mode source result} (parsed : Consumed mode source result)
    (nonEOF : result.token ≠ .eof) : result.rest.length < source.length := by
  obtain ⟨comments, token, consumed, core, rfl⟩ := parsed
  exact Nat.lt_of_lt_of_le (core.progress nonEOF) consumed.length_le

theorem consumeToken_progress (mode : Bool) (source : List Char)
    (nonEOF : (consumeToken mode source).token ≠ .eof) :
    (consumeToken mode source).rest.length < source.length :=
  (consumeToken_sound mode source).progress nonEOF

theorem Consumed.eof_rest {mode source result} (parsed : Consumed mode source result)
    (eof : result.token = .eof) : result.rest = [] := by
  obtain ⟨comments, token, consumed, core, rfl⟩ := parsed
  exact core.eof_rest eof

theorem Consumed.length_le {mode source result} (parsed : Consumed mode source result) :
    result.rest.length ≤ source.length := by
  by_cases eof : result.token = .eof
  · simp [parsed.eof_rest eof]
  · exact Nat.le_of_lt (parsed.progress eof)

def consumeInput (rangesAllowed : Bool) (source : List Char) : CssToken.Result :=
  consumeToken rangesAllowed (CssInput.preprocess source)

def InputConsumed (rangesAllowed : Bool) (source : List Char) (result : CssToken.Result) : Prop :=
  ∃ normalized, CssInput.Preprocess source normalized ∧ Consumed rangesAllowed normalized result

theorem consumeInput_iff (mode : Bool) (source : List Char) (result : CssToken.Result) :
    consumeInput mode source = result ↔ InputConsumed mode source result := by
  rw [consumeInput, consumeToken_iff]
  constructor
  · intro parsed; exact ⟨_, CssInput.preprocess_sound source, parsed⟩
  · rintro ⟨normalized, processed, parsed⟩; simpa [processed.result] using parsed

theorem InputConsumed.progress {mode source result} (parsed : InputConsumed mode source result)
    (nonEOF : result.token ≠ .eof) : result.rest.length < source.length := by
  obtain ⟨normalized, processed, parsed⟩ := parsed
  exact Nat.lt_of_lt_of_le (parsed.progress nonEOF) processed.length_le

theorem InputConsumed.eof_rest {mode source result} (parsed : InputConsumed mode source result)
    (eof : result.token = .eof) : result.rest = [] := by
  obtain ⟨normalized, processed, parsed⟩ := parsed
  exact parsed.eof_rest eof

end CssSemantics.CssTokenizer
