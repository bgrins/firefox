import BadURL
import Escape
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace URLScan
abbrev Byte := BadURL.Byte
inductive Action where
 | copy | close | invalid | space | nul | escape
 deriving DecidableEq, Repr
inductive Kind where
 | url | bad
 deriving DecidableEq, Repr
structure Value where
 kind : Kind
 output : List Byte
 count : Nat
 deriving DecidableEq, Repr

def nativeWhitespace (b : Byte) : Bool := b == 32 || b == 9 || b == 10 || b == 12 || b == 13
def referenceWhitespace (b : Byte) : Bool := ([9,10,12,13,32] : List Byte).contains b

def nativeClass (b : Byte) : Action :=
 if nativeWhitespace b then .space
 else if b == 41 then .close
 else if (1 ≤ b.val ∧ b.val ≤ 8) ∨ b.val = 11 ∨ (14 ≤ b.val ∧ b.val ≤ 31) ∨
     b.val = 127 ∨ b.val = 34 ∨ b.val = 39 ∨ b.val = 40 then .invalid
 else if b == 92 then .escape else if b == 0 then .nul else .copy

def referenceClass (b : Byte) : Action :=
 if referenceWhitespace b then .space
 else if ([34,39,40] : List Byte).contains b ∨ b.val ∈ [1,2,3,4,5,6,7,8,11,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,127] then .invalid
 else if b == 0 then .nul else if b == 41 then .close else if b == 92 then .escape else .copy

theorem whitespace_equivalence : ∀ b, nativeWhitespace b = referenceWhitespace b := by decide
theorem class_equivalence : ∀ b, nativeClass b = referenceClass b := by decide

def newline (xs : List Byte) : Bool := xs.head?.any (fun b => b == 10 || b == 12 || b == 13)

def extend (pre : List Byte) (n : Nat) (r : Value) : Value :=
 ⟨r.kind, if r.kind == .url then pre++r.output else [], n+r.count⟩

def badNative (xs : List Byte) : Value := ⟨.bad,[],(BadURL.native xs).count⟩
def badReference (xs : List Byte) : Value := ⟨.bad,[],(BadURL.reference xs).count⟩

def endNative : List Byte → Value
 | [] => ⟨.url,[],0⟩
 | b::bs => if b == 41 then ⟨.url,[],1⟩
   else if nativeWhitespace b then extend [] 1 (endNative bs)
   else badNative (b::bs)

def endReference (xs : List Byte) : Value :=
 let rest := xs.dropWhile referenceWhitespace
 let skipped := xs.length-rest.length
 match rest with
 | [] => ⟨.url,[],skipped⟩
 | b::bs => if b == 41 then ⟨.url,[],skipped+1⟩
   else extend [] skipped (badReference (b::bs))

theorem end_empty_output (xs : List Byte) : (endNative xs).output = [] := by
 induction xs with
 | nil => rfl
 | cons b bs ih =>
   simp only [endNative]
   split
   · rfl
   · split
     · simp [extend,ih]
     · rfl

theorem drop_bound (xs : List Byte) : (xs.dropWhile referenceWhitespace).length ≤ xs.length := by
 induction xs with
 | nil => simp
 | cons b bs ih =>
   by_cases h : referenceWhitespace b = true
   · simpa [List.dropWhile_cons,h] using Nat.le_succ_of_le ih
   · simp [List.dropWhile_cons,h]

theorem end_equivalence (xs : List Byte) : endNative xs = endReference xs := by
 induction xs with
 | nil => rfl
 | cons b bs ih =>
   by_cases close : b = 41
   · subst b; simp [endNative,endReference,referenceWhitespace]
   · by_cases ws : referenceWhitespace b = true
     · have hle : (bs.dropWhile referenceWhitespace).length ≤ bs.length := drop_bound bs
       simp only [endNative,close,beq_eq_false_iff_ne.mpr close,whitespace_equivalence,ws,↓reduceIte,ih]
       simp only [endReference,List.dropWhile_cons,ws,↓reduceIte,List.length_cons]
       cases hr : bs.dropWhile referenceWhitespace with
       | nil => simp [extend]; omega
       | cons c cs =>
         simp only [hr,List.length_cons] at hle
         by_cases hc : c = 41
         · simp [hc,extend]; omega
         · simp [hc,beq_eq_false_iff_ne.mpr hc,extend,badReference]; omega
     · have wf : referenceWhitespace b = false := by simpa using ws
       simp [endNative,endReference,close,beq_eq_false_iff_ne.mpr close,whitespace_equivalence,wf,badNative,badReference,BadURL.native_reference,extend]

