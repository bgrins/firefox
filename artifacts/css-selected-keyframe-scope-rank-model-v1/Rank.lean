import Std

namespace ScopeRank

def physical (start : Nat) : List Bool → Nat
  | [] => start
  | _ :: rest => physical (start + 1) rest

def callbacks (start : Nat) : List Bool → Nat
  | [] => start
  | present :: rest => callbacks (start + if present then 1 else 0) rest

def present : List Bool → Nat
  | [] => 0
  | b :: rest => (if b then 1 else 0) + present rest

def missing : List Bool → Nat
  | [] => 0
  | b :: rest => (if b then 0 else 1) + missing rest

theorem physical_closed (start : Nat) (path : List Bool) :
    physical start path = start + path.length := by
  induction path generalizing start with
  | nil => simp [physical]
  | cons b rest ih => simp [physical, ih, Nat.add_comm, Nat.add_left_comm]

theorem callbacks_closed (start : Nat) (path : List Bool) :
    callbacks start path = start + present path := by
  induction path generalizing start with
  | nil => simp [callbacks, present]
  | cons b rest ih => cases b <;> simp [callbacks, present, ih, Nat.add_assoc]

theorem partition (path : List Bool) : path.length = present path + missing path := by
  induction path with
  | nil => simp [present, missing]
  | cons b rest ih => cases b <;> simp [present, missing] <;> omega

theorem callback_gap (start : Nat) (path : List Bool) :
    physical start path = callbacks start path + missing path := by
  rw [physical_closed, callbacks_closed]
  have h := partition path
  omega

def encode (distance : Nat) : Nat := min distance 7

def increment (rank : Nat) : Nat := if rank < 7 then rank + 1 else rank

def walkRank : Nat → Nat
  | 0 => 0
  | n + 1 => increment (walkRank n)

theorem increment_encode (n : Nat) : increment (encode n) = encode (n + 1) := by
  unfold increment
  split <;> simp only [encode] at * <;> omega

theorem walkRank_eq (n : Nat) : walkRank n = encode n := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [walkRank, ih, increment_encode]

def signedEncode (rank : Int) : Int :=
  if rank < -7 then -7 else if rank > 7 then 7 else rank

theorem classification_preserved (rank : Int) :
    signedEncode rank > 0 ↔ rank > 0 := by
  by_cases low : rank < -7
  · simp [signedEncode, low]
    omega
  · by_cases high : rank > 7 <;> simp [signedEncode, low, high] <;> omega

theorem exact_rank_iff (distance : Nat) : encode distance = distance ↔ distance ≤ 7 := by
  simp only [encode]
  omega

theorem sparse_recovery_iff {Root : Type} (root : Nat → Root)
    (distinct : Function.Injective root) (start : Nat) (path : List Bool)
    (bounded : physical start path ≤ 7) :
    root (encode (callbacks start path)) = root (physical start path) ↔ missing path = 0 := by
  have gap := callback_gap start path
  have cb : callbacks start path ≤ 7 := by omega
  have ec := (exact_rank_iff (callbacks start path)).mpr cb
  rw [ec]
  constructor
  · intro same
    have eq := distinct same
    omega
  · intro none
    have eq : callbacks start path = physical start path := by omega
    rw [eq]

inductive Root where
  | containing : Nat → Root
  | slot : Nat → Root
  | own
  deriving DecidableEq, Repr

def decodeNegative (slots magnitude : Nat) : Option Root :=
  if magnitude = 0 then none
  else if magnitude ≤ slots then some (.slot magnitude)
  else if magnitude = slots + 1 then some .own
  else none

theorem own_recovery_iff (slots : Nat) :
    decodeNegative slots (encode (slots + 1)) = some .own ↔ slots ≤ 6 := by
  by_cases h : slots ≤ 6
  · have bound : slots + 1 ≤ 7 := by omega
    rw [(exact_rank_iff _).mpr bound]
    simp [decodeNegative, h]
  · have ge : 7 ≤ slots + 1 := by omega
    have le : 7 ≤ slots := by omega
    simp [encode, Nat.min_eq_right ge, decodeNegative, le, h]

example : physical 1 [false, true, false] = 4 ∧ callbacks 1 [false, true, false] = 2 := by decide
example : Root.containing (encode 8) ≠ Root.containing 8 := by decide
example : decodeNegative 7 (encode 8) = some (.slot 7) := by decide

end ScopeRank
