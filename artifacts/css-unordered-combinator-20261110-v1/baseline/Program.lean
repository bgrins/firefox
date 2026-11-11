import Grammar

namespace CssGrammar

inductive Op where
  | keyword (word : String)
  | alt
  | seq
  | optional
  deriving Repr, DecidableEq

def execute : List Op → List Grammar → Option (List Grammar)
  | [], stack => some stack
  | .keyword word :: code, stack => execute code (.keyword word :: stack)
  | .alt :: code, right :: left :: stack => execute code (.alt left right :: stack)
  | .seq :: code, right :: left :: stack => execute code (.seq left right :: stack)
  | .optional :: code, body :: stack => execute code (.optional body :: stack)
  | _, _ => none

def encode : Grammar → List Op
  | .keyword word => [.keyword word]
  | .alt left right => encode left ++ encode right ++ [.alt]
  | .seq left right => encode left ++ encode right ++ [.seq]
  | .optional body => encode body ++ [.optional]

def decode (code : List Op) : Option Grammar :=
  match execute code [] with
  | some [grammar] => some grammar
  | _ => none

end CssGrammar
