import TokenSummary
namespace ResolvedDependencies

inductive Piece where
  | literal (tokens : List Token)
  | replacement (primary fallback : Option (List Token))

def select : Piece → Option (List Token)
  | .literal tokens => some tokens
  | .replacement (some tokens) _ => some tokens
  | .replacement none fallback => fallback

def execute (boundary : Boundary) : List Piece → List Token → Option (List Token)
  | [], out => some out
  | piece :: rest, out =>
      match select piece with
      | none => none
      | some tokens => execute boundary rest (emit boundary out tokens)

def accumulate : List Piece → Scan → Option Scan
  | [], summary => some summary
  | .literal tokens :: rest, summary =>
      accumulate rest (combine summary (scan tokens))
  | .replacement (some primary) _ :: rest, summary =>
      accumulate rest (combine summary (scan primary))
  | .replacement none (some fallback) :: rest, summary =>
      accumulate rest (combine summary (scan fallback))
  | .replacement none none :: _, _ => none

theorem selected_output_summary (boundary : Boundary) (pieces : List Piece) (out : List Token) :
    (execute boundary pieces out).map scan = accumulate pieces (scan out) := by
  induction pieces generalizing out with
  | nil => rfl
  | cons piece rest ih =>
    cases piece with
    | literal tokens => simp [execute, select, accumulate, ih, emit_scan]
    | replacement primary fallback =>
      cases primary with
      | some tokens => simp [execute, select, accumulate, ih, emit_scan]
      | none =>
        cases fallback <;> simp [execute, select, accumulate, ih, emit_scan]

theorem execute_append (boundary : Boundary) (left right : List Piece) (out : List Token) :
    execute boundary (left ++ right) out =
      (execute boundary left out).bind (execute boundary right) := by
  induction left generalizing out with
  | nil => rfl
  | cons piece rest ih =>
    simp only [List.cons_append, execute]
    cases select piece <;> simp [ih]

theorem unused_fallback_independence (boundary : Boundary) (before after : List Piece)
    (out primary : List Token) (fallback₁ fallback₂ : Option (List Token)) :
    execute boundary (before ++ .replacement (some primary) fallback₁ :: after) out =
      execute boundary (before ++ .replacement (some primary) fallback₂ :: after) out := by
  simp [execute_append, execute, select]

theorem unused_fallback_summary_independence (before after : List Piece)
    (out primary : List Token) (fallback₁ fallback₂ : Option (List Token)) :
    accumulate (before ++ .replacement (some primary) fallback₁ :: after) (scan out) =
      accumulate (before ++ .replacement (some primary) fallback₂ :: after) (scan out) := by
  rw [← selected_output_summary (fun _ _ => false), ← selected_output_summary (fun _ _ => false)]
  rw [unused_fallback_independence]

theorem failed_primary_uses_fallback (boundary : Boundary) (rest : List Piece)
    (out fallback : List Token) :
    execute boundary (.replacement none (some fallback) :: rest) out =
      execute boundary rest (emit boundary out fallback) := rfl

theorem failed_selected_output_propagates (boundary : Boundary) (before after : List Piece)
    (out : List Token) :
    execute boundary (before ++ .replacement none none :: after) out = none := by
  rw [execute_append]
  cases execute boundary before out <;> rfl

theorem successful_unknown_is_distinct_from_failure (boundary : Boundary) :
    (execute boundary [.literal [.unresolved]] []).map scan = some none ∧
    (execute boundary [.replacement none none] []).map scan = none := by
  simp [execute, select, emit, scan, tokenScan, combine]

theorem successful_primary_ignores_unknown_fallback (boundary : Boundary) :
    (execute boundary [.replacement (some [.dimension .font]) (some [.unresolved])] []).map scan =
      some (some (unitFlags .font)) := by
  simp [execute, select, emit, scan, tokenScan, combine]

theorem tokenizer_bridge (boundary : Boundary) (pieces : List Piece) (out emitted : List Token)
    (tokenize : String → List Token) (css : String)
    (execution : execute boundary pieces out = some emitted)
    (correspondence : eraseSeparators (tokenize css) = eraseSeparators emitted) :
    accumulate pieces (scan out) = some (scan (tokenize css)) := by
  rw [← selected_output_summary boundary, execution]
  simp only [Option.map_some]
  rw [equal_tokens_modulo_separators (tokenize css) emitted correspondence]

end ResolvedDependencies
