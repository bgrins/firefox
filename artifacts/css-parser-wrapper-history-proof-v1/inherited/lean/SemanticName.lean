import EscapeBoundary
namespace SemanticName
open HexPrefix Escape

structure Result where
  output : List Byte
  count : Nat
  rest : List Byte
  deriving DecidableEq, Repr

def project (r : Name.Result) : Result := ⟨r.output,r.count,r.rest⟩

def reference (xs : List Byte) : Result :=
  match xs with
  | [] => ⟨[],0,[]⟩
  | b::bs =>
    if Name.referenceOrdinary b then
      let r := reference bs
      ⟨b::r.output,1+r.count,r.rest⟩
    else if b.val = 0 then
      let r := reference bs
      ⟨encode 65533 ++ r.output,1+r.count,r.rest⟩
    else if b.val = 92 ∧ Name.newlineAfter bs = false then
      let escaped := Escape.reference bs
      let r := reference (bs.drop escaped.count)
      ⟨escaped.output ++ r.output,1+escaped.count+r.count,r.rest⟩
    else ⟨[],0,b::bs⟩
termination_by xs.length
decreasing_by all_goals simp_wf <;> omega

theorem source_semantics (owned : Bool) (xs : List Byte) :
    project (Name.run owned xs) = reference xs := by
  induction owned, xs using Name.run.induct with
  | case1 owned => simp [Name.run,project,reference]
  | case2 owned b bs h ih =>
    have hr : Name.referenceOrdinary b = true := by simpa [← Name.ordinary_classification] using h
    have ho := congrArg Result.output ih
    have hc := congrArg Result.count ih
    have ht := congrArg Result.rest ih
    simp only [project] at ho hc ht
    simp [Name.run,h,reference,hr,project,ho,hc,ht,Nat.add_comm]
  | case3 owned b bs h hz ih =>
    have hr : Name.referenceOrdinary b = false := by simpa [← Name.ordinary_classification] using h
    have ho := congrArg Result.output ih
    have hc := congrArg Result.count ih
    have ht := congrArg Result.rest ih
    simp only [project] at ho hc ht
    simp [Name.run,h,hz,reference,hr,project,ho,hc,ht,Nat.add_comm]
  | case4 owned b bs h hz hb hn =>
    simp [Name.run,h,hz,hb,hn,reference,← Name.ordinary_classification,project]
  | case5 owned b bs h hz hb hn e ih =>
    dsimp [e] at ih
    have ho := congrArg Result.output ih
    have hc := congrArg Result.count ih
    have ht := congrArg Result.rest ih
    simp only [project] at ho hc ht
    simp [Name.run,h,hz,hb,hn,reference,← Name.ordinary_classification,project,
      ← Escape.native_reference,ho,hc,ht]
  | case6 owned b bs h hz hb =>
    simp [Name.run,h,hz,hb,reference,← Name.ordinary_classification,project]

#print axioms source_semantics
end SemanticName
