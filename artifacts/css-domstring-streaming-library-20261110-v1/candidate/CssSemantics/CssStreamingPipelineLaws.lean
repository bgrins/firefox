import CssSemantics.CssStreamingPipeline
import CssSemantics.CssStreamingAdapterLaws

namespace CssSemantics.Streaming

open CssSemantics

theorem pipe_chunks_factor (first : Machine Input Middle) (second : Machine Middle Output)
    (inputPending middlePending input) :
    pipeChunks first second inputPending middlePending input =
      let decoded := chunks first inputPending input
      let prepared := feed second middlePending decoded.output
      ⟨prepared.output, decoded.pending, prepared.pending⟩ := by
  induction input generalizing inputPending middlePending with
  | nil => rfl
  | cons chunk rest ih => simp [pipeChunks, chunks, ih, feed_append]

theorem pipe_finish_factor (first : Machine Input Middle) (second : Machine Middle Output)
    (middlePending) (decoded : Emission Input Middle) :
    pipeFinish first second
        ⟨(feed second middlePending decoded.output).output, decoded.pending,
          (feed second middlePending decoded.output).pending⟩ =
      finish second (feed second middlePending (finish first decoded)) := by
  simp [pipeFinish, finish, feed_append, List.append_assoc]

theorem pipeline_batch (first : Machine Input Middle) (second : Machine Middle Output) (input) :
    pipeline first second input = batch second (batch first input.flatten) := by
  rw [pipeline, pipe_chunks_factor, pipe_finish_factor, feed_finish]
  change batch second (stream first input) = _
  rw [stream_batch]

theorem domstring_preprocessing_chunks (input) :
    pipeline utf16 css input = DomString.preprocess input.flatten := by
  rw [pipeline_batch, utf16_batch, css_batch]
  rfl

theorem domstring_prepared_iff (input output) :
    pipeline utf16 css input = output ↔ DomString.Prepared input.flatten output := by
  rw [domstring_preprocessing_chunks, DomString.preprocess_iff]

theorem composed_output_normalized (input) :
    CodePointInput.Normalized (pipeline utf16 css input) := by
  rw [domstring_preprocessing_chunks]
  exact DomString.preprocess_normalized _

theorem composed_length_bound (input) :
    (pipeline utf16 css input).length ≤ input.flatten.length := by
  rw [domstring_preprocessing_chunks]
  exact DomString.preprocess_length_le _

theorem pipeline_pending_domain (input) :
    (∀ unit, (pipeChunks utf16 css none none input).inputPending = some unit → DomString.Leading unit) ∧
    (∀ point, (pipeChunks utf16 css none none input).middlePending = some point → point.val = 0x0d) := by
  rw [pipe_chunks_factor]
  constructor
  · intro unit pending
    exact utf16_pending_high input unit pending
  · intro point pending
    have held := feed_pending_valid css none (chunks utf16 none input).output (by simp) point pending
    simpa [css] using held

end CssSemantics.Streaming
