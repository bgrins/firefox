import CssDerivation.Codec.DataLaws

namespace CssDerivation.DocumentDesign
open FirstOrder TypedCodec

def appendEnv : Env Γ → Env Δ → Env (Γ ++ Δ)
  | .nil, tail => tail
  | .cons value rest, tail => .cons value (appendEnv rest tail)

def weakenVar (Δ : List Ty) : Var Γ t → Var (Γ ++ Δ) t
  | .here => .here
  | .there v => .there (weakenVar Δ v)

def weakenExpr (Δ : List Ty) : Expr Γ t → Expr (Γ ++ Δ) t
  | .nat n => .nat n
  | .scalar c => .scalar c
  | .bool b => .bool b
  | .nil => .nil
  | .unit => .unit
  | .var v => .var (weakenVar Δ v)
  | .code a => .code (weakenExpr Δ a)
  | .scalarOf a => .scalarOf (weakenExpr Δ a)
  | .add a b => .add (weakenExpr Δ a) (weakenExpr Δ b)
  | .sub a b => .sub (weakenExpr Δ a) (weakenExpr Δ b)
  | .mul a b => .mul (weakenExpr Δ a) (weakenExpr Δ b)
  | .leNat a b => .leNat (weakenExpr Δ a) (weakenExpr Δ b)
  | .ltNat a b => .ltNat (weakenExpr Δ a) (weakenExpr Δ b)
  | .eqNat a b => .eqNat (weakenExpr Δ a) (weakenExpr Δ b)
  | .leChar a b => .leChar (weakenExpr Δ a) (weakenExpr Δ b)
  | .eqChar a b => .eqChar (weakenExpr Δ a) (weakenExpr Δ b)
  | .and a b => .and (weakenExpr Δ a) (weakenExpr Δ b)
  | .or a b => .or (weakenExpr Δ a) (weakenExpr Δ b)
  | .cons a b => .cons (weakenExpr Δ a) (weakenExpr Δ b)
  | .ite a b c => .ite (weakenExpr Δ a) (weakenExpr Δ b) (weakenExpr Δ c)
  | .foldNat xs z f => .foldNat (weakenExpr Δ xs) (weakenExpr Δ z) (weakenExpr Δ f)

end CssDerivation.DocumentDesign
