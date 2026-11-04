import Numeric
namespace ShadowOrder
set_option maxHeartbeats 2000000
structure Priority where
 origin : Nat
 important : Bool
 order : Int
 layer : Nat
 flags : Nat
 deriving DecidableEq, Repr

def Priority.admitted (p : Priority) : Prop :=
 p.origin < 8 ∧ (p.important = true → p.origin = 0 ∨ p.origin = 1 ∨ p.origin = 3) ∧
 -(maxOrder : Int) ≤ p.order ∧ p.order ≤ maxOrder ∧ p.layer ≤ 65535

def bucket (p : Priority) : Int :=
 if p.important then 10-(p.origin : Int) else if p.origin = 7 then 11 else p.origin

def levelKey (p : Priority) : Int :=
 bucket p * 268435455 + (if p.important then -p.order else p.order) + maxOrder

def nativeLevelLE (a b : Priority) : Prop :=
 if a.important = b.important then
   if a.important then b.origin < a.origin ∨ (a.origin = b.origin ∧ b.order ≤ a.order)
   else a.origin < b.origin ∨ (a.origin = b.origin ∧ a.order ≤ b.order)
 else if a.important then b.origin = 7 else a.origin ≠ 7

instance (a b : Priority) : Decidable (nativeLevelLE a b) := by unfold nativeLevelLE; infer_instance

theorem level_key_refinement (a b : Priority) (ha : a.admitted) (hb : b.admitted) :
 nativeLevelLE a b ↔ levelKey a ≤ levelKey b := by
 rcases a with ⟨ao, ai, ac, al, af⟩
 rcases b with ⟨bo, bi, bc, bl, bf⟩
 simp only [Priority.admitted,maxOrder] at ha hb
 cases ai <;> cases bi <;> simp_all only [nativeLevelLE,levelKey,bucket,maxOrder,Bool.false_eq_true,Bool.true_eq_false,↓reduceIte,not_false_eq_true]
 all_goals (try split) <;> (try split) <;> simp_all <;> omega

def layerKey (important : Bool) (layer : Nat) : Nat :=
 if important && layer != 65535 then 65534-layer else layer

def nativeLayerLE (important : Bool) (a b : Nat) : Prop :=
 if important && a != 65535 && b != 65535 then b ≤ a else a ≤ b

theorem layer_key_bounded (important : Bool) (layer : Nat) (h : layer ≤ 65535) :
 layerKey important layer ≤ 65535 := by
 unfold layerKey
 split <;> omega

theorem layer_key_refinement (important : Bool) (a b : Nat)
 (ha : a ≤ 65535) (hb : b ≤ 65535) :
 nativeLayerLE important a b ↔ layerKey important a ≤ layerKey important b := by
 cases important <;> simp only [nativeLayerLE,layerKey,Bool.false_and,Bool.true_and,↓reduceIte]
 · rfl
 · by_cases hab : a = 65535 <;> by_cases hbb : b = 65535 <;> simp_all <;> omega

def priorityKey (p : Priority) : Int := levelKey p * 65536 + layerKey p.important p.layer

theorem priority_key_lex (a b : Priority) (ha : a.admitted) (hb : b.admitted) :
 priorityKey a ≤ priorityKey b ↔ levelKey a < levelKey b ∨
   (levelKey a = levelKey b ∧ layerKey a.important a.layer ≤ layerKey b.important b.layer) := by
 have la := layer_key_bounded a.important a.layer ha.2.2.2.2
 have lb := layer_key_bounded b.important b.layer hb.2.2.2.2
 unfold priorityKey
 omega

#print axioms level_key_refinement
#print axioms layer_key_refinement
#print axioms priority_key_lex
end ShadowOrder
