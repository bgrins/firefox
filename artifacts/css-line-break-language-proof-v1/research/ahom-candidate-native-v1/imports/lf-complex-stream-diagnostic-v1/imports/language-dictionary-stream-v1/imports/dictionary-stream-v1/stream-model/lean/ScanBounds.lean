import IdentityWorld

namespace LanguageBreak

theorem completed_immediate_indices (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) :
    (completeImmediate providers width chunk scan).position = scan.position ∧
    (completeImmediate providers width chunk scan).wordStart = scan.wordStart ∧
    (completeImmediate providers width chunk scan).finished = scan.finished := by
  unfold completeImmediate segmentImmediate
  repeat first | exact ⟨rfl,rfl,rfl⟩ | split

theorem scan_step_progress (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (noBreaks : Bool) (scan : Scan) :
    (scanStep providers width chunk noBreaks scan).finished = true ∨
    (scanStep providers width chunk noBreaks scan).position = scan.position+1 := by
  dsimp only [scanStep]
  split
  · exact Or.inr rfl
  · split
    · exact Or.inr rfl
    · exact Or.inl rfl

theorem scan_loop_complete (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (noBreaks : Bool) (fuel : Nat) (scan : Scan)
    (enough : chunk.storage.decode.length ≤ scan.position+fuel) :
    (scanLoop providers width chunk noBreaks fuel scan).finished = true ∨
    chunk.storage.decode.length ≤ (scanLoop providers width chunk noBreaks fuel scan).position := by
  induction fuel generalizing scan with
  | zero => exact Or.inr (by simpa [scanLoop] using enough)
  | succ fuel ih =>
    unfold scanLoop
    split
    next stop =>
      simp only [Bool.or_eq_true,decide_eq_true_eq] at stop
      exact stop
    next running =>
      have progress := scan_step_progress providers width chunk noBreaks scan
      rcases progress with finished | advanced
      · cases fuel with
        | zero => exact Or.inl finished
        | succ rest => simp [scanLoop,finished]
      · apply ih
        omega

theorem initial_scan_fuel_sufficient (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (noBreaks : Bool) (scan : Scan) :
    (scanLoop providers width chunk noBreaks chunk.storage.decode.length scan).finished = true ∨
    chunk.storage.decode.length ≤ (scanLoop providers width chunk noBreaks chunk.storage.decode.length scan).position :=
  scan_loop_complete providers width chunk noBreaks _ scan (by omega)

end LanguageBreak
