import FirstOrder

namespace CssDerivation.FirstOrder

theorem scan_lowering (predicate : Expr (.scalar :: Γ) .bool) (env : Env Γ)
    (budget : Nat) (source : List Char) :
    scanData predicate env budget source = scanPrefix (fun c => eval predicate (.cons c env)) budget source := by
  induction budget generalizing source with
  | zero => rfl
  | succ budget ih =>
      cases source with
      | nil => rfl
      | cons c rest => simp [scanData, scanPrefix, ih]

theorem lowering_correct (program : Stmt Γ t) (env : Env Γ) (state : State) :
    run (lower program env) state = interpret program env state := by
  induction program generalizing state with
  | ret value => rfl
  | letE value next ih => simpa [lower, run, interpret] using ih (.cons (eval value env) env) state
  | read eof present eofIH presentIH =>
      cases input : state.input with
      | nil => simpa [lower, run, interpret, input] using eofIH env state
      | cons c rest =>
          simpa [lower, run, interpret, input] using presentIH (.cons c env) { state with input := rest }
  | scan budget predicate next ih =>
      simpa [lower, run, interpret, scan_lowering] using
        ih (.cons (scanPrefix (fun c => eval predicate (.cons c env)) budget state.input).1 env)
          { state with input := (scanPrefix (fun c => eval predicate (.cons c env)) budget state.input).2 }
  | raiseError next ih => simpa [lower, run, interpret] using ih env { state with error := true }
  | branch condition yes no yesIH noIH =>
      simp only [lower, run, interpret]
      split
      · exact yesIH env state
      · exact noIH env state

theorem execute_lowering (program : Stmt [] .scalar) (source : List Char) :
    CssDerivation.execute (lower program .nil) source = execute program source := by
  have equal := lowering_correct program .nil ⟨source, false⟩
  unfold CssDerivation.execute execute
  rw [equal]

#print axioms lowering_correct

end CssDerivation.FirstOrder
