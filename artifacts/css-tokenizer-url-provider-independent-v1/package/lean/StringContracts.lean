import StringUTF8
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace StringContracts
open StringTransitions
abbrev Byte := CommentScan.Byte

theorem bad_class : ∀ single (b : Byte), referenceClass single b = .bad →
    nativeNewline [b] = true := by decide

theorem bad_newline (single : Bool) (xs : List Byte)
    (h : (reference single xs).ending = .bad) :
    nativeNewline (xs.drop (reference single xs).count) = true := by
  induction xs using reference.induct single with
  | case1 => simp [reference] at h
  | case2 b bs hc => simp [reference,hc] at h
  | case3 b bs hc =>
    have hn := bad_class single b hc
    simpa [reference,hc,nativeNewline] using hn
  | case4 b bs hc ih =>
    have ht := ih (by simpa [reference,hc,extend] using h)
    simpa [reference,hc,extend,Nat.add_comm 1] using ht
  | case5 b bs hc ih =>
    have ht := ih (by simpa [reference,hc,extend] using h)
    simpa [reference,hc,extend,Nat.add_comm 1] using ht
  | case6 b bs hc e ih =>
    dsimp [e] at ih
    have ht := ih (by simpa [reference,hc,extend] using h)
    simpa [reference,hc,extend,← List.drop_drop,Nat.add_assoc] using ht

theorem eof_exhausts (single : Bool) (xs : List Byte)
    (h : (reference single xs).ending = .eof) : (reference single xs).count = xs.length := by
  induction xs using reference.induct single with
  | case1 => simp [reference]
  | case2 b bs hc => simp [reference,hc] at h
  | case3 b bs hc => simp [reference,hc] at h
  | case4 b bs hc ih =>
    have ht := ih (by simpa [reference,hc,extend] using h)
    simp [reference,hc,extend,ht,Nat.add_comm]
  | case5 b bs hc ih =>
    have ht := ih (by simpa [reference,hc,extend] using h)
    simp [reference,hc,extend,ht,Nat.add_comm]
  | case6 b bs hc e ih =>
    dsimp [e] at ih
    have ht := ih (by simpa [reference,hc,extend] using h)
    have hb := escape_bound bs
    rw [escape_equivalence] at hb
    simp only [List.length_drop] at ht
    simp [reference,hc,extend]; omega

def terminatorLength (ending : Ending) : Nat := if ending = .closed then 1 else 0

theorem borrowed_slice (single : Bool) (xs pre : List Byte)
    (h : (borrowed single xs pre).allocated = false) :
    ∃ n, n ≤ xs.length ∧
      (borrowed single xs pre).value.output = pre ++ xs.take n ∧
      (borrowed single xs pre).value.count = n+terminatorLength (borrowed single xs pre).value.ending := by
  induction xs generalizing pre with
  | nil => exact ⟨0,by simp,by simp [borrowed],by simp [borrowed,terminatorLength]⟩
  | cons b bs ih =>
    cases hc : nativeClass single b with
    | close => exact ⟨0,by simp,by simp [borrowed,hc],by simp [borrowed,hc,terminatorLength]⟩
    | bad => exact ⟨0,by simp,by simp [borrowed,hc],by simp [borrowed,hc,terminatorLength]⟩
    | nul => simp [borrowed,hc] at h
    | escape => simp [borrowed,hc] at h
    | copy =>
      have hh : (borrowed single bs (pre++[b])).allocated = false := by simpa [borrowed,hc] using h
      obtain ⟨n,hn,ho,he⟩ := ih (pre++[b]) hh
      refine ⟨n+1,by simp; omega,?_,?_⟩
      · simpa [borrowed,hc,extend,List.append_assoc] using ho
      · simp [borrowed,hc,extend,he,terminatorLength]
        omega

def nativeRaw (input : List Byte) : Option NativeValue :=
  match input with
  | 34::tail => let r := borrowed false tail []; some ⟨extend [] 1 r.value,r.allocated⟩
  | 39::tail => let r := borrowed true tail []; some ⟨extend [] 1 r.value,r.allocated⟩
  | _ => none

def referenceRaw (input : List Byte) : Option Value :=
  match input with
  | [] => none
  | b::tail =>
    if ([34,39] : List Byte).contains b then some (extend [] 1 (reference (b == 39) tail)) else none

theorem raw_reference (input : List Byte) : (nativeRaw input).map NativeValue.value = referenceRaw input := by
  cases input with
  | nil => rfl
  | cons b tail =>
    by_cases h34 : b = 34 <;> by_cases h39 : b = 39 <;>
      simp_all [nativeRaw,referenceRaw,borrowed_reference,extend]

theorem raw_progress (input : List Byte) (v : NativeValue) (h : nativeRaw input = some v) :
    1 ≤ v.value.count ∧ v.value.count ≤ input.length := by
  cases input with
  | nil => simp [nativeRaw] at h
  | cons b tail =>
    by_cases h34 : b = 34
    · subst b
      have hb := reference_bound false tail
      simp [nativeRaw,borrowed_reference,extend] at h
      cases h
      simp [borrowed_reference,extend]
      omega
    · by_cases h39 : b = 39
      · subst b
        have hb := reference_bound true tail
        simp [nativeRaw,borrowed_reference,extend] at h
        cases h
        simp [borrowed_reference,extend]
        omega
      · simp [nativeRaw,h34,h39] at h
end StringContracts
