import StringTrace
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace StringAdmission
open StringTransitions
abbrev Byte := CommentScan.Byte

theorem encoded_length (n : Nat) : (Escape.encode n).length ≤ 4 := by
  unfold Escape.encode
  repeat' first | split | simp_all

theorem generic_escape_output_bound (xs : List Byte) : (Escape.native xs).output.length ≤ 4 := by
  cases xs with
  | nil => simpa [Escape.native] using encoded_length 65533
  | cons b bs =>
    cases hd : HexPrefix.nativeDigit b with
    | some d => simpa [Escape.native,hd] using encoded_length (Escape.nativeScalar (HexPrefix.run 6 (b::bs) 0).value)
    | none =>
      by_cases hz : b.val = 0
      · simpa [Escape.native,hd,hz] using encoded_length 65533
      · have hw : ∀ b : Byte, Escape.width b ≤ 4 := by decide
        simp only [Escape.native,hd,hz,↓reduceIte,List.length_take]
        exact Nat.le_trans (Nat.min_le_left _ _) (hw b)

theorem escape_output_bound (xs : List Byte) : (nativeEscape xs).output.length ≤ 4 := by
  unfold nativeEscape
  split
  · simp
  · split
    · simp
    · exact generic_escape_output_bound xs

theorem output_bound (single : Bool) (xs : List Byte) :
    (reference single xs).output.length ≤ 4*xs.length := by
  induction xs using reference.induct single with
  | case1 => simp [reference]
  | case2 b bs h => simp [reference,h]
  | case3 b bs h => simp [reference,h]
  | case4 b bs h ih =>
    have hr : (Escape.encode 65533).length = 3 := by decide
    simp [reference,h,extend,hr]; omega
  | case5 b bs h ih => simp [reference,h,extend]; omega
  | case6 b bs h e ih =>
    have he := escape_output_bound bs
    rw [escape_equivalence] at he
    dsimp [e] at ih
    simp only [List.length_drop] at ih
    simp [reference,h,extend]; omega

theorem owned_output_bound (single : Bool) (xs buffer : List Byte) :
    (owned single xs buffer).output.length ≤ buffer.length+4*xs.length := by
  rw [owned_reference]
  simp only [extend,List.length_append]
  have h := output_bound single xs
  omega

theorem raw_valid (units : List Boundary.Unit) (v : NativeValue)
    (h : StringContracts.nativeRaw (Boundary.bytes units) = some v) : StringUTF8.Valid v.value.output := by
  cases hi : Boundary.bytes units with
  | nil => simp [hi,StringContracts.nativeRaw] at h
  | cons b tail =>
    by_cases h34 : b = 34
    · subst b
      obtain ⟨remaining,hr⟩ := Boundary.ascii_step units 34 tail hi (by decide)
      have hv := StringUTF8.borrowed_return_valid false remaining
      simp [hi,StringContracts.nativeRaw] at h
      cases h
      simpa [hr,extend] using hv
    · by_cases h39 : b = 39
      · subst b
        obtain ⟨remaining,hr⟩ := Boundary.ascii_step units 39 tail hi (by decide)
        have hv := StringUTF8.borrowed_return_valid true remaining
        simp [hi,StringContracts.nativeRaw] at h
        cases h
        simpa [hr,extend] using hv
      · simp [hi,StringContracts.nativeRaw,h34,h39] at h

def nativeRawObserved (input : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) : Option StringTrace.Observed :=
  match input with
  | 34::tail =>
    let r := StringTrace.nativeObserved false tail (CommentObservers.advance 1 s) urls
    some ⟨extend [] 1 r.value,r.state,r.urls⟩
  | 39::tail =>
    let r := StringTrace.nativeObserved true tail (CommentObservers.advance 1 s) urls
    some ⟨extend [] 1 r.value,r.state,r.urls⟩
  | _ => none

def referenceRawObserved (input : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) : Option StringTrace.Observed :=
  (StringContracts.referenceRaw input).map (fun v =>
    ⟨v,CommentObservers.referenceObserve (input.take v.count) s,urls⟩)

theorem quote_observer (single : Bool) (tail : List Byte) (s : CommentObservers.State) :
    CommentObservers.referenceObserve (quote single::tail) s =
      CommentObservers.referenceObserve tail (CommentObservers.advance 1 s) := by
  have v34 : (34 : Byte).val = 34 := rfl
  have v39 : (39 : Byte).val = 39 := rfl
  cases single <;> simp [v34,v39,quote,CommentObservers.referenceObserve,CommentObservers.referenceStep,
    CommentObservers.referenceWidth,CommentObservers.advance]

theorem raw_observer_reference (input : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) :
    nativeRawObserved input s urls = referenceRawObserved input s urls := by
  cases input with
  | nil => rfl
  | cons b tail =>
    by_cases h34 : b = 34
    · subst b
      have ho := quote_observer false (tail.take (reference false tail).count) s
      simp only [quote,Bool.false_eq_true,↓reduceIte] at ho
      simp [nativeRawObserved,referenceRawObserved,StringContracts.referenceRaw,StringTrace.observer_reference,
        StringTrace.referenceObserved,extend,Nat.add_comm 1,ho]
    · by_cases h39 : b = 39
      · subst b
        have ho := quote_observer true (tail.take (reference true tail).count) s
        simp only [quote,↓reduceIte] at ho
        simp [nativeRawObserved,referenceRawObserved,StringContracts.referenceRaw,StringTrace.observer_reference,
          StringTrace.referenceObserved,extend,Nat.add_comm 1,ho]
      · simp [nativeRawObserved,referenceRawObserved,StringContracts.referenceRaw,h34,h39]
end StringAdmission
