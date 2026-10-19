import URLScan
import BadURLSpec
import StringUTF8
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace URLUTF8
open URLScan
abbrev Unit := Boundary.Unit
abbrev bytes := Boundary.bytes
abbrev Valid := StringUTF8.Valid

theorem extend_valid (pre : List Byte) (n : Nat) (r : Value)
 (hp : Valid pre) (hr : Valid r.output) : Valid (extend pre n r).output := by
 cases r with
 | mk kind output count =>
   cases kind
   · exact StringUTF8.valid_append hp hr
   · exact StringUTF8.valid_nil

theorem copy_prefix (pre tail : List Byte) (h : ∀ b ∈ pre, nativeClass b = .copy) :
 reference (pre++tail) = extend pre pre.length (reference tail) := by
 induction pre with
 | nil => simp [extend_identity]
 | cons b bs ih =>
   have hb := h b (by simp)
   have ht := ih (fun c hc => h c (by simp [hc]))
   simp [reference,← class_equivalence,hb,ht,extend_composition,Nat.add_comm 1]

theorem nonascii_copy : ∀ (b : Byte), 128 ≤ b.val → nativeClass b = .copy := by decide

theorem unit_copy (u : Unit) (h : nativeClass u.first = .copy) :
 ∀ b ∈ u.bytes, nativeClass b = .copy := by
 intro b hb
 rcases List.mem_cons.mp hb with rfl | hb
 · exact h
 · exact nonascii_copy b (u.continuation b hb).1

theorem noncopy_ascii (b : Byte) (h : nativeClass b ≠ .copy) : b.val < 128 := by
 by_cases ha : b.val < 128
 · exact ha
 · have hh := nonascii_copy b (by omega)
   contradiction

theorem whitespace_ascii : ∀ (b : Byte), nativeWhitespace b = true → b.val < 128 := by decide

theorem end_valid (units : List Unit) :
 Valid ((bytes units).drop (endNative (bytes units)).count) := by
 induction units with
 | nil => exact StringUTF8.valid_nil
 | cons u us ih =>
   by_cases close : u.first=41
   · have empty := Boundary.unit_ascii_singleton u (by rw [close]; decide)
     simpa [Boundary.bytes,Boundary.Unit.bytes,empty,close,endNative] using (show Valid (bytes us) from ⟨us,rfl⟩)
   · by_cases ws : nativeWhitespace u.first = true
     · have empty := Boundary.unit_ascii_singleton u (whitespace_ascii u.first ws)
       have form : bytes (u::us)=u.first::bytes us := by simp [Boundary.bytes,Boundary.Unit.bytes,empty]
       simpa [form,endNative,close,ws,extend,Nat.add_comm 1] using ih
     · have form : bytes (u::us)=u.first::(u.rest++bytes us) := rfl
       simpa [form,endNative,close,ws,badNative] using BadURLSpec.residual_valid (u::us)

