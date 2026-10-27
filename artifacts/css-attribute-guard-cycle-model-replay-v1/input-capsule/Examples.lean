import GuardCycle

namespace AttributeGuard.Examples

def red : Expr := .literal [.atom 7]
def green : Expr := .literal [.atom 11]
def five : Expr := .literal [.number 5]
def selfFallback : Expr := .variable 0 red
def empty : Environment := ⟨fun _ => .invalid, fun _ => none, fun _ _ => true⟩

def missingSelf : Environment :=
  { empty with properties := fun n => if n = 0 then .raw 0 selfFallback else .invalid }

def missingMutual : Environment :=
  { empty with properties := fun n =>
    if n = 0 then .raw 0 (.variable 1 red)
    else if n = 1 then .raw 1 selfFallback else .variable 0 green }

def rawContent : Attribute := ⟨[100, 101], .raw 0 .invalid, none⟩

def nestedRaw : Environment :=
  { empty with
    properties := fun _ => .typed 0 red
    attributes := fun n => if n = 0 then some rawContent else none }

def presentRaw : Environment :=
  { nestedRaw with properties := fun _ => .raw 0 selfFallback }

def invalidPrimitive : Environment :=
  { nestedRaw with properties := fun _ => .primitive 0 selfFallback }

def validPrimitive : Environment :=
  { invalidPrimitive with attributes := fun _ => some ⟨[55], .variable 0 red, some [.number 5]⟩ }

def missingPrimitive : Environment :=
  { empty with properties := fun _ => .primitive 0 selfFallback }

def crossContext : Environment :=
  { nestedRaw with attributes := fun _ => some ⟨[100], selfFallback, none⟩ }

def typedSelf : Environment :=
  { nestedRaw with attributes := fun _ => some ⟨[100], .typed 0 .invalid, none⟩ }

def unusedVariable : Environment :=
  { empty with properties := fun n => if n = 0 then .variable 1 selfFallback else five }

def eagerFallback : Environment :=
  { presentRaw with properties := fun _ => .append selfFallback (.raw 0 .invalid) }

def missingAcyclic : Environment :=
  { empty with properties := fun _ => .raw 0 red }

def rejectedTyped : Environment :=
  { nestedRaw with accepts := fun _ _ => false }

def twoRawAttributes : Environment :=
  { nestedRaw with attributes := fun n =>
      if n = 0 then some ⟨[100], .typed 1 red, none⟩
      else some ⟨[101], .append (.raw 0 .invalid) (.raw 1 .invalid), none⟩ }

def typedMutual : Environment :=
  { nestedRaw with attributes := fun n =>
      if n = 0 then some ⟨[100], .typed 1 .invalid, none⟩
      else some ⟨[101], .typed 0 .invalid, none⟩ }

def unchecked : Policy := ⟨false, false⟩
def eagerRaw : Policy := ⟨true, true⟩

theorem missing_self_invalid :
    (property {} missingSelf 64 0).outcome = .invalid := by decide +kernel

theorem missing_mutual_invalid :
    (property {} missingMutual 64 0).outcome = .invalid ∧
    (property {} missingMutual 64 1).outcome = .invalid := by decide +kernel

theorem missing_mutual_marks_both :
    (property {} missingMutual 64 0).state.poisoned = [.property 1, .property 0] := by
  decide +kernel

theorem independent_consumer_can_fallback :
    (property {} missingMutual 64 2).outcome = .value [.atom 11] ∧
    Key.property 2 ∉ (property {} missingMutual 64 2).state.poisoned := by decide +kernel

theorem unchecked_guard_rescues_incorrectly :
    (property unchecked missingSelf 64 0).outcome = .value [.atom 7] := by decide +kernel

theorem raw_nested_literal :
    (property {} nestedRaw 64 0).outcome = .value [.string [100, 101]] ∧
    (property {} nestedRaw 64 0).state.poisoned = [] := by decide +kernel

theorem raw_nested_guard_trace :
    (property {} nestedRaw 64 0).state.guardTrace = [.property 0, .attribute 0] := by
  decide +kernel

theorem eager_raw_changes_result :
    (property eagerRaw nestedRaw 64 0).outcome = .value [.atom 7] := by decide +kernel

theorem present_raw_ignores_cyclic_fallback :
    (property {} presentRaw 64 0).outcome = .value [.string [100, 101]] ∧
    (property {} presentRaw 64 0).state.guardTrace = [.property 0] := by decide +kernel

theorem eager_fallback_poison :
    (property {} eagerFallback 64 0).outcome = .invalid := by decide +kernel

theorem invalid_primitive_self_invalid :
    (property {} invalidPrimitive 64 0).outcome = .invalid := by decide +kernel

theorem missing_primitive_self_invalid :
    (property {} missingPrimitive 64 0).outcome = .invalid := by decide +kernel

theorem valid_primitive_no_cycle :
    (property {} validPrimitive 64 0).outcome = .value [.number 5] ∧
    (property {} validPrimitive 64 0).state.guardTrace = [.property 0] := by decide +kernel

theorem cross_context_all_participants :
    (property {} crossContext 64 0).outcome = .invalid ∧
    (property {} crossContext 64 0).state.poisoned = [.attribute 0, .property 0] := by
  decide +kernel

theorem typed_cycle_outer_fallback :
    (property {} typedSelf 64 0).outcome = .value [.atom 7] ∧
    (property {} typedSelf 64 0).state.poisoned = [.attribute 0] := by decide +kernel

theorem unused_variable_fallback :
    (property {} unusedVariable 64 0).outcome = .value [.number 5] ∧
    (property {} unusedVariable 64 0).state.guardTrace = [.property 0, .property 1] := by
  decide +kernel

theorem missing_acyclic_fallback :
    (property {} missingAcyclic 64 0).outcome = .value [.atom 7] := by decide +kernel

theorem typed_parse_failure_fallback :
    (property {} rejectedTyped 64 0).outcome = .value [.atom 7] := by decide +kernel

theorem enclosing_nonparticipant_not_poisoned :
    (guarded {} (.property 0)
      ⟨[.property 1, .attribute 0, .property 0, .property 9], [], []⟩
      (fun state => ⟨.value [], state⟩)).state.poisoned =
        [.property 1, .attribute 0, .property 0] := by decide +kernel

theorem namespaces_of_guard_keys_are_distinct :
    Key.property 0 ≠ Key.attribute 0 := by decide +kernel

theorem zero_fuel_not_a_cycle :
    (property {} missingSelf 0 0).outcome = .exhausted ∧
    (property {} missingSelf 0 0).state.poisoned = [] := by decide +kernel

theorem two_raw_attributes_remain_literal :
    (property {} twoRawAttributes 64 0).outcome = .value [.string [100], .string [101]] ∧
    (property {} twoRawAttributes 64 0).state.guardTrace =
      [.property 0, .attribute 0, .attribute 1] := by decide +kernel

theorem typed_mutual_marks_only_attribute_cycle :
    (property {} typedMutual 64 0).outcome = .value [.atom 7] ∧
    (property {} typedMutual 64 0).state.poisoned = [.attribute 1, .attribute 0] := by
  decide +kernel

end AttributeGuard.Examples
