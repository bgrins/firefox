import CommentObservers
import CommentDirectives
set_option maxRecDepth 4096
set_option maxHeartbeats 3000000
namespace CommentExecution
open CommentScan CommentObservers CommentDirectives
structure Output where
  part : Result
  state : State
  deriving DecidableEq, Repr

def prepend (bytes : List Byte) (n : Nat) (r : Output) : Output :=
  ⟨⟨bytes++r.part.body,r.part.count+n,r.part.closed⟩,r.state⟩

def run : List Byte → State → Output
  | [], s => ⟨⟨[],0,false⟩,s⟩
  | b::bs, s =>
    if stop b bs then ⟨⟨[],2,true⟩,advance 2 s⟩
    else if isNewline b then
      if b == 13 && bs.head? == some 10 then prepend [b,10] 2 (run bs.tail (newline 2 s))
      else prepend [b] 1 (run bs (newline 1 s))
    else prepend [b] 1 (run bs (ordinary b s))
termination_by xs => xs.length

theorem run_scan (xs : List Byte) (s : State) : (run xs s).part = scan xs := by
  induction xs, s using run.induct with
  | case1 s => simp [run,scan]
  | case2 b bs s h => simp [run,h,scan]
  | case3 b bs s h hn hc ih =>
    cases bs with
    | nil => simp at hc
    | cons c cs =>
      simp at hc
      obtain ⟨rfl,rfl⟩ := hc
      simp only [List.tail_cons] at ih
      simp [run,scan,stop,isNewline,prepend,ih,Nat.add_assoc]
  | case4 b bs s h hn hc ih => simp [run,h,hn,hc,scan,prepend,ih]
  | case5 b bs s h hn ih => simp [run,h,hn,scan,prepend,ih]

theorem head_take_not (xs : List Byte) (n : Nat) (b : Byte) (h : xs.head? ≠ some b) :
    (xs.take n).head? ≠ some b := by
  cases xs <;> cases n <;> simpa using h

theorem run_observer (xs : List Byte) (s : State) :
    (run xs s).state = nativeObserve (xs.take (scan xs).count) s := by
  induction xs, s using run.induct with
  | case1 s => simp [run,scan,nativeObserve]
  | case2 b bs s h =>
    obtain ⟨tail,rfl,rfl⟩ := stop_tail b bs h
    have h42 : nativeWidth (42 : Byte) = 1 := by decide
    have h47 : nativeWidth (47 : Byte) = 1 := by decide
    simp [run,stop,scan,nativeObserve,isNewline,ordinary,h42,h47,advance,Nat.add_assoc]
  | case3 b bs s h hn hc ih =>
    cases bs with
    | nil => simp at hc
    | cons c cs =>
      simp at hc
      obtain ⟨rfl,rfl⟩ := hc
      simp only [List.tail_cons] at ih
      simpa [run,scan,stop,isNewline,prepend,nativeObserve,Nat.add_assoc] using ih
  | case4 b bs s h hn hc ih =>
    simp only [isNewline,Bool.or_eq_true,beq_iff_eq] at hn
    rcases hn with (rfl | rfl) | rfl
    · simpa [run,scan,stop,isNewline,prepend,nativeObserve] using ih
    · simpa [run,scan,stop,isNewline,prepend,nativeObserve] using ih
    · have ht : bs.head? ≠ some 10 := by simpa using hc
      have htake := head_take_not bs (scan bs).count 10 ht
      simpa [run,scan,stop,isNewline,prepend,nativeObserve,ht,htake] using ih
  | case5 b bs s h hn ih =>
    simpa [run,scan,h,hn,prepend,nativeObserve] using ih

def reference (xs : List Byte) (s : State) : Output :=
  let part := CommentScan.reference xs
  ⟨part,referenceObserve (xs.take part.count) s⟩

theorem execution_reference (xs : List Byte) (s : State) : run xs s = reference xs s := by
  change Output.mk (run xs s).part (run xs s).state = reference xs s
  simp only [reference,run_scan,run_observer,native_reference,scan_reference]

structure Complete where
  output : Output
  urls : URLs
  deriving DecidableEq, Repr

def nativeBody (xs : List Byte) (s : State) (urls : URLs) : Complete :=
  let r := run xs s
  ⟨r,nativeUpdate r.part.body urls⟩

def referenceBody (xs : List Byte) (s : State) (urls : URLs) : Complete :=
  let r := reference xs s
  ⟨r,referenceUpdate r.part.body urls⟩

theorem body_reference (xs : List Byte) (s : State) (urls : URLs) :
    nativeBody xs s urls = referenceBody xs s urls := by
  simp [nativeBody,referenceBody,execution_reference,update_reference]

def nativeRaw (input : List Byte) (s : State) (urls : URLs) : Option Complete :=
  match input with
  | 47::42::tail => some (nativeBody tail (advance 2 s) urls)
  | _ => none

def referenceRaw (input : List Byte) (s : State) (urls : URLs) : Option Complete :=
  (consumeLiteral [47,42] input).map (fun tail => referenceBody tail (advance 2 s) urls)

theorem raw_reference (input : List Byte) (s : State) (urls : URLs) :
    nativeRaw input s urls = referenceRaw input s urls := by
  cases input with
  | nil => rfl
  | cons a rest =>
    cases rest with
    | nil => simp [nativeRaw,referenceRaw,consumeLiteral]
    | cons b tail =>
      have ea : ((47 : Byte) = a) ↔ a = 47 := eq_comm
      have eb : ((42 : Byte) = b) ↔ b = 42 := eq_comm
      by_cases ha : a = 47 <;> by_cases hb : b = 42 <;>
        simp_all [nativeRaw,referenceRaw,consumeLiteral,body_reference,ea,eb]
end CommentExecution
