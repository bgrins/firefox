import GraphIdentity
namespace QualifiedAttributes

inductive ApplyTarget where
 | custom (name : Nat)
 | attr (key : Key)
 deriving DecidableEq

def applyArguments : ApplyTarget → Nat × Option Nat
 | .custom name => (name,none)
 | .attr key => (key.name,some key.ns)

def fromApplyArguments (arguments : Nat × Option Nat) : ApplyTarget :=
 match arguments.2 with
 | none => .custom arguments.1
 | some ns => .attr ⟨arguments.1,ns⟩

theorem apply_arguments_roundtrip (target : ApplyTarget) : fromApplyArguments (applyArguments target) = target := by
 cases target with
 | custom name => rfl
 | attr key => cases key; rfl

theorem apply_arguments_are_injective : Function.Injective applyArguments := by
 intro left right same
 have decoded := congrArg fromApplyArguments same
 simpa only [apply_arguments_roundtrip] using decoded

theorem null_attribute_is_not_custom_apply (name : Nat) :
 applyArguments (.attr ⟨name,0⟩) ≠ applyArguments (.custom name) := by simp [applyArguments]

inductive AttributePlan where
 | primary (key : Key)
 | usedFallback (references : List Node)
 deriving DecidableEq

def planAttribute (name : Nat) (resolvedNamespace : Option Nat) (fallback : List Node) : AttributePlan :=
 match resolveKey name resolvedNamespace with
 | some key => .primary key
 | none => .usedFallback fallback

theorem unknown_namespace_uses_fallback (name : Nat) (fallback : List Node) :
 planAttribute name none fallback = .usedFallback fallback := rfl

theorem unknown_namespace_creates_no_primary (name : Nat) (fallback : List Node) (key : Key) :
 planAttribute name none fallback ≠ .primary key := by simp [planAttribute,resolveKey]

theorem known_namespace_selects_exact_primary (name ns : Nat) (fallback : List Node) :
 planAttribute name (some ns) fallback = .primary ⟨name,ns⟩ := rfl

theorem resolved_prefix_aliases_have_identical_plan (name ns : Nat)
 (leftPrefix rightPrefix : Nat) (resolvePrefix : Nat → Option Nat)
 (left : resolvePrefix leftPrefix = some ns) (right : resolvePrefix rightPrefix = some ns)
 (fallback : List Node) :
 planAttribute name (resolvePrefix leftPrefix) fallback =
 planAttribute name (resolvePrefix rightPrefix) fallback := by rw [left,right]

end QualifiedAttributes
