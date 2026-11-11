namespace CssGrammar

inductive Grammar where
  | keyword (word : String)
  | alt (left right : Grammar)
  | seq (left right : Grammar)
  | optional (body : Grammar)
  deriving Repr, DecidableEq

inductive Matches : Grammar → List String → List String → Prop where
  | keyword : Matches (.keyword word) (word :: rest) rest
  | left : Matches left input rest → Matches (.alt left right) input rest
  | right : Matches right input rest → Matches (.alt left right) input rest
  | seq : Matches left input middle → Matches right middle rest →
      Matches (.seq left right) input rest
  | absent : Matches (.optional body) input input
  | present : Matches body input rest → Matches (.optional body) input rest

def run : Grammar → List String → List (List String)
  | .keyword word, input => match input with
    | [] => []
    | first :: rest => if first == word then [rest] else []
  | .alt left right, input => run left input ++ run right input
  | .seq left right, input => (run left input).flatMap (run right)
  | .optional body, input => input :: run body input

def accepts (grammar : Grammar) (input : List String) : Bool :=
  (run grammar input).contains []

end CssGrammar
