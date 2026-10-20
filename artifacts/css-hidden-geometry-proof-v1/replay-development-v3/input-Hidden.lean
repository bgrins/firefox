import Std

namespace Hidden

structure Size where
  i : Int
  b : Int
  deriving DecidableEq, Repr

structure Key where
  computed : Size
  containingBlock : Size
  borderIStart : Int
  borderIEnd : Int
  borderBStart : Int
  borderBEnd : Int
  minB : Int
  maxB : Int
  availableB : Int
  deriving DecidableEq, Repr

structure Measurement where
  key : Key
  bSize : Int
  deriving DecidableEq, Repr

structure Frame where
  dirty : Bool
  geometry : Size
  cache : Option Measurement
  deriving DecidableEq, Repr

structure Result where
  frame : Frame
  measuredB : Int
  reused : Bool
  deriving DecidableEq, Repr

def zero : Size := ⟨0, 0⟩

def cacheableB (k : Key) (output : Size) : Int :=
  max 0 (output.b - (k.borderBStart + k.borderBEnd))

def canReuse (k : Key) (f : Frame) : Bool :=
  !f.dirty && match f.cache with
    | none => false
    | some cached => decide (cached.key = k)

def measure (repair hidden : Bool) (layout : Key → Size) (k : Key)
    (f : Frame) : Result :=
  if canReuse k f then
    ⟨f, (f.cache.getD ⟨k, 0⟩).bSize, true⟩
  else
    let marked := f.dirty || (repair && hidden)
    let output := if hidden then zero else layout k
    let dirty := if hidden then marked else false
    let measured := cacheableB k output
    ⟨⟨dirty, output, some ⟨k, measured⟩⟩, measured, false⟩

def geometryQuery (hasHiddenAncestor : Bool) (layout : Key → Size)
    (forcedKey : Key) (f : Frame) : Frame :=
  if f.dirty && hasHiddenAncestor then
    (measure false false layout forcedKey f).frame
  else f

def fixedBlock (k : Key) : Size :=
  ⟨k.computed.i + k.borderIStart + k.borderIEnd,
   max k.minB (min k.maxB k.computed.b) + k.borderBStart + k.borderBEnd⟩

theorem dirty_misses (k : Key) (f : Frame) (h : f.dirty = true) :
    canReuse k f = false := by simp [canReuse, h]

theorem absent_misses (k : Key) (f : Frame) (h : f.cache = none) :
    canReuse k f = false := by simp [canReuse, h]

theorem changed_key_misses (k : Key) (f : Frame) (cached : Measurement)
    (hc : f.cache = some cached) (hk : cached.key ≠ k) :
    canReuse k f = false := by simp [canReuse, hc, hk]

theorem clean_hit (repair hidden : Bool) (layout : Key → Size) (k : Key)
    (f : Frame) (cached : Measurement) (hd : f.dirty = false)
    (hc : f.cache = some cached) (hk : cached.key = k) :
    measure repair hidden layout k f = ⟨f, cached.bSize, true⟩ := by
  simp [measure, canReuse, hd, hc, hk]

theorem valid_reuse_preserves_geometry (repair hidden : Bool)
    (layout : Key → Size) (k : Key) (f : Frame) (h : canReuse k f = true) :
    (measure repair hidden layout k f).frame = f := by simp [measure, h]

theorem no_effect_on_hits (hidden : Bool) (layout : Key → Size)
    (k : Key) (f : Frame) (h : canReuse k f = true) :
    measure true hidden layout k f = measure false hidden layout k f := by
  simp [measure, h]

theorem no_effect_when_not_hidden (layout : Key → Size) (k : Key) (f : Frame) :
    measure true false layout k f = measure false false layout k f := by
  simp [measure]

theorem no_effect_when_already_dirty (hidden : Bool) (layout : Key → Size)
    (k : Key) (f : Frame) (hd : f.dirty = true) :
    measure true hidden layout k f = measure false hidden layout k f := by
  simp [measure, canReuse, hd]

theorem old_hidden_miss_retains_clean (layout : Key → Size) (k : Key)
    (f : Frame) (hd : f.dirty = false) (miss : canReuse k f = false) :
    (measure false true layout k f).frame.dirty = false := by
  simp [measure, miss, hd]

theorem hidden_miss_publishes_zero (repair : Bool) (layout : Key → Size)
    (k : Key) (f : Frame) (miss : canReuse k f = false) :
    (measure repair true layout k f).frame.geometry = zero := by
  simp [measure, miss]

theorem repaired_hidden_miss_stays_dirty (layout : Key → Size) (k : Key)
    (f : Frame) (miss : canReuse k f = false) :
    (measure true true layout k f).frame.dirty = true := by
  simp [measure, miss]

theorem cache_records_observed_output (repair hidden : Bool)
    (layout : Key → Size) (k : Key) (f : Frame) (miss : canReuse k f = false) :
    (measure repair hidden layout k f).frame.cache =
      some ⟨k, cacheableB k (if hidden then zero else layout k)⟩ := by
  simp [measure, miss]

theorem clean_query_is_noop (hasHiddenAncestor : Bool) (layout : Key → Size)
    (forcedKey : Key) (f : Frame) (hd : f.dirty = false) :
    geometryQuery hasHiddenAncestor layout forcedKey f = f := by
  simp [geometryQuery, hd]

theorem no_hidden_ancestor_no_force (layout : Key → Size) (forcedKey : Key)
    (f : Frame) : geometryQuery false layout forcedKey f = f := by
  simp [geometryQuery]

