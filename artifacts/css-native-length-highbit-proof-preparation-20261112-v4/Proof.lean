import Target

set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

namespace CssNativeHighBit

theorem low_value (b : UInt8) :
    (low b).toNat < 128 ∧ ((low b = b) ↔ b.toNat < 128) := by
  have h : ∀ v : BitVec 8,
      (low (UInt8.ofBitVec v)).toNat < 128 ∧
        ((low (UInt8.ofBitVec v) = UInt8.ofBitVec v) ↔ v.toNat < 128) := by
    decide
  simpa using h b.toBitVec

theorem high_value (b : UInt8) :
    128 ≤ (high b).toNat ∧ ((high b = b) ↔ 128 ≤ b.toNat) := by
  have h : ∀ v : BitVec 8,
      128 ≤ (high (UInt8.ofBitVec v)).toNat ∧
        ((high (UInt8.ofBitVec v) = UInt8.ofBitVec v) ↔ 128 ≤ v.toNat) := by
    decide
  simpa using h b.toBitVec

theorem high_suffix (j : Fin 5) (b : Backing) (i : Fin 5) (h : j.val < i.val) :
    firstHigh j b i = b i := by
  have hlt : ¬ i.val < j.val := by omega
  have hne : i ≠ j := by intro e; subst i; omega
  simp [firstHigh, hlt, hne]

theorem length_and_tail (n : Nat) (cell : Cell) (b : Backing)
    (_hn : goodLength n) (hc : admissible n cell) :
    (List.ofFn (generate n cell b)).length = 5 ∧
      ∀ i : Fin 5, n ≤ i.val → generate n cell b i = b i := by
  constructor
  · simp
  · intro i hi
    cases cell with
    | ascii => simp [generate, ascii, show ¬ i.val < n by omega]
    | high j =>
      change j.val < n at hc
      exact high_suffix j b i (by omega)

theorem image_membership (n : Nat) (cell : Cell) (b : Backing)
    (_hn : goodLength n) (_hc : admissible n cell) :
    belongs n cell (generate n cell b) := by
  cases cell with
  | ascii =>
    intro i hi
    simpa [generate, ascii, hi] using (low_value (b i)).1
  | high j =>
    constructor
    · simpa [generate, firstHigh] using (high_value (b j)).1
    · intro i hi
      simpa [generate, firstHigh, hi] using (low_value (b i)).1

theorem fixed_on_class (n : Nat) (cell : Cell) (b : Backing)
    (_hn : goodLength n) (_hc : admissible n cell) (hb : belongs n cell b) :
    generate n cell b = b := by
  funext i
  cases cell with
  | ascii =>
    by_cases hi : i.val < n
    · simpa [generate, ascii, hi] using (low_value (b i)).2.mpr (hb i hi)
    · simp [generate, ascii, hi]
  | high j =>
    by_cases hi : i.val < j.val
    · simpa [generate, firstHigh, hi] using (low_value (b i)).2.mpr (hb.2 i hi)
    · by_cases he : i = j
      · subst i
        simpa [generate, firstHigh] using (high_value (b j)).2.mpr hb.1
      · simp [generate, firstHigh, hi, he]

theorem class_exists (n : Nat) (b : Backing) :
    n ≤ 5 → ∃ cell, admissible n cell ∧ belongs n cell b := by
  induction n with
  | zero =>
    intro _
    refine ⟨.ascii, trivial, ?_⟩
    intro i hi
    omega
  | succ k ih =>
    intro hn
    obtain ⟨cell, hc, hb⟩ := ih (by omega)
    cases cell with
    | high j =>
      refine ⟨.high j, ?_, hb⟩
      change j.val < k at hc
      change j.val < k + 1
      omega
    | ascii =>
      let j : Fin 5 := ⟨k, by omega⟩
      by_cases hj : (b j).toNat < 128
      · refine ⟨.ascii, trivial, ?_⟩
        intro i hi
        by_cases hik : i.val < k
        · exact hb i hik
        · have e : i = j := Fin.ext (by dsimp [j]; omega)
          subst i
          exact hj
      · refine ⟨.high j, ?_, ?_⟩
        · change k < k + 1
          omega
        · constructor
          · omega
          · intro i hi
            exact hb i hi

theorem class_unique (n : Nat) (b : Backing) (a c : Cell)
    (ha : admissible n a) (hb : belongs n a b)
    (hc : admissible n c) (hd : belongs n c b) : a = c := by
  cases a with
  | ascii =>
    cases c with
    | ascii => rfl
    | high j =>
      have lo := hb j hc
      have hi := hd.1
      omega
  | high i =>
    cases c with
    | ascii =>
      have lo := hd i ha
      have hi := hb.1
      omega
    | high j =>
      by_cases h : i.val = j.val
      · have e : i = j := Fin.ext h
        subst j
        rfl
      · by_cases hij : i.val < j.val
        · have lo := hd.2 i hij
          have hi := hb.1
          omega
        · have lo := hb.2 j (by omega)
          have hi := hd.1
          omega

