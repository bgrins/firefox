import Std

namespace CssNativeHighBit

abbrev Backing := Fin 5 → UInt8

def goodLength (n : Nat) : Prop := 2 ≤ n ∧ n ≤ 5

def lengths : List Nat := [2, 3, 4, 5]

inductive Feature where
  | gecko
  | servo
  deriving DecidableEq, Repr

inductive Cell where
  | ascii
  | high (j : Fin 5)
  deriving DecidableEq, Repr

def low (b : UInt8) : UInt8 := b &&& 127

def high (b : UInt8) : UInt8 := b ||| 128

def ascii (n : Nat) (b : Backing) : Backing :=
  fun i => if i.val < n then low (b i) else b i

def firstHigh (j : Fin 5) (b : Backing) : Backing :=
  fun i => if i.val < j.val then low (b i)
    else if i = j then high (b i) else b i

def generate (n : Nat) (cell : Cell) (b : Backing) : Backing :=
  match cell with
  | .ascii => ascii n b
  | .high j => firstHigh j b

def admissible (n : Nat) : Cell → Prop
  | .ascii => True
  | .high j => j.val < n

def isAscii (n : Nat) (b : Backing) : Prop :=
  ∀ i : Fin 5, i.val < n → (b i).toNat < 128

def isFirstHigh (j : Fin 5) (b : Backing) : Prop :=
  128 ≤ (b j).toNat ∧ ∀ i : Fin 5, i.val < j.val → (b i).toNat < 128

def belongs (n : Nat) (cell : Cell) (b : Backing) : Prop :=
  match cell with
  | .ascii => isAscii n b
  | .high j => isFirstHigh j b

def onState {C : Type} (n : Nat) (cell : Cell) (state : Backing × C) : Backing × C :=
  (generate n cell state.1, state.2)

def asciiChild (n : Nat) (a : Fin 128) (b : Backing) : Backing :=
  fun i => if i.val = 0 then UInt8.ofNat a.val else ascii n b i

structure Obligations : Prop where
  low_value : ∀ b : UInt8,
    (low b).toNat < 128 ∧ ((low b = b) ↔ b.toNat < 128)
  high_value : ∀ b : UInt8,
    128 ≤ (high b).toNat ∧ ((high b = b) ↔ 128 ≤ b.toNat)
  length_and_tail : ∀ n cell b, goodLength n → admissible n cell →
    (List.ofFn (generate n cell b)).length = 5 ∧
      ∀ i : Fin 5, n ≤ i.val → generate n cell b i = b i
  high_suffix : ∀ (j : Fin 5) (b : Backing) (i : Fin 5), j.val < i.val → firstHigh j b i = b i
  image_membership : ∀ n cell b, goodLength n → admissible n cell →
    belongs n cell (generate n cell b)
  fixed_on_class : ∀ n cell b, goodLength n → admissible n cell →
    belongs n cell b → generate n cell b = b
  unique_class : ∀ n b, goodLength n →
    ∃! cell, admissible n cell ∧ belongs n cell b
  image_exact : ∀ n cell b, goodLength n → admissible n cell →
    (belongs n cell b ↔ ∃ raw : Backing, generate n cell raw = b)
  universal : ∀ n, goodLength n → ∀ (C : Type) (P : Backing → C → Prop),
    ((∀ b c, P b c) ↔
      (∀ cell, admissible n cell → ∀ raw c, P (generate n cell raw) c))
  filtered : ∀ n, goodLength n →
    ∀ (C : Type) (V : Backing → Prop) (P : Backing → C → Prop),
      ((∀ b c, V b → P b c) ↔
        (∀ cell, admissible n cell → ∀ raw c,
          V (generate n cell raw) → P (generate n cell raw) c))
  cover_union : ∀ n, goodLength n → ∀ (C : Type) (E : Backing → C → Prop),
    ((∃ b c, E b c) ↔
      (∃ cell, admissible n cell ∧ ∃ raw c, E (generate n cell raw) c))
  nonvacuity_and_tails :
    (∀ n cell, goodLength n → admissible n cell → ∀ (C : Type) (c : C),
      ∃ raw : Backing, belongs n cell (generate n cell raw) ∧
        (onState n cell (raw, c)).2 = c) ∧
    (∀ n cell, goodLength n → n < 5 → admissible n cell →
      ∃ raw₀ raw₁ : Backing,
        (∀ i : Fin 5, i.val < n → generate n cell raw₀ i = generate n cell raw₁ i) ∧
        (∀ i : Fin 5, n ≤ i.val →
          generate n cell raw₀ i = 0 ∧ generate n cell raw₁ i = 255) ∧
        generate n cell raw₀ ≠ generate n cell raw₁)
  validity_split : ∀ n cell, goodLength n → admissible n cell →
    ∀ (C : Type) (V : Backing → Prop) (P : Backing → C → Prop),
      ((∀ raw c, P (generate n cell raw) c) ↔
        ((∀ raw c, V (generate n cell raw) → P (generate n cell raw) c) ∧
          (∀ raw c, ¬ V (generate n cell raw) → P (generate n cell raw) c))) ∧
      (∀ raw, ¬ (V (generate n cell raw) ∧ ¬ V (generate n cell raw)))
  ascii_refinement : ∀ n, goodLength n →
    ∀ (C : Type) (V : Backing → Prop) (P E : Backing → C → Prop),
      ((∀ b c, isAscii n b → P b c) ↔
        (∀ a raw c, P (asciiChild n a raw) c)) ∧
      ((∀ b c, isAscii n b → V b → P b c) ↔
        (∀ a raw c, V (asciiChild n a raw) → P (asciiChild n a raw) c)) ∧
      ((∃ b c, isAscii n b ∧ E b c) ↔
        (∃ a raw c, E (asciiChild n a raw) c))
  length_feature_aggregation : ∀ (C : Type) (P : Nat → Feature → Backing → C → Prop),
    ((∀ n, goodLength n → ∀ feature b c, P n feature b c) ↔
      (∀ n, n ∈ lengths → ∀ feature cell,
        admissible n cell → ∀ raw c, P n feature (generate n cell raw) c))

end CssNativeHighBit
