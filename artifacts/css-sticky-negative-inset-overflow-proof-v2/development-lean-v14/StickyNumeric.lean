import StickyGeometry
namespace StickyNumeric

def machineMin : Int := -2147483648
def machineMax : Int := 2147483647
def coordMax : Int := 1073741823
def coordMin : Int := -1073741823
def sentinelLow : Int := -536870911
def sentinelHigh : Int := 536870912

def InMachine (x : Int) : Prop := machineMin ≤ x ∧ x ≤ machineMax
def InCoordinate (x : Int) : Prop := coordMin ≤ x ∧ x ≤ coordMax

def signed32 (x : Int) : Int :=
  let bits := x % 4294967296
  if bits ≥ 2147483648 then bits-4294967296 else bits

theorem signed32_exact (x : Int) (bound : InMachine x) : signed32 x = x := by
  simp only [signed32, InMachine, machineMin, machineMax] at *
  split <;> omega

theorem coordinate_fits_machine (x : Int) (bound : InCoordinate x) : InMachine x := by
  unfold InCoordinate InMachine coordMin coordMax machineMin machineMax at *; omega

theorem unbounded_constants :
    Int.tdiv coordMin 2 = sentinelLow ∧ sentinelLow+coordMax=sentinelHigh := by
  decide +kernel

def encodeInset : Option Int → Int
  | none => coordMax
  | some x => x

def decodeInset (raw : Int) : Option Int := if raw=coordMax then none else some raw

def InsetAdmitted : Option Int → Prop
  | none => True
  | some x => InCoordinate x ∧ x ≠ coordMax

theorem inset_roundtrip (value : Option Int) (admitted : InsetAdmitted value) :
    decodeInset (encodeInset value) = value := by
  cases value with
  | none => simp [decodeInset,encodeInset]
  | some x => simp only [InsetAdmitted] at admitted; simp [decodeInset,encodeInset,admitted.2]

inductive Expr where
  | literal (x : Int)
  | add (a b : Expr)
  | subtract (a b : Expr)
  | lesser (a b : Expr)
  | greater (a b : Expr)
  | ifLess (a b yes no : Expr)
  deriving Repr

def evaluate : Expr → Int
  | .literal x => x
  | .add a b => evaluate a + evaluate b
  | .subtract a b => evaluate a - evaluate b
  | .lesser a b => min (evaluate a) (evaluate b)
  | .greater a b => max (evaluate a) (evaluate b)
  | .ifLess a b yes no => if evaluate a < evaluate b then evaluate yes else evaluate no

def machineEvaluate : Expr → Int
  | .literal x => signed32 x
  | .add a b => signed32 (machineEvaluate a + machineEvaluate b)
  | .subtract a b => signed32 (machineEvaluate a - machineEvaluate b)
  | .lesser a b => min (machineEvaluate a) (machineEvaluate b)
  | .greater a b => max (machineEvaluate a) (machineEvaluate b)
  | .ifLess a b yes no => if machineEvaluate a < machineEvaluate b then machineEvaluate yes else machineEvaluate no

def Admitted : Expr → Prop
  | .literal x => InMachine x
  | .add a b => Admitted a ∧ Admitted b ∧ InMachine (evaluate a + evaluate b)
  | .subtract a b => Admitted a ∧ Admitted b ∧ InMachine (evaluate a - evaluate b)
  | .lesser a b => Admitted a ∧ Admitted b
  | .greater a b => Admitted a ∧ Admitted b
  | .ifLess a b yes no => Admitted a ∧ Admitted b ∧
      (if evaluate a < evaluate b then Admitted yes else Admitted no)

instance (x : Int) : Decidable (InMachine x) := by unfold InMachine; infer_instance

instance admittedDecidable : (e : Expr) → Decidable (Admitted e)
  | .literal x => inferInstanceAs (Decidable (InMachine x))
  | .add a b =>
    let _ := admittedDecidable a
    let _ := admittedDecidable b
    inferInstanceAs (Decidable (Admitted a ∧ Admitted b ∧ InMachine (evaluate a+evaluate b)))
  | .subtract a b =>
    let _ := admittedDecidable a
    let _ := admittedDecidable b
    inferInstanceAs (Decidable (Admitted a ∧ Admitted b ∧ InMachine (evaluate a-evaluate b)))
  | .lesser a b | .greater a b =>
    let _ := admittedDecidable a
    let _ := admittedDecidable b
    inferInstanceAs (Decidable (Admitted a ∧ Admitted b))
  | .ifLess a b yes no =>
    let _ := admittedDecidable a
    let _ := admittedDecidable b
    let _ := admittedDecidable yes
    let _ := admittedDecidable no
    inferInstanceAs (Decidable (Admitted a ∧ Admitted b ∧
      (if evaluate a < evaluate b then Admitted yes else Admitted no)))

theorem admitted_result_bound (e : Expr) (safe : Admitted e) : InMachine (evaluate e) := by
  induction e with
  | literal x => exact safe
  | add a b _ _ => exact safe.2.2
  | subtract a b _ _ => exact safe.2.2
  | lesser a b ia ib =>
    have ha := ia safe.1; have hb := ib safe.2
    change InMachine (min (evaluate a) (evaluate b))
    unfold InMachine at *; omega
  | greater a b ia ib =>
    have ha := ia safe.1; have hb := ib safe.2
    change InMachine (max (evaluate a) (evaluate b))
    unfold InMachine at *; omega

  | ifLess a b yes no _ _ iy ino =>
    simp only [evaluate]
    split
    · rename_i h; exact iy (by simpa [Admitted,h] using safe.2.2)
    · rename_i h; exact ino (by simpa [Admitted,h] using safe.2.2)

theorem admitted_arithmetic_refines (e : Expr) (safe : Admitted e) :
    machineEvaluate e = evaluate e := by
  induction e with
  | literal x => exact signed32_exact x safe
  | add a b ia ib =>
    simp only [machineEvaluate,evaluate,ia safe.1,ib safe.2.1]
    exact signed32_exact _ safe.2.2
  | subtract a b ia ib =>
    simp only [machineEvaluate,evaluate,ia safe.1,ib safe.2.1]
    exact signed32_exact _ safe.2.2
  | lesser a b ia ib => simp only [machineEvaluate,evaluate,ia safe.1,ib safe.2]
  | greater a b ia ib => simp only [machineEvaluate,evaluate,ia safe.1,ib safe.2]

  | ifLess a b yes no ia ib iy ino =>
    simp only [machineEvaluate,evaluate,ia safe.1,ib safe.2.1]
    split
    · rename_i h; exact iy (by simpa [Admitted,h] using safe.2.2)
    · rename_i h; exact ino (by simpa [Admitted,h] using safe.2.2)

theorem finite_sentinels_are_not_infinity :
    StickyGeometry.position 700000000 (StickyGeometry.missingOffsets sentinelLow sentinelHigh) =
      sentinelHigh ∧ InCoordinate 700000000 := by
  unfold InCoordinate; decide +kernel

theorem unchecked_machine_overflow :
    machineEvaluate (.add (.literal machineMax) (.literal 1)) ≠
      evaluate (.add (.literal machineMax) (.literal 1)) := by decide +kernel
end StickyNumeric