theorem unique_class (n : Nat) (b : Backing) (hn : goodLength n) :
    ∃ cell, (admissible n cell ∧ belongs n cell b) ∧
      (∀ other, (admissible n other ∧ belongs n other b) → other = cell) := by
  obtain ⟨cell, hc, hb⟩ := class_exists n b hn.2
  exact ⟨cell, ⟨hc, hb⟩, fun other ho => class_unique n b other cell ho.1 ho.2 hc hb⟩

theorem image_exact (n : Nat) (cell : Cell) (b : Backing)
    (hn : goodLength n) (hc : admissible n cell) :
    belongs n cell b ↔ ∃ raw : Backing, generate n cell raw = b := by
  constructor
  · intro hb
    exact ⟨b, fixed_on_class n cell b hn hc hb⟩
  · rintro ⟨raw, rfl⟩
    exact image_membership n cell raw hn hc

theorem universal (n : Nat) (hn : goodLength n)
    (C : Type) (P : Backing → C → Prop) :
    (∀ b c, P b c) ↔
      (∀ cell, admissible n cell → ∀ raw c, P (generate n cell raw) c) := by
  constructor
  · intro h cell _ raw c
    exact h _ c
  · intro h b c
    obtain ⟨cell, hc, hb⟩ := class_exists n b hn.2
    simpa only [fixed_on_class n cell b hn hc hb] using h cell hc b c

theorem filtered (n : Nat) (hn : goodLength n)
    (C : Type) (V : Backing → Prop) (P : Backing → C → Prop) :
    (∀ b c, V b → P b c) ↔
      (∀ cell, admissible n cell → ∀ raw c,
        V (generate n cell raw) → P (generate n cell raw) c) := by
  constructor
  · intro h cell _ raw c hv
    exact h _ c hv
  · intro h b c hv
    obtain ⟨cell, hc, hb⟩ := class_exists n b hn.2
    have he := fixed_on_class n cell b hn hc hb
    have hp := h cell hc b c (he.symm ▸ hv)
    simpa only [he] using hp

theorem cover_union (n : Nat) (hn : goodLength n)
    (C : Type) (E : Backing → C → Prop) :
    (∃ b c, E b c) ↔
      (∃ cell, admissible n cell ∧ ∃ raw c, E (generate n cell raw) c) := by
  constructor
  · rintro ⟨b, c, he⟩
    obtain ⟨cell, hc, hb⟩ := class_exists n b hn.2
    exact ⟨cell, hc, b, c, (fixed_on_class n cell b hn hc hb).symm ▸ he⟩
  · rintro ⟨cell, _, raw, c, he⟩
    exact ⟨generate n cell raw, c, he⟩

theorem generate_at_congr (n : Nat) (cell : Cell) (a b : Backing) (i : Fin 5)
    (h : a i = b i) : generate n cell a i = generate n cell b i := by
  cases cell <;> simp [generate, ascii, firstHigh, h]

theorem nonvacuity_and_tails :
    (∀ n cell, goodLength n → admissible n cell → ∀ (C : Type) (c : C),
      ∃ raw : Backing, belongs n cell (generate n cell raw) ∧
        (onState n cell (raw, c)).2 = c) ∧
    (∀ n cell, goodLength n → n < 5 → admissible n cell →
      ∃ raw₀ raw₁ : Backing,
        (∀ i : Fin 5, i.val < n → generate n cell raw₀ i = generate n cell raw₁ i) ∧
        (∀ i : Fin 5, n ≤ i.val →
          generate n cell raw₀ i = 0 ∧ generate n cell raw₁ i = 255) ∧
        generate n cell raw₀ ≠ generate n cell raw₁) := by
  constructor
  · intro n cell hn hc C c
    exact ⟨fun _ => 0, image_membership n cell _ hn hc, rfl⟩
  · intro n cell hn hlt hc
    let a : Backing := fun _ => 0
    let b : Backing := fun i => if i.val < n then 0 else 255
    have tail : ∀ i : Fin 5, n ≤ i.val →
        generate n cell a i = 0 ∧ generate n cell b i = 255 := by
      intro i hi
      rw [(length_and_tail n cell a hn hc).2 i hi,
        (length_and_tail n cell b hn hc).2 i hi]
      simp [a, b, show ¬ i.val < n by omega]
    refine ⟨a, b, ?_, tail, ?_⟩
    · intro i hi
      exact generate_at_congr n cell a b i (by simp [a, b, hi])
    · intro he
      let i : Fin 5 := ⟨n, hlt⟩
      have ht := tail i (Nat.le_refl n)
      have eq := congrFun he i
      rw [ht.1, ht.2] at eq
      exact (by decide : (0 : UInt8) ≠ 255) eq

