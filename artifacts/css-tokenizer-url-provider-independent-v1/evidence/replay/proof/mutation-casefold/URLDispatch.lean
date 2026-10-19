import URLTrace
import SemanticName
import Integration
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace URLDispatch
abbrev Byte := CommentScan.Byte

def lower (b : Byte) : Nat := if 65≤b.val ∧ b.val≤90 then b.val+32 else b.val

def nativeURL (name : List Byte) : Bool := name.map Fin.val == [117,114,108]
def referenceURL (name : List Byte) : Bool :=
 match name with
 | [a,b,c] => (a==117 || a==85) && (b==114 || b==82) && (c==108 || c==76)
 | _ => false

theorem url_casefold (name : List Byte) : nativeURL name=referenceURL name := by
 have u : ∀ b, lower b=117 ↔ b=117 ∨ b=85 := by decide
 have r : ∀ b, lower b=114 ↔ b=114 ∨ b=82 := by decide
 have l : ∀ b, lower b=108 ↔ b=108 ∨ b=76 := by decide
 cases name with
 | nil => rfl
 | cons a tail =>
   cases tail with
   | nil => simp [nativeURL,referenceURL]
   | cons b tail =>
     cases tail with
     | nil => simp [nativeURL,referenceURL]
     | cons c tail =>
       cases tail with
       | nil =>
         apply Bool.eq_iff_iff.mpr
         simp [nativeURL,referenceURL,u,r,l,and_assoc]
       | cons d ds => simp [nativeURL,referenceURL]

inductive Kind where
 | ident | function | url | bad
 deriving DecidableEq, Repr
structure Token where
 kind : Kind
 payload : List Byte
 count : Nat
 pending : Bool
 seen : Bool
 deriving DecidableEq, Repr

def finish (name : List Byte) (count : Nat) (rest : List Byte)
 (isURL : Bool) (leading : List Byte → URLLeading.Result) (seen : Bool) : Token :=
 match rest with
 | 40::body =>
   if isURL then
     match leading body with
     | .function => ⟨.function,name,count+1,true,true⟩
     | .token value => ⟨if value.kind==.url then .url else .bad,value.output,count+1+value.count,false,seen⟩
   else ⟨.function,name,count+1,true,seen⟩
 | _ => ⟨.ident,name,count,false,seen⟩

def native (xs : List Byte) (seen : Bool) : Token :=
 let name := Name.run false xs
 finish name.output name.count name.rest (nativeURL name.output) (fun body => URLLeading.native body 0) seen

def reference (xs : List Byte) (seen : Bool) : Token :=
 let name := SemanticName.reference xs
 finish name.output name.count name.rest (referenceURL name.output) (fun body => URLLeading.reference body 0) seen

theorem providers_refine (xs : List Byte) (seen : Bool) : native xs seen=reference xs seen := by
 have sem := SemanticName.source_semantics false xs
 have ho := congrArg SemanticName.Result.output sem
 have hc := congrArg SemanticName.Result.count sem
 have hr := congrArg SemanticName.Result.rest sem
 simp only [SemanticName.project] at ho hc hr
 simp only [native,reference,ho,hc,hr,url_casefold]
 congr 1
 funext body
 exact URLLeading.native_reference body 0

theorem no_observer_on_url (name : List Byte) (count : Nat) (body : List Byte)
 (value : URLScan.Value) (h : URLLeading.native body 0=.token value) (seen : Bool) :
 (finish name count (40::body) true (fun b => URLLeading.native b 0) seen).seen=seen := by
 simp [finish,h]

theorem pending_only_function (xs : List Byte) (seen : Bool) :
 (native xs seen).pending = ((native xs seen).kind==.function) := by
 unfold native
 dsimp only
 unfold finish
 split
 · split
   · split
     · rfl
     · simp only [Token.pending,Token.kind]
       split <;> decide
   · rfl
 · rfl

theorem count_bound (xs : List Byte) (seen : Bool) : (native xs seen).count ≤ xs.length := by
 have bound := Name.consumed_bound false xs
 have remain := Name.exact_remainder false xs
 have total : (Name.run false xs).count+(Name.run false xs).rest.length=xs.length := by
   rw [remain,List.length_drop]; omega
 unfold native
 dsimp only
 unfold finish
 split
 · rename_i body hr
   have t : (Name.run false xs).count+1+body.length=xs.length := by rw [hr] at total; simp only [List.length_cons] at total; omega
   split
   · split
     · dsimp only; omega
     · rename_i v hv
       have vb := URLLeading.bounds body 0 v hv
       simp only [Nat.zero_add] at vb
       dsimp only; omega
   · dsimp only; omega
 · exact bound

theorem admitted_progress (xs : List Byte) (seen : Bool)
 (h : IdentifierStart.corrected (xs.map Fin.val)=true) : 0<(native xs seen).count := by
 have positive := Integration.repaired_ident_progress false xs h
 unfold native
 dsimp only
 unfold finish
 split
 · split
   · split <;> (dsimp only; omega)
   · dsimp only; omega
 · exact positive

end URLDispatch
