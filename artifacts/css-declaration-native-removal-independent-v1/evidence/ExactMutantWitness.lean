import PublicAPI
set_option linter.unusedSectionVars false
namespace ReviewMutation
open AllOrder PublicStorage PublicRemoval
variable {ι ν : Type} [DecidableEq ι]
local notation "E" => Entry ι ν

structure Result (ι ν : Type) where
  raw : Storage ι ν
  index : Nat
  len : Nat
  fault : Bool
  steps : Nat

def loop (selected : ι → Bool) (raw : Storage ι ν) (index len : Nat) : Result ι ν :=
  if _h : index < len then
    match raw.declarations[index]? with
    | none => ⟨raw,index,len,true,0⟩
    | some old =>
      let next := if selected old.1 then
        loop selected (rawDelete raw old.1 index) (index+1) (len-1)
      else loop selected raw (index+1) len
      {next with steps := next.steps+1}
  else ⟨raw,index,len,false,0⟩
termination_by len-index
decreasing_by all_goals omega


def demo : Storage Nat Nat := ⟨[(0,7),(1,8),(2,9)],[false,true,false],fun id => decide (id < 3)⟩
def select (id : Nat) : Bool := decide (id < 2)
example : (loop select demo 0 3).raw.declarations = [(1,8),(2,9)] ∧
    (loop select demo 0 3).fault = false := by simp [loop,demo,select,rawDelete]
end ReviewMutation
