import URLDelegation
set_option maxRecDepth 4096
set_option maxHeartbeats 5000000
namespace URLWhitespace
open CommentObservers
abbrev Byte := CommentScan.Byte

structure Stats where
 lines : Nat
 last : Nat
 deriving DecidableEq, Repr

def marks (b : Byte) (bs : List Byte) : Bool :=
 b == 10 || b == 12 || (b == 13)

def scan : List Byte → Nat → Stats → Stats
 | [], _, s => s
 | b::bs, index, s =>
   scan bs (index+1) (if marks b bs then ⟨s.lines+1,index⟩ else s)

def summary : List Byte → Stats
 | [] => ⟨0,0⟩
 | b::bs =>
   let r := summary bs
   ⟨r.lines + if marks b bs then 1 else 0,
    if r.lines>0 then r.last+1 else 0⟩

theorem scan_summary (xs : List Byte) (index : Nat) (s : Stats) :
 scan xs index s =
 let r := summary xs
 ⟨s.lines+r.lines,if r.lines>0 then index+r.last else s.last⟩ := by
 induction xs generalizing index s with
 | nil => simp [scan,summary]
 | cons b bs ih =>
   simp only [scan,ih,summary]
   by_cases hm : marks b bs=true <;> by_cases hl : (summary bs).lines>0
   all_goals simp_all [Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
   all_goals omega

theorem last_bound (xs : List Byte) (h : (summary xs).lines>0) : (summary xs).last < xs.length := by
 induction xs with
 | nil => simp [summary] at h
 | cons b bs ih =>
   simp only [summary] at h ⊢
   split
   · have ht := ih (by assumption)
     simp only [List.length_cons]; omega
   · simp

def applySummary (xs : List Byte) (s : State) : State :=
 let r := summary xs
 ⟨s.offset+xs.length,s.line+r.lines,
  if r.lines>0 then xs.length-r.last else s.column+xs.length⟩

def nativeBulk (xs : List Byte) (s : State) : State :=
 let r := scan xs 0 ⟨0,0⟩
 ⟨s.offset+xs.length,s.line+r.lines,
  if r.lines>0 then xs.length-r.last else s.column+xs.length⟩

theorem bulk_summary (xs : List Byte) (s : State) : nativeBulk xs s=applySummary xs s := by
 simp only [nativeBulk,scan_summary,applySummary,Nat.zero_add]
 split <;> simp_all

theorem ordinary_step (b : Byte) (bs : List Byte) (s : State)
 (hmark : marks b bs=false) (hw : nativeWidth b=1) :
 applySummary (b::bs) s = applySummary bs (ordinary b s) := by
 simp only [applySummary,summary,hmark,↓reduceIte,Nat.add_zero,List.length_cons,ordinary,hw]
 by_cases h : (summary bs).lines>0
 · have bound := last_bound bs h
   simp [h,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] <;> (repeat' first | omega | split)
 · have hz : (summary bs).lines=0 := by omega
   simp [hz,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] <;> (repeat' first | omega | split)

theorem newline_step (b : Byte) (bs : List Byte) (s : State) (hm : marks b bs=true) :
 applySummary (b::bs) s = applySummary bs (newline 1 s) := by
 simp only [applySummary,summary,hm,↓reduceIte,List.length_cons,newline]
 by_cases h : (summary bs).lines>0
 · have bound := last_bound bs h
   simp [h,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] <;> (repeat' first | omega | split)
 · have hz : (summary bs).lines=0 := by omega
   simp [hz,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] <;> (repeat' first | omega | split)

theorem crlf_step (xs : List Byte) (s : State) :
 applySummary (13::10::xs) s = applySummary xs (newline 2 s) := by
 simp only [applySummary,summary,marks,List.head?_cons]
 simp only [show ((13:Byte)==10)=false by decide,show ((13:Byte)==12)=false by decide,show ((13:Byte)==13)=true by decide,show ((10:Byte)==10)=true by decide,show (some (10:Byte)!=some 10)=false by decide,Bool.false_or,Bool.true_or,Bool.true_and,↓reduceIte,Nat.add_zero,List.length_cons,newline]
 by_cases h : (summary xs).lines>0
 · have bound := last_bound xs h
   simp [h,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] <;> (repeat' first | omega | split)
 · have hz : (summary xs).lines=0 := by omega
   simp [hz,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] <;> (repeat' first | omega | split)

theorem native_metadata (xs : List Byte) (s : State)
 (ws : ∀ b ∈ xs, URLScan.nativeWhitespace b=true) :
 nativeBulk xs s = nativeObserve xs s := by
 rw [bulk_summary]
 induction xs,s using nativeObserve.induct with
 | case1 s => simp [applySummary,summary,nativeObserve]
 | case2 b bs s hn hc ih =>
   cases bs with
   | nil => simp at hc
   | cons c cs =>
     simp only [Bool.and_eq_true,beq_iff_eq,List.head?_cons,Option.some.injEq] at hc
     obtain ⟨rfl,rfl⟩ := hc
     rw [crlf_step]
     have ht : ∀ b ∈ cs, URLScan.nativeWhitespace b=true := by intro b hb; exact ws b (by simp [hb])
     simpa [nativeObserve,isNewline] using ih ht
 | case3 b bs s hn hc ih =>
   have hm : marks b bs=true := by
     simp only [isNewline,Bool.or_eq_true,beq_iff_eq] at hn
     rcases hn with (rfl|rfl)|rfl
     · simp [marks]
     · simp [marks]
     · have ht : bs.head? ≠ some 10 := by simpa using hc
       simp [marks,ht]
   rw [newline_step b bs s hm]
   have ht : ∀ b ∈ bs, URLScan.nativeWhitespace b=true := by intro b hb; exact ws b (by simp [hb])
   simpa [nativeObserve,hn,hc] using ih ht
 | case4 b bs s hn ih =>
   have hb := ws b (by simp)
   have only : ∀ b, URLScan.nativeWhitespace b=true → isNewline b=false → (nativeWidth b=1 ∧ (b≠10 ∧ b≠12 ∧ b≠13)) := by decide
   have info := only b hb (by simpa using hn)
   have hm : marks b bs=false := by simp [marks,info.2.1,info.2.2.1,info.2.2.2]
   rw [ordinary_step b bs s hm info.1]
   have ht : ∀ b ∈ bs, URLScan.nativeWhitespace b=true := by intro b hb; exact ws b (by simp [hb])
   simpa [nativeObserve,hn] using ih ht

end URLWhitespace
