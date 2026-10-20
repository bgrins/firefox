import ScanOutput

namespace VariableOrigin

def directOutput (text : List Char) (tainted : Bool) (collectTaint : Bool) : Output :=
  ⟨text, if tainted && collectTaint then [⟨0,byteLength text⟩] else [], tainted⟩

theorem direct_safe (text : List Char) (tainted collectTaint : Bool) :
    OutputSafe (directOutput text tainted collectTaint) := by
  intro r hr
  cases tainted <;> cases collectTaint <;> simp [directOutput] at hr
  subst r
  exact ⟨Nat.zero_le _, boundary_zero _, boundary_end _⟩

theorem direct_payload_and_provenance (text : List Char) (tainted collectTaint : Bool) :
    (directOutput text tainted collectTaint).text = text ∧
    (directOutput text tainted collectTaint).aggregate = tainted := by
  exact ⟨rfl,rfl⟩

theorem direct_empty_taint :
    (directOutput [] true true).ranges = [⟨0,0⟩] ∧
    (directOutput [] true true).aggregate = true := by decide

def stripEmptyRanges (rs : List Range) : List Range := rs.filter (fun r => r.start != r.stop)

theorem direct_vs_append (text : List Char) (tainted : Bool) :
    let direct := directOutput text tainted true
    let appended := appendPiece ⟨[],[],false⟩ ⟨text,tainted,false⟩
    direct.text = appended.text ∧ direct.aggregate = appended.aggregate ∧
    stripEmptyRanges direct.ranges = stripEmptyRanges appended.ranges := by
  cases text <;> cases tainted <;>
    simp [directOutput,appendPiece,separatorText,stripEmptyRanges]

def wholeReference (start limit : Nat) (rs : List ReferenceSpan) : Option ReferenceSpan :=
  match rs with
  | [r] => if r.start == start && r.stop == limit then some r else none
  | _ => none

def nativeDispatch (text : List Char) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) (cursor limit : Nat) (rs : List ReferenceSpan)
    (collectTaint : Bool) : Except Unit Output :=
  if cursor == limit then .ok ⟨[],[],false⟩ else
  if rs.isEmpty then .ok (directOutput (byteSlice text cursor limit) false false) else
  match wholeReference cursor limit rs with
  | some r =>
      match provider r with
      | .error e => .error e
      | .ok p => .ok (directOutput p.text p.tainted collectTaint)
  | none =>
      match executeScan text provider separator cursor limit rs with
      | .error e => .error e
      | .ok result => .ok (if collectTaint then result else { result with ranges := [] })

theorem native_dispatch_safe (text : List Char) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) (cursor limit : Nat) (rs : List ReferenceSpan)
    (collectTaint : Bool) (result : Output)
    (success : nativeDispatch text provider separator cursor limit rs collectTaint = .ok result) :
    OutputSafe result := by
  unfold nativeDispatch at success
  split at success
  · cases success
    intro r hr
    simp at hr
  · split at success
    · cases success
      exact direct_safe _ _ _
    · split at success
      next r heq =>
        cases hp : provider r with
        | error e => simp [hp] at success
        | ok p =>
            simp only [hp,Except.ok.injEq] at success
            subst result
            exact direct_safe _ _ _
      next heq =>
        cases h : scanPieces text provider separator cursor limit rs with
        | error e => simp [executeScan,h] at success
        | ok ps =>
            simp only [executeScan,h,Except.ok.injEq] at success
            cases collectTaint with
            | false =>
                simp only [Bool.false_eq_true,↓reduceIte] at success
                subst result
                intro r hr
                simp at hr
            | true =>
                simp only [↓reduceIte] at success
                subst result
                exact output_history_safe _ _ (by intro r hr; simp at hr)

theorem whole_covers_only (tree : Component) (valid : ValidHeaders tree)
    (r : ReferenceSpan) (rs : List ReferenceSpan)
    (list : outerSpans tree = r :: rs) (whole : r.stop = byteLength (render tree)) : rs = [] := by
  have separated := outer_separated tree
  rw [list] at separated
  have next := (List.pairwise_cons.mp separated).1
  cases rs with
  | nil => rfl
  | cons s ss =>
      have mem : s ∈ referenceSpans tree := outer_mem_all tree s (by rw [list]; simp)
      have hs := (spans_ordered tree valid s mem).1
      have he := boundary_le (span_boundaries tree s mem).2.1
      have hn := next s (by simp)
      unfold Separated at hn
      omega

end VariableOrigin
