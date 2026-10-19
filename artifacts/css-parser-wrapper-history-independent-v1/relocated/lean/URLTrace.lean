import URLLeading
import URLWhitespace
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace URLTrace
open URLScan
abbrev Byte := CommentScan.Byte
structure Trace where
 value : Value
 consumed : List Byte
 closed : Bool
 deriving DecidableEq, Repr

def add (output consumed : List Byte) (r : Trace) : Trace :=
 ⟨extend output consumed.length r.value,consumed++r.consumed,r.closed⟩

def bad (xs : List Byte) : Trace :=
 let r := BadURL.native xs
 ⟨⟨.bad,[],r.count⟩,xs.take r.count,r.closed⟩

def ending : List Byte → Trace
 | [] => ⟨⟨.url,[],0⟩,[],false⟩
 | b::bs => if b == 41 then ⟨⟨.url,[],1⟩,[b],true⟩
   else if nativeWhitespace b then add [] [b] (ending bs)
   else bad (b::bs)

def run : List Byte → Trace
 | [] => ⟨⟨.url,[],0⟩,[],false⟩
 | b::bs => match nativeClass b with
   | .close => ⟨⟨.url,[],1⟩,[b],true⟩
   | .invalid => add [] [b] (bad bs)
   | .space => ending (b::bs)
   | .nul => add (Escape.encode 65533) [b] (run bs)
   | .copy => add [b] [b] (run bs)
   | .escape => if newline bs then add [] [b] (bad bs)
     else let e := Escape.native bs
          add e.output (b::bs.take e.count) (run (bs.drop e.count))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

theorem ending_value (xs : List Byte) : (ending xs).value=endNative xs := by
 induction xs with
 | nil => rfl
 | cons b bs ih =>
   simp only [ending,endNative]
   split
   · rfl
   · split <;> simp [add,ih,bad,badNative]

theorem ending_trace (xs : List Byte) : (ending xs).consumed=xs.take (ending xs).value.count := by
 induction xs with
 | nil => rfl
 | cons b bs ih =>
   simp only [ending]
   split
   · rfl
   · split
     · simpa [add,extend,Nat.add_comm 1] using congrArg (List.cons b) ih
     · rfl

theorem value_reference (xs : List Byte) : (run xs).value=reference xs := by
 induction xs using run.induct with
 | case1 => simp [run,reference]
 | case2 b bs h => simp [run,reference,← class_equivalence,h]
 | case3 b bs h => simp [run,reference,← class_equivalence,h,add,bad,badReference,BadURL.native_reference]
 | case4 b bs h => simp [run,reference,← class_equivalence,h,ending_value,end_equivalence]
 | case5 b bs h ih => simp [run,reference,← class_equivalence,h,add,ih]
 | case6 b bs h ih => simp [run,reference,← class_equivalence,h,add,ih]
 | case7 b bs h hn => simp [run,reference,← class_equivalence,h,hn,add,bad,badReference,BadURL.native_reference]
 | case8 b bs h hn e ih =>
   dsimp [e] at ih
   have bound := Escape.consumption_bound bs
   simp [run,reference,← class_equivalence,h,hn,add,ih,← Escape.native_reference,List.length_take,Nat.min_eq_left bound,Nat.add_comm 1]

theorem trace_exact (xs : List Byte) : (run xs).consumed=xs.take (run xs).value.count := by
 induction xs using run.induct with
 | case1 => simp [run,reference]
 | case2 b bs h => simp [run,h]
 | case3 b bs h => simp [run,h,add,bad,extend,Nat.add_comm 1]
 | case4 b bs h => simpa [run,h] using ending_trace (b::bs)
 | case5 b bs h ih => simpa [run,h,add,extend,Nat.add_comm 1] using congrArg (List.cons b) ih
 | case6 b bs h ih => simpa [run,h,add,extend,Nat.add_comm 1] using congrArg (List.cons b) ih
 | case7 b bs h hn => simp [run,h,hn,add,bad,extend,Nat.add_comm 1]
 | case8 b bs h hn e ih =>
   dsimp [e] at ih
   have bound := Escape.consumption_bound bs
   simp [run,h,hn,add,extend,ih,List.length_take,Nat.min_eq_left bound,Nat.add_assoc,Nat.add_comm 1,StringTrace.take_split _ _ _ bound]
   rw [← Nat.add_assoc]
   rfl

def rawPayload (r : Trace) : List Byte :=
 r.consumed.take (r.consumed.length-if r.closed then 1 else 0)

def observed (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) :
 Value × CommentObservers.State × CommentDirectives.URLs :=
 let r := run xs
 (r.value,CommentObservers.nativeObserve r.consumed s,urls)

theorem metadata (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) :
 observed xs s urls = (reference xs,CommentObservers.referenceObserve (xs.take (reference xs).count) s,urls) := by
 simp [observed,trace_exact,value_reference,CommentObservers.native_reference]

theorem source_endpoint (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) :
 (observed xs s urls).2.1.offset=s.offset+(reference xs).count := by
 simp [observed,trace_exact,value_reference,CommentObservers.consumed_offset,List.length_take,Nat.min_eq_left (reference_bound xs)]

theorem raw_span_bound (xs : List Byte) : (rawPayload (run xs)).length ≤ xs.length := by
 have bound := reference_bound xs
 simp only [rawPayload,List.length_take,trace_exact,value_reference,List.length_take]
 omega

end URLTrace
