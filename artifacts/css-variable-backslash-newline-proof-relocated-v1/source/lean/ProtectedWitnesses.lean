import ProtectedBoundary
set_option autoImplicit false
namespace ProtectedSpan.Witnesses

def slash : Token := ⟨.other,[92],true⟩
def lf : Token := ⟨.whitespace,[10],false⟩
def crlf : Token := ⟨.whitespace,[13,10],false⟩
def mixed : Token := ⟨.whitespace,[13,10,32,9],false⟩
def space : Token := ⟨.whitespace,[32],false⟩
def ordinary : Token := ⟨.other,[38],false⟩
def escaped : Token := ⟨.ident,[120,92,32],false⟩
def comment : Token := ⟨.delimSlash,[47,42,42,47],false⟩
def block : Token := ⟨.function,[102,40,92,10,41],false⟩
def eofIdent : Token := ⟨.ident,[92],false⟩

def asciiWhite (b : UInt8) : Bool := b==32 || b==9 || b==10 || b==12 || b==13
def oldTrim (raw : List UInt8) : List UInt8 := (raw.reverse.dropWhile asciiWhite).reverse
def standaloneStored (ts : List Token) : List UInt8 :=
  if persistent ts then bytes ts else oldTrim (bytes ts)

theorem lf_is_saved : stored [slash,lf]=[92,10] := by decide +kernel
theorem crlf_is_saved : stored [slash,crlf]=[92,13,10] := by decide +kernel
theorem whole_run_is_saved : stored [slash,mixed]=[92,13,10,32,9] := by decide +kernel
theorem old_trim_loses_required_newline : oldTrim (bytes [slash,lf])=[92] := by decide +kernel
theorem saved_suffix_metadata : lastMetadata [slash,lf]=some .whitespace := by decide +kernel
theorem same_class_different_lexical_role :
    slash.kind=ordinary.kind ∧ stored [ordinary,lf]=[38] := by decide +kernel
theorem final_flags_are_not_equal :
    (scan {} [slash,lf]).previousBackslash=false ∧ persistent [slash,lf]=true := by decide +kernel

theorem coalescing_is_required :
    stored [slash,lf,space]=[92,10] ∧
    bytes (retained [slash,lf,space])=[92,10,32] ∧
    standaloneStored [slash,lf,space]=[92,10,32] := by decide +kernel

theorem terminal_backslash_guard_counterexample :
    persistent [slash]=true ∧ protect [slash]=false := by decide +kernel

theorem integration_preserves_escaped_space : stored [escaped]=[120,92,32] := by decide +kernel
theorem standalone_still_has_prior_bug : standaloneStored [escaped]=[120,92] := by decide +kernel
theorem comment_resets_protection : stored [slash,lf,comment,space]=bytes [slash,lf,comment] := by decide +kernel
theorem outer_block_resets_protection : stored [slash,lf,block,space]=bytes [slash,lf,block] := by decide +kernel
theorem eof_ident_is_distinct :
    persistent [eofIdent]=false ∧ finishStored [eofIdent] 0 [239,191,189]=[92,239,191,189] := by decide +kernel

end ProtectedSpan.Witnesses
