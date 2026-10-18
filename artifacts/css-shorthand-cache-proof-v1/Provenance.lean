import Std

namespace ShorthandProvenance

inductive Side where
  | top | right | bottom | left
  deriving DecidableEq, Repr

structure Declaration where
  identity : Nat
  shorthand : Nat
  payload : Nat
  deriving Repr

structure Candidate where
  source : Declaration
  side : Side
  eligible : Bool
  deriving Repr

abbrev Environment := Nat → Int
abbrev Expansion := Environment → Declaration → Side → Option Int
abbrev Meaning := Nat → Side → Option Int
abbrev Cache := Nat → Side → Option (Nat × Int)
abbrev Output := Side → Option (Option Int)

def emptyCache : Cache := fun _ _ => none
def emptyOutput : Output := fun _ => none

def CacheSound (meaning : Meaning) (cache : Cache) : Prop :=
  ∀ shorthand side identity value,
    cache shorthand side = some (identity, value) → meaning identity side = some value

def Admitted (expand : Expansion) (env : Environment) (meaning : Meaning)
    (scan : List Candidate) : Prop :=
  ∀ candidate ∈ scan, ∀ side,
    expand env candidate.source side = meaning candidate.source.identity side

def populate (expand : Expansion) (env : Environment) (cache : Cache)
    (source : Declaration) : Cache :=
  fun shorthand side => if shorthand = source.shorthand then
    match expand env source side with
    | some value => some (source.identity, value)
    | none => cache shorthand side
  else cache shorthand side

def guardedLookup (cache : Cache) (source : Declaration) (side : Side) : Option Int :=
  match cache source.shorthand side with
  | some (identity, value) => if identity = source.identity then some value else none
  | none => none

def unguardedLookup (cache : Cache) (source : Declaration) (side : Side) : Option Int :=
  (cache source.shorthand side).map Prod.snd

def cachedExpansion (expand : Expansion) (env : Environment) (cache : Cache)
    (candidate : Candidate) : Option Int × Cache :=
  match guardedLookup cache candidate.source candidate.side with
  | some value => (some value, cache)
  | none =>
    let populated := populate expand env cache candidate.source
    (guardedLookup populated candidate.source candidate.side, populated)

def put (output : Output) (side : Side) (value : Option Int) : Output :=
  fun query => if query = side then some value else output query

def selected (scan : List Candidate) (query : Side) : Option Declaration :=
  match scan with
  | [] => none
  | candidate :: rest =>
    if candidate.eligible = true ∧ candidate.side = query then some candidate.source
    else selected rest query

def reference (expand : Expansion) (env : Environment) (scan : List Candidate)
    (query : Side) : Option (Option Int) :=
  (selected scan query).map (fun source => expand env source query)

def run (expand : Expansion) (env : Environment) : List Candidate → Cache → Output → Output
  | [], _, output => output
  | candidate :: rest, cache, output =>
    if candidate.eligible = true ∧ output candidate.side = none then
      let (value, nextCache) := cachedExpansion expand env cache candidate
      run expand env rest nextCache (put output candidate.side value)
    else run expand env rest cache output

theorem populate_sound (expand : Expansion) (env : Environment) (meaning : Meaning)
    (cache : Cache) (source : Declaration)
    (sound : CacheSound meaning cache)
    (identityStable : ∀ side, expand env source side = meaning source.identity side) :
    CacheSound meaning (populate expand env cache source) := by
  intro shorthand side identity value hit
  by_cases same : shorthand = source.shorthand
  · cases expanded : expand env source side with
    | none => exact sound shorthand side identity value (by simpa [populate, same, expanded] using hit)
    | some actual =>
      simp [populate, same, expanded] at hit
      rcases hit with ⟨rfl, rfl⟩
      exact (identityStable side).symm.trans expanded
  · exact sound shorthand side identity value (by simpa [populate, same] using hit)

theorem lookup_sound (meaning : Meaning) (cache : Cache) (source : Declaration)
    (side : Side) (value : Int) (sound : CacheSound meaning cache)
    (hit : guardedLookup cache source side = some value) :
    meaning source.identity side = some value := by
  unfold guardedLookup at hit
  cases entry : cache source.shorthand side with
  | none => simp [entry] at hit
  | some pair =>
    rcases pair with ⟨identity, actual⟩
    simp only [entry] at hit
    split at hit
    next same =>
      subst identity
      simp only [Option.some.injEq] at hit
      subst actual
      exact sound _ _ _ _ entry
    next different => cases hit

theorem populated_lookup (expand : Expansion) (env : Environment) (meaning : Meaning)
    (cache : Cache) (source : Declaration) (side : Side)
    (sound : CacheSound meaning cache)
    (identityStable : ∀ side, expand env source side = meaning source.identity side) :
    guardedLookup (populate expand env cache source) source side = expand env source side := by
  cases expanded : expand env source side with
  | some value => simp [guardedLookup, populate, expanded]
  | none =>
    have sameLookup : guardedLookup (populate expand env cache source) source side =
        guardedLookup cache source side := by simp [guardedLookup, populate, expanded]
    rw [sameLookup]
    cases found : guardedLookup cache source side with
    | none => rfl
    | some value =>
      have impossible := lookup_sound meaning cache source side value sound found
      rw [← identityStable side, expanded] at impossible
      cases impossible

