import GraphIdentity
namespace NativeAttributeIndices
open QualifiedAttributes

structure IndexMaps where
 custom : Nat → Option Nat
 attr : Nat → Nat → Option Nat
 nonCustom : Nat → Option Nat

def lookup (maps : IndexMaps) : Node → Option Nat
 | .custom name => maps.custom name
 | .attr key => maps.attr key.ns key.name
 | .nonCustom property => maps.nonCustom property

def insert (maps : IndexMaps) (node : Node) (index : Nat) : IndexMaps :=
 match node with
 | .custom name => { maps with custom := fun other => if other = name then some index else maps.custom other }
 | .attr key => { maps with attr := fun ns name =>
     if ns = key.ns ∧ name = key.name then some index else maps.attr ns name }
 | .nonCustom property => { maps with nonCustom := fun other => if other = property then some index else maps.nonCustom other }

theorem index_bucket_insert_is_tagged_write (maps : IndexMaps) (node other : Node) (index : Nat) :
 lookup (insert maps node index) other = if other = node then some index else lookup maps other := by
 cases node <;> cases other <;> simp [insert,lookup,key_equal_iff,and_comm]

theorem existing_index_preserved_for_other_namespace (maps : IndexMaps)
 (name left right index : Nat) (different : left ≠ right) :
 lookup (insert maps (.attr ⟨name,left⟩) index) (.attr ⟨name,right⟩) =
 lookup maps (.attr ⟨name,right⟩) := by
 rw [index_bucket_insert_is_tagged_write]
 simp [Ne.symm (different_namespaces_are_distinct name left right different)]

def emptyMaps : IndexMaps := ⟨fun _ => none,fun _ _ => none,fun _ => none⟩

end NativeAttributeIndices
