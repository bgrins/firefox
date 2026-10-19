import Std

namespace HyphenRangeProvider

structure Cell where
  unit : Nat
  node : Nat
  original : Nat
  skipped : Bool
  trimmable : Bool
  segmentSpace : Bool
  deriving DecidableEq, Repr

structure StyledRange where
  policy : Nat
  cells : List Cell
  deriving DecidableEq, Repr

structure Owned where
  cell : Cell
  policy : Nat
  deriving DecidableEq, Repr

def contribute (range : StyledRange) : List Owned :=
  (range.cells.filter fun c => !c.skipped).map fun c => ⟨c, range.policy⟩

def flatten (ranges : List StyledRange) : List Owned := ranges.flatMap contribute

def insertCoalesced (r : StyledRange) : List StyledRange → List StyledRange
  | [] => [r]
  | s :: rest => if r.policy = s.policy then
      { r with cells := r.cells ++ s.cells } :: rest else r :: s :: rest

def coalesce : List StyledRange → List StyledRange
  | [] => []
  | r :: rest => insertCoalesced r (coalesce rest)

theorem merged_contribution (r s : StyledRange) (h : r.policy = s.policy) :
    contribute {r with cells := r.cells ++ s.cells} = contribute r ++ contribute s := by
  simp [contribute, List.filter_append, List.map_append, h]

theorem insert_preserves (r : StyledRange) (rest : List StyledRange) :
    flatten (insertCoalesced r rest) = contribute r ++ flatten rest := by
  cases rest with
  | nil => simp [flatten, insertCoalesced]
  | cons s rest =>
    by_cases h : r.policy = s.policy
    · simp [insertCoalesced, h, flatten, contribute, List.filter_append, List.map_append, List.append_assoc]
    · simp [insertCoalesced, h, flatten]

theorem coalescing_exact_ownership (ranges : List StyledRange) :
    flatten (coalesce ranges) = flatten ranges := by
  induction ranges with
  | nil => rfl
  | cons r rest ih =>
    change flatten (insertCoalesced r (coalesce rest)) = _
    rw [insert_preserves, ih]
    rfl

theorem splitting_exact_ownership (style : Nat) (left right : List Cell) :
    contribute ⟨style, left ++ right⟩ = contribute ⟨style, left⟩ ++ contribute ⟨style, right⟩ := by
  exact merged_contribution ⟨style, left⟩ ⟨style, right⟩ rfl

theorem all_skipped_no_contribution (r : StyledRange)
    (h : ∀ c ∈ r.cells, c.skipped = true) : contribute r = [] := by
  simp only [contribute, List.map_eq_nil_iff, List.filter_eq_nil_iff]
  intro c hc
  simp [h c hc]

def compressedLeadingSpace : List Cell → Bool
  | [] => false
  | c :: rest => c.skipped && (c.trimmable || compressedLeadingSpace rest)

def events (r : StyledRange) : List (Option Owned) :=
  (if compressedLeadingSpace r.cells then [none] else []) ++
    (contribute r).map some

structure Scanner where
  transformedOffset : Nat
  firstTextRange : Bool
  sinks : List (Nat × Nat)
  submitted : List (Option Owned)
  deriving DecidableEq, Repr

def scan (s : Scanner) (r : StyledRange) : Scanner :=
  let n := (contribute r).length
  ⟨s.transformedOffset + n, s.firstTextRange && n == 0,
    s.sinks ++ [(s.transformedOffset, n)], s.submitted ++ events r⟩

theorem each_range_has_sink (s : Scanner) (r : StyledRange) :
    (scan s r).sinks.length = s.sinks.length + 1 := by simp [scan]

theorem empty_range_keeps_first (s : Scanner) (r : StyledRange)
    (h : contribute r = []) : (scan s r).firstTextRange = s.firstTextRange := by
  simp [scan, h]

theorem nonempty_range_consumes_first (s : Scanner) (r : StyledRange)
    (h : contribute r ≠ []) : (scan s r).firstTextRange = false := by
  have : (contribute r).length ≠ 0 := by simpa using h
  simp [scan, this]

theorem sink_at_current_offset (s : Scanner) (r : StyledRange) :
    (scan s r).sinks = s.sinks ++ [(s.transformedOffset, (contribute r).length)] := rfl

theorem omitted_characters_not_owned (r : StyledRange) (x : Owned)
    (h : x ∈ contribute r) : x.cell.skipped = false ∧ x.policy = r.policy := by
  simp only [contribute, List.mem_map] at h
  obtain ⟨c, hc, he⟩ := h
  subst x
  simp only [List.mem_filter] at hc
  simp_all

theorem whole_flow_and_multi_flow (flows : List (List StyledRange)) :
    flows.flatMap (fun flow => flatten (coalesce flow)) =
      flows.flatMap flatten := by
  simp only [coalescing_exact_ownership]

structure Frame where
  offset : Nat
  policy : Nat
  deriving DecidableEq, Repr

def frameRanges (source : List Cell) : List Frame → List StyledRange
  | [] => []
  | [f] => [⟨f.policy, source.drop (min f.offset source.length)⟩]
  | f :: g :: rest =>
      let start := min f.offset source.length
      let finish := min g.offset source.length
      ⟨f.policy, (source.drop start).take (finish - start)⟩ :: frameRanges source (g :: rest)
termination_by fs => fs.length

def cells (ranges : List StyledRange) : List Cell := ranges.flatMap StyledRange.cells

theorem frame_coverage (source : List Cell) (frames : List Frame)
    (ordered : frames.Pairwise fun f g => f.offset ≤ g.offset) :
    cells (frameRanges source frames) =
      match frames with
      | [] => []
      | f :: _ => source.drop (min f.offset source.length) := by
  induction frames using frameRanges.induct source with
  | case1 => simp [frameRanges, cells]
  | case2 f => simp [frameRanges, cells]
  | case3 f g rest ih =>
    have hp := List.pairwise_cons.mp ordered
    have ho := hp.1 g (by simp)
    have hi := ih hp.2
    simp only [frameRanges, cells, List.flatMap_cons] at *
    rw [hi]
    have hc : min f.offset source.length ≤ min g.offset source.length := by omega
    have he : min f.offset source.length +
        (min g.offset source.length - min f.offset source.length) = min g.offset source.length := by omega
    simpa only [List.drop_drop, he] using
      (List.take_append_drop (min g.offset source.length - min f.offset source.length)
        (source.drop (min f.offset source.length)))

theorem mapped_coverage (ranges : List StyledRange) :
    (flatten ranges).map Owned.cell = (cells ranges).filter (fun c => !c.skipped) := by
  induction ranges with
  | nil => rfl
  | cons r rest ih => simp_all [flatten, cells, contribute, List.map_append, List.filter_append, Function.comp_def]

theorem full_mapped_flow_coverage (source : List Cell) (f : Frame) (rest : List Frame)
    (ordered : (f :: rest).Pairwise fun f g => f.offset ≤ g.offset) (start : f.offset = 0) :
    (flatten (coalesce (frameRanges source (f :: rest)))).map Owned.cell =
      source.filter (fun c => !c.skipped) := by
  rw [coalescing_exact_ownership, mapped_coverage, frame_coverage source (f :: rest) ordered]
  simp [start]

#print axioms frame_coverage
#print axioms full_mapped_flow_coverage
#print axioms coalescing_exact_ownership
#print axioms splitting_exact_ownership
#print axioms all_skipped_no_contribution
#print axioms each_range_has_sink
#print axioms nonempty_range_consumes_first
#print axioms omitted_characters_not_owned
#print axioms whole_flow_and_multi_flow
end HyphenRangeProvider
