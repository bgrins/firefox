import CursorHistory

namespace MapIterator

def shadowExample : Chain Nat Nat := [[(0,some 20)],[(0,some 10),(1,some 30)]]
def tombstoneExample : Chain Nat Nat := [[(0,none)],[(0,some 10),(1,some 30)]]
def deepExample : Chain Nat Nat := [[(0,some 40)],[],[(0,some 10),(1,some 30)]]

def originalEnumeration (c : Chain Nat Nat) : Node Nat Nat := c.flatten

theorem original_duplicate :
    originalEnumeration shadowExample = [(0,some 20),(0,some 10),(1,some 30)] := by simp [originalEnumeration, shadowExample]

theorem original_not_reference : originalEnumeration shadowExample ≠ reference shadowExample := by simp [originalEnumeration, shadowExample, reference, owns]

theorem corrected_shadow : drain (start shadowExample) = [(0,some 20),(1,some 30)] := by simp [shadowExample, drain, start, walk, shadow, owns]

theorem corrected_deep : drain (start deepExample) = [(0,some 40),(1,some 30)] := by simp [deepExample, drain, start, walk, shadow, owns]

theorem corrected_tombstone : drain (start tombstoneExample) = [(0,none),(1,some 30)] := by simp [tombstoneExample, drain, start, walk, shadow, owns]

theorem tombstone_no_resurrection : nativeGet tombstoneExample 0 = none ∧
    lookupOwner tombstoneExample 0 = some none := by simp [tombstoneExample, nativeGet, lookupOwner, nearest, ownFind]

theorem live_index_tombstone : getIndex tombstoneExample 1 0 = some (1,some 30) := by simp [tombstoneExample, getIndex, drain, start, walk, live, shadow, owns]

theorem raw_index_is_different : getIndexRaw tombstoneExample 2 0 = some (0,none) := by simp [tombstoneExample, getIndexRaw, drain, start, walk, shadow, owns]

theorem stored_count_is_independent :
    getIndex shadowExample 1 1 = none ∧ (live (reference shadowExample))[1]? = some (1,some 30) := by simp [shadowExample, getIndex, reference, live, owns]

theorem inflated_count_does_not_create_entry : getIndex shadowExample 3 2 = none := by simp [shadowExample, getIndex, drain, start, walk, live, shadow, owns]

theorem empty_nodes_terminate : drain (start ([[],[],[]] : Chain Nat Nat)) = [] := by simp [drain, start, walk]

theorem invalid_own_keys_not_claimed :
    ¬Valid ([[(0,some 1),(0,some 2)]] : Chain Nat Nat) := by simp [Valid, Unique]

end MapIterator