theorem dirty_query_uses_actual_provider (layout : Key → Size)
    (forcedKey : Key) (f : Frame) (hd : f.dirty = true) :
    (geometryQuery true layout forcedKey f).geometry = layout forcedKey := by
  simp [geometryQuery, measure, canReuse, hd]

theorem dirty_query_completes_clean (layout : Key → Size)
    (forcedKey : Key) (f : Frame) (hd : f.dirty = true) :
    (geometryQuery true layout forcedKey f).dirty = false := by
  simp [geometryQuery, measure, canReuse, hd]

theorem repaired_hidden_miss_recovers (layout : Key → Size)
    (k forcedKey : Key) (f : Frame) (miss : canReuse k f = false) :
    (geometryQuery true layout forcedKey
      (measure true true layout k f).frame).geometry = layout forcedKey := by
  apply dirty_query_uses_actual_provider
  exact repaired_hidden_miss_stays_dirty layout k f miss

theorem repaired_hidden_miss_clears_after_recovery (layout : Key → Size)
    (k forcedKey : Key) (f : Frame) (miss : canReuse k f = false) :
    (geometryQuery true layout forcedKey
      (measure true true layout k f).frame).dirty = false := by
  apply dirty_query_completes_clean
  exact repaired_hidden_miss_stays_dirty layout k f miss

theorem repeated_query_after_recovery (layout : Key → Size)
    (k forcedKey nextKey : Key) (f : Frame) (miss : canReuse k f = false) :
    let recovered := geometryQuery true layout forcedKey (measure true true layout k f).frame
    geometryQuery true layout nextKey recovered = recovered := by
  apply clean_query_is_noop
  exact repaired_hidden_miss_clears_after_recovery layout k forcedKey f miss

theorem old_clean_hidden_miss_stays_zero (layout : Key → Size)
    (k forcedKey : Key) (f : Frame) (hd : f.dirty = false)
    (miss : canReuse k f = false) :
    (geometryQuery true layout forcedKey
      (measure false true layout k f).frame).geometry = zero := by
  rw [clean_query_is_noop _ _ _ _ (old_hidden_miss_retains_clean layout k f hd miss)]
  exact hidden_miss_publishes_zero false layout k f miss

theorem fixed_block_dimensions (k : Key)
    (hlo : k.minB ≤ k.computed.b) (hhi : k.computed.b ≤ k.maxB) :
    fixedBlock k = ⟨k.computed.i + k.borderIStart + k.borderIEnd,
      k.computed.b + k.borderBStart + k.borderBEnd⟩ := by
  have hm : min k.maxB k.computed.b = k.computed.b := by omega
  have hx : max k.minB k.computed.b = k.computed.b := by omega
  simp [fixedBlock, hm, hx]

def key (cbB : Int) : Key := ⟨⟨24, 32⟩, ⟨320, cbB⟩, 0, 0, 0, 0, 0, 1000, 1000⟩
def warm : Frame := ⟨false, ⟨24, 32⟩, some ⟨key 32, 32⟩⟩

theorem containing_block_only_miss : canReuse (key 0) warm = false := by decide

theorem old_zero_clean_witness :
    (measure false true fixedBlock (key 0) warm).frame.geometry = zero ∧
    (measure false true fixedBlock (key 0) warm).frame.dirty = false ∧
    (geometryQuery true fixedBlock (key 32)
      (measure false true fixedBlock (key 0) warm).frame).geometry = zero := by decide

theorem repaired_witness :
    (measure true true fixedBlock (key 0) warm).frame.dirty = true ∧
    (geometryQuery true fixedBlock (key 32)
      (measure true true fixedBlock (key 0) warm).frame).geometry = ⟨24, 32⟩ := by decide

theorem cache_hit_does_not_prove_geometry :
    let corrupt : Frame := ⟨false, zero, some ⟨key 32, 32⟩⟩
    canReuse (key 32) corrupt = true ∧
      (measure true true fixedBlock (key 32) corrupt).frame.geometry ≠ fixedBlock (key 32) := by decide

theorem repair_does_not_immediately_publish_real_geometry :
    (measure true true fixedBlock (key 0) warm).frame.geometry ≠ fixedBlock (key 0) := by decide

structure TwoFrames where
  measured : Frame
  descendant : Frame
  deriving DecidableEq, Repr

def descendantQuery (forceSubtree : TwoFrames → TwoFrames) (w : TwoFrames) : TwoFrames :=
  if w.descendant.dirty then forceSubtree w else w

theorem clean_descendant_does_not_force_ancestor (forceSubtree : TwoFrames → TwoFrames)
    (w : TwoFrames) (hc : w.descendant.dirty = false) :
    descendantQuery forceSubtree w = w := by simp [descendantQuery, hc]

theorem dirty_parent_clean_descendant_countermodel
    (forceSubtree : TwoFrames → TwoFrames) :
    let w : TwoFrames := ⟨(measure true true fixedBlock (key 0) warm).frame,
                          ⟨false, ⟨8, 9⟩, none⟩⟩
    w.measured.dirty = true ∧ w.descendant.dirty = false ∧
      descendantQuery forceSubtree w = w ∧ w.measured.geometry = zero := by
  simp [descendantQuery, measure, canReuse, key, warm, zero]

theorem clean_changed_key_retains_obsolete_geometry :
    let changed := {key 32 with computed := ⟨24, 50⟩}
    (geometryQuery true fixedBlock changed warm).geometry = ⟨24, 32⟩ ∧
    (geometryQuery true fixedBlock changed warm).geometry ≠ fixedBlock changed := by decide

end Hidden
