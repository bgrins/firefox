import StringTransitions
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace StringUTF8
open StringTransitions
abbrev Byte := CommentScan.Byte
abbrev Unit := Boundary.Unit
abbrev bytes := Boundary.bytes
def Valid (xs : List Byte) : Prop := ∃ units : List Unit, xs = bytes units

theorem valid_nil : Valid [] := ⟨[],rfl⟩
theorem valid_append {a b : List Byte} (ha : Valid a) (hb : Valid b) : Valid (a++b) := by
  obtain ⟨ua,rfl⟩ := ha
  obtain ⟨ub,rfl⟩ := hb
  exact ⟨ua++ub,by simp [bytes,Boundary.bytes]⟩

theorem valid_ascii (b : Byte) (h : b.val < 128) : Valid [b] := by
  refine ⟨[⟨b,[],Or.inl h,by simp,?_⟩],rfl⟩
  simp [Escape.width,h]

theorem encode_shape (n : Nat) (bound : n < 1114112) : Valid (Escape.encode n) := by
  by_cases h1 : n < 128
  · simp only [Escape.encode,h1,↓reduceIte]
    apply valid_ascii
    simp only [Escape.byte]
    omega
  · by_cases h2 : n < 2048
    · have ha : 192+n/64 < 256 := by omega
      have hb : 128+n%64 < 256 := by omega
      refine ⟨[⟨Escape.byte (192+n/64),[Escape.byte (128+n%64)],?_,?_,?_⟩],?_⟩
      · simp [Escape.byte,Nat.mod_eq_of_lt ha] <;> omega
      · simp [Escape.byte,Nat.mod_eq_of_lt hb] <;> omega
      · simp [Escape.width,Escape.byte,Nat.mod_eq_of_lt ha]
        all_goals repeat' first | omega | split
      · simp [Escape.encode,h1,h2,bytes,Boundary.bytes,Boundary.Unit.bytes]
    · by_cases h3 : n < 65536
      · have ha : 224+n/4096 < 256 := by omega
        have hb : 128+n/64%64 < 256 := by omega
        have hc : 128+n%64 < 256 := by omega
        refine ⟨[⟨Escape.byte (224+n/4096),[Escape.byte (128+n/64%64),Escape.byte (128+n%64)],?_,?_,?_⟩],?_⟩
        · simp [Escape.byte,Nat.mod_eq_of_lt ha] <;> omega
        · simp [Escape.byte,Nat.mod_eq_of_lt hb,Nat.mod_eq_of_lt hc] <;> omega
        · simp [Escape.width,Escape.byte,Nat.mod_eq_of_lt ha]
          all_goals repeat' first | omega | split
        · simp [Escape.encode,h1,h2,h3,bytes,Boundary.bytes,Boundary.Unit.bytes]
      · have ha : 240+n/262144 < 256 := by omega
        have hb : 128+n/4096%64 < 256 := by omega
        have hc : 128+n/64%64 < 256 := by omega
        have hd : 128+n%64 < 256 := by omega
        refine ⟨[⟨Escape.byte (240+n/262144),[Escape.byte (128+n/4096%64),Escape.byte (128+n/64%64),Escape.byte (128+n%64)],?_,?_,?_⟩],?_⟩
        · simp [Escape.byte,Nat.mod_eq_of_lt ha] <;> omega
        · simp [Escape.byte,Nat.mod_eq_of_lt hb,Nat.mod_eq_of_lt hc,Nat.mod_eq_of_lt hd] <;> omega
        · simp [Escape.width,Escape.byte,Nat.mod_eq_of_lt ha]
          all_goals repeat' first | omega | split
        · simp [Escape.encode,h1,h2,h3,bytes,Boundary.bytes,Boundary.Unit.bytes]

theorem scalar_domain (n : Nat) :
    Escape.nativeScalar n < 1114112 ∧
      (Escape.nativeScalar n < 55296 ∨ 57343 < Escape.nativeScalar n) ∧
      0 < Escape.nativeScalar n := by
  unfold Escape.nativeScalar
  split
  · omega
  · split <;> omega

theorem replacement_valid : Valid (Escape.encode 65533) := encode_shape _ (by decide)

theorem whitespace_suffix (units : List Unit) :
    Valid ((bytes units).drop (Escape.nativeWhitespace (bytes units))) := by
  cases units with
  | nil => exact valid_nil
  | cons u us =>
    by_cases ha : u.first.val < 128
    · have hr := Boundary.unit_ascii_singleton u ha
      have hx : bytes (u::us) = u.first::bytes us := by simp [bytes,Boundary.bytes,Boundary.Unit.bytes,hr]
      simp only [hx,Escape.nativeWhitespace]
      split
      · exact ⟨us,rfl⟩
      · split
        · split
          · rename_i h
            have hs : (bytes us).head? = some (Escape.byte 10) := h.2
            cases hu : bytes us with
            | nil => simp [hu] at hs
            | cons b bs =>
              have hb : b = Escape.byte 10 := by simpa [hu] using hs
              obtain ⟨remaining,hrem⟩ := Boundary.ascii_step us b bs hu (by rw [hb]; decide)
              exact ⟨remaining,by simpa [hu] using hrem⟩
          · exact ⟨us,rfl⟩
        · exact ⟨u::us,by simp [hx]⟩
    · have hh : 128 ≤ u.first.val := by omega
      have ne : u.first.val ≠ 32 ∧ u.first.val ≠ 9 ∧ u.first.val ≠ 10 ∧ u.first.val ≠ 12 ∧ u.first.val ≠ 13 := by omega
      exact ⟨u::us,by simp [bytes,Boundary.bytes,Boundary.Unit.bytes,Escape.nativeWhitespace,ne]⟩

