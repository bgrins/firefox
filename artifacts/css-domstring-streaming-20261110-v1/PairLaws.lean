import PairStream

namespace CssStreaming

theorem batch_single (machine : Machine Input Output) (first : Input) (rest)
    (unpaired : ∀ second, machine.combine first second = none) :
    batch machine (first :: rest) = machine.single first :: batch machine rest := by
  cases rest <;> simp [batch, unpaired]

theorem batch_buffered (machine : Machine Input Output) (pending) :
    batch machine (buffered pending) = flush machine pending := by
  cases pending <;> rfl

theorem accept_continuation (machine : Machine Input Output) (pending input suffix) :
    batch machine (buffered pending ++ input :: suffix) =
      (accept machine pending input).output ++
        batch machine (buffered (accept machine pending input).pending ++ suffix) := by
  cases pending with
  | none =>
    by_cases hold : machine.holds input = true
    · simp [accept, hold, buffered]
    · have no : machine.holds input = false := by cases h : machine.holds input <;> simp_all
      simp [accept, no, buffered, batch_single machine input suffix (machine.unheld input no)]
  | some previous =>
    cases pair : machine.combine previous input with
    | some combined => simp [accept, pair, buffered, batch]
    | none =>
      by_cases hold : machine.holds input = true
      · simp [accept, pair, hold, buffered, batch]
      · have no : machine.holds input = false := by cases h : machine.holds input <;> simp_all
        simp [accept, pair, no, buffered, batch,
          batch_single machine input suffix (machine.unheld input no)]

theorem feed_continuation (machine : Machine Input Output) (pending input suffix) :
    batch machine (buffered pending ++ (input ++ suffix)) =
      (feed machine pending input).output ++
        batch machine (buffered (feed machine pending input).pending ++ suffix) := by
  induction input generalizing pending with
  | nil => simp [feed]
  | cons first rest ih =>
    simp only [List.cons_append]
    rw [accept_continuation, ih]
    simp [feed, List.append_assoc]

theorem chunks_continuation (machine : Machine Input Output) (pending input suffix) :
    batch machine (buffered pending ++ (input.flatten ++ suffix)) =
      (chunks machine pending input).output ++
        batch machine (buffered (chunks machine pending input).pending ++ suffix) := by
  induction input generalizing pending with
  | nil => simp [chunks]
  | cons first rest ih =>
    simp only [List.flatten_cons, List.append_assoc]
    rw [feed_continuation, ih]
    simp [chunks, List.append_assoc]

theorem stream_batch (machine : Machine Input Output) (input) :
    stream machine input = batch machine input.flatten := by
  have result := chunks_continuation machine none input []
  simp only [List.append_nil, batch_buffered] at result
  simpa [buffered, stream, finish] using result.symm

theorem feed_append (machine : Machine Input Output) (pending first second) :
    feed machine pending (first ++ second) =
      let left := feed machine pending first
      let right := feed machine left.pending second
      ⟨left.output ++ right.output, right.pending⟩ := by
  induction first generalizing pending with
  | nil => simp [feed]
  | cons input rest ih => simp [feed, ih, List.append_assoc]

theorem chunks_feed (machine : Machine Input Output) (pending input) :
    chunks machine pending input = feed machine pending input.flatten := by
  induction input generalizing pending with
  | nil => rfl
  | cons first rest ih => simp [chunks, feed_append, ih]

theorem feed_finish (machine : Machine Input Output) (pending input) :
    finish machine (feed machine pending input) = batch machine (buffered pending ++ input) := by
  have result := feed_continuation machine pending input []
  simpa [finish, batch_buffered] using result.symm

theorem accept_pending_valid (machine : Machine Input Output) (pending input value)
    (held : (accept machine pending input).pending = some value) : machine.holds value = true := by
  cases pending <;> simp only [accept] at held
  · split at held <;> simp_all
  · split at held
    · simp at held
    · split at held <;> simp_all

theorem feed_pending_valid (machine : Machine Input Output) (pending input)
    (prior : ∀ value, pending = some value → machine.holds value = true) :
    ∀ value, (feed machine pending input).pending = some value → machine.holds value = true := by
  induction input generalizing pending with
  | nil => exact prior
  | cons first rest ih =>
    exact ih _ (accept_pending_valid machine pending first)

end CssStreaming
