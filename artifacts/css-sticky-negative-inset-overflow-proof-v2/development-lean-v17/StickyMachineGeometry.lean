import StickyNumeric
namespace StickyMachineGeometry
open StickyNumeric StickyGeometry

private def lit := Expr.literal
private def add := Expr.add
private def sub := Expr.subtract
private def mn := Expr.lesser
private def mx := Expr.greater

def endExpr (port box start ending : Expr) : Expr :=
  let view := sub port (add start ending)
  .ifLess view box (sub ending (sub box view)) ending

theorem end_expression (p b s e : Expr) :
    evaluate (endExpr p b s e) =
      StickyAxis.nativeEnd (evaluate p) (evaluate b) (evaluate s) (evaluate e) := rfl

def normalizedExpr (g : Raw) (endIsFar : Bool) : Expr × Expr :=
  let a := lit (StickyAxis.value g.insets.near)
  let b := lit (StickyAxis.value g.insets.far)
  if StickyAxis.active g.insets then
    if endIsFar then (a,endExpr (lit g.portSize) (lit g.border.size) a b)
    else (endExpr (lit g.portSize) (lit g.border.size) b a,b)
  else (a,b)

theorem normalized_expression (g : Raw) (endIsFar : Bool) :
    (evaluate (normalizedExpr g endIsFar).1,evaluate (normalizedExpr g endIsFar).2) =
    ((StickyAxis.nativeNormalize g.insets g.portSize g.border.size endIsFar).near,
     (StickyAxis.nativeNormalize g.insets g.portSize g.border.size endIsFar).far) := by
  unfold normalizedExpr StickyAxis.nativeNormalize
  split <;> simp only
  · split <;> rfl
  · rfl

structure Fields where
  near : Expr
  width : Expr
  containNear : Expr
  containWidth : Expr
  writes : List Expr

def construct (g : Raw) (endIsFar ignoreScroll : Bool) : Fields :=
  let e := normalizedExpr g endIsFar
  let frameOffset := sub (lit g.framePosition) (lit g.border.origin)
  let marginNear := sub (lit g.border.origin) (lit g.margin.origin)
  let marginFar := sub (add (lit g.margin.origin) (lit g.margin.size))
                       (add (lit g.border.origin) (lit g.border.size))
  let firstOrigin := add (lit g.containing.origin) marginNear
  let firstWidth := mx (lit 0) (sub (lit g.containing.size) (add marginNear marginFar))
  let containWidth := mx (lit 0) (sub firstWidth (add (lit 0) (lit g.border.size)))
  let containNear := add (add firstOrigin (lit 0)) frameOffset
  let scroll := lit (if ignoreScroll then 0 else g.scroll)
  let nearValue := add (sub (add (add scroll (lit g.padding)) e.1) (lit g.parentToScroll)) frameOffset
  let farValue := add (sub (sub (sub (add (add scroll (lit g.padding)) (lit g.portSize)) e.2)
                           (lit g.border.size)) (lit g.parentToScroll)) frameOffset
  let low := lit sentinelLow
  let width := lit coordMax
  let near := if g.insets.near.isSome then nearValue else low
  let firstWidth := if g.insets.near.isSome then sub (add low width) nearValue else width
  let finalWidth := if g.insets.far.isSome then sub farValue near else firstWidth
  ⟨near,finalWidth,containNear,containWidth,
   [e.1,e.2,frameOffset,marginNear,marginFar,firstOrigin,firstWidth,
    containNear,containWidth,finalWidth]⟩

def fieldsValue (f : Fields) : Limits :=
  ⟨evaluate f.near,evaluate (add f.near f.width),
   evaluate f.containNear,evaluate (add f.containNear f.containWidth)⟩

def machineFields (f : Fields) : Limits :=
  ⟨machineEvaluate f.near,machineEvaluate (add f.near f.width),
   machineEvaluate f.containNear,machineEvaluate (add f.containNear f.containWidth)⟩

def ArithmeticSafe (f : Fields) : Prop :=
  (∀ e ∈ f.writes, Admitted e) ∧ Admitted f.near ∧ Admitted (add f.near f.width) ∧
    Admitted f.containNear ∧ Admitted (add f.containNear f.containWidth)

instance (f : Fields) : Decidable (ArithmeticSafe f) := by
  unfold ArithmeticSafe; infer_instance

theorem machine_fields_refine (f : Fields) (safe : ArithmeticSafe f) :
    machineFields f = fieldsValue f := by
  rcases safe with ⟨_,hn,hw,hc,hcw⟩
  simp only [machineFields,fieldsValue,admitted_arithmetic_refines _ hn,
    admitted_arithmetic_refines _ hw,admitted_arithmetic_refines _ hc,
    admitted_arithmetic_refines _ hcw]

