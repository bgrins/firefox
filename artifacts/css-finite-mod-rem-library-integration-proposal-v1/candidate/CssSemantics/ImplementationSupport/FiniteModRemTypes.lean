namespace CssSemantics.ImplementationSupport.ModRemInfinity

inductive Op where
  | mod | rem
  deriving DecidableEq, Repr

inductive Finite (α : Type) where
  | zero (negative : Bool)
  | nonzero (negative : Bool) (magnitude : α)
  deriving DecidableEq, Repr

inductive Number (α : Type) where
  | finite (value : Finite α)
  | infinity (negative : Bool)
  | nan
  deriving DecidableEq, Repr

abbrev FiniteBackend (α : Type) := Op → Finite α → Bool → α → Number α

end CssSemantics.ImplementationSupport.ModRemInfinity