theorem reference_valid (units : List Unit) :
 Valid (reference (bytes units)).output ∧ Valid ((bytes units).drop (reference (bytes units)).count) := by
 generalize heq : (bytes units).length = n
 induction n using Nat.strongRecOn generalizing units with
 | ind n ih =>
   cases units with
   | nil => simpa [reference,Boundary.bytes] using (show Valid [] ∧ Valid [] from ⟨StringUTF8.valid_nil,StringUTF8.valid_nil⟩)
   | cons u us =>
     have shorter : (bytes us).length < n := by
       change (u.first::(u.rest++bytes us)).length=n at heq
       simp only [List.length_cons,List.length_append] at heq
       omega
     have hu : Valid u.bytes := ⟨[u],by simp [Boundary.bytes]⟩
     by_cases hc : nativeClass u.first = .copy
     · have cp := copy_prefix u.bytes (bytes us) (unit_copy u hc)
       have ht := ih (bytes us).length shorter us rfl
       have form : bytes (u::us)=u.bytes++bytes us := rfl
       rw [form,cp]
       exact ⟨extend_valid _ _ _ hu ht.1,by simpa [extend,← List.drop_drop] using ht.2⟩
     · have empty := Boundary.unit_ascii_singleton u (noncopy_ascii u.first hc)
       have form : bytes (u::us)=u.first::bytes us := by simp [Boundary.bytes,Boundary.Unit.bytes,empty]
       cases ha : nativeClass u.first with
       | copy => contradiction
       | close => simpa [form,reference,← class_equivalence,ha] using (show Valid [] ∧ Valid (bytes us) from ⟨StringUTF8.valid_nil,⟨us,rfl⟩⟩)
       | invalid =>
         have ht := BadURLSpec.residual_valid us
         rw [BadURL.native_reference] at ht
         simpa [form,reference,← class_equivalence,ha,extend,badReference,Nat.add_comm 1] using (show Valid [] ∧ Valid ((bytes us).drop (BadURL.reference (bytes us)).count) from ⟨StringUTF8.valid_nil,ht⟩)
       | space =>
         simp only [form,reference,← class_equivalence,ha,← end_equivalence]
         rw [← form]
         exact ⟨by rw [end_empty_output]; exact StringUTF8.valid_nil,end_valid _⟩
       | nul =>
         have ht := ih (bytes us).length shorter us rfl
         simp only [form,reference,← class_equivalence,ha]
         exact ⟨extend_valid _ _ _ StringUTF8.replacement_valid ht.1,by simpa [extend,Nat.add_comm 1] using ht.2⟩
       | escape =>
         by_cases hn : newline (bytes us) = true
         · have ht := BadURLSpec.residual_valid us
           rw [BadURL.native_reference] at ht
           simpa [form,reference,← class_equivalence,ha,hn,extend,badReference,Nat.add_comm 1] using (show Valid [] ∧ Valid ((bytes us).drop (BadURL.reference (bytes us)).count) from ⟨StringUTF8.valid_nil,ht⟩)
         · have he := StringUTF8.escape_valid us
           obtain ⟨remaining,hr⟩ := he.2
           change (bytes us).drop (Escape.native (bytes us)).count=bytes remaining at hr
           have small : (bytes remaining).length<n := by rw [← hr,List.length_drop]; omega
           have ht := ih (bytes remaining).length small remaining rfl
           rw [← hr] at ht
           simp only [form,reference,← class_equivalence,ha,hn,↓reduceIte,← Escape.native_reference]
           constructor
           · exact extend_valid _ _ _ he.1 ht.1
           · change Valid ((u.first::bytes us).drop ((1+(Escape.native (bytes us)).count)+(reference ((bytes us).drop (Escape.native (bytes us)).count)).count))
             rw [show (1+(Escape.native (bytes us)).count)+(reference ((bytes us).drop (Escape.native (bytes us)).count)).count = ((Escape.native (bytes us)).count+(reference ((bytes us).drop (Escape.native (bytes us)).count)).count)+1 by omega]
             simpa only [List.drop_succ_cons,← List.drop_drop] using ht.2

theorem borrowed_return_valid (units : List Unit) :
 Valid (borrowed (bytes units) []).value.output ∧
 Valid ((bytes units).drop (borrowed (bytes units) []).value.count) := by
 simpa only [borrowed_reference,extend_identity] using reference_valid units

theorem owned_return_valid (units : List Unit) (buffer : List Byte) (hb : Valid buffer) :
 Valid (owned (bytes units) buffer).output := by
 rw [owned_reference]
 exact extend_valid _ _ _ hb (reference_valid units).1

theorem owned_copy_prefix (pre tail buffer : List Byte)
 (h : ∀ b ∈ pre, nativeClass b = .copy) :
 owned (pre++tail) buffer = extend [] pre.length (owned tail (buffer++pre)) := by
 rw [owned_reference,copy_prefix pre tail h,owned_reference]
 cases hc : (reference tail).kind <;> simp [extend,hc,List.append_assoc]

theorem partial_copy_rejoin (u : Unit) (pre post : List Byte)
 (splitUnit : u.bytes=pre++post) (copyUnit : nativeClass u.first=.copy)
 (remaining : List Unit) (buffer : List Byte) :
 owned (post++bytes remaining) (buffer++pre) =
 extend [] post.length (owned (bytes remaining) (buffer++u.bytes)) := by
 have hc : ∀ b ∈ post, nativeClass b=.copy := by
   intro b hb
   exact unit_copy u copyUnit b (by simp [splitUnit,hb])
 rw [owned_copy_prefix post (bytes remaining) (buffer++pre) hc]
 simp [splitUnit,List.append_assoc]

end URLUTF8
