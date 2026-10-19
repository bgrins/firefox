import URLDispatch
namespace URLObservers
open URLDispatch
abbrev Byte := CommentScan.Byte
inductive Status where
 | off
 | looking (names : List (List Byte))
 | seen
 deriving DecidableEq, Repr

def sameASCII (a b : List Byte) : Bool := a.map lower == b.map lower

def nativeSee (status : Status) (name : List Byte) : Status :=
 match status with
 | .looking names => if names.any (fun requested => sameASCII name requested) then .seen else status
 | _ => status

def referenceSee (status : Status) (name : List Byte) : Status :=
 match status with
 | .looking names => if name.map lower ∈ names.map (List.map lower) then .seen else status
 | _ => status

theorem any_membership (name : List Byte) (names : List (List Byte)) :
 names.any (fun requested => sameASCII name requested) = decide (name.map lower ∈ names.map (List.map lower)) := by
 apply Bool.eq_iff_iff.mpr
 simp only [List.any_eq_true,decide_eq_true_eq,List.mem_map,sameASCII,beq_iff_eq]
 constructor
 · rintro ⟨a,ha,he⟩; exact ⟨a,ha,he.symm⟩
 · rintro ⟨a,ha,he⟩; exact ⟨a,ha,he.symm⟩

theorem observer_reference (status : Status) (name : List Byte) :
 nativeSee status name=referenceSee status name := by
 cases status <;> simp [nativeSee,referenceSee,any_membership]

def resultStatus (xs : List Byte) (status : Status) : Status :=
 let token := URLDispatch.native xs false
 if token.kind==.function then nativeSee status token.payload else status

theorem only_function_event (xs : List Byte) (status : Status)
 (h : (URLDispatch.native xs false).kind≠.function) : resultStatus xs status=status := by
 simp [resultStatus,h]

theorem off_preserved (xs : List Byte) : resultStatus xs .off=.off := by
 unfold resultStatus
 dsimp only
 split <;> rfl

theorem seen_preserved (xs : List Byte) : resultStatus xs .seen=.seen := by
 unfold resultStatus
 dsimp only
 split <;> rfl

theorem url_not_an_event (name : List Byte) (count : Nat) (body : List Byte)
 (value : URLScan.Value) (h : URLLeading.native body 0=.token value) :
 (finish name count (40::body) true (fun b => URLLeading.native b 0) false).kind≠.function := by
 simp [finish,h]
 split <;> decide

theorem source_directives_framed (xs : List Byte) (s : CommentObservers.State)
 (urls : CommentDirectives.URLs) : (URLTrace.observed xs s urls).2.2=urls := rfl

end URLObservers