theorem hit_provenance (expand : Expansion) (env : Environment) (meaning : Meaning)
    (cache : Cache) (candidate : Candidate)
    (sound : CacheSound meaning cache)
    (identityStable : ∀ side,
      expand env candidate.source side = meaning candidate.source.identity side) :
    (cachedExpansion expand env cache candidate).1 = expand env candidate.source candidate.side ∧
    CacheSound meaning (cachedExpansion expand env cache candidate).2 := by
  unfold cachedExpansion
  cases hit : guardedLookup cache candidate.source candidate.side with
  | none => exact ⟨populated_lookup expand env meaning cache candidate.source candidate.side sound identityStable,
      populate_sound expand env meaning cache candidate.source sound identityStable⟩
  | some value =>
    exact ⟨((identityStable candidate.side).trans
      (lookup_sound meaning cache candidate.source candidate.side value sound hit)).symm, sound⟩

theorem scan_refinement (expand : Expansion) (env : Environment) (meaning : Meaning)
    (scan : List Candidate) (cache : Cache) (output : Output)
    (admitted : Admitted expand env meaning scan) (sound : CacheSound meaning cache) :
    ∀ query, run expand env scan cache output query =
      (output query).or (reference expand env scan query) := by
  induction scan generalizing cache output with
  | nil => intro query; simp [run, reference, selected]
  | cons candidate rest ih =>
    have stable : ∀ side, expand env candidate.source side = meaning candidate.source.identity side :=
      admitted candidate (by simp)
    have remaining : Admitted expand env meaning rest := by
      intro c member; exact admitted c (by simp [member])
    intro query
    by_cases active : candidate.eligible = true ∧ output candidate.side = none
    · simp only [run, ite_eq_left active]
      have hit := hit_provenance expand env meaning cache candidate sound stable
      rw [ih _ _ remaining hit.2]
      rw [hit.1]
      by_cases same : query = candidate.side
      · subst query
        simp [put, reference, selected, active.1, active.2]
      · have different : candidate.side ≠ query := Ne.symm same
        simp [put, same, reference, selected, different]
    · simp only [run, ite_eq_right active]
      rw [ih _ _ remaining sound]
      by_cases eligible : candidate.eligible = true
      · have occupied : output candidate.side ≠ none := by simpa [eligible] using active
        by_cases same : query = candidate.side
        · subst query
          cases present : output candidate.side with
          | none => exact False.elim (occupied present)
          | some value => simp
        · simp [reference, selected, Ne.symm same]
      · simp [reference, selected, eligible]

theorem fresh_scan_refinement (expand : Expansion) (env : Environment) (meaning : Meaning)
    (scan : List Candidate) (admitted : Admitted expand env meaning scan) :
    ∀ query, run expand env scan emptyCache emptyOutput query = reference expand env scan query := by
  intro query
  have sound : CacheSound meaning emptyCache := by
    intro shorthand side identity value hit; cases hit
  simpa [emptyOutput] using scan_refinement expand env meaning scan emptyCache emptyOutput admitted sound query

def oldExpansion (expand : Expansion) (env : Environment) (cache : Cache)
    (candidate : Candidate) : Option Int × Cache :=
  match unguardedLookup cache candidate.source candidate.side with
  | some value => (some value, cache)
  | none =>
    let populated := populate expand env cache candidate.source
    (unguardedLookup populated candidate.source candidate.side, populated)

def oldRun (expand : Expansion) (env : Environment) : List Candidate → Cache → Output → Output
  | [], _, output => output
  | candidate :: rest, cache, output =>
    if candidate.eligible = true ∧ output candidate.side = none then
      let (value, nextCache) := oldExpansion expand env cache candidate
      oldRun expand env rest nextCache (put output candidate.side value)
    else oldRun expand env rest cache output

def witnessExpansion : Expansion := fun env source side =>
  if side = .top ∨ side = .bottom then some (env source.payload) else some (env (source.payload + 1))

def witnessEnv : Environment := fun slot => match slot with
  | 0 => 10 | 1 => 20 | 2 => 30 | _ => 40

def high : Declaration := ⟨100, 0, 0⟩
def low : Declaration := ⟨200, 0, 2⟩
def witness : List Candidate :=
  [⟨high, .top, true⟩, ⟨high, .right, true⟩, ⟨high, .bottom, true⟩,
   ⟨high, .left, false⟩, ⟨low, .top, true⟩, ⟨low, .right, true⟩,
   ⟨low, .bottom, true⟩, ⟨low, .left, true⟩]

theorem partial_rollback_counterexample :
    reference witnessExpansion witnessEnv witness .left = some (some 40) ∧
    oldRun witnessExpansion witnessEnv witness emptyCache emptyOutput .left = some (some 20) ∧
    run witnessExpansion witnessEnv witness emptyCache emptyOutput .left = some (some 40) := by
  decide

def omittedExpansion : Expansion := fun env source side =>
  if source.identity = low.identity ∧ side = .left then none
  else witnessExpansion env source side

def postUnguarded (expand : Expansion) (env : Environment) (cache : Cache)
    (candidate : Candidate) : Option Int :=
  unguardedLookup (populate expand env cache candidate.source) candidate.source candidate.side

theorem omitted_entry_counterexample :
    let cache := populate omittedExpansion witnessEnv emptyCache high
    let candidate : Candidate := ⟨low, .left, true⟩
    (cachedExpansion omittedExpansion witnessEnv cache candidate).1 = none ∧
    postUnguarded omittedExpansion witnessEnv cache candidate = some 20 := by
  decide

#print axioms populate_sound
#print axioms lookup_sound
#print axioms populated_lookup
#print axioms hit_provenance
#print axioms scan_refinement
#print axioms fresh_scan_refinement
#print axioms partial_rollback_counterexample
#print axioms omitted_entry_counterexample

end ShorthandProvenance