def reference : List Byte → Value
 | [] => ⟨.url,[],0⟩
 | b::bs => match referenceClass b with
   | .close => ⟨.url,[],1⟩
   | .invalid => extend [] 1 (badReference bs)
   | .space => endReference (b::bs)
   | .nul => extend (Escape.encode 65533) 1 (reference bs)
   | .copy => extend [b] 1 (reference bs)
   | .escape => if newline bs then extend [] 1 (badReference bs)
     else let e := Escape.reference bs
          extend e.output (1+e.count) (reference (bs.drop e.count))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

def owned : List Byte → List Byte → Value
 | [], buffer => ⟨.url,buffer,0⟩
 | b::bs, buffer => match nativeClass b with
   | .close => ⟨.url,buffer,1⟩
   | .invalid => extend [] 1 (badNative bs)
   | .space => extend buffer 0 (endNative (b::bs))
   | .nul => extend [] 1 (owned bs (buffer++Escape.encode 65533))
   | .copy => extend [] 1 (owned bs (buffer++[b]))
   | .escape => if newline bs then extend [] 1 (badNative bs)
     else let e := Escape.native bs
          extend [] (1+e.count) (owned (bs.drop e.count) (buffer++e.output))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

theorem extend_composition (a b : List Byte) (m n) (r : Value) :
 extend a m (extend b n r) = extend (a++b) (m+n) r := by
 cases r with
 | mk kind output count => cases kind <;> simp [extend,List.append_assoc,Nat.add_assoc]

theorem owned_reference (xs buffer : List Byte) : owned xs buffer = extend buffer 0 (reference xs) := by
 induction xs,buffer using owned.induct with
 | case1 buffer => simp [owned,reference,extend]
 | case2 b bs buffer h => simp [owned,reference,← class_equivalence,h,extend]
 | case3 b bs buffer h => simp [owned,reference,← class_equivalence,h,extend,badNative,badReference,BadURL.native_reference]
 | case4 b bs buffer h => simp [owned,reference,← class_equivalence,h,end_equivalence]
 | case5 b bs buffer h ih =>
   simp only [owned,h,reference,← class_equivalence,h,ih]
   simp only [extend_composition]
   simp [extend,List.append_assoc]
 | case6 b bs buffer h ih =>
   simp only [owned,h,reference,← class_equivalence,h,ih]
   simp only [extend_composition]
   simp [extend,List.append_assoc]
 | case7 b bs buffer h hn => simp [owned,reference,← class_equivalence,h,hn,extend,badNative,badReference,BadURL.native_reference]
 | case8 b bs buffer h hn e ih =>
   dsimp [e] at ih
   simp only [owned,h,hn,↓reduceIte,reference,← class_equivalence,h,hn,↓reduceIte,← Escape.native_reference,ih]
   cases hk : (reference (bs.drop (Escape.native bs).count)).kind <;>
     simp [extend,hk,List.append_assoc]

structure NativeValue where
 value : Value
 allocated : Bool
 deriving DecidableEq, Repr

def borrowed : List Byte → List Byte → NativeValue
 | [], pre => ⟨⟨.url,pre,0⟩,false⟩
 | b::bs, pre => match nativeClass b with
   | .close => ⟨⟨.url,pre,1⟩,false⟩
   | .invalid => ⟨extend [] 1 (badNative bs),false⟩
   | .space => ⟨extend pre 0 (endNative (b::bs)),false⟩
   | .copy => let r := borrowed bs (pre++[b]); ⟨extend [] 1 r.value,r.allocated⟩
   | _ => ⟨owned (b::bs) pre,true⟩

