import Program

namespace CssGrammar

theorem encode_execute (grammar : Grammar) (code : List Op) (stack : List Grammar) :
    execute (encode grammar ++ code) stack = execute code (grammar :: stack) := by
  induction grammar generalizing code stack with
  | keyword word => rfl
  | alt left right ihL ihR =>
    simp only [encode, List.append_assoc, ihL, ihR, List.cons_append, List.nil_append,
      execute]
  | seq left right ihL ihR =>
    simp only [encode, List.append_assoc, ihL, ihR, List.cons_append, List.nil_append,
      execute]
  | optional body ih =>
    simp only [encode, List.append_assoc, ih, List.cons_append, List.nil_append, execute]

theorem decode_encode (grammar : Grammar) : decode (encode grammar) = some grammar := by
  have h := encode_execute grammar [] []
  simp only [List.append_nil, execute] at h
  simp [decode, h]

end CssGrammar
