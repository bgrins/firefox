import Std
namespace QualifiedAttributes

structure Key where
 name : Nat
 ns : Nat
 deriving DecidableEq, Repr

def resolveKey (name : Nat) (ns : Option Nat) : Option Key :=
 ns.map fun ns => ⟨name,ns⟩

theorem key_equal_iff (left right : Key) :
 left = right ↔ left.name = right.name ∧ left.ns = right.ns := by
 cases left; cases right; simp only [Key.mk.injEq]

theorem different_namespaces_are_distinct (name left right : Nat) (different : left ≠ right) :
 (⟨name,left⟩ : Key) ≠ ⟨name,right⟩ := by
 intro same
 exact different (congrArg Key.ns same)

theorem unknown_namespace_has_no_key (name : Nat) : resolveKey name none = none := rfl

theorem known_null_namespace_has_key (name : Nat) :
 resolveKey name (some 0) = some ⟨name,0⟩ := rfl

abbrev AttributeMap (Value : Type) := Key → Option (Option Value)

def write (values : AttributeMap Value) (key : Key) (value : Option Value) : AttributeMap Value :=
 fun other => if other = key then some value else values other

def invalidate (values : AttributeMap Value) (key : Key) := write values key none

theorem write_at_key (values : AttributeMap Value) (key : Key) (value : Option Value) :
 write values key value key = some value := by simp [write]

theorem write_preserves_other (values : AttributeMap Value) (key other : Key)
 (different : other ≠ key) (value : Option Value) :
 write values key value other = values other := by simp [write,different]

theorem invalidation_preserves_other_namespace (values : AttributeMap Value)
 (name left right : Nat) (different : left ≠ right) :
 invalidate values ⟨name,left⟩ ⟨name,right⟩ = values ⟨name,right⟩ := by
 apply write_preserves_other
 exact Ne.symm (different_namespaces_are_distinct name left right different)

theorem writes_to_distinct_keys_commute (values : AttributeMap Value) (left right : Key)
 (different : left ≠ right) (leftValue rightValue : Option Value) :
 write (write values left leftValue) right rightValue =
 write (write values right rightValue) left leftValue := by
 funext key
 by_cases l : key = left
 · subst key
   simp [write,different]
 · by_cases r : key = right
   · subst key
     simp [write,l]
   · simp [write,l,r]

end QualifiedAttributes