theorem validity_split (n : Nat) (cell : Cell)
    (_hn : goodLength n) (_hc : admissible n cell)
    (C : Type) (V : Backing → Prop) (P : Backing → C → Prop) :
    ((∀ raw c, P (generate n cell raw) c) ↔
      ((∀ raw c, V (generate n cell raw) → P (generate n cell raw) c) ∧
        (∀ raw c, ¬ V (generate n cell raw) → P (generate n cell raw) c))) ∧
    (∀ raw, ¬ (V (generate n cell raw) ∧ ¬ V (generate n cell raw))) := by
  classical
  constructor
  · constructor
    · intro h
      exact ⟨fun raw c _ => h raw c, fun raw c _ => h raw c⟩
    · rintro ⟨hy, hn⟩ raw c
      by_cases h : V (generate n cell raw)
      · exact hy raw c h
      · exact hn raw c h
  · intro raw h
    exact h.2 h.1

theorem ascii_child_member (n : Nat) (_hn : goodLength n)
    (a : Fin 128) (raw : Backing) : isAscii n (asciiChild n a raw) := by
  intro i hi
  by_cases hz : i.val = 0
  · simp only [asciiChild, hz, ite_true]
    rw [UInt8.toNat_ofNat_of_lt' (by change a.val < 256; have := a.isLt; omega)]
    exact a.isLt
  · simpa [asciiChild, hz, ascii, hi] using (low_value (raw i)).1

theorem ascii_child_recovers (n : Nat) (hn : goodLength n) (b : Backing)
    (hb : isAscii n b) : ∃ a : Fin 128, asciiChild n a b = b := by
  let a : Fin 128 := ⟨(b 0).toNat, hb 0 (by change 0 < n; have := hn.1; omega)⟩
  refine ⟨a, ?_⟩
  have fixed := fixed_on_class n .ascii b hn trivial hb
  funext i
  by_cases hz : i.val = 0
  · have hi : i = 0 := Fin.ext hz
    subst i
    simp [asciiChild, a]
  · simp only [asciiChild, hz, ite_false]
    exact congrFun fixed i

theorem ascii_refinement (n : Nat) (hn : goodLength n)
    (C : Type) (V : Backing → Prop) (P E : Backing → C → Prop) :
    ((∀ b c, isAscii n b → P b c) ↔
      (∀ a raw c, P (asciiChild n a raw) c)) ∧
    ((∀ b c, isAscii n b → V b → P b c) ↔
      (∀ a raw c, V (asciiChild n a raw) → P (asciiChild n a raw) c)) ∧
    ((∃ b c, isAscii n b ∧ E b c) ↔
      (∃ a raw c, E (asciiChild n a raw) c)) := by
  constructor
  · constructor
    · intro h a raw c
      exact h _ c (ascii_child_member n hn a raw)
    · intro h b c hb
      obtain ⟨a, ha⟩ := ascii_child_recovers n hn b hb
      simpa only [ha] using h a b c
  · constructor
    · constructor
      · intro h a raw c hv
        exact h _ c (ascii_child_member n hn a raw) hv
      · intro h b c hb hv
        obtain ⟨a, ha⟩ := ascii_child_recovers n hn b hb
        have hp := h a b c (ha.symm ▸ hv)
        simpa only [ha] using hp
    · constructor
      · rintro ⟨b, c, hb, he⟩
        obtain ⟨a, ha⟩ := ascii_child_recovers n hn b hb
        exact ⟨a, b, c, ha.symm ▸ he⟩
      · rintro ⟨a, raw, c, he⟩
        exact ⟨asciiChild n a raw, c, ascii_child_member n hn a raw, he⟩

theorem length_mem (n : Nat) : n ∈ lengths ↔ goodLength n := by
  simp [lengths, goodLength]
  omega

theorem length_feature_aggregation
    (C : Type) (P : Nat → Feature → Backing → C → Prop) :
    (∀ n, goodLength n → ∀ feature b c, P n feature b c) ↔
      (∀ n, n ∈ lengths → ∀ feature cell,
        admissible n cell → ∀ raw c, P n feature (generate n cell raw) c) := by
  constructor
  · intro h n hn feature cell _ raw c
    exact h n ((length_mem n).mp hn) feature _ c
  · intro h n hn feature b c
    exact (universal n hn C (P n feature)).mpr
      (h n ((length_mem n).mpr hn) feature) b c

theorem obligations : Obligations where
  low_value := low_value
  high_value := high_value
  length_and_tail := length_and_tail
  high_suffix := high_suffix
  image_membership := image_membership
  fixed_on_class := fixed_on_class
  unique_class := unique_class
  image_exact := image_exact
  universal := universal
  filtered := filtered
  cover_union := cover_union
  nonvacuity_and_tails := nonvacuity_and_tails
  validity_split := validity_split
  ascii_refinement := ascii_refinement
  length_feature_aggregation := length_feature_aggregation

end CssNativeHighBit
