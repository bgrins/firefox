import StringContracts
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace StringTrace
open StringTransitions
abbrev Byte := CommentScan.Byte
structure Trace where
  value : Value
  consumed : List Byte
  deriving DecidableEq, Repr

def add (output consumed : List Byte) (r : Trace) : Trace :=
  ⟨extend output consumed.length r.value,consumed++r.consumed⟩

def run (single : Bool) : List Byte → Trace
  | [] => ⟨⟨[],0,.eof⟩,[]⟩
  | b::bs =>
    match nativeClass single b with
    | .close => ⟨⟨[],1,.closed⟩,[b]⟩
    | .bad => ⟨⟨[],0,.bad⟩,[]⟩
    | .nul => add (Escape.encode 65533) [b] (run single bs)
    | .copy => add [b] [b] (run single bs)
    | .escape =>
      let e := nativeEscape bs
      add e.output (b::bs.take e.count) (run single (bs.drop e.count))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

theorem value_reference (single : Bool) (xs : List Byte) : (run single xs).value = reference single xs := by
  induction xs using run.induct single with
  | case1 => simp [run,reference]
  | case2 b bs h => simp [run,h,reference,← class_equivalence,h]
  | case3 b bs h => simp [run,h,reference,← class_equivalence,h]
  | case4 b bs h ih => simp [run,h,reference,← class_equivalence,h,add,ih]
  | case5 b bs h ih => simp [run,h,reference,← class_equivalence,h,add,ih]
  | case6 b bs h e ih =>
    dsimp [e] at ih
    have hb := escape_bound bs
    simp [run,h,reference,← class_equivalence,h,← escape_equivalence,add,ih,List.length_take,Nat.min_eq_left hb,Nat.add_comm 1]

theorem consumed_bound (single : Bool) (xs : List Byte) : (run single xs).value.count ≤ xs.length := by
  rw [value_reference]
  exact reference_bound single xs

theorem take_split (xs : List Byte) (n m : Nat) (h : n ≤ xs.length) :
    xs.take n ++ (xs.drop n).take m = xs.take (n+m) := by
  rw [← List.take_add]

theorem trace_exact (single : Bool) (xs : List Byte) :
    (run single xs).consumed = xs.take (run single xs).value.count := by
  induction xs using run.induct single with
  | case1 => simp [run]
  | case2 b bs h => simp [run,h]
  | case3 b bs h => simp [run,h]
  | case4 b bs h ih => simpa [run,h,add,extend,Nat.add_comm 1] using congrArg (List.cons b) ih
  | case5 b bs h ih => simpa [run,h,add,extend,Nat.add_comm 1] using congrArg (List.cons b) ih
  | case6 b bs h e ih =>
    dsimp [e] at ih
    have hb := escape_bound bs
    simp [run,h,add,extend,ih,List.length_take,Nat.min_eq_left hb,Nat.add_assoc,Nat.add_comm 1,take_split _ _ _ hb]
    rw [← Nat.add_assoc]
    rfl

structure Observed where
  value : Value
  state : CommentObservers.State
  urls : CommentDirectives.URLs
  deriving DecidableEq, Repr

def nativeObserved (single : Bool) (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) : Observed :=
  let r := run single xs
  ⟨r.value,CommentObservers.nativeObserve r.consumed s,urls⟩

def referenceObserved (single : Bool) (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) : Observed :=
  let r := reference single xs
  ⟨r,CommentObservers.referenceObserve (xs.take r.count) s,urls⟩

theorem observer_reference (single : Bool) (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) :
    nativeObserved single xs s urls = referenceObserved single xs s urls := by
  simp [nativeObserved,referenceObserved,trace_exact,value_reference,CommentObservers.native_reference]

theorem endpoint (single : Bool) (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) :
    (nativeObserved single xs s urls).state.offset = s.offset+(reference single xs).count := by
  simp [nativeObserved,trace_exact,CommentObservers.consumed_offset,List.length_take,value_reference,Nat.min_eq_left (reference_bound single xs)]

theorem borrowed_observation (single : Bool) (xs : List Byte) :
    (borrowed single xs []).value = (run single xs).value := by
  simp [borrowed_reference,value_reference,extend]

theorem urls_unchanged (single : Bool) (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) :
    (nativeObserved single xs s urls).urls = urls := rfl

theorem location_capacity (single : Bool) (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) (limit : Nat)
    (hp : s.offset+xs.length < limit) (hl : s.line+xs.length < 1073741824)
    (hc : s.column+2*xs.length < 4294967296) :
    (nativeObserved single xs s urls).state.offset < limit ∧
    (nativeObserved single xs s urls).state.line < 1073741824 ∧
    (nativeObserved single xs s urls).state.column < 4294967296 := by
  have hb : (run single xs).consumed.length ≤ xs.length := by rw [trace_exact,List.length_take]; exact Nat.min_le_right _ _
  apply CommentNativeBounds.native_capacity
  all_goals omega
end StringTrace
