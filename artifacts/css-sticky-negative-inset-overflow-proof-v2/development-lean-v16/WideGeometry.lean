import WideNormalization
import StickyMachineGeometry

namespace WideGeometry
open StickyNumeric StickyGeometry

private def lit := Expr.literal
private def add := Expr.add
private def sub := Expr.subtract
private def mx := Expr.greater

structure Fields where
  near : Expr
  far : Expr
  containNear : Expr
  containWidth : Expr
  writes : List Expr

def constructWith (g : Raw) (offsets : Int × Int) (ignoreScroll : Bool) : Fields :=
  let a := lit offsets.1
  let b := lit offsets.2
  let frameOffset := sub (lit g.framePosition) (lit g.border.origin)
  let marginNear := sub (lit g.border.origin) (lit g.margin.origin)
  let marginFar := sub (add (lit g.margin.origin) (lit g.margin.size))
    (add (lit g.border.origin) (lit g.border.size))
  let firstOrigin := add (lit g.containing.origin) marginNear
  let firstWidth := mx (lit 0) (sub (lit g.containing.size) (add marginNear marginFar))
  let containWidth := mx (lit 0) (sub firstWidth (add (lit 0) (lit g.border.size)))
  let containNear := add (add firstOrigin (lit 0)) frameOffset
  let scroll := lit (if ignoreScroll then 0 else g.scroll)
  let nearValue := add (sub (add (add scroll (lit g.padding)) a) (lit g.parentToScroll)) frameOffset
  let farValue := add (sub (sub (sub (add (add scroll (lit g.padding)) (lit g.portSize)) b)
    (lit g.border.size)) (lit g.parentToScroll)) frameOffset
  let near := if g.insets.near.isSome then nearValue else lit sentinelLow
  let far := if g.insets.far.isSome then farValue else lit sentinelHigh
  ⟨near,far,containNear,containWidth,
    [a,b,frameOffset,marginNear,marginFar,firstOrigin,firstWidth,
     containNear,containWidth,near,far]⟩

def construct (g : Raw) (modern endFar ignoreScroll : Bool) : Fields :=
  constructWith g (WideNormalization.source modern g.insets g.portSize g.border.size endFar) ignoreScroll

def machineConstruct (g : Raw) (modern endFar ignoreScroll : Bool) : Fields :=
  constructWith g (WideNormalization.machine modern g.insets g.portSize g.border.size endFar) ignoreScroll

def values (f : Fields) : Limits :=
  ⟨evaluate f.near,evaluate f.far,evaluate f.containNear,
   evaluate (add f.containNear f.containWidth)⟩

def machineFields (f : Fields) : Limits :=
  ⟨machineEvaluate f.near,machineEvaluate f.far,machineEvaluate f.containNear,
   machineEvaluate (add f.containNear f.containWidth)⟩

def ArithmeticSafe (f : Fields) : Prop :=
  (∀ e ∈ f.writes, Admitted e) ∧ Admitted f.near ∧ Admitted f.far ∧
    Admitted f.containNear ∧ Admitted (add f.containNear f.containWidth)

instance (f : Fields) : Decidable (ArithmeticSafe f) := by
  unfold ArithmeticSafe; infer_instance

def Safe (g : Raw) (modern endFar ignoreScroll : Bool) : Prop :=
  WideNormalization.Safe modern g.insets g.portSize g.border.size endFar ∧
  ArithmeticSafe (construct g modern endFar ignoreScroll)

instance (g : Raw) (m e i : Bool) : Decidable (Safe g m e i) := by
  unfold Safe; infer_instance

def sourceLimits (g : Raw) (modern endFar ignoreScroll : Bool) : Limits :=
  let e := WideNormalization.source modern g.insets g.portSize g.border.size endFar
  let c := nativeContain g
  ⟨if g.insets.near.isSome then origin g ignoreScroll + e.1 else sentinelLow,
   if g.insets.far.isSome then origin g ignoreScroll + g.portSize - e.2 - g.border.size else sentinelHigh,
   c.origin,ending c⟩

def referenceLimits (g : Raw) (modern endFar ignoreScroll : Bool) : Limits :=
  let e := WideNormalization.reference modern g.insets g.portSize g.border.size endFar
  let c := referenceContain g
  ⟨(g.insets.near.map (fun _ => origin g ignoreScroll + e.1)).getD sentinelLow,
   (g.insets.far.map (fun _ => origin g ignoreScroll + g.portSize - e.2 - g.border.size)).getD sentinelHigh,
   c.origin,ending c⟩

theorem complete_expression (g : Raw) (modern endFar ignoreScroll : Bool) :
    values (construct g modern endFar ignoreScroll) = sourceLimits g modern endFar ignoreScroll := by
  by_cases n : g.insets.near.isSome = true <;>
    by_cases f : g.insets.far.isSome = true <;> cases ignoreScroll <;>
    simp [values,construct,constructWith,sourceLimits,nativeContain,deflate,move,ending,
      origin,lit,add,sub,mx,evaluate,n,f,↓reduceIte]
  all_goals first | omega | (constructor <;> omega)

theorem source_reference (g : Raw) (modern endFar ignoreScroll : Bool)
    (nonnegative : 0 ≤ g.border.size) :
    sourceLimits g modern endFar ignoreScroll = referenceLimits g modern endFar ignoreScroll := by
  simp only [sourceLimits,referenceLimits,WideNormalization.source_reference,
    containment_geometry_refines g nonnegative]
  cases g.insets.near <;> cases g.insets.far <;> rfl

