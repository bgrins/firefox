import Adapters
import PairLaws

namespace CssStreaming

open CssSemantics

theorem utf16_batch (input : List DomString.CodeUnit) : batch utf16 input = DomString.decode input := by
  cases input with
  | nil => rfl
  | cons first rest =>
    cases rest with
    | nil => rfl
    | cons second tail =>
      by_cases pair : DomString.Leading first ∧ DomString.Trailing second
      · simpa only [batch, utf16, DomString.decode, dite_eq_left pair] using
          congrArg (List.cons (DomString.pairPoint first second pair.1 pair.2)) (utf16_batch tail)
      · simpa only [batch, utf16, DomString.decode, dite_eq_right pair] using
          congrArg (List.cons (DomString.unitPoint first)) (utf16_batch (second :: tail))
termination_by input.length

theorem css_batch (input : List CodePointInput.CodePoint) : batch css input = CodePointInput.preprocess input := by
  cases input with
  | nil => rfl
  | cons first rest =>
    cases rest with
    | nil => rfl
    | cons second tail =>
      by_cases pair : first.val = 0x0d ∧ second.val = 0x0a
      · simpa only [batch, css, CodePointInput.preprocess, ite_eq_left pair] using
          congrArg (List.cons '\n') (css_batch tail)
      · simpa only [batch, css, CodePointInput.preprocess, ite_eq_right pair] using
          congrArg (List.cons (CodePointInput.point first)) (css_batch (second :: tail))
termination_by input.length

theorem utf16_chunks (input) : stream utf16 input = DomString.decode input.flatten := by
  rw [stream_batch, utf16_batch]

theorem css_chunks (input) : stream css input = CodePointInput.preprocess input.flatten := by
  rw [stream_batch, css_batch]

theorem utf16_decoded_iff (input output) :
    stream utf16 input = output ↔ DomString.Decoded input.flatten output := by
  rw [utf16_chunks, DomString.decode_iff]

theorem css_preprocess_iff (input output) :
    stream css input = output ↔ CodePointInput.Preprocess input.flatten output := by
  rw [css_chunks, CodePointInput.preprocess_iff]

theorem utf16_pending_high (input unit)
    (pending : (chunks utf16 none input).pending = some unit) : DomString.Leading unit := by
  rw [chunks_feed] at pending
  have holds := feed_pending_valid utf16 none input.flatten (by simp) unit pending
  simpa [utf16] using holds

theorem css_pending_cr (input point)
    (pending : (chunks css none input).pending = some point) : point.val = 0x0d := by
  rw [chunks_feed] at pending
  have holds := feed_pending_valid css none input.flatten (by simp) point pending
  simpa [css] using holds

end CssStreaming