theorem escape_valid (units : List Unit) :
    Valid (Escape.native (bytes units)).output ∧
      Valid ((bytes units).drop (Escape.native (bytes units)).count) := by
  cases units with
  | nil => exact ⟨replacement_valid,valid_nil⟩
  | cons u us =>
    have hx : bytes (u::us) = u.first :: (u.rest ++ bytes us) := rfl
    cases hd : HexPrefix.nativeDigit u.first with
    | some d =>
      obtain ⟨remaining,hr⟩ := Boundary.hex_suffix 6 (u::us) (bytes (u::us)) 0 rfl
      have hv := whitespace_suffix remaining
      constructor
      · simpa [hx,Escape.native,hd] using encode_shape (Escape.nativeScalar (HexPrefix.run 6 (bytes (u::us)) 0).value) (scalar_domain _).1
      · have hdrop := HexPrefix.exact_remainder 6 (bytes (u::us)) 0
        have hfinal : Valid ((bytes (u::us)).drop ((HexPrefix.run 6 (bytes (u::us)) 0).count + Escape.nativeWhitespace (HexPrefix.run 6 (bytes (u::us)) 0).rest)) := by
          rw [← List.drop_drop,← hdrop,hr]
          exact hv
        simpa [hx,Escape.native,hd] using hfinal
    | none =>
      by_cases hz : u.first.val = 0
      · have hr := Boundary.unit_ascii_singleton u (by omega)
        simpa [hx,Escape.native,hd,hz,hr] using (show Valid (Escape.encode 65533) ∧ Valid (bytes us) from ⟨replacement_valid,⟨us,rfl⟩⟩)
      · have hw : Escape.width u.first = u.bytes.length := by simpa [Boundary.Unit.bytes,Nat.add_comm] using u.lengthWidth.symm
        have ht : (bytes (u::us)).take (Escape.width u.first) = u.bytes := by change (u.bytes++bytes us).take _ = _; simp [hw]
        have hdro : (bytes (u::us)).drop u.bytes.length = bytes us := by change (u.bytes++bytes us).drop _ = _; simp
        have he : Escape.native (bytes (u::us)) = ⟨u.bytes,u.bytes.length⟩ := by
          rw [hx]
          simp only [Escape.native,hd,hz,↓reduceIte]
          rw [← hx,ht]
        rw [he,hdro]
        exact ⟨⟨[u],by simp [bytes,Boundary.bytes]⟩,⟨us,rfl⟩⟩
theorem string_escape_valid (units : List Unit) :
    Valid (nativeEscape (bytes units)).output ∧
      Valid ((bytes units).drop (nativeEscape (bytes units)).count) := by
  unfold nativeEscape
  split
  · exact ⟨valid_nil,⟨units,by simp⟩⟩
  · split
    · rename_i hn
      have h : referenceNewline (bytes units) = true := by simpa [newline_equivalence] using hn
      have hc := newline_count (bytes units) h
      rw [← Escape.whitespace_reference] at hc
      exact ⟨valid_nil,by simpa only [hc] using whitespace_suffix units⟩
    · exact escape_valid units

theorem copy_prefix (single : Bool) (pre tail : List Byte)
    (h : ∀ b ∈ pre, nativeClass single b = .copy) :
    reference single (pre++tail) = extend pre pre.length (reference single tail) := by
  induction pre with
  | nil => simp [extend]
  | cons b bs ih =>
    have hb := h b (by simp)
    have ht := ih (fun c hc => h c (by simp [hc]))
    simp [reference,← class_equivalence,hb,ht,extend,List.append_assoc,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]

theorem nonascii_copy : ∀ single (b : Byte), 128 ≤ b.val → nativeClass single b = .copy := by decide

theorem unit_copy (single : Bool) (u : Unit) (h : nativeClass single u.first = .copy) :
    ∀ b ∈ u.bytes, nativeClass single b = .copy := by
  intro b hb
  simp only [Boundary.Unit.bytes,List.mem_cons] at hb
  rcases hb with rfl | hb
  · exact h
  · exact nonascii_copy single b (u.continuation b hb).1

theorem noncopy_ascii (single : Bool) (b : Byte) (h : nativeClass single b ≠ .copy) : b.val < 128 := by
  by_cases hn : b.val < 128
  · exact hn
  · have hh := nonascii_copy single b (by omega)
    contradiction

