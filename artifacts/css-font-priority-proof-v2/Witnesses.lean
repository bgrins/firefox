namespace PriorityWitness
open Priority

structure Face where
  identity : Nat
  key : Key
  deriving DecidableEq, Repr

def faceOrder := pullback fallbackOrder Face.key
def faceWidth := pullback widthOrder Face.key
def faceStyle := pullback styleOrder Face.key
def faceWeight := pullback weightOrder Face.key
def facePresentation := pullback presentationOrder Face.key

def chosen (xs : List Face) :=
  (successive faceWidth faceStyle faceWeight (minima facePresentation xs)).map Face.identity

def weighted (x : Face) :=
  x.key.width * 100000000 + x.key.style * 10000 + x.key.weight

def weightedOrder := lex facePresentation (pullback natural weighted)
def weightedChoice (xs : List Face) := (minima weightedOrder xs).map Face.identity

def rounded (x : Face) := (weighted x + 1048576) / 2097152

def roundedOrder := lex facePresentation (pullback natural rounded)
def roundedChoice (xs : List Face) := (minima roundedOrder xs).map Face.identity

def lt (x y : Face) : Bool := decide (faceOrder.le x y ∧ ¬faceOrder.le y x)
def le (x y : Face) : Bool := decide (faceOrder.le x y)

def walk (compare : Face → Face → Bool) (stop : Key → Bool)
    (best : Option Face) : List Face → Option Face
  | [] => best
  | x :: xs =>
    let next := match best with
      | none => some x
      | some b => if compare x b then some x else best
    if (next.map (fun f => stop f.key)).getD false then next
    else walk compare stop next xs

def globalChoice (compare : Face → Face → Bool) (stop : Key → Bool) (xs : List Face) :=
  ((walk compare stop none xs).toList).map Face.identity

def falseZero (x : Key) : Bool := x.width == 0 && x.style == 0 && x.weight == 0

def withoutPresentation (xs : List Face) :=
  xs.map (fun f => { f with key := { f.key with presentation := 0 } })

def noClear (xs : List Face) : List Nat :=
  let state := xs.foldl (fun (state : Option Face × List Face) x =>
    match state.1 with
    | none => (some x, state.2)
    | some b =>
      if lt x b then (some x, state.2)
      else if le x b then (some x, state.2 ++ [b])
      else state) (none, [])
  (state.2 ++ state.1.toList).map Face.identity

