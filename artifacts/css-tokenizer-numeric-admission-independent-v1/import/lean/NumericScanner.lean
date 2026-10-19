import NumericPayload
namespace NumericScanner
open NumericDigits

structure Step where
  consumed : Nat
  remaining : List Byte
  flags : Nat
  deriving DecidableEq,Repr

def step (xs : List Byte) : Step :=
  let token := NumericToken.native xs
  ⟨token.count,xs.drop token.count,NumericUnits.tokenFlags token⟩

theorem suffix (xs : List Byte) : (step xs).remaining = (NumericToken.native xs).rest :=
  (NumericToken.exact_suffix xs).symm

theorem progress (xs : List Byte) (h : NumericEntry.nativeStart xs = true) :
    0 < (step xs).consumed ∧ (step xs).consumed ≤ xs.length :=
  ⟨NumericToken.positive xs h,NumericToken.count_bound xs⟩

theorem boundary (units : List Boundary.Unit) (xs : List Byte) (h : Boundary.bytes units = xs) :
    Boundary.marker xs (step xs).consumed := NumericBoundary.token_boundary units xs h

theorem selected_dimension (xs : List Byte) (h : (NumericToken.native xs).kind = .dimension) :
    (step xs).flags = NumericUnits.referenceFlags
      ((SemanticName.reference (NumericLexical.native xs).rest).output.map NumericUnits.lower) :=
  NumericUnits.dimension_decoded xs h

theorem selected_nondimension (xs : List Byte) (h : (NumericToken.native xs).kind ≠ .dimension) :
    (step xs).flags = 0 := NumericUnits.nondimension_zero _ h

theorem one_step_reference (xs : List Byte) :
    step xs = ⟨(NumericToken.reference xs).count,(NumericToken.reference xs).rest,
      NumericUnits.tokenFlags (NumericToken.reference xs)⟩ := by
  have hr := NumericToken.native_reference xs
  simp only [step,←hr,NumericToken.exact_suffix]

#print axioms suffix
#print axioms progress
#print axioms boundary
#print axioms selected_dimension
#print axioms selected_nondimension
#print axioms one_step_reference
end NumericScanner
