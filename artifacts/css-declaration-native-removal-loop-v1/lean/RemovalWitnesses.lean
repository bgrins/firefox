import NativeRemovalAPI
namespace RemovalWitnesses
open AllOrder PublicStorage NativeRemoval

def raw : Storage Nat Nat := ⟨[(0,7),(1,8),(2,9)],[false,true,false],fun id => decide (id < 3)⟩
def selected (id : Nat) : Bool := decide (id < 2)

def altered (advanceDelete decrementLen : Bool) : Nat → Storage Nat Nat → Nat → Nat → Result Nat Nat
  | 0, raw, i, len => ⟨raw,i,len,true,0⟩
  | fuel+1, raw, i, len =>
    if i < len then
      match raw.declarations[i]? with
      | none => ⟨raw,i,len,true,0⟩
      | some old =>
        let next := if selected old.1 then
          altered advanceDelete decrementLen fuel (rawDelete raw old.1 i)
            (if advanceDelete then i+1 else i) (if decrementLen then len-1 else len)
        else altered advanceDelete decrementLen fuel raw (i+1) len
        {next with steps := next.steps+1}
    else ⟨raw,i,len,false,0⟩

theorem adjacent_removal_control :
    (loop selected raw 0 3).raw.declarations = [(2,9)] ∧
    (loop selected raw 0 3).raw.importance = [false] ∧
    (loop selected raw 0 3).fault = false ∧ (loop selected raw 0 3).steps = 3 := by simp [loop,raw,selected,rawDelete]

theorem advance_after_delete_counterexample :
    (altered true true 5 raw 0 3).raw.declarations = [(1,8),(2,9)] ∧
    (altered true true 5 raw 0 3).fault = false ∧
    (altered true true 5 raw 0 3).raw.declarations ≠ (loop selected raw 0 3).raw.declarations := by simp [loop,altered,raw,selected,rawDelete]

theorem retained_length_counterexample :
    (altered false false 5 raw 0 3).fault = true ∧
    (altered false false 5 raw 0 3).index = 1 ∧
    (altered false false 5 raw 0 3).len = 3 ∧
    (altered false false 5 raw 0 3).raw.declarations.length = 1 := by simp [altered,raw,selected,rawDelete]

theorem no_match_control :
    (loop (fun _ => false) raw 0 3).raw.declarations = raw.declarations ∧
    (loop (fun _ => false) raw 0 3).index = 3 ∧
    (loop (fun _ => false) raw 0 3).fault = false := by simp [loop,raw]

theorem exhausted_index_control :
    (loop selected raw 3 3).raw.declarations = raw.declarations ∧
    (loop selected raw 3 3).steps = 0 ∧ (loop selected raw 3 3).fault = false := by simp [loop,raw]

end RemovalWitnesses
