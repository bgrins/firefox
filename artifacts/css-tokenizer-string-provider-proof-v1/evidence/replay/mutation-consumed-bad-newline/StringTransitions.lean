import CommentNativeBounds
import CommentCodepoints
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace StringTransitions
open CommentScan
inductive Action where
  | copy | close | bad | nul | escape
  deriving DecidableEq, Repr
inductive Ending where
  | closed | eof | bad
  deriving DecidableEq, Repr
structure Value where
  output : List Byte
  count : Nat
  ending : Ending
  deriving DecidableEq, Repr

def quote (single : Bool) : Byte := if single then 39 else 34

def nativeClass (single : Bool) (b : Byte) : Action :=
  if b == 10 || b == 12 || b == 13 then .bad
  else if b == 34 then if single then .copy else .close
  else if b == 39 then if single then .close else .copy
  else if b == 92 then .escape
  else if b == 0 then .nul else .copy

def referenceClass (single : Bool) (b : Byte) : Action :=
  if b == quote single then .close
  else (([(0,Action.nul),(10,.bad),(12,.bad),(13,.bad),(92,.escape)] : List (Byte × Action)).find?
    (fun pair => pair.1 == b)).map Prod.snd |>.getD .copy

theorem class_equivalence : ∀ single b, nativeClass single b = referenceClass single b := by decide

def nativeNewline (xs : List Byte) : Bool := xs.head?.any (fun b => b == 10 || b == 12 || b == 13)
def referenceNewline (xs : List Byte) : Bool := xs.head?.any (fun b => ([10,12,13] : List Byte).contains b)

theorem newline_equivalence (xs : List Byte) : nativeNewline xs = referenceNewline xs := by
  cases xs with
  | nil => rfl
  | cons b bs =>
    have h : ∀ b : Byte, (b == 10 || b == 12 || b == 13) = ([10,12,13] : List Byte).contains b := by decide
    simp [nativeNewline,referenceNewline,h]

def newlineCount (xs : List Byte) : Nat := if xs.take 2 = [13,10] then 2 else 1

def nativeEscape (xs : List Byte) : Escape.Result :=
  if xs.isEmpty then ⟨[],0⟩
  else if nativeNewline xs then ⟨[],newlineCount xs⟩ else Escape.native xs

def referenceEscape (xs : List Byte) : Escape.Result :=
  match xs with
  | [] => ⟨[],0⟩
  | _::_ => if referenceNewline xs then ⟨[],Escape.referenceWhitespace xs⟩ else Escape.reference xs

theorem newline_count (xs : List Byte) (h : referenceNewline xs = true) :
    newlineCount xs = Escape.referenceWhitespace xs := by
  cases xs with
  | nil => simp [referenceNewline] at h
  | cons b bs =>
    simp [referenceNewline] at h
    have v10 : (10 : Byte).val = 10 := rfl
    have v12 : (12 : Byte).val = 12 := rfl
    have v13 : (13 : Byte).val = 13 := rfl
    rcases h with rfl | rfl | rfl <;> cases bs <;>
      simp [newlineCount,Escape.referenceWhitespace,Escape.byte,v10,v12,v13]

theorem escape_equivalence (xs : List Byte) : nativeEscape xs = referenceEscape xs := by
  cases xs with
  | nil => rfl
  | cons b bs =>
    by_cases h : referenceNewline (b::bs) = true
    · simp [nativeEscape,referenceEscape,newline_equivalence,h,newline_count _ h]
    · simp [nativeEscape,referenceEscape,newline_equivalence,h,Escape.native_reference]

theorem escape_bound (xs : List Byte) : (nativeEscape xs).count ≤ xs.length := by
  cases xs with
  | nil => simp [nativeEscape]
  | cons b bs =>
    by_cases h : nativeNewline (b::bs) = true
    · have hn : referenceNewline (b::bs) = true := by simpa [newline_equivalence] using h
      have hw := Escape.whitespace_bound (b::bs)
      simpa [nativeEscape,h,newline_count _ hn,← Escape.whitespace_reference] using hw
    · simpa [nativeEscape,h] using Escape.consumption_bound (b::bs)

def extend (pre : List Byte) (n : Nat) (r : Value) : Value :=
  ⟨pre++r.output,n+r.count,r.ending⟩

