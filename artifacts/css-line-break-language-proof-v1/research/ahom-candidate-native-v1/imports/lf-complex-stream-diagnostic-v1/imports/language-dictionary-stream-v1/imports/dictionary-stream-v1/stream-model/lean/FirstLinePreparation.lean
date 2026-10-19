import Std

namespace HyphenFirstLinePreparation

structure Frame where
  identity : Nat
  style : Nat
  cachedRun : Option Nat
  deriving DecidableEq, Repr

structure Flow where
  principal : List Frame
  overflow : List Frame
  deriving DecidableEq, Repr

def order (flows : List Flow) : List Frame := flows.flatMap (fun f => f.principal ++ f.overflow)

def pullOne : List Flow → Option (Frame × List Flow)
  | [] => none
  | f :: rest =>
    match f.principal with
    | c :: cs => some (c, { f with principal := cs } :: rest)
    | [] => match f.overflow with
      | c :: cs => some (c, { f with overflow := cs } :: rest)
      | [] => pullOne rest

theorem pull_head (flows : List Flow) (frame : Frame) (rest : List Flow)
    (h : pullOne flows = some (frame, rest)) : order flows = frame :: order rest := by
  induction flows with
  | nil => simp [pullOne] at h
  | cons f fs ih =>
    cases hp : f.principal with
    | cons c cs =>
      simp [pullOne, hp] at h
      obtain ⟨rfl, rfl⟩ := h
      simp [order, hp]
    | nil =>
      cases ho : f.overflow with
      | cons c cs =>
        simp [pullOne, hp, ho] at h
        obtain ⟨rfl, rfl⟩ := h
        simp [order, hp, ho]
      | nil => simpa [order, hp, ho] using ih (by simpa [pullOne, hp, ho] using h)

theorem no_pull_empty (flows : List Flow) (h : pullOne flows = none) : order flows = [] := by
  induction flows with
  | nil => rfl
  | cons f fs ih =>
    cases hp : f.principal with
    | cons c cs => simp [pullOne, hp] at h
    | nil =>
      cases ho : f.overflow with
      | cons c cs => simp [pullOne, hp, ho] at h
      | nil => simpa [order, hp, ho] using ih (by simpa [pullOne, hp, ho] using h)

def reparentAndDirty (provider : Nat → Nat) (f : Frame) : Frame :=
  { f with style := provider f.identity, cachedRun := none }

def ready (provider : Nat → Nat) (f : Frame) : Prop :=
  f.style = provider f.identity ∧ f.cachedRun = none

def pullAll (provider : Nat → Nat) : Nat → List Flow → List Frame → List Frame
  | 0, _, accumulated => accumulated
  | fuel+1, flows, accumulated =>
    match pullOne flows with
    | none => accumulated
    | some (frame, rest) => pullAll provider fuel rest (accumulated ++ [reparentAndDirty provider frame])

theorem pull_all_reference (provider : Nat → Nat) (fuel : Nat)
    (flows : List Flow) (accumulated : List Frame) (enough : (order flows).length ≤ fuel) :
    pullAll provider fuel flows accumulated =
      accumulated ++ (order flows).map (reparentAndDirty provider) := by
  induction fuel generalizing flows accumulated with
  | zero =>
    have empty : order flows = [] := by simpa using enough
    simp [pullAll, empty]
  | succ fuel ih =>
    cases hp : pullOne flows with
    | none => simp [pullAll, hp, no_pull_empty flows hp]
    | some pair =>
      obtain ⟨frame, rest⟩ := pair
      have he := pull_head flows frame rest hp
      have hn : (order rest).length ≤ fuel := by rw [he] at enough; simp only [List.length_cons] at enough; omega
      simp only [pullAll, hp]
      rw [ih rest _ hn, he]
      simp [List.append_assoc]

theorem all_pulled_ready (provider : Nat → Nat) (fuel : Nat) (flows : List Flow)
    (enough : (order flows).length ≤ fuel) :
    ∀ frame ∈ pullAll provider fuel flows [], ready provider frame := by
  rw [pull_all_reference provider fuel flows [] enough]
  simp only [List.nil_append, List.mem_map]
  intro frame h
  obtain ⟨original, _, rfl⟩ := h
  exact ⟨rfl,rfl⟩

theorem no_frame_omitted_or_duplicated (provider : Nat → Nat) (flows : List Flow) :
    (pullAll provider (order flows).length flows []).map Frame.identity =
      (order flows).map Frame.identity := by
  rw [pull_all_reference provider _ flows [] (Nat.le_refl _)]
  simp [reparentAndDirty, Function.comp_def]

def prepare (provider : Nat → Nat) (current selfOverflow : List Frame) (later : List Flow) : List Frame :=
  current ++ pullAll provider (selfOverflow.length + (order later).length)
    (⟨[],selfOverflow⟩ :: later) []

theorem prepare_order (provider : Nat → Nat) (current selfOverflow : List Frame) (later : List Flow) :
    prepare provider current selfOverflow later =
      current ++ (selfOverflow ++ order later).map (reparentAndDirty provider) := by
  unfold prepare
  rw [pull_all_reference]
  · simp [order]
  · simp [order]

theorem consumer_entry_ready (provider : Nat → Nat) (current selfOverflow : List Frame)
    (later : List Flow) (alreadyReady : ∀ f ∈ current, ready provider f) :
    ∀ f ∈ prepare provider current selfOverflow later, ready provider f := by
  rw [prepare_order]
  intro f hf
  rcases List.mem_append.mp hf with old | moved
  · exact alreadyReady f old
  · obtain ⟨original, _, rfl⟩ := List.mem_map.mp moved
    exact ⟨rfl,rfl⟩

def valid (provider runStyles : Nat → Nat) (f : Frame) : Prop :=
  f.style = provider f.identity ∧
    ∀ run ∈ f.cachedRun, runStyles run = provider f.identity

theorem ready_valid (provider runStyles : Nat → Nat) (f : Frame)
    (h : ready provider f) : valid provider runStyles f := by
  exact ⟨h.1, by simp [h.2]⟩

theorem consumer_entry_preserves_valid_reuse (provider runStyles : Nat → Nat)
    (current selfOverflow : List Frame) (later : List Flow)
    (alreadyValid : ∀ f ∈ current, valid provider runStyles f) :
    ∀ f ∈ prepare provider current selfOverflow later, valid provider runStyles f := by
  rw [prepare_order]
  intro f hf
  rcases List.mem_append.mp hf with old | moved
  · exact alreadyValid f old
  · obtain ⟨original, _, rfl⟩ := List.mem_map.mp moved
    exact ready_valid provider runStyles _ ⟨rfl,rfl⟩

#print axioms consumer_entry_preserves_valid_reuse

theorem omitted_dirtying_retains_stale_run (provider : Nat → Nat) (identity run : Nat) :
    ¬ready provider ⟨identity, provider identity, some run⟩ := by
  simp [ready]

#print axioms pull_head
#print axioms pull_all_reference
#print axioms no_frame_omitted_or_duplicated
#print axioms consumer_entry_ready
#print axioms omitted_dirtying_retains_stale_run
end HyphenFirstLinePreparation
