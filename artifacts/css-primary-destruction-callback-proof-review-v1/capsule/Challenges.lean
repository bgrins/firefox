import Witnesses

namespace IndependentReview
open Destruction

def nonemptyHasBuffer (line : LinePayload) : Bool :=
  line.frames.isEmpty || line.buffer.isSome

theorem sample_has_nonempty_unbuffered_items :
    nonemptyHasBuffer ⟨none, [0]⟩ = false ∧
    (.shared 50 (some 60) [⟨some 70, [0, 2]⟩, ⟨none, [0]⟩, ⟨some 80, []⟩]) ∈
      sampleTable.entries := by decide

def missingBufferTable : PropertyTable :=
  ⟨some 90, [.shared 50 (some 60) [⟨none, [0]⟩]]⟩

theorem incomplete_buffer_encoding_is_admitted :
    (removeAll (write sample 0 (some (.frame 1 true missingBufferTable))) 0).isSome = true := by
  decide

def firstTable : PropertyTable := ⟨some 90, [.itemCache 30]⟩
def otherTable : PropertyTable := ⟨some 91, [.itemCache 30]⟩
def crossOwner : Heap :=
  write (write (write sample 0 (some (.frame 1 true firstTable)))
    2 (some (.frame 3 true otherTable))) 91 (some (.allocation .propertiesBuffer))

theorem other_owner_survives_with_freed_shared_cache :
    (removeAll crossOwner 0).map (fun h =>
      (h 2, bitRead h 2, pointerRead h 2, h 30, h 91)) =
    some (some (.frame 3 true otherTable), some true, some true,
      none, some (.allocation .propertiesBuffer)) := by decide

theorem second_owner_cleanup_rejects_freed_shared_cache :
    ((removeAll crossOwner 0).bind (fun h => removeAll h 2)).isNone = true := by
  decide

#print axioms sample_has_nonempty_unbuffered_items
#print axioms incomplete_buffer_encoding_is_admitted
#print axioms other_owner_survives_with_freed_shared_cache
#print axioms second_owner_cleanup_rejects_freed_shared_cache
end IndependentReview
