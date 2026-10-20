import ProtectedWitnesses
set_option autoImplicit false
set_option linter.unusedSimpArgs false
namespace Independent86
open ProtectedSpan ProtectedSpan.Witnesses

def ident : Token := ⟨.ident,[122],false⟩
def unmarkedSlash : Token := ⟨.other,[92],false⟩
def emptyWhite : Token := ⟨.whitespace,[],false⟩
def good : List Token := [ident,space,slash,mixed]

example : coalesced good.reverse ∧ Followed good ∧
    (∀ t∈good,t.raw≠[]) ∧ InitialReady good := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : persistent good=protect good ∧ stored good=bytes (retained good) ∧
    (scan {} good).first=(retained good).head?.map Token.kind ∧
    lastMetadata good=(retained good).getLast?.map Token.kind :=
  protected_component good (by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel) (by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel)
    (by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel) (by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel)
example : stored good=[122,32,92,13,10,32,9] ∧
    lastMetadata good=some .whitespace := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : WellFormed unmarkedSlash ∧ WellFormed slash := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : Followed [unmarkedSlash,lf] ∧ coalesced [unmarkedSlash,lf].reverse ∧
    InitialReady [unmarkedSlash,lf] ∧ stored [unmarkedSlash,lf]=[92] := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : stored [slash,lf]≠stored [unmarkedSlash,lf] := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : ¬Followed [slash] ∧ persistent [slash]≠protect [slash] := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : ¬coalesced [slash,lf,space].reverse ∧
    stored [slash,lf,space]≠bytes (retained [slash,lf,space]) := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : (scan {} [space]).first≠(retained [space]).head?.map Token.kind := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : lastMetadata [ordinary,emptyWhite]≠(retained [ordinary,emptyWhite]).getLast?.map Token.kind := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : ¬EOFReady [ordinary,lf] 0 [41] ∧
    finishStored [ordinary,lf] 0 [41]≠completed [ordinary,lf] 0 [41] := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : EOFReady [block] 0 [41] ∧
    finishStored [block] 0 [41]=completed [block] 0 [41] := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : (scan {} [slash,mixed,comment,crlf]).trailing=2 ∧
    stored [slash,mixed,comment,crlf]=bytes [slash,mixed,comment] := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : persistent [slash,lf,escaped]=false ∧
    stored [slash,lf,escaped]≠standaloneStored [slash,lf,escaped] := by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel
example : ((stored good).take 3).drop 1=((bytes good).take 3).drop 1 :=
  retained_slice good (by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel) 1 3 (by simp [WellFormed, EOFReady, Followed, coalesced, InitialReady, startsNewline, good, ident, unmarkedSlash, emptyWhite, slash, lf, crlf, mixed, space, ordinary, escaped, comment, block, white] <;> decide +kernel)
end Independent86
