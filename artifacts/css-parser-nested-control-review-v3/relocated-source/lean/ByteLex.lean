import PublicCache
import URLDispatch
set_option autoImplicit false
namespace ByteLex
open PublicCache
inductive Family where
 | whitespace | string | numeric | hash | atKeyword | punctuation
 deriving DecidableEq, Repr

def digit (b : Byte) : Bool := 48 ≤ b.val && b.val ≤ 57

def numberTail : List Byte → Bool
 | b::bs => digit b || (b==46 && ((bs.head?.map digit).getD false))
 | [] => false

def selected : List Byte → Bool
 | [] => false
 | b::bs =>
   if b==45 then
     if numberTail bs then false
     else if ([45,45,62] : List Byte).isPrefixOf (b::bs) then false
     else IdentifierStart.corrected ((b::bs).map Fin.val)
   else if IdentifierStart.nativeAscii b.val then true
   else if b==92 then !IdentifierStart.newlineAt ((b::bs).map Fin.val) 1
   else !(b.val<128)

def family : List Byte → Family
 | [] => .punctuation
 | b::bs =>
   if URLScan.nativeWhitespace b then .whitespace
   else if b==34 || b==39 then .string
   else if digit b || ((b==43 || b==45) && numberTail bs) ||
       (b==46 && (bs.head?.map digit).getD false) then .numeric
   else if b==35 then .hash
   else if b==64 then .atKeyword
   else .punctuation

def pending : Token → Option Block
 | .function _ => some .parenthesis
 | .open b => some b
 | _ => none

def identToken (token : URLDispatch.Token) : Token :=
 if token.kind==.function then .function token.payload else .other

structure Relative where
 token : Token
 count : Nat
 deriving DecidableEq, Repr

def other (provider : Family → List Byte → Nat) (xs : List Byte) : Relative :=
 match xs with
 | 47::42::tail => let value := CommentScan.scan tail
                  ⟨.comment value.body,2+value.count⟩
 | 40::_ => ⟨.open .parenthesis,1⟩
 | 91::_ => ⟨.open .square,1⟩
 | 123::_ => ⟨.open .curly,1⟩
 | 41::_ => ⟨.close .parenthesis,1⟩
 | 93::_ => ⟨.close .square,1⟩
 | 125::_ => ⟨.close .curly,1⟩
 | 58::_ => ⟨.colon,1⟩
 | [] => ⟨.other,0⟩
 | _ => ⟨.other,provider (family xs) xs⟩

def native (provider : Family → List Byte → Nat) (xs : List Byte) : Relative :=
 if selected xs then
   let value := URLDispatch.native xs false
   ⟨identToken value,value.count⟩
 else other provider xs

def reference (provider : Family → List Byte → Nat) (xs : List Byte) : Relative :=
 if selected xs then
   let value := URLDispatch.reference xs false
   ⟨identToken value,value.count⟩
 else other provider xs

def read (provider : Family → List Byte → Nat) (source : List Byte) (position : Nat) : Lexeme :=
 let value := native provider (source.drop position)
 ⟨value.token,⟨position+value.count,pending value.token⟩⟩

theorem selected_admits_name (xs : List Byte) (h : selected xs=true) :
 IdentifierStart.corrected (xs.map Fin.val)=true := by
 cases xs with
 | nil => simp [selected] at h
 | cons b bs =>
   by_cases h45 : b=45
   · subst b
     simp only [selected,beq_self_eq_true,↓reduceIte] at h
     split at h
     · contradiction
     · split at h
       · contradiction
       · exact h
   · have hv45 : b.val ≠ 45 := by
       intro he
       exact h45 (Fin.ext he)
     by_cases ha : IdentifierStart.nativeAscii b.val=true
     · simp [List.map_cons,IdentifierStart.corrected,ha]
     · have hf : IdentifierStart.nativeAscii b.val=false := by simpa using ha
       by_cases h92 : b=92
       · subst b
         have hv : (92 : Byte).val=92 := rfl
         simpa [selected,IdentifierStart.corrected,IdentifierStart.nativeAscii,hv] using h
       · have hv92 : b.val ≠ 92 := by
           intro he
           exact h92 (Fin.ext he)
         simpa [selected,IdentifierStart.corrected,h45,h92,hv45,hv92,hf] using h

theorem provider_refinement (provider : Family → List Byte → Nat) (xs : List Byte) :
 native provider xs=reference provider xs := by
 simp [native,reference,URLDispatch.providers_refine]

theorem nonfunction_other (provider : Family → List Byte → Nat) (xs : List Byte)
 (names : List (List Byte)) : relevant names (other provider xs).token=false := by
 unfold other
 split <;> rfl

theorem function_observation (provider : Family → List Byte → Nat) (xs : List Byte)
 (names : List (List Byte)) :
 relevant names (native provider xs).token =
   if selected xs then relevant names (identToken (URLDispatch.reference xs false)) else false := by
 rw [provider_refinement]
 unfold reference
 split
 · rfl
 · exact nonfunction_other provider xs names

theorem ident_count_positive (provider : Family → List Byte → Nat) (xs : List Byte)
 (h : selected xs=true) : 0<(native provider xs).count := by
 simpa [native,h] using URLDispatch.admitted_progress xs false (selected_admits_name xs h)

theorem read_deterministic (provider : Family → List Byte → Nat) (source : List Byte)
 (a b : Nat) (h : a=b) : read provider source a=read provider source b := by rw [h]

end ByteLex
