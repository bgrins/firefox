import CssDerivation.Parser.Lowering

namespace CssParserLowering

open CssDerivation CssDerivation.ParserIR

theorem legacy_preserved (program : CssDerivation.Program α) (state) :
    run (.legacy program) state = CssDerivation.run program state := rfl

theorem pure_preserved (value : α) (state) : run (pure value) state = (value, state) := rfl

theorem state_read (state) : run .getState state = (state, state) := rfl

theorem state_write (before after) : run (.putState after) before = ((), after) := rfl

theorem transaction_result (program : Program (Option α)) (state) :
    run (transaction program) state =
      match run program state with
      | (none, _) => (none, state)
      | (some value, final) => (some value, final) := by
  simp only [transaction, run]
  cases outcome : run program state with
  | mk value final => cases value <;> rfl

theorem transaction_failure (program : Program (Option α)) (before after)
    (failed : run program before = (none, after)) :
    run (transaction program) before = (none, before) := by
  rw [transaction_result, failed]

theorem transaction_success (program : Program (Option α)) (before after value)
    (success : run program before = (some value, after)) :
    run (transaction program) before = (some value, after) := by
  rw [transaction_result, success]

theorem maximal_scan (predicate : Predicate) (source) :
    CssDerivation.scanPrefix (accepts predicate) source.length source = scanWhile predicate source := by
  rw [scan_matches_length_bound, FirstOrder.scan_lowering]
  rfl

theorem lowering_correct (parser : Parser shape) (state) :
    run (lower parser) state = observed state (ParserIR.run parser state) := by
  induction parser generalizing state with
  | legacy program =>
    simp [lower, run, pure, FirstOrder.lowering_correct, CssDerivation.run, ParserIR.run, observed]
  | take predicate =>
    rw [lower, transaction_result]
    cases input : state.input with
    | nil => simp [run, CssDerivation.run, input, pure, ParserIR.run, observed]
    | cons c rest =>
      by_cases accepted : accepts predicate c = true <;>
        simp [run, CssDerivation.run, input, pure, ParserIR.run, observed, accepted]
  | scan predicate =>
    simp [lower, run, CssDerivation.run, pure, ParserIR.run, observed, maximal_scan]
  | nonempty parser ih =>
    rw [lower, transaction_result]
    simp only [run, ih]
    cases result : ParserIR.run parser state with
    | none => simp [observed, pure, run, CssDerivation.run, ParserIR.run, result]
    | some value =>
      obtain ⟨chars, final⟩ := value
      cases chars <;> simp [observed, pure, run, CssDerivation.run, ParserIR.run, result]
  | pair left right leftIH rightIH =>
    rw [lower, transaction_result]
    simp only [run, leftIH]
    cases first : ParserIR.run left state with
    | none => simp [observed, pure, run, CssDerivation.run, ParserIR.run, first]
    | some value =>
      obtain ⟨a, next⟩ := value
      simp only [observed, run, rightIH]
      cases second : ParserIR.run right next <;>
        simp [pure, run, CssDerivation.run, ParserIR.run, first, second]
  | right left right leftIH rightIH =>
    rw [lower, transaction_result]
    simp only [run, leftIH]
    cases first : ParserIR.run left state with
    | none => simp [observed, pure, run, CssDerivation.run, ParserIR.run, first]
    | some value =>
      obtain ⟨a, next⟩ := value
      simp only [observed, rightIH]
      cases second : ParserIR.run right next <;>
        simp [ParserIR.run, first, second]
  | optional parser ih =>
    simp only [lower, run, ih]
    cases result : ParserIR.run parser state <;>
      simp [observed, pure, run, CssDerivation.run, ParserIR.run, result]

end CssParserLowering
