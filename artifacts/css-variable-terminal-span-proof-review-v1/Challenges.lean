import Span
open TerminalSpan

def escapedSP : Token := ⟨.ident, [120,92,32]⟩
def escapedHT : Token := ⟨.ident, [120,92,9]⟩
def hexTerminator : Token := ⟨.ident, [120,92,50,48,32]⟩
def outerCRLF : Token := ⟨.whitespace, [13,10]⟩
def outerSP : Token := ⟨.whitespace, [32]⟩
def commentAfter : Token := ⟨.delimSlash, [47,42,32,42,47]⟩
def ordinaryBlock : Token := ⟨.function, [102,40,32,9,41]⟩

theorem escaped_SP_without_terminal_token : stored [escapedSP] = [120,92,32] := by decide
theorem escaped_HT_before_CRLF : stored [escapedHT,outerCRLF] = [120,92,9] := by decide
theorem hex_terminator_preserved : stored [hexTerminator,outerSP] = [120,92,50,48,32] := by decide
theorem double_escaped_SP : stored [⟨.ident,[120,92,32,92,32]⟩,outerCRLF] = [120,92,32,92,32] := by decide
theorem CRLF_uses_raw_extent : (scan {} [escapedSP,outerCRLF]).trailing = 2 := by decide
theorem comment_preserves_preceding_whitespace : stored [escapedSP,outerCRLF,commentAfter] = [120,92,32,13,10,47,42,32,42,47] := by decide
theorem block_ignores_inner_whitespace : stored [ordinaryBlock] = [102,40,32,9,41] := by decide
theorem block_outer_trim_only : stored [ordinaryBlock,outerCRLF] = [102,40,32,9,41] := by decide
theorem block_class_remains_opener : lastMetadata [ordinaryBlock,outerSP] = some .function := by decide
theorem empty_after_old_leading_trim : storedAfterLeading [outerCRLF] 2 = [] := by decide
theorem excess_old_leading_trim_saturates : storedAfterLeading [outerCRLF] 3 = [] := by decide
theorem partial_leading_prefix : storedAfterLeading [⟨.ident,[120,121]⟩,outerCRLF] 1 = [121] := by decide
theorem zero_payload_invalidates_metadata_claim : lastMetadata [escapedSP,⟨.whitespace,[]⟩] ≠ some .ident := by decide
theorem uncoalesced_extent_differs : stored [escapedSP,outerSP,outerCRLF] ≠ escapedSP.raw := by decide
theorem unskipped_initial_class_differs : (scan {} [outerSP,escapedSP]).first = some .whitespace := by decide
theorem EOF_open_block : finishStored [⟨.function,[102,40,32]⟩] 0 [41] = [102,40,32,41] := by decide
theorem EOF_comment : finishStored [⟨.delimSlash,[47,42,32]⟩] 0 [42,47] = [47,42,32,42,47] := by decide
theorem EOF_drop_backslash_quote : finishStored [⟨.other,[34,120,92]⟩] 1 [34] = [34,120,34] := by decide
theorem invalid_EOF_provider_corrupts_closer : finishStored [⟨.ident,[120]⟩,outerSP] 0 [41] = [120,32] := by decide
theorem UTF8_prefix_bytes_retained : stored [⟨.ident,[195,169,228,184,173,240,144,144,128]⟩,outerCRLF] = [195,169,228,184,173,240,144,144,128] := by decide
theorem fallback_summary_not_trimmed_locally : (scan {} [escapedSP,outerSP]).last = some .whitespace := by decide
theorem residual_backslash_newline : stored [⟨.other,[92]⟩,⟨.whitespace,[10]⟩] = [92] := by decide

theorem current_constructor_metadata_guard (ts : List Token) (co : coalesced ts.reverse) :
    (bytes ts).length - (scan {} ts).trailing ≠ (bytes ts).length ↔
      0 < (scan {} ts).trailing := by
  have bound := trim_bound ts co
  omega
