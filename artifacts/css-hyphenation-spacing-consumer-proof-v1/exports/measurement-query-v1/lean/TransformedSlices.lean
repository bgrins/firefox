import RangeProvider
import Buffer

namespace HyphenTransformedSlices

open HyphenRangeProvider LanguageBreak

def keptPrefix (source : List Cell) (offset : Nat) : Nat :=
  ((source.take offset).filter fun c => !c.skipped).length

theorem filter_drop_by_prefix (source : List α) (keep : α → Bool) (start : Nat) :
    (source.filter keep).drop ((source.take start).filter keep).length =
      (source.drop start).filter keep := by
  have decomposition := congrArg (fun xs => xs.filter keep) (List.take_append_drop start source)
  simp only [List.filter_append] at decomposition
  rw [← decomposition,List.drop_left]

theorem filter_take_by_prefix (source : List α) (keep : α → Bool) (count : Nat) :
    (source.filter keep).take ((source.take count).filter keep).length =
      (source.take count).filter keep := by
  have decomposition := congrArg (fun xs => xs.filter keep) (List.take_append_drop count source)
  simp only [List.filter_append] at decomposition
  rw [← decomposition,List.take_left]

theorem filtered_prefix_length (source : List α) (keep : α → Bool) (start finish : Nat)
    (ordered : start ≤ finish) :
    ((source.take finish).filter keep).length =
      ((source.take start).filter keep).length +
        (((source.drop start).take (finish-start)).filter keep).length := by
  have offset : finish = start+(finish-start) := by omega
  conv =>
    lhs
    rw [offset,List.take_add]
  simp

theorem native_skip_slice_reference (source : List Cell) (start finish : Nat)
    (ordered : start ≤ finish) :
    ((source.filter fun c => !c.skipped).drop (keptPrefix source start)).take
      (keptPrefix source finish-keptPrefix source start) =
        ((source.drop start).take (finish-start)).filter (fun c => !c.skipped) := by
  unfold keptPrefix
  rw [filtered_prefix_length source _ start finish ordered]
  simp only [Nat.add_sub_cancel_left]
  rw [filter_drop_by_prefix,filter_take_by_prefix]

theorem clamped_slice_reference (source : List Cell) (start finish : Nat)
    (ordered : start ≤ finish) :
    ((source.filter fun c => !c.skipped).drop (keptPrefix source (min start source.length))).take
      (keptPrefix source (min finish source.length)-keptPrefix source (min start source.length)) =
    ((source.drop (min start source.length)).take (min finish source.length-min start source.length)).filter
      (fun c => !c.skipped) :=
  native_skip_slice_reference source _ _ (by omega)

def nativeUnits (decodeCell : Cell → CodeUnit) (source : List Cell) : List CodeUnit :=
  (source.filter fun c => !c.skipped).map decodeCell

def slicedUnits (decodeCell : Cell → CodeUnit) (source : List Cell) (start finish : Nat) : List CodeUnit :=
  ((nativeUnits decodeCell source).drop (keptPrefix source (min start source.length))).take
    (keptPrefix source (min finish source.length)-keptPrefix source (min start source.length))

theorem rangeSlice_decode_equals_contributed_cells (decodeCell : Cell → CodeUnit) (source : List Cell)
    (start finish policy : Nat) (ordered : start ≤ finish) :
    slicedUnits decodeCell source start finish =
      (contribute ⟨policy,(source.drop (min start source.length)).take
        (min finish source.length-min start source.length)⟩).map (fun owned => decodeCell owned.cell) := by
  unfold slicedUnits nativeUnits
  rw [← List.map_drop,← List.map_take,clamped_slice_reference source start finish ordered]
  simp [contribute,List.map_map]

theorem slice_of_parts (before middle after : List α) :
    ((before ++ middle ++ after).drop before.length).take middle.length = middle := by
  simp [List.append_assoc]

def sliceStorage (stored : StoredUnits) (start length : Nat) : StoredUnits :=
  match stored with
  | .bytes units => .bytes ((units.drop start).take length)
  | .utf16 units => .utf16 ((units.drop start).take length)

