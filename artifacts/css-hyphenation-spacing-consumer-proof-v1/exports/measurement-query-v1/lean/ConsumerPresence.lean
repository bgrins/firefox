import NestedSpacingQueries

namespace ConsumerPresence

structure Answer (Value : Type) where
  present : Bool
  before : Value
  after : Value
  deriving DecidableEq, Repr

def Contract (zero : Value) (answer : Answer Value) : Prop :=
  answer.present = false → answer.before = zero ∧ answer.after = zero

def addBefore (add : Value → Value → Value) (width : Value) (answer : Answer Value) : Value :=
  if answer.present then add width answer.before else width

def addAfter (add : Value → Value → Value) (width : Value) (answer : Answer Value) : Value :=
  if answer.present then add width answer.after else width

theorem before_projection (add : Value → Value → Value) (zero width : Value)
    (zeroRight : ∀ value, add value zero = value) (answer : Answer Value) (valid : Contract zero answer) :
    addBefore add width answer = add width answer.before := by
  cases flag : answer.present
  · have absent := valid flag
    simp [addBefore,flag,absent.1,zeroRight]
  · simp [addBefore,flag]

theorem after_projection (add : Value → Value → Value) (zero width : Value)
    (zeroRight : ∀ value, add value zero = value) (answer : Answer Value) (valid : Contract zero answer) :
    addAfter add width answer = add width answer.after := by
  cases flag : answer.present
  · have absent := valid flag
    simp [addAfter,flag,absent.2,zeroRight]
  · simp [addAfter,flag]

theorem ligature_observation (add : Value → Value → Value) (zero width : Value)
    (zeroRight : ∀ value, add value zero = value) (left right : Answer Value)
    (leftValid : Contract zero left) (rightValid : Contract zero right) :
    addAfter add (addBefore add width left) right = add (add width left.before) right.after := by
  rw [after_projection add zero _ zeroRight right rightValid,before_projection add zero width zeroRight left leftValid]

theorem same_values_same_ligature_observation (add : Value → Value → Value) (zero width : Value)
    (zeroRight : ∀ value, add value zero = value) (a b c d : Answer Value)
    (ha : Contract zero a) (hb : Contract zero b) (hc : Contract zero c) (hd : Contract zero d)
    (beforeEqual : a.before = c.before) (afterEqual : b.after = d.after) :
    addAfter add (addBefore add width a) b = addAfter add (addBefore add width c) d := by
  rw [ligature_observation add zero width zeroRight a b ha hb,
    ligature_observation add zero width zeroRight c d hc hd,beforeEqual,afterEqual]

def directBuffer (answer : Bool × List (Value × Value)) : List (Value × Value) := answer.2

theorem direct_ignores_flag (values : List (Value × Value)) (first second : Bool) :
    directBuffer (first,values) = directBuffer (second,values) := rfl

def arrayBuffer (answer : Bool × List (Value × Value)) : Option (List (Value × Value)) :=
  if answer.1 then some answer.2 else none

theorem array_preserves_presence_distinction :
    arrayBuffer (false,[(0,0)]) ≠ arrayBuffer (true,[(0,0)]) := by decide

theorem arbitrary_arithmetic_cannot_erase_presence :
    addBefore (fun (a b : Nat) => a+b+1) 3 ⟨false,0,0⟩ ≠
      addBefore (fun (a b : Nat) => a+b+1) 3 ⟨true,0,0⟩ := by decide

end ConsumerPresence