theorem complete_expression_limits (g : Raw) (endIsFar ignoreScroll : Bool) :
    fieldsValue (construct g endIsFar ignoreScroll) =
      nativeLimits g endIsFar ignoreScroll sentinelLow sentinelHigh := by
  have hn := congrArg Prod.fst (normalized_expression g endIsFar)
  have hf := congrArg Prod.snd (normalized_expression g endIsFar)
  dsimp only at hn hf
  by_cases n : g.insets.near.isSome = true <;>
    by_cases f : g.insets.far.isSome = true <;> cases ignoreScroll <;>
    simp [fieldsValue,construct,nativeLimits,nativeContain,deflate,move,ending,origin,
      lit,add,sub,mx,evaluate,n,f,↓reduceIte,hn,hf,coordMax,sentinelLow,sentinelHigh]
  all_goals first | omega | (constructor <;> omega)

theorem complete_machine_limits (g : Raw) (endIsFar ignoreScroll : Bool)
    (safe : ArithmeticSafe (construct g endIsFar ignoreScroll))
    (borderNonnegative : 0 ≤ g.border.size) :
    machineFields (construct g endIsFar ignoreScroll) =
      referenceLimits g endIsFar ignoreScroll sentinelLow sentinelHigh := by
  rw [machine_fields_refine _ safe,complete_expression_limits,
      full_axis_limits_refine g endIsFar ignoreScroll sentinelLow sentinelHigh borderNonnegative]

def positionExpr (normal : Int) (f : Fields) : Expr :=
  mn (mx (lit normal) (mn f.near (add f.containNear f.containWidth)))
     (mx (add f.near f.width) f.containNear)

theorem position_expression (normal : Int) (f : Fields) :
    evaluate (positionExpr normal f) = position normal (fieldsValue f) := rfl

theorem complete_machine_position (g : Raw) (endIsFar ignoreScroll : Bool)
    (_fullSafe : ArithmeticSafe (construct g endIsFar ignoreScroll))
    (safe : Admitted (positionExpr g.normal (construct g endIsFar ignoreScroll)))
    (borderNonnegative : 0 ≤ g.border.size) :
    machineEvaluate (positionExpr g.normal (construct g endIsFar ignoreScroll)) =
      position g.normal (referenceLimits g endIsFar ignoreScroll sentinelLow sentinelHigh) := by
  rw [admitted_arithmetic_refines _ safe,position_expression,complete_expression_limits,
      full_axis_limits_refine g endIsFar ignoreScroll sentinelLow sentinelHigh borderNonnegative]

def translationExpr (position normal : Expr) : Expr := sub position normal

theorem machine_translation_refines (position normal : Expr)
    (safe : Admitted (translationExpr position normal)) :
    machineEvaluate (translationExpr position normal) = evaluate position-evaluate normal :=
  admitted_arithmetic_refines _ safe

def rangeExpr (normal boundary limit : Expr) (near : Bool) : Expr × Expr :=
  (sub normal boundary, mx (lit 0) (if near then sub limit normal else sub normal limit))

theorem machine_range_refines (normal boundary limit : Expr) (near : Bool)
    (firstSafe : Admitted (rangeExpr normal boundary limit near).1)
    (secondSafe : Admitted (rangeExpr normal boundary limit near).2) :
    (machineEvaluate (rangeExpr normal boundary limit near).1,
     machineEvaluate (rangeExpr normal boundary limit near).2) =
    (evaluate normal-evaluate boundary,
     max 0 (if near then evaluate limit-evaluate normal else evaluate normal-evaluate limit)) := by
  rw [admitted_arithmetic_refines _ firstSafe,admitted_arithmetic_refines _ secondSafe]
  cases near <;> rfl

def continuationExpr (current target storedNormal borderOrigin : Int) : Expr × Expr :=
  let position := add (lit storedNormal) (lit target)
  (position, add (lit borderOrigin) (sub position (lit current)))

theorem machine_continuation_refines (current translation normal borderOrigin : Int)
    (positionSafe : Admitted (continuationExpr current translation normal borderOrigin).1)
    (originSafe : Admitted (continuationExpr current translation normal borderOrigin).2) :
    (machineEvaluate (continuationExpr current translation normal borderOrigin).1,
     machineEvaluate (continuationExpr current translation normal borderOrigin).2) =
    (normal+translation,borderOrigin+(normal+translation-current)) := by
  rw [admitted_arithmetic_refines _ positionSafe,admitted_arithmetic_refines _ originSafe]
  rfl

def exampleRaw (near far : Option Int) : Raw :=
  ⟨⟨40,200⟩,⟨30,230⟩,⟨0,800⟩,40,40,100,5,7,120,⟨near,far⟩⟩

theorem arithmetic_domain_inhabited :
    ∀ a ∈ ([none,some 20] : List (Option Int)),
    ∀ b ∈ ([none,some 20] : List (Option Int)),
    ∀ ending ∈ [false,true], ∀ ignore ∈ [false,true],
      ArithmeticSafe (construct (exampleRaw a b) ending ignore) ∧
      Admitted (positionExpr (exampleRaw a b).normal (construct (exampleRaw a b) ending ignore)) := by
  simp only [List.mem_cons,List.not_mem_nil,or_false,forall_eq_or_imp,forall_eq]
  decide +kernel

end StickyMachineGeometry