theorem slice_storage_decodes (stored : StoredUnits) (start length : Nat) :
    (sliceStorage stored start length).decode = (stored.decode.drop start).take length := by
  cases stored <;> simp [sliceStorage,StoredUnits.decode,List.map_take,List.map_drop]

theorem whole_buffer_binding_implies_range_admission (decodeCell : Cell → CodeUnit)
    (source : List Cell) (stored : StoredUnits) (start finish policy : Nat)
    (binding : stored.decode = nativeUnits decodeCell source) (ordered : start ≤ finish) :
    (sliceStorage stored (keptPrefix source (min start source.length))
      (keptPrefix source (min finish source.length)-keptPrefix source (min start source.length))).decode =
    (contribute ⟨policy,(source.drop (min start source.length)).take
      (min finish source.length-min start source.length)⟩).map (fun owned => decodeCell owned.cell) := by
  rw [slice_storage_decodes,binding]
  exact rangeSlice_decode_equals_contributed_cells decodeCell source start finish policy ordered

theorem bounded_slice_in_context (before whole after : List α) (start count : Nat)
    (bounded : start + count ≤ whole.length) :
    ((before ++ whole ++ after).drop (before.length+start)).take count =
      (whole.drop start).take count := by
  have prefixDrop : (before ++ whole ++ after).drop (before.length+start) = (whole++after).drop start := by
    rw [← List.drop_drop]
    simp [List.append_assoc]
  rw [prefixDrop,List.drop_append_of_le_length (by omega)]
  exact List.take_append_of_le_length (by simp; omega)

theorem kept_prefix_bound (source : List Cell) (offset : Nat) :
    keptPrefix source offset ≤ (source.filter fun c => !c.skipped).length := by
  have parts := congrArg (fun xs => (xs.filter fun c => !c.skipped).length)
    (List.take_append_drop offset source)
  simp only [List.filter_append,List.length_append] at parts
  unfold keptPrefix
  omega

theorem multi_flow_range_admission (decodeCell : Cell → CodeUnit) (before after : List CodeUnit)
    (source : List Cell) (stored : StoredUnits) (start finish policy : Nat)
    (binding : stored.decode = before ++ nativeUnits decodeCell source ++ after)
    (ordered : start ≤ finish) :
    (sliceStorage stored (before.length + keptPrefix source (min start source.length))
      (keptPrefix source (min finish source.length)-keptPrefix source (min start source.length))).decode =
    (contribute ⟨policy,(source.drop (min start source.length)).take
      (min finish source.length-min start source.length)⟩).map (fun owned => decodeCell owned.cell) := by
  rw [slice_storage_decodes,binding,bounded_slice_in_context]
  · exact rangeSlice_decode_equals_contributed_cells decodeCell source start finish policy ordered
  · have first := kept_prefix_bound source (min start source.length)
    have last := kept_prefix_bound source (min finish source.length)
    simp only [nativeUnits,List.length_map]
    omega

theorem clamped_content_offset_rebases (base offset length : Nat) (atOrAfter : base ≤ offset) :
    min offset (base+length)-base = min (offset-base) length := by omega

theorem mapped_flow_content_coordinates (decodeCell : Cell → CodeUnit) (before after : List CodeUnit)
    (source : List Cell) (stored : StoredUnits) (base start finish policy : Nat)
    (binding : stored.decode = before ++ nativeUnits decodeCell source ++ after)
    (atOrAfter : base ≤ start) (ordered : start ≤ finish) :
    (sliceStorage stored (before.length + keptPrefix source (min start (base+source.length)-base))
      (keptPrefix source (min finish (base+source.length)-base)-
       keptPrefix source (min start (base+source.length)-base))).decode =
    (contribute ⟨policy,(source.drop (min start (base+source.length)-base)).take
      ((min finish (base+source.length)-base)-(min start (base+source.length)-base))⟩).map
        (fun owned => decodeCell owned.cell) := by
  rw [clamped_content_offset_rebases base start source.length atOrAfter,
    clamped_content_offset_rebases base finish source.length (by omega)]
  exact multi_flow_range_admission decodeCell before after source stored (start-base) (finish-base)
    policy binding (by omega)

end HyphenTransformedSlices