theorem machine_fields_refine (f : Fields) (safe : ArithmeticSafe f) :
    machineFields f = values f := by
  rcases safe with ⟨_,hn,hf,hc,hcw⟩
  simp only [machineFields,values,admitted_arithmetic_refines _ hn,
    admitted_arithmetic_refines _ hf,admitted_arithmetic_refines _ hc,
    admitted_arithmetic_refines _ hcw]

theorem machine_construct_refines (g : Raw) (m e i : Bool)
    (safe : WideNormalization.Safe m g.insets g.portSize g.border.size e) :
    machineConstruct g m e i = construct g m e i := by
  unfold machineConstruct construct
  rw [WideNormalization.machine_reference _ _ _ _ _ safe,← WideNormalization.source_reference]

theorem complete_machine_limits (g : Raw) (m e i : Bool) (safe : Safe g m e i)
    (nonnegative : 0 ≤ g.border.size) :
    machineFields (machineConstruct g m e i) = referenceLimits g m e i := by
  rw [machine_construct_refines g m e i safe.1,
    machine_fields_refine _ safe.2,complete_expression,source_reference _ _ _ _ nonnegative]

def machineContain (g : Raw) (m e i : Bool) : Interval :=
  let f := machineConstruct g m e i
  ⟨machineEvaluate f.containNear,machineEvaluate f.containWidth⟩

theorem complete_contain_record (g : Raw) (m e i : Bool) (safe : Safe g m e i) :
    machineContain g m e i = nativeContain g := by
  have width : Admitted (construct g m e i).containWidth :=
    safe.2.1 _ (by simp [construct,constructWith])
  unfold machineContain
  rw [machine_construct_refines _ _ _ _ safe.1]
  dsimp only
  rw [admitted_arithmetic_refines _ safe.2.2.2.2.1,admitted_arithmetic_refines _ width]
  simp [construct,constructWith,nativeContain,deflate,move,lit,add,sub,mx,evaluate]


theorem source_scroll_relation (g : Raw) (m e : Bool) :
    sourceLimits g m e false =
      {sourceLimits g m e true with
       stickNear := if g.insets.near.isSome then (sourceLimits g m e true).stickNear+g.scroll else sentinelLow,
       stickFar := if g.insets.far.isSome then (sourceLimits g m e true).stickFar+g.scroll else sentinelHigh} := by
  by_cases n : g.insets.near.isSome = true <;> by_cases f : g.insets.far.isSome = true <;>
    simp [sourceLimits,origin,n,f]
  all_goals omega

def legacyWidth (nearActive farActive : Bool) (near far : Int) : Expr :=
  let initial := lit coordMax
  let afterNear := if nearActive then sub (add (lit sentinelLow) initial) (lit near) else initial
  if farActive then sub (lit far) (if nearActive then lit near else lit sentinelLow) else afterNear

def legacyNear (active : Bool) (near : Int) : Expr := if active then lit near else lit sentinelLow

def LegacyStorageSafe (na fa : Bool) (near far : Int) : Prop :=
  Admitted (legacyNear na near) ∧ Admitted (lit far) ∧
  (if na then Admitted (sub (add (lit sentinelLow) (lit coordMax)) (lit near)) else True) ∧
  Admitted (legacyWidth na fa near far) ∧
  Admitted (add (legacyNear na near) (legacyWidth na fa near far))

instance (n f : Bool) (a b : Int) : Decidable (LegacyStorageSafe n f a b) := by
  unfold LegacyStorageSafe; infer_instance

theorem defined_legacy_edges (na fa : Bool) (near far : Int)
    (safe : LegacyStorageSafe na fa near far) :
    (machineEvaluate (legacyNear na near),
     machineEvaluate (add (legacyNear na near) (legacyWidth na fa near far))) =
    (if na then near else sentinelLow,if fa then far else sentinelHigh) := by
  rw [admitted_arithmetic_refines _ safe.1,admitted_arithmetic_refines _ safe.2.2.2.2]
  cases na <;> cases fa <;>
    simp [legacyNear,legacyWidth,lit,add,sub,evaluate,coordMax,sentinelLow,sentinelHigh] <;> omega

def PreparationSafe (fromScroll : Bool) (raw : Interval) (near far : Int) : Prop :=
  if fromScroll then
    Admitted (add (lit raw.origin) (lit near)) ∧
    Admitted (mx (lit 0) (sub (lit raw.size) (add (lit near) (lit far))))
  else True

instance (f : Bool) (r : Interval) (n e : Int) : Decidable (PreparationSafe f r n e) := by
  unfold PreparationSafe; infer_instance

theorem local_padding_deflate_exact (r : Interval) (n f : Int)
    (safe : PreparationSafe true r n f) :
    (machineEvaluate (add (lit r.origin) (lit n)),
     machineEvaluate (mx (lit 0) (sub (lit r.size) (add (lit n) (lit f))))) =
    ((deflate r n f).origin,(deflate r n f).size) := by
  rw [admitted_arithmetic_refines _ safe.1,admitted_arithmetic_refines _ safe.2]
  rfl

def wideRaw : Raw :=
  ⟨⟨12000,600⟩,⟨12000,600⟩,⟨0,60000⟩,12000,12000,6000,0,0,0,
    ⟨some (-1073741823),some (-1073741823)⟩⟩

theorem wide_core_admitted : Safe wideRaw true true false ∧
    (sourceLimits wideRaw true true false).stickNear = -1073741823 ∧
    (sourceLimits wideRaw true true false).stickFar = 1073747223 ∧
    ¬ LegacyStorageSafe true true (-1073741823) 1073747223 := by
  decide +kernel

end WideGeometry