def reference (single : Bool) : List Byte → Value
  | [] => ⟨[],0,.eof⟩
  | b::bs =>
    match referenceClass single b with
    | .close => ⟨[],1,.closed⟩
    | .bad => ⟨[],0,.bad⟩
    | .nul => extend (Escape.encode 65533) 1 (reference single bs)
    | .copy => extend [b] 1 (reference single bs)
    | .escape =>
      let e := referenceEscape bs
      extend e.output (1+e.count) (reference single (bs.drop e.count))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

def owned (single : Bool) : List Byte → List Byte → Value
  | [], buffer => ⟨buffer,0,.eof⟩
  | b::bs, buffer =>
    match nativeClass single b with
    | .close => ⟨buffer,1,.closed⟩
    | .bad => ⟨buffer,1,.bad⟩
    | .nul => extend [] 1 (owned single bs (buffer++Escape.encode 65533))
    | .copy => extend [] 1 (owned single bs (buffer++[b]))
    | .escape =>
      let e := nativeEscape bs
      extend [] (1+e.count) (owned single (bs.drop e.count) (buffer++e.output))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

theorem owned_reference (single : Bool) (xs buffer : List Byte) :
    owned single xs buffer = extend buffer 0 (reference single xs) := by
  induction xs,buffer using owned.induct single with
  | case1 buffer => simp [owned,reference,extend]
  | case2 b bs buffer h => simp [owned,h,reference,← class_equivalence,h,extend]
  | case3 b bs buffer h => simp [owned,h,reference,← class_equivalence,h,extend]
  | case4 b bs buffer h ih => simp [owned,h,reference,← class_equivalence,h,ih,extend,List.append_assoc]
  | case5 b bs buffer h ih => simp [owned,h,reference,← class_equivalence,h,ih,extend,List.append_assoc]
  | case6 b bs buffer h e ih =>
    dsimp [e] at ih
    simp [owned,h,reference,← class_equivalence,h,← escape_equivalence,ih,extend,List.append_assoc]

structure NativeValue where
  value : Value
  allocated : Bool
  deriving DecidableEq, Repr

def borrowed (single : Bool) : List Byte → List Byte → NativeValue
  | [], pre => ⟨⟨pre,0,.eof⟩,false⟩
  | b::bs, pre =>
    match nativeClass single b with
    | .close => ⟨⟨pre,1,.closed⟩,false⟩
    | .bad => ⟨⟨pre,0,.bad⟩,false⟩
    | .copy => let r := borrowed single bs (pre++[b]); ⟨extend [] 1 r.value,r.allocated⟩
    | _ => ⟨owned single (b::bs) pre,true⟩

theorem borrowed_reference (single : Bool) (xs pre : List Byte) :
    (borrowed single xs pre).value = extend pre 0 (reference single xs) := by
  induction xs generalizing pre with
  | nil => simp [borrowed,reference,extend]
  | cons b bs ih =>
    cases h : nativeClass single b with
    | copy => simp [borrowed,h,reference,← class_equivalence,h,ih,extend,List.append_assoc]
    | close => simp [borrowed,h,reference,← class_equivalence,h,extend]
    | bad => simp [borrowed,h,reference,← class_equivalence,h,extend]
    | nul => simpa [borrowed,h] using owned_reference single (b::bs) pre
    | escape => simpa [borrowed,h] using owned_reference single (b::bs) pre

theorem prefix_composition (a b : List Byte) (m n : Nat) (r : Value) :
    extend a m (extend b n r) = extend (a++b) (m+n) r := by
  simp [extend,List.append_assoc,Nat.add_assoc]

theorem reference_bound (single : Bool) (xs : List Byte) : (reference single xs).count ≤ xs.length := by
  induction xs using (reference.induct single) with
  | case1 => simp [reference]
  | case2 b bs h => simp [reference,h]
  | case3 b bs h => simp [reference,h]
  | case4 b bs h ih => simp [reference,h,extend]; omega
  | case5 b bs h ih => simp [reference,h,extend]; omega
  | case6 b bs h e ih =>
    have hb := escape_bound bs
    rw [escape_equivalence] at hb
    dsimp [e] at ih
    simp only [List.length_drop] at ih
    simp [reference,h,extend]; omega

theorem escaped_eof_distinction : nativeEscape [] = ⟨[],0⟩ ∧ Escape.native [] = ⟨Escape.encode 65533,0⟩ := by decide
end StringTransitions
