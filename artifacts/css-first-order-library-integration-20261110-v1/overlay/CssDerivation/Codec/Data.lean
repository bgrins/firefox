import CssDerivation.FirstOrder

namespace CssDerivation.TypedCodec
open FirstOrder

inductive DataExpr where
  | nat : Nat → DataExpr
  | scalar : Char → DataExpr
  | bool : Bool → DataExpr
  | nil | unit
  | var : Nat → DataExpr
  | code : DataExpr → DataExpr
  | scalarOf : DataExpr → DataExpr
  | add : DataExpr → DataExpr → DataExpr
  | sub : DataExpr → DataExpr → DataExpr
  | mul : DataExpr → DataExpr → DataExpr
  | leNat : DataExpr → DataExpr → DataExpr
  | ltNat : DataExpr → DataExpr → DataExpr
  | eqNat : DataExpr → DataExpr → DataExpr
  | leChar : DataExpr → DataExpr → DataExpr
  | eqChar : DataExpr → DataExpr → DataExpr
  | and : DataExpr → DataExpr → DataExpr
  | or : DataExpr → DataExpr → DataExpr
  | cons : DataExpr → DataExpr → DataExpr
  | ite : DataExpr → DataExpr → DataExpr → DataExpr
  | foldNat : DataExpr → DataExpr → DataExpr → DataExpr
  | scope : Ty → DataExpr → DataExpr
  deriving Repr, DecidableEq

inductive DataStmt where
  | ret : DataExpr → DataStmt
  | letE : DataExpr → DataStmt → DataStmt
  | read : DataStmt → DataStmt → DataStmt
  | scan : Nat → DataExpr → DataStmt → DataStmt
  | raiseError : DataStmt → DataStmt
  | branch : DataExpr → DataStmt → DataStmt → DataStmt
  deriving Repr, DecidableEq

def encodeVar : Var Γ t → Nat
  | .here => 0
  | .there v => encodeVar v + 1

def inferVar : (Γ : List Ty) → Nat → Option (Σ t, Var Γ t)
  | [], _ => none
  | t :: _, 0 => some ⟨t, .here⟩
  | _ :: Γ, n + 1 => do
      let ⟨t, v⟩ ← inferVar Γ n
      pure ⟨t, .there v⟩

def expect {F : Ty → Type} (t : Ty) : (Σ u, F u) → Option (F t)
  | ⟨u, e⟩ => if h : u = t then some (h ▸ e) else none

def decodeVar (Γ : List Ty) (t : Ty) (n : Nat) : Option (Var Γ t) :=
  (inferVar Γ n).bind (expect t)

def encodeExpr : Expr Γ t → DataExpr
  | .nat n => .nat n
  | .scalar c => .scalar c
  | .bool b => .bool b
  | .nil => .nil
  | .unit => .unit
  | .var v => .var (encodeVar v)
  | .code a => .code (encodeExpr a)
  | .scalarOf a => .scalarOf (encodeExpr a)
  | .add a b => .add (encodeExpr a) (encodeExpr b)
  | .sub a b => .sub (encodeExpr a) (encodeExpr b)
  | .mul a b => .mul (encodeExpr a) (encodeExpr b)
  | .leNat a b => .leNat (encodeExpr a) (encodeExpr b)
  | .ltNat a b => .ltNat (encodeExpr a) (encodeExpr b)
  | .eqNat a b => .eqNat (encodeExpr a) (encodeExpr b)
  | .leChar a b => .leChar (encodeExpr a) (encodeExpr b)
  | .eqChar a b => .eqChar (encodeExpr a) (encodeExpr b)
  | .and a b => .and (encodeExpr a) (encodeExpr b)
  | .or a b => .or (encodeExpr a) (encodeExpr b)
  | .cons a b => .cons (encodeExpr a) (encodeExpr b)
  | .ite c a b => .ite (encodeExpr c) (encodeExpr a) (encodeExpr b)
  | .foldNat xs z f => .foldNat (encodeExpr xs) (encodeExpr z) (encodeExpr f)

