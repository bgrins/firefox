import OrderedScopes

namespace QuoteScopes.Examples
open QuoteAppend QuoteScopes

def pair : Content := .quote .openQuote (.quote .closeQuote .empty)
def children : Content := .scope pair (.scope (.scope pair .empty) (.scope .empty .empty))
def inserted : Content := .quote .noOpen children

def stale : Render := .quote (cell explicitPairs 0 .noOpen) (staged explicitPairs 0 children)

theorem stale_append : stale ≠ staged explicitPairs 0 inserted := by
  simp only [stale, staged_eq_reference]
  decide +kernel

theorem new_delivery :
    staged explicitPairs 0 inserted =
      .quote ⟨0, ""⟩ (.scope (.quote ⟨1, "AAA"⟩ (.quote ⟨2, "AAA"⟩ .empty))
        (.scope (.scope (.quote ⟨1, "AAA"⟩ (.quote ⟨2, "AAA"⟩ .empty)) .empty)
          (.scope .empty .empty))) := by
  rw [staged_eq_reference]
  decide +kernel

def interleaved : Content :=
  .scope pair (.quote .noOpen (.scope (.scope pair .empty) (.quote .noOpen (.scope .empty .empty))))

theorem ordered_positions : scopePositions interleaved = [0, 1, 2] := by decide +kernel

theorem ordered_starts :
    (scopePositions interleaved).map (precedingLookup 0 (parentPass explicitPairs 0 interleaved)) = [0, 1, 2] := by decide +kernel

theorem end_is_not_preceding :
    scanChildStarts 0 interleaved ≠ [finish 0 (parentOps interleaved),
      finish 0 (parentOps interleaved), finish 0 (parentOps interleaved)] := by decide +kernel

example : staged explicitPairs 3 (.scope (.scope pair .empty) .empty) =
    .scope (.scope (.quote ⟨3, "AAA"⟩ (.quote ⟨4, "AAA"⟩ .empty)) .empty) .empty := by
  rw [staged_eq_reference]
  decide +kernel

example : staged explicitPairs 0 (.scope (.quote .noOpen .empty) (.scope pair .empty)) =
    .scope (.quote ⟨0, ""⟩ .empty) (.scope (.quote ⟨0, "A"⟩ (.quote ⟨1, "A"⟩ .empty)) .empty) := by
  rw [staged_eq_reference]
  decide +kernel

example : staged explicitPairs 0 (.scope .empty (.scope .empty .empty)) =
    .scope .empty (.scope .empty .empty) := by rw [staged_eq_reference]; decide +kernel

example : staged explicitPairs 0 (embed [.closeQuote, .noClose, .openQuote]) =
    renderCells [⟨0, ""⟩, ⟨0, ""⟩, ⟨0, "A"⟩] := by rw [childless_fastpath]; decide +kernel

example : precedingLookup 7 (parentPass explicitPairs 7 interleaved) 0 = 7 := by decide +kernel
example : parentOps children = [] := by decide +kernel
example : (parentPass explicitPairs 0 inserted).length = 1 := by decide +kernel

end QuoteScopes.Examples
