import ByteSlices
import Output

namespace VariableOrigin

def cleanPiece (text : List Char) (separator : Bool) : Piece := ⟨text,false,separator⟩

def scanPieces (text : List Char) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) (cursor limit : Nat) : List ReferenceSpan → Except Unit (List Piece)
  | [] => .ok [cleanPiece (byteSlice text cursor limit) (separator cursor)]
  | r :: rs =>
      match provider r with
      | .error e => .error e
      | .ok replacement =>
          match scanPieces text provider separator r.stop limit rs with
          | .error e => .error e
          | .ok tail => .ok (cleanPiece (byteSlice text cursor r.start) (separator cursor) :: replacement :: tail)

inductive ReplacementReading (text : List Char) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) : Nat → Nat → List ReferenceSpan → List Piece → Prop where
  | done (cursor limit : Nat) (inside : List Char)
      (slice : ∃ before after, text = before ++ inside ++ after ∧
        byteLength before = cursor ∧ byteLength (before ++ inside) = limit) :
      ReplacementReading text provider separator cursor limit [] [cleanPiece inside (separator cursor)]
  | next (cursor limit : Nat) (r : ReferenceSpan) (rs : List ReferenceSpan)
      (before removed : List Char) (replacement : Piece) (tail : List Piece)
      (cleanRead : ∃ left right, text = left ++ before ++ right ∧
        byteLength left = cursor ∧ byteLength (left ++ before) = r.start)
      (original : ∃ left right, text = left ++ removed ++ right ∧
        byteLength left = r.start ∧ byteLength (left ++ removed) = r.stop)
      (selected : provider r = .ok replacement)
      (rest : ReplacementReading text provider separator r.stop limit rs tail) :
      ReplacementReading text provider separator cursor limit (r :: rs)
        (cleanPiece before (separator cursor) :: replacement :: tail)

theorem reading_erases (text : List Char) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) (cursor limit : Nat) (rs : List ReferenceSpan) (pieces : List Piece)
    (h : ReplacementReading text provider separator cursor limit rs pieces) :
    scanPieces text provider separator cursor limit rs = .ok pieces := by
  induction h with
  | done cursor limit inside slice =>
      obtain ⟨before,after,rfl,rfl,rfl⟩ := slice
      simp only [scanPieces,slice_exact]
  | next cursor limit r rs before removed replacement tail cleanRead original selected rest ih =>
      obtain ⟨left,right,eq,hstart,hstop⟩ := cleanRead
      have exactSlice : byteSlice text cursor r.start = before := by
        rw [eq,← hstart,← hstop,slice_exact]
      simp [scanPieces,selected,ih,exactSlice]

theorem safe_scan_has_reading (text : List Char) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) (cursor limit : Nat) (rs : List ReferenceSpan)
    (safe : ScanSafe text cursor limit rs) (pieces : List Piece)
    (success : scanPieces text provider separator cursor limit rs = .ok pieces) :
    ReplacementReading text provider separator cursor limit rs pieces := by
  induction rs generalizing cursor pieces with
  | nil =>
      simp only [scanPieces,Except.ok.injEq] at success
      subst pieces
      obtain ⟨before,inside,after,eq,hs,he⟩ := safe
      have exactSlice : byteSlice text cursor limit = inside := by
        rw [eq,← hs,← he,slice_exact]
      rw [exactSlice]
      exact ReplacementReading.done _ _ inside ⟨before,after,eq,hs,he⟩
  | cons r rs ih =>
      obtain ⟨cleanRead,original,tailSafe⟩ := safe
      cases hp : provider r with
      | error e => simp [scanPieces,hp] at success
      | ok replacement =>
          cases ht : scanPieces text provider separator r.stop limit rs with
          | error e => simp [scanPieces,hp,ht] at success
          | ok tail =>
              simp only [scanPieces,hp,ht,Except.ok.injEq] at success
              subst pieces
              obtain ⟨a,b,c,eq,hs,he⟩ := cleanRead
              have exactSlice : byteSlice text cursor r.start = b := by
                rw [eq,← hs,← he,slice_exact]
              rw [exactSlice]
              obtain ⟨d,e,f,eq2,hs2,he2⟩ := original
              exact ReplacementReading.next _ _ _ _ b e replacement tail
                ⟨a,c,eq,hs,he⟩ ⟨d,f,eq2,hs2,he2⟩ hp (ih _ tailSafe _ ht)

def executeScan (text : List Char) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) (cursor limit : Nat) (rs : List ReferenceSpan) : Except Unit Output :=
  match scanPieces text provider separator cursor limit rs with
  | .error e => .error e
  | .ok pieces => .ok (pieces.foldl appendPiece ⟨[],[],false⟩)

theorem constructed_substitution_output (tree : Component) (valid : ValidHeaders tree)
    (provider : ReferenceSpan → Except Unit Piece) (separator : Nat → Bool)
    (result : Output)
    (success : executeScan (render tree) provider separator 0 (byteLength (render tree))
      (outerSpans tree) = .ok result) :
    ∃ pieces,
      ReplacementReading (render tree) provider separator 0 (byteLength (render tree))
        (outerSpans tree) pieces ∧
      result.text = referenceText pieces ∧ result.ranges = referenceRanges 0 pieces ∧
      result.aggregate = anyTaint pieces ∧ OutputSafe result := by
  cases h : scanPieces (render tree) provider separator 0 (byteLength (render tree)) (outerSpans tree) with
  | error e => simp [executeScan,h] at success
  | ok pieces =>
      simp only [executeScan,h,Except.ok.injEq] at success
      subst result
      have projection := output_history_refinement pieces ⟨[],[],false⟩
      refine ⟨pieces,safe_scan_has_reading _ _ _ _ _ _ (constructed_chunk_scan tree valid) _ h,?_,?_,?_,?_⟩
      · simpa using projection.1
      · simpa using projection.2.1
      · simpa using projection.2.2
      · exact output_history_safe pieces _ (by intro r hr; simp at hr)

theorem failed_provider_no_publication (text : List Char) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) (cursor limit : Nat) (r : ReferenceSpan) (rs : List ReferenceSpan)
    (failure : provider r = .error ()) :
    executeScan text provider separator cursor limit (r::rs) = .error () := by
  simp [executeScan,scanPieces,failure]

end VariableOrigin