def inferExpr (Γ : List Ty) : DataExpr → Option (Σ t, Expr Γ t)
  | .nat n => some ⟨.nat, .nat n⟩
  | .scalar c => some ⟨.scalar, .scalar c⟩
  | .bool b => some ⟨.bool, .bool b⟩
  | .nil => some ⟨.chars, .nil⟩
  | .unit => some ⟨.unit, .unit⟩
  | .var n => do
      let ⟨t, v⟩ ← inferVar Γ n
      pure ⟨t, .var v⟩
  | .code a => do
      let a ← (inferExpr Γ a).bind (expect .scalar)
      pure ⟨.nat, .code a⟩
  | .scalarOf a => do
      let a ← (inferExpr Γ a).bind (expect .nat)
      pure ⟨.scalar, .scalarOf a⟩
  | .add a b => do
      let a ← (inferExpr Γ a).bind (expect .nat)
      let b ← (inferExpr Γ b).bind (expect .nat)
      pure ⟨.nat, .add a b⟩
  | .sub a b => do
      let a ← (inferExpr Γ a).bind (expect .nat)
      let b ← (inferExpr Γ b).bind (expect .nat)
      pure ⟨.nat, .sub a b⟩
  | .mul a b => do
      let a ← (inferExpr Γ a).bind (expect .nat)
      let b ← (inferExpr Γ b).bind (expect .nat)
      pure ⟨.nat, .mul a b⟩
  | .leNat a b => do
      let a ← (inferExpr Γ a).bind (expect .nat)
      let b ← (inferExpr Γ b).bind (expect .nat)
      pure ⟨.bool, .leNat a b⟩
  | .ltNat a b => do
      let a ← (inferExpr Γ a).bind (expect .nat)
      let b ← (inferExpr Γ b).bind (expect .nat)
      pure ⟨.bool, .ltNat a b⟩
  | .eqNat a b => do
      let a ← (inferExpr Γ a).bind (expect .nat)
      let b ← (inferExpr Γ b).bind (expect .nat)
      pure ⟨.bool, .eqNat a b⟩
  | .leChar a b => do
      let a ← (inferExpr Γ a).bind (expect .scalar)
      let b ← (inferExpr Γ b).bind (expect .scalar)
      pure ⟨.bool, .leChar a b⟩
  | .eqChar a b => do
      let a ← (inferExpr Γ a).bind (expect .scalar)
      let b ← (inferExpr Γ b).bind (expect .scalar)
      pure ⟨.bool, .eqChar a b⟩
  | .and a b => do
      let a ← (inferExpr Γ a).bind (expect .bool)
      let b ← (inferExpr Γ b).bind (expect .bool)
      pure ⟨.bool, .and a b⟩
  | .or a b => do
      let a ← (inferExpr Γ a).bind (expect .bool)
      let b ← (inferExpr Γ b).bind (expect .bool)
      pure ⟨.bool, .or a b⟩
  | .cons a b => do
      let a ← (inferExpr Γ a).bind (expect .scalar)
      let b ← (inferExpr Γ b).bind (expect .chars)
      pure ⟨.chars, .cons a b⟩
  | .ite c a b => do
      let c ← (inferExpr Γ c).bind (expect .bool)
      let ⟨t, a⟩ ← inferExpr Γ a
      let b ← (inferExpr Γ b).bind (expect t)
      pure ⟨t, .ite c a b⟩
  | .foldNat xs z f => do
      let xs ← (inferExpr Γ xs).bind (expect .chars)
      let z ← (inferExpr Γ z).bind (expect .nat)
      let f ← (inferExpr (.scalar :: .nat :: Γ) f).bind (expect .nat)
      pure ⟨.nat, .foldNat xs z f⟩
  | .scope head e => do
      if Γ.head? = some head then inferExpr Γ e else none

def decodeExpr (Γ : List Ty) (t : Ty) (e : DataExpr) : Option (Expr Γ t) :=
  (inferExpr Γ e).bind (expect t)

