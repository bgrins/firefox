import BaseModel
namespace BaseMetadata
open EndpointTaint

theorem entry_decomposition (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (entry : Entry K P) :
    entryChanged cmp custom old entry =
      (!endpointSame cmp entry.2 (old entry.1) ||
        (custom entry.1 && !(tainted entry.2 == tainted (old entry.1)))) := by
  rcases entry with ⟨key, value⟩
  cases value <;> cases prior : old key <;> simp [entryChanged, endpointSame, tainted, prior]

theorem scan_decomposition (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (entries : List (Entry K P)) :
    changed cmp custom old entries = (oldChanged cmp old entries || metaChanged custom old entries) := by
  induction entries with
  | nil => rfl
  | cons e rest ih =>
    simp only [changed, oldChanged, metaChanged, List.any_cons] at ih ⊢
    rw [entry_decomposition, ih]
    cases endpointSame cmp e.2 (old e.1) <;>
      cases custom e.1 <;> cases tainted e.2 <;> cases tainted (old e.1) <;> simp

theorem old_change_preserved (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (entries : List (Entry K P))
    (previous : oldChanged cmp old entries = true) :
    changed cmp custom old entries = true := by simp [scan_decomposition, previous]

theorem exact_added_decision (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (entries : List (Entry K P)) :
    changed cmp custom old entries ≠ oldChanged cmp old entries ↔
      oldChanged cmp old entries = false ∧ metaChanged custom old entries = true := by
  rw [scan_decomposition]
  cases oldChanged cmp old entries <;> cases metaChanged custom old entries <;> simp

theorem changed_iff_entry (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (entries : List (Entry K P)) :
    changed cmp custom old entries = true ↔
      ∃ entry ∈ entries, endpointSame cmp entry.2 (old entry.1) = false ∨
        (custom entry.1 = true ∧ tainted entry.2 ≠ tainted (old entry.1)) := by
  simp only [changed, List.any_eq_true, entry_decomposition]
  simp

theorem unchanged_selected_metadata (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (entries : List (Entry K P)) (entry : Entry K P)
    (selected : entry ∈ entries) (isCustom : custom entry.1 = true)
    (unchanged : changed cmp custom old entries = false) :
    tainted entry.2 = tainted (old entry.1) := by
  by_cases same : tainted entry.2 = tainted (old entry.1)
  · exact same
  · have yes := (changed_iff_entry cmp custom old entries).2 ⟨entry, selected, Or.inr ⟨isCustom, same⟩⟩
    rw [unchanged] at yes
    contradiction

theorem ordinary_entry_unchanged (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (entry : Entry K P) (ordinary : custom entry.1 = false) :
    entryChanged cmp custom old entry = !endpointSame cmp entry.2 (old entry.1) := by
  simp [entry_decomposition, ordinary]

theorem absent_old_detected (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (key : K) (value : Option (TaintShortcut.Value P))
    (absent : old key = none) : entryChanged cmp custom old (key, some value) = true := by
  simp [entryChanged, absent, endpointSame]

theorem null_pair_unchanged (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (key : K) (null : old key = none) :
    entryChanged cmp custom old (key, none) = false := by
  simp [entryChanged, null, endpointSame, tainted]

theorem depends_only_on_new_keys (cmp : P → P → Bool) (custom : K → Bool)
    (old other : Lookup K P) (entries : List (Entry K P))
    (agree : ∀ entry ∈ entries, old entry.1 = other entry.1) :
    changed cmp custom old entries = changed cmp custom other entries := by
  induction entries with
  | nil => rfl
  | cons e rest ih =>
    have head := agree e (by simp)
    have tail : ∀ entry ∈ rest, old entry.1 = other entry.1 :=
      fun entry member => agree entry (List.mem_cons_of_mem _ member)
    simp only [changed, List.any_cons] at ih ⊢
    rw [ih tail]
    simp only [entryChanged, head]

theorem no_target_no_flag (compare delta : Bool) : baseFlag false compare delta = false := rfl

theorem comparison_disabled_no_flag (target delta : Bool) : baseFlag target false delta = false := by
  simp [baseFlag]

theorem restyle_decision (propertiesChanged target delta : Bool) :
    requestsRestyle propertiesChanged target delta = (propertiesChanged || (target && delta)) := by
  cases propertiesChanged <;> cases target <;> cases delta <;> rfl

theorem scheduled_sample (published : Endpoint P) (state : SampleState P) (force : Bool) :
    (tick true force published state).sampled = published := rfl

theorem unnotified_retains_sample (published : Endpoint P) (state : SampleState P) :
    (tick false false published state).sampled = state.sampled := rfl

theorem base_published_even_without_notification (published : Endpoint P) (state : SampleState P) :
    (tick false false published state).base = published := rfl

theorem selected_sample_metadata_after_request
    (cmp : P → P → Bool) (custom : K → Bool) (old : Lookup K P)
    (entries : List (Entry K P)) (entry : Entry K P) (state : SampleState P)
    (selected : entry ∈ entries) (isCustom : custom entry.1 = true)
    (priorCoherent : tainted state.sampled = tainted (old entry.1)) :
    tainted (tick (requestsRestyle false true (changed cmp custom old entries))
      false entry.2 state).sampled = tainted entry.2 := by
  cases decision : changed cmp custom old entries with
  | true => simp [requestsRestyle, baseFlag, tick]
  | false =>
    have bits := unchanged_selected_metadata cmp custom old entries entry selected isCustom decision
    simpa [requestsRestyle, baseFlag, tick, decision, priorCoherent] using bits.symm

end BaseMetadata