theorem borrowed_reference (xs pre : List Byte) : (borrowed xs pre).value = extend pre 0 (reference xs) := by
 induction xs generalizing pre with
 | nil => simp [borrowed,reference,extend]
 | cons b bs ih =>
   cases h : nativeClass b with
   | close => simp [borrowed,reference,← class_equivalence,h,extend]
   | invalid => simp [borrowed,reference,← class_equivalence,h,extend,badNative,badReference,BadURL.native_reference]
   | space => simp [borrowed,reference,← class_equivalence,h,end_equivalence]
   | copy =>
     simp only [borrowed,h,reference,← class_equivalence,h,ih,extend_composition]
     simp
   | nul => simpa [borrowed,h] using owned_reference (b::bs) pre
   | escape => simpa [borrowed,h] using owned_reference (b::bs) pre
theorem end_bound (xs : List Byte) : (endNative xs).count ≤ xs.length := by
 induction xs with
 | nil => simp [endNative]
 | cons b bs ih =>
   simp only [endNative]
   split
   · simp
   · split
     · simpa [extend,Nat.add_comm] using Nat.succ_le_succ ih
     · exact BadURL.bounded (b::bs)

theorem reference_bound (xs : List Byte) : (reference xs).count ≤ xs.length := by
 induction xs using reference.induct with
 | case1 => simp [reference]
 | case2 b bs h => simp [reference,h]
 | case3 b bs h =>
   have hb := BadURL.bounded bs
   rw [BadURL.native_reference] at hb
   simpa [reference,h,extend,badReference,Nat.add_comm] using Nat.succ_le_succ hb
 | case4 b bs h => simpa [reference,h,← end_equivalence] using end_bound (b::bs)
 | case5 b bs h ih => simpa [reference,h,extend,Nat.add_comm] using Nat.succ_le_succ ih
 | case6 b bs h ih => simpa [reference,h,extend,Nat.add_comm] using Nat.succ_le_succ ih
 | case7 b bs h hn =>
   have hb := BadURL.bounded bs
   rw [BadURL.native_reference] at hb
   simpa [reference,h,hn,extend,badReference,Nat.add_comm] using Nat.succ_le_succ hb
 | case8 b bs h hn e ih =>
   dsimp [e] at ih
   have he := Escape.consumption_bound bs
   rw [Escape.native_reference] at he
   simp only [List.length_drop] at ih
   simp [reference,h,hn,extend]
   omega

theorem borrowed_bound (xs pre : List Byte) : (borrowed xs pre).value.count ≤ xs.length := by
 simpa [borrowed_reference,extend] using reference_bound xs

theorem end_of_empty_url : (borrowed [] []).value = ⟨.url,[],0⟩ := rfl

theorem escaped_eof_is_replacement :
 reference [92] = ⟨.url,Escape.encode 65533,1⟩ := by
 have hc : referenceClass (92:Byte) = .escape := by decide
 simp [reference,hc,newline,Escape.reference,extend]

theorem escaped_newline_is_bad : reference [92,10,41,65] = ⟨.bad,[],3⟩ := by
 have hc : referenceClass (92:Byte) = .escape := by decide
 simp [reference,hc,newline,extend,badReference,← BadURL.native_reference,BadURL.native,BadURL.add]

theorem bad_empty (xs : List Byte) (h : (reference xs).kind=.bad) : (reference xs).output=[] := by
 induction xs using reference.induct with
 | case1 => simp [reference] at h
 | case2 b bs hc => simp [reference,hc] at h
 | case3 b bs hc => simp [reference,hc,extend,badReference]
 | case4 b bs hc => simp [reference,hc,← end_equivalence,end_empty_output]
 | case5 b bs hc ih => simp [reference,hc,extend] at h ⊢; simp [h]
 | case6 b bs hc ih => simp [reference,hc,extend] at h ⊢; simp [h]
 | case7 b bs hc hn => simp [reference,hc,hn,extend,badReference]
 | case8 b bs hc hn e ih => simp [reference,hc,hn,extend] at h ⊢; simp [h]

theorem extend_identity (xs : List Byte) : extend [] 0 (reference xs) = reference xs := by
 cases hr : reference xs with
 | mk kind output count =>
   cases kind
   · simp [extend]
   · have he := bad_empty xs (by simp [hr])
     simp only [hr] at he
     simp [extend,he]

end URLScan