def encodeStmt : Stmt Γ t → DataStmt
  | .ret e => .ret (encodeExpr e)
  | .letE e next => .letE (encodeExpr e) (encodeStmt next)
  | .read eof next => .read (encodeStmt eof) (encodeStmt next)
  | .scan budget p next => .scan budget (encodeExpr p) (encodeStmt next)
  | .raiseError next => .raiseError (encodeStmt next)
  | .branch c a b => .branch (encodeExpr c) (encodeStmt a) (encodeStmt b)

def decodeStmt (Γ : List Ty) (t : Ty) : DataStmt → Option (Stmt Γ t)
  | .ret e => do
      let e ← decodeExpr Γ t e
      pure (.ret e)
  | .letE e next => do
      let ⟨u, e⟩ ← inferExpr Γ e
      let next ← decodeStmt (u :: Γ) t next
      pure (.letE e next)
  | .read eof next => do
      let eof ← decodeStmt Γ t eof
      let next ← decodeStmt (.scalar :: Γ) t next
      pure (.read eof next)
  | .scan budget p next => do
      let p ← decodeExpr (.scalar :: Γ) .bool p
      let next ← decodeStmt (.chars :: Γ) t next
      pure (.scan budget p next)
  | .raiseError next => do
      let next ← decodeStmt Γ t next
      pure (.raiseError next)
  | .branch c a b => do
      let c ← decodeExpr Γ .bool c
      let a ← decodeStmt Γ t a
      let b ← decodeStmt Γ t b
      pure (.branch c a b)

def normalizeExpr : DataExpr → DataExpr
  | .scope _ e => normalizeExpr e
  | .nat n => .nat n
  | .scalar c => .scalar c
  | .bool b => .bool b
  | .nil => .nil
  | .unit => .unit
  | .var n => .var n
  | .code a => .code (normalizeExpr a)
  | .scalarOf a => .scalarOf (normalizeExpr a)
  | .add a b => .add (normalizeExpr a) (normalizeExpr b)
  | .sub a b => .sub (normalizeExpr a) (normalizeExpr b)
  | .mul a b => .mul (normalizeExpr a) (normalizeExpr b)
  | .leNat a b => .leNat (normalizeExpr a) (normalizeExpr b)
  | .ltNat a b => .ltNat (normalizeExpr a) (normalizeExpr b)
  | .eqNat a b => .eqNat (normalizeExpr a) (normalizeExpr b)
  | .leChar a b => .leChar (normalizeExpr a) (normalizeExpr b)
  | .eqChar a b => .eqChar (normalizeExpr a) (normalizeExpr b)
  | .and a b => .and (normalizeExpr a) (normalizeExpr b)
  | .or a b => .or (normalizeExpr a) (normalizeExpr b)
  | .cons a b => .cons (normalizeExpr a) (normalizeExpr b)
  | .ite a b c => .ite (normalizeExpr a) (normalizeExpr b) (normalizeExpr c)
  | .foldNat a b c => .foldNat (normalizeExpr a) (normalizeExpr b) (normalizeExpr c)

def normalizeStmt : DataStmt → DataStmt
  | .ret e => .ret (normalizeExpr e)
  | .letE e next => .letE (normalizeExpr e) (normalizeStmt next)
  | .read eof next => .read (normalizeStmt eof) (normalizeStmt next)
  | .scan n e next => .scan n (normalizeExpr e) (normalizeStmt next)
  | .raiseError next => .raiseError (normalizeStmt next)
  | .branch e a b => .branch (normalizeExpr e) (normalizeStmt a) (normalizeStmt b)

def checkExpr (Γ : List Ty) (t : Ty) (data : DataExpr) : Option (Expr Γ t) := do
  let e ← decodeExpr Γ t data
  if encodeExpr e = normalizeExpr data then some e else none

def checkStmt (Γ : List Ty) (t : Ty) (data : DataStmt) : Option (Stmt Γ t) := do
  let p ← decodeStmt Γ t data
  if encodeStmt p = normalizeStmt data then some p else none

end CssDerivation.TypedCodec
