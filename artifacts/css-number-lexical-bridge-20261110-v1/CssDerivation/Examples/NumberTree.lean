import CssDerivation.Parser.Syntax

namespace CssDerivation.NumberTransfer

open ParserIR

def digitPredicate : Predicate :=
  .and (.leChar (.scalar '0') (.var .here)) (.leChar (.var .here) (.scalar '9'))

def signPredicate : Predicate :=
  .or (.eqChar (.var .here) (.scalar '+')) (.eqChar (.var .here) (.scalar '-'))

def dotPredicate : Predicate := .eqChar (.var .here) (.scalar '.')

def exponentPredicate : Predicate :=
  .or (.eqChar (.var .here) (.scalar 'e')) (.eqChar (.var .here) (.scalar 'E'))

abbrev SignShape := Shape.optional (.base .scalar)
abbrev ExponentShape := Shape.pair SignShape (.base .chars)
abbrev NumberShape := Shape.pair SignShape
  (.pair (.base .chars) (.pair (.optional (.base .chars)) (.optional ExponentShape)))

def signTree : Parser SignShape := .optional (.take signPredicate)
def digitsTree : Parser (.base .chars) := .scan digitPredicate
def nonemptyDigitsTree : Parser (.base .chars) := .nonempty digitsTree
def fractionTree : Parser (.base .chars) := .right (.take dotPredicate) nonemptyDigitsTree
def exponentTree : Parser ExponentShape :=
  .right (.take exponentPredicate) (.pair signTree nonemptyDigitsTree)

def numberTree : Parser NumberShape :=
  .pair signTree (.pair digitsTree (.pair (.optional fractionTree) (.optional exponentTree)))

def magnitudeExpression : FirstOrder.Expr [.chars] .nat :=
  .foldNat (.var .here) (.nat 0)
    (.add (.mul (.var (.there .here)) (.nat 10)) (.sub (.code (.var .here)) (.nat 48)))

def magnitude (digits : List Char) : Nat := FirstOrder.eval magnitudeExpression (.cons digits .nil)

def signedMagnitude (sign : Option Char) (value : Nat) : Int :=
  if sign = some '-' then -(value : Int) else value

structure Exact where
  significand : Int
  scale : Int
  isNumber : Bool
  sign : Option Char
  deriving DecidableEq, Repr

def project (parts : NumberShape.Value) : Exact :=
  let fraction := parts.2.2.1.getD []
  let exponent := match parts.2.2.2 with
    | none => 0
    | some (sign, digits) => signedMagnitude sign (magnitude digits)
  ⟨signedMagnitude parts.1 (magnitude (parts.2.1 ++ fraction)),
    exponent - fraction.length, parts.2.2.1.isSome || parts.2.2.2.isSome, parts.1⟩

def execute (state : State) : Option (Exact × State) :=
  (ParserIR.run numberTree state).map fun (parts, next) => (project parts, next)

end CssDerivation.NumberTransfer