theorem reference_valid (single : Bool) (units : List Unit) :
    Valid (reference single (bytes units)).output ∧
      Valid ((bytes units).drop (reference single (bytes units)).count) := by
  generalize heq : (bytes units).length = n
  induction n using Nat.strongRecOn generalizing units with
  | ind n ih =>
    cases units with
    | nil => simpa [reference,bytes,Boundary.bytes] using (show Valid [] ∧ Valid [] from ⟨valid_nil,valid_nil⟩)
    | cons u us =>
      have shorter : (bytes us).length < n := by
        change (u.first::(u.rest++bytes us)).length = n at heq
        simp only [List.length_cons,List.length_append] at heq
        omega
      have hu : Valid u.bytes := ⟨[u],by simp [bytes,Boundary.bytes]⟩
      by_cases hc : nativeClass single u.first = .copy
      · have cp := copy_prefix single u.bytes (bytes us) (unit_copy single u hc)
        have ht := ih (bytes us).length shorter us rfl
        have hx : bytes (u::us) = u.bytes++bytes us := rfl
        rw [hx,cp]
        constructor
        · exact valid_append hu ht.1
        · simpa [extend,← List.drop_drop] using ht.2
      · have hr := Boundary.unit_ascii_singleton u (noncopy_ascii single u.first hc)
        have hx : bytes (u::us) = u.first::bytes us := by simp [bytes,Boundary.bytes,Boundary.Unit.bytes,hr]
        cases ha : nativeClass single u.first with
        | copy => contradiction
        | close => simpa [hx,reference,← class_equivalence,ha] using (show Valid [] ∧ Valid (bytes us) from ⟨valid_nil,⟨us,rfl⟩⟩)
        | bad => simpa [hx,reference,← class_equivalence,ha] using (show Valid [] ∧ Valid (bytes (u::us)) from ⟨valid_nil,⟨u::us,rfl⟩⟩)
        | nul =>
          have ht := ih (bytes us).length shorter us rfl
          simp only [hx,reference,← class_equivalence,ha,extend]
          constructor
          · exact valid_append replacement_valid ht.1
          · rw [Nat.add_comm 1]
            exact ht.2
        | escape =>
          have he := string_escape_valid us
          obtain ⟨remaining,hrem⟩ := he.2
          have small : (bytes remaining).length < n := by rw [← hrem,List.length_drop]; omega
          have ht := ih (bytes remaining).length small remaining rfl
          rw [← hrem] at ht
          constructor
          · simpa [hx,reference,← class_equivalence,ha,← escape_equivalence,extend] using valid_append he.1 ht.1
          · simpa [hx,reference,← class_equivalence,ha,← escape_equivalence,extend,← List.drop_drop,Nat.add_assoc] using ht.2

theorem owned_return_valid (single : Bool) (units : List Unit) (buffer : List Byte) (hb : Valid buffer) :
    Valid (owned single (bytes units) buffer).output := by
  rw [owned_reference]
  exact valid_append hb (reference_valid single units).1

theorem borrowed_return_valid (single : Bool) (units : List Unit) :
    Valid (borrowed single (bytes units) []).value.output := by
  rw [borrowed_reference]
  simpa [extend] using (reference_valid single units).1
theorem owned_copy_prefix (single : Bool) (pre tail buffer : List Byte)
    (h : ∀ b ∈ pre, nativeClass single b = .copy) :
    owned single (pre++tail) buffer = extend [] pre.length (owned single tail (buffer++pre)) := by
  rw [owned_reference,copy_prefix single pre tail h,owned_reference]
  simp [extend,List.append_assoc]

theorem partial_copy_rejoin (single : Bool) (u : Unit) (pre post : List Byte)
    (splitUnit : u.bytes = pre++post) (copyUnit : nativeClass single u.first = .copy)
    (remaining : List Unit) (buffer : List Byte) :
    owned single (post++bytes remaining) (buffer++pre) =
      extend [] post.length (owned single (bytes remaining) (buffer++u.bytes)) := by
  have hc : ∀ b ∈ post, nativeClass single b = .copy := by
    intro b hb
    apply unit_copy single u copyUnit b
    simp [splitUnit,hb]
  rw [owned_copy_prefix single post (bytes remaining) (buffer++pre) hc]
  simp [splitUnit,List.append_assoc]

theorem partial_copy_return_valid (single : Bool) (u : Unit) (pre post : List Byte)
    (splitUnit : u.bytes = pre++post) (copyUnit : nativeClass single u.first = .copy)
    (remaining : List Unit) (buffer : List Byte) (hb : Valid buffer) :
    Valid (owned single (post++bytes remaining) (buffer++pre)).output := by
  rw [partial_copy_rejoin single u pre post splitUnit copyUnit remaining buffer]
  simpa [extend] using owned_return_valid single remaining (buffer++u.bytes)
    (valid_append hb ⟨[u],by simp [bytes,Boundary.bytes]⟩)
end StringUTF8
