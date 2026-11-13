import FlexViolationCaller.Target
import FlexViolation.Selection

namespace FlexViolationCaller

def Bounded (item : ItemState) : Prop :=
  FieldsValid item.fields ∧ item.fields.minimum ≤ item.current ∧
  item.current ≤ item.fields.maximum ∧ ¬(item.minFlag = true ∧ item.maxFlag = true)

theorem count_cons (item : ItemState) (items : List ItemState) :
    countedFrozen (item :: items) = (if item.frozen then 1 else 0) + countedFrozen items := by
  cases h : item.frozen <;> simp [countedFrozen, h, Nat.add_comm]

theorem active_cons (item : ItemState) (items : List ItemState) :
    active (item :: items) = if item.frozen then active items else item :: active items := by
  cases h : item.frozen <;> simp [active, h]

theorem count_partition (items : List ItemState) :
    countedFrozen items + (active items).length = items.length := by
  induction items with
  | nil => simp [countedFrozen, active]
  | cons item items ih =>
    rw [count_cons, active_cons]
    cases item.frozen <;> simp <;> omega

theorem count_append (xs ys : List ItemState) :
    countedFrozen (xs ++ ys) = countedFrozen xs + countedFrozen ys := by
  simp [countedFrozen, List.filter_append]

theorem append_fold (seeds : List Seed) (line : Line) :
    seeds.foldl (fun line seed => appendItem line (seedItem seed)) line =
      ⟨line.items ++ seeds.map seedItem, line.frozenCount + countedFrozen (seeds.map seedItem)⟩ := by
  induction seeds generalizing line with
  | nil => simp [countedFrozen]
  | cons seed seeds ih =>
    rw [List.foldl_cons, ih]
    simp [appendItem, count_cons, List.append_assoc, Nat.add_assoc]

theorem initial_exact (seeds : List Seed) :
    initialLine seeds = ⟨seeds.map seedItem, countedFrozen (seeds.map seedItem)⟩ := by
  simpa [initialLine] using append_fold seeds ⟨[],0⟩

theorem initial_count (seeds : List Seed) : CountAgrees (initialLine seeds) := by
  rw [initial_exact]
  rfl

theorem bounded_asItem (item : ItemState) (h : Bounded item) :
    FlexViolation.ValidItem (asItem item) := by
  rcases h with ⟨hf, hl, hu, _⟩
  rcases hf with ⟨_, hm, horder, hx⟩
  refine ⟨?_, hm, horder, hx⟩
  simp only [FlexViolation.Fits32, asItem, FlexViolation.min32, FlexViolation.max32] at *
  omega

theorem supplied_asItem (item : ItemState) (hf : FieldsValid item.fields)
    (hi : FlexViolation.Fits32 item.current) : FlexViolation.ValidItem (asItem item) :=
  ⟨hi, hf.2⟩

theorem seed_bounded (seed : Seed) (h : SeedValid seed) : Bounded (seedItem seed) := by
  rcases seed with ⟨fields, frozen⟩
  cases frozen with
  | none =>
    have hf := h.1
    have hi : FlexViolation.ValidItem ⟨fields.identity, fields.base, fields.minimum, fields.maximum⟩ :=
      ⟨hf.1, hf.2⟩
    have hc := FlexViolation.clamped_bounds _ hi
    exact ⟨hf, hc.1, hc.2, by simp [seedItem]⟩
  | some value =>
    rcases value with ⟨size, minFlag, maxFlag⟩
    exact h

theorem seed_fresh (seed : Seed) :
    (seedItem seed).frozen = false →
    (seedItem seed).minFlag = false ∧ (seedItem seed).maxFlag = false := by
  rcases seed with ⟨fields, frozen⟩
  cases frozen <;> simp [seedItem]

theorem initial_valid (seeds : List Seed) (h : SeedsValid seeds) : LineValid (initialLine seeds) := by
  rw [initial_exact]
  refine ⟨rfl, ?_, ?_⟩
  · intro item hi
    obtain ⟨seed, hs, rfl⟩ := List.mem_map.mp hi
    exact seed_fresh seed
  · intro item hi
    obtain ⟨seed, hs, rfl⟩ := List.mem_map.mp hi
    exact seed_bounded seed (h.2 seed hs)

theorem bounded_delta_range (delta : Int) :
    -preferredMax ≤ boundedDelta delta ∧ boundedDelta delta ≤ preferredMax := by
  simp only [boundedDelta, preferredMax]
  omega

theorem delta_admission_target : DeltaAdmissionTarget := by
  intro base delta minimum maximum hb0 hb hm0 horder hm
  have hd := bounded_delta_range delta
  refine ⟨?_, ?_⟩
  · simp only [FlexViolation.Fits32, FlexViolation.min32, FlexViolation.max32,
      preferredMax] at *
    omega
  · by_cases h1 : base + boundedDelta delta < minimum <;>
      by_cases h2 : maximum < base + boundedDelta delta <;>
      by_cases h3 : base + delta < minimum <;>
      by_cases h4 : maximum < base + delta <;>
      simp only [FlexViolation.clamped, h1, h2, h3, h4, if_true, if_false] <;>
      simp only [boundedDelta, preferredMax] at * <;> omega

theorem diagnostic_delta (base delta : Int) :
    (base + boundedDelta delta) - base = boundedDelta delta ∧
    FlexViolation.Fits32 ((base + boundedDelta delta) - base) := by
  have hd := bounded_delta_range delta
  constructor
  · omega
  · simp only [FlexViolation.Fits32, FlexViolation.min32, FlexViolation.max32,
      preferredMax] at *
    omega

end FlexViolationCaller
