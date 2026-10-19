import CommentScan
namespace Mutation
abbrev Byte := CommentScan.Byte
structure End where
  count : Nat
  closed : Bool
  deriving DecidableEq, Repr

def add (n : Nat) (r : End) : End := ⟨n+r.count,r.closed⟩

def native : List Byte → End
  | [] => ⟨0,false⟩
  | b::bs =>
    if b == 41 then ⟨1,true⟩
    else if b == 92 && (bs.head? == some 92) then
      add 2 (native bs.tail)
    else add 1 (native bs)
termination_by xs => xs.length

-- The reference labels each source byte with the parity of its preceding slash run.
def labels : Bool → List Byte → List Bool
  | _, [] => []
  | escaped, b::bs => (b == 41 && !escaped) :: labels (b == 92 && !escaped) bs

def reference (xs : List Byte) : End :=
  let position := (labels false xs).findIdx id
  ⟨if position < xs.length then position+1 else position, position < xs.length⟩

def scan : Bool → List Byte → End
  | _, [] => ⟨0,false⟩
  | escaped, b::bs =>
    if b == 41 && !escaped then ⟨1,true⟩
    else add 1 (scan (b == 92 && !escaped) bs)


example : native [92,41,41] ≠ reference [92,41,41] := by simp [native,reference,labels,add,List.findIdx_cons]
end Mutation
