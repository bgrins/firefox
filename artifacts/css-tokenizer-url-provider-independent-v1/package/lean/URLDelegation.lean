import StringTrace
import URLScan
set_option maxRecDepth 4096
set_option maxHeartbeats 5000000
namespace URLDelegation
open CommentObservers
abbrev Byte := CommentScan.Byte

structure Split where
 pre : List Byte
 last : List Byte
 deriving DecidableEq, Repr

def splitLast (xs : List Byte) : Split :=
 match xs.reverse with
 | [] => ⟨[],[]⟩
 | b::bs =>
   if b == 10 && bs.head? == some 13 then ⟨bs.tail.reverse,[13,10]⟩
   else ⟨bs.reverse,[b]⟩

def NoSplit (a b : List Byte) : Prop := a.getLast? ≠ some 13 ∨ b.head? ≠ some 10

theorem split_exact (xs : List Byte) : (splitLast xs).pre ++ (splitLast xs).last = xs := by
 have eq : xs.reverse.reverse = xs := List.reverse_reverse xs
 cases hr : xs.reverse with
 | nil => simp [splitLast,hr] at ⊢ eq; exact eq
 | cons b bs =>
   cases bs with
   | nil => simpa [splitLast,hr] using eq
   | cons c cs =>
     by_cases pair : b = 10 ∧ c = 13
     · obtain ⟨rfl,rfl⟩ := pair
       simpa [splitLast,hr,List.reverse_cons,List.append_assoc] using eq
     · have hp : (b == 10 && (some c == some 13)) = false := by simpa using pair
       simpa [splitLast,hr,pair,List.reverse_cons,List.append_assoc] using eq

theorem split_safe (xs : List Byte) : NoSplit (splitLast xs).pre (splitLast xs).last := by
 cases hr : xs.reverse with
 | nil => simp [splitLast,hr,NoSplit]
 | cons b bs =>
   cases bs with
   | nil => simp [splitLast,hr,NoSplit]
   | cons c cs =>
     by_cases pair : b = 10 ∧ c = 13
     · obtain ⟨rfl,rfl⟩ := pair
       simp [splitLast,hr,NoSplit]
     · have hp : (b == 10 && (some c == some 13)) = false := by simpa using pair
       simp [splitLast,hr,pair,NoSplit,List.reverse_cons]
       by_cases hb : b=10
       · left; intro hc; exact pair ⟨hb,hc⟩
       · exact Or.inr hb

theorem afterCR (xs : List Byte) (r : RefState) :
 (xs.foldl referenceStep r).afterCR = (xs.getLast?.map (fun b => b == 13)).getD r.afterCR := by
 induction xs generalizing r with
 | nil => simp
 | cons b bs ih =>
   rw [List.foldl_cons,ih]
   cases bs with
   | nil =>
     simp only [List.getLast?_singleton,Option.map_some,Option.getD_some]
     unfold referenceStep
     split
     · simp_all
     · split
       · split <;> simp_all
       · split <;> simp_all
   | cons c cs =>
     cases hl : (c::cs).getLast? with
     | none => simp at hl
     | some v => simp [hl]

theorem observe_append (a b : List Byte) (s : State) (safe : NoSplit a b) :
 nativeObserve (a++b) s = nativeObserve b (nativeObserve a s) := by
 rw [native_reference,native_reference,native_reference]
 simp only [referenceObserve,List.foldl_append]
 let r := a.foldl referenceStep ⟨s,false⟩
 change (b.foldl referenceStep r).state = (b.foldl referenceStep ⟨r.state,false⟩).state
 cases hr : r.afterCR
 · have he : r = ⟨r.state,false⟩ := congrArg (RefState.mk r.state) hr
   rw [he]
 · have last : a.getLast? = some 13 := by
     have hh := afterCR a ⟨s,false⟩
     change r.afterCR = _ at hh
     rw [hr] at hh
     cases ha : a.getLast? with
     | none => simp [ha] at hh
     | some v => simpa [ha] using hh.symm
   have head : b.head? ≠ some 10 := by
     rcases safe with h | h
     · exact False.elim (h last)
     · exact h
   have he : r = ⟨r.state,true⟩ := congrArg (RefState.mk r.state) hr
   rw [he]
   exact irrelevant_pending b r.state head

theorem combined_whitespace (ws : List Byte) (s : State) :
 nativeObserve (splitLast ws).last (nativeObserve (splitLast ws).pre s) = nativeObserve ws s := by
 rw [← observe_append _ _ _ (split_safe ws),split_exact]

structure Observation where
 value : StringTransitions.Value
 state : State
 urls : CommentDirectives.URLs
 deriving DecidableEq, Repr

def nativeCombined (single : Bool) (ws body : List Byte) (s : State)
 (urls : CommentDirectives.URLs) : Observation :=
 let afterWhitespace := nativeObserve ws s
 let afterQuote := ordinary (if single then 39 else 34) afterWhitespace
 let result := StringTrace.nativeObserved single body afterQuote urls
 ⟨result.value,result.state,result.urls⟩

def specCombined (single : Bool) (ws body : List Byte) (s : State)
 (urls : CommentDirectives.URLs) : Observation :=
 let functionState := nativeObserve (splitLast ws).pre s
 let afterWhitespace := nativeObserve (splitLast ws).last functionState
 let afterQuote := ordinary (if single then 39 else 34) afterWhitespace
 let result := StringTrace.referenceObserved single body afterQuote urls
 ⟨result.value,result.state,result.urls⟩

theorem combined_string (single : Bool) (ws body : List Byte) (s : State)
 (urls : CommentDirectives.URLs) :
 nativeCombined single ws body s urls = specCombined single ws body s urls := by
 simp [nativeCombined,specCombined,combined_whitespace,StringTrace.observer_reference]

theorem function_cursor_counterexample :
 nativeObserve (splitLast [32,32]).pre ⟨4,0,5⟩ ≠ (⟨4,0,5⟩:State) := by
 simp [splitLast,nativeObserve,isNewline,ordinary,nativeWidth]

theorem crlf_cut : splitLast [32,13,10] = ⟨[32],[13,10]⟩ := by decide

theorem newline_observation :
 nativeObserve [13,10,13,12,32] ⟨4,0,5⟩ = ⟨9,3,2⟩ := by
 simp [nativeObserve,isNewline,newline,ordinary,nativeWidth]
 decide

end URLDelegation
