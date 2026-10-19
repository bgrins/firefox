import Model
namespace TaintShortcut
variable {P U : Type}
theorem metadata_same_sound (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (old next : State P) (h : metadataSame cmp old next = true) : old = next := by
  cases old with
  | none => cases next <;> simp_all [metadataSame]
  | some a =>
    cases next with
    | none => simp [metadataSame] at h
    | some b =>
      rcases a with ⟨p,t⟩; rcases b with ⟨q,u⟩
      simp only [metadataSame, Bool.and_eq_true, beq_iff_eq] at h
      have hp := sound p q h.1
      rcases h with ⟨_, rfl⟩
      subst q
      rfl
theorem unique_updates (same : State P → State P → Bool) (old next : State P) :
    mapUpdate same true old next = next := by simp [mapUpdate]
theorem map_correct (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (unique : Bool) (old next : State P) :
    mapUpdate (metadataSame cmp) unique old next = next := by
  unfold mapUpdate
  split
  · rfl
  · split
    · exact metadata_same_sound cmp sound old next (by assumption)
    · rfl
theorem map_url_correct (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (unique : Bool) (old next : State P) (parse : P → Option U) :
    observeURL parse (mapUpdate (metadataSame cmp) unique old next) = observeURL parse next := by
  rw [map_correct cmp sound]
theorem removed_stays_absent (cmp : P → P → Bool) (unique : Bool) (old : State P) :
    mapUpdate (metadataSame cmp) unique old none = none := by
  cases old <;> cases unique <;> simp [mapUpdate, metadataSame]
theorem different_taint_never_skips (cmp : P → P → Bool) (p q : P) (t u : Bool)
    (different : t ≠ u) : metadataSame cmp (some ⟨p,t⟩) (some ⟨q,u⟩) = false := by
  simp [metadataSame, different]
theorem gate_correct (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (resolve : Incoming P → State P) (provider : ReferenceFreeProvider resolve)
    (d : Incoming P) (domain : EligibleDomain d) (old : State P)
    (skip : (d.eligible && metadataSame cmp old (some (declaredValue d))) = true) :
    old = resolve d := by
  have pair : d.eligible = true ∧ metadataSame cmp old (some (declaredValue d)) = true := by
    simpa only [Bool.and_eq_true] using skip
  rw [provider d pair.1 (domain pair.1)]
  exact metadata_same_sound cmp sound _ _ pair.2
theorem pipeline_correct (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (resolve : Incoming P → State P) (provider : ReferenceFreeProvider resolve)
    (unique : Bool) (old : State P) (d : Incoming P) (domain : EligibleDomain d) :
    pipeline (metadataSame cmp) (metadataSame cmp) resolve unique old d = resolve d := by
  unfold pipeline
  split
  · exact gate_correct cmp sound resolve provider d domain old (by assumption)
  · exact map_correct cmp sound unique old (resolve d)
theorem repaired_correct (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (resolve : Incoming P → State P) (provider : ReferenceFreeProvider resolve)
    (unique : Bool) (old : State P) (d : Incoming P) (domain : EligibleDomain d) :
    repaired cmp resolve unique old d = resolve d :=
  pipeline_correct cmp sound resolve provider unique old d domain
theorem ineligible_pipeline (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (resolve : Incoming P → State P) (unique : Bool) (old : State P)
    (d : Incoming P) (h : d.eligible = false) :
    pipeline (metadataSame cmp) (metadataSame cmp) resolve unique old d = resolve d := by
  simp only [pipeline, h, Bool.false_and, Bool.false_eq_true, ↓reduceIte]
  exact map_correct cmp sound _ _ _
theorem pipeline_url_correct (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (resolve : Incoming P → State P) (provider : ReferenceFreeProvider resolve)
    (unique : Bool) (old : State P) (d : Incoming P) (domain : EligibleDomain d)
    (parse : P → Option U) :
    observeURL parse (pipeline (metadataSame cmp) (metadataSame cmp) resolve unique old d) =
      observeURL parse (resolve d) := by rw [pipeline_correct cmp sound resolve provider unique old d domain]
theorem direct_provider : ReferenceFreeProvider (fun d : Incoming P => some (declaredValue d)) := by
  intro d _ _; rfl
theorem history_correct (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (resolve : Incoming P → State P) (provider : ReferenceFreeProvider resolve)
    (ops : List (Op P)) (domain : ∀ op ∈ ops, EligibleDomain op.input) (initial : State P) :
    optimizedHistory cmp resolve initial ops = referenceHistory resolve initial ops := by
  induction ops generalizing initial with
  | nil => rfl
  | cons op rest ih =>
    simp only [optimizedHistory, referenceHistory, repaired]
    rw [pipeline_correct cmp sound resolve provider op.unique initial op.input (domain op (by simp))]
    exact ih (fun x hx => domain x (by simp [hx])) _
theorem every_prefix_url (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (resolve : Incoming P → State P) (provider : ReferenceFreeProvider resolve)
    (ops : List (Op P)) (domain : ∀ op ∈ ops, EligibleDomain op.input)
    (initial : State P) (n : Nat) (parse : P → Option U) :
    observeURL parse (optimizedHistory cmp resolve initial (ops.take n)) =
      observeURL parse (referenceHistory resolve initial (ops.take n)) := by
  rw [history_correct cmp sound resolve provider (ops.take n)
    (fun op h => domain op (List.mem_of_mem_take h)) initial]
end TaintShortcut
