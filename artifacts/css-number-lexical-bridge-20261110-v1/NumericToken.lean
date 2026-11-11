import NumericLexical
import Integration
import SemanticName
namespace NumericToken
open NumericDigits NumericEntry

inductive Kind where
  | number | percentage | dimension
  deriving DecidableEq,Repr

structure Result where
  kind : Kind
  numeric : NumericLexical.Result
  unit : List Byte
  count : Nat
  rest : List Byte
  deriving DecidableEq,Repr

def percent (xs : List Byte) : Bool := xs.head?.any (fun b => b.val == 37)
def ident (xs : List Byte) : Bool := IdentifierStart.corrected (xs.map Fin.val)

def native (xs : List Byte) : Result :=
  let n := NumericLexical.native xs
  if percent n.rest then ⟨.percentage,n,[],n.text.length+1,n.rest.drop 1⟩
  else if ident n.rest then
    let u := Name.run false n.rest
    ⟨.dimension,n,u.output,n.text.length+u.count,u.rest⟩
  else ⟨.number,n,[],n.text.length,n.rest⟩

def reference (xs : List Byte) : Result :=
  let n := NumericLexical.reference xs
  if ident n.rest then
    let u := SemanticName.reference n.rest
    ⟨.dimension,n,u.output,n.text.length+u.count,u.rest⟩
  else if percent n.rest then ⟨.percentage,n,[],n.text.length+1,n.rest.drop 1⟩
  else ⟨.number,n,[],n.text.length,n.rest⟩

theorem percent_excludes_ident (xs : List Byte) (h : percent xs = true) : ident xs = false := by
  cases xs with
  | nil => simp [percent] at h
  | cons b bs =>
    have hb : b.val = 37 := by simpa [percent] using h
    simp [ident,IdentifierStart.corrected,IdentifierStart.nativeAscii,hb]

theorem native_reference (xs : List Byte) : native xs = reference xs := by
  have hn := NumericLexical.native_reference xs
  have hu := SemanticName.source_semantics false (NumericLexical.native xs).rest
  have ho := congrArg SemanticName.Result.output hu
  have hc := congrArg SemanticName.Result.count hu
  have hr := congrArg SemanticName.Result.rest hu
  simp only [SemanticName.project] at ho hc hr
  unfold native reference
  rw [← hn]
  cases hp : percent (NumericLexical.native xs).rest
  · cases hi : ident (NumericLexical.native xs).rest <;> simp [hp,hi,ho,hc,hr]
  · have hi := percent_excludes_ident _ hp
    simp [hp,hi]

theorem count_bound (xs : List Byte) : (native xs).count ≤ xs.length := by
  have cover := congrArg List.length (NumericLexical.cover xs)
  simp only [List.length_append] at cover
  unfold native
  dsimp only
  split
  · rename_i h
    have hr : 0 < (NumericLexical.native xs).rest.length := by
      cases he : (NumericLexical.native xs).rest with
      | nil => simp [he,percent] at h
      | cons b bs => simp
    simp only
    omega
  · split
    · have hb := Name.consumed_bound false (NumericLexical.native xs).rest
      simp only
      omega
    · simp only
      omega

theorem exact_suffix (xs : List Byte) : (native xs).rest = xs.drop (native xs).count := by
  have hn := NumericLexical.exact_suffix xs
  unfold native
  dsimp only
  split
  · simp only
    rw [hn,List.drop_drop]
  · split
    · simp only
      rw [Name.exact_remainder,hn,List.drop_drop]
    · exact hn

theorem positive (xs : List Byte) (h : nativeStart xs = true) : 0 < (native xs).count := by
  have hn := NumericLexical.positive xs h
  unfold native
  dsimp only
  split
  · simp only; omega
  · split <;> simp only <;> omega

theorem dimension_unit (xs : List Byte) (h : (native xs).kind = .dimension) :
    (native xs).unit = (SemanticName.reference (NumericLexical.native xs).rest).output := by
  have hu := SemanticName.source_semantics false (NumericLexical.native xs).rest
  have ho := congrArg SemanticName.Result.output hu
  simp only [SemanticName.project] at ho
  unfold native at h ⊢
  dsimp only at h ⊢
  split at h <;> simp_all
  split at h <;> simp_all

#print axioms percent_excludes_ident
#print axioms native_reference
#print axioms count_bound
#print axioms exact_suffix
#print axioms positive
#print axioms dimension_unit
end NumericToken
