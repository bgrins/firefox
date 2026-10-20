import Span
namespace TerminalSpan

def escaped : Token := ⟨.ident, [120, 92, 32]⟩
def ws : Token := ⟨.whitespace, [32, 9, 13, 10, 12]⟩
def crlf : Token := ⟨.whitespace, [13, 10]⟩
def comment : Token := ⟨.delimSlash, [47, 42, 32, 42, 47]⟩
def block : Token := ⟨.function, [102, 40, 32, 41]⟩
def asciiWhite (b : UInt8) : Bool := b == 32 || b == 9 || b == 13 || b == 10 || b == 12
def oldTrim (bs : List UInt8) : List UInt8 := (bs.reverse.dropWhile asciiWhite).reverse

theorem escaped_bytes_preserved : stored [escaped, ws] = escaped.raw := by decide
theorem original_ascii_trim_corrupts : oldTrim (bytes [escaped, ws]) ≠ escaped.raw := by decide
theorem old_last_metadata_wrong : (scan {} [escaped, ws]).last ≠ lastMetadata [escaped, ws] := by decide
theorem crlf_is_two_raw_bytes : (scan {} [escaped, crlf]).trailing = 2 := by decide
theorem comment_resets_trim : stored [escaped, ws, comment] = bytes [escaped, ws, comment] := by decide
theorem block_resets_trim : stored [escaped, ws, block] = bytes [escaped, ws, block] := by decide
theorem standalone_empty_overlap : storedAfterLeading [ws] ws.raw.length = [] := by decide
theorem noncoalesced_counterexample :
    stored [escaped, crlf, ws] ≠ bytes (retained [escaped, crlf, ws]) := by decide
theorem repaired_block_not_trimmed :
    finishStored [⟨.function, [102,40,32]⟩] 0 [41] = [102,40,32,41] := by decide
theorem backslash_newline_still_trimmed :
    stored [⟨.other, [92]⟩, ⟨.whitespace, [10]⟩] = [92] := by decide
end TerminalSpan
