import PublicEpochs
import ByteLexProgress
import FunctionMatching
set_option autoImplicit false
set_option linter.unusedSimpArgs false
set_option maxRecDepth 10000
set_option maxHeartbeats 10000000
namespace PublicByteWitnesses
open PublicCache

def varInput : List Byte := [118,97,114,40,45,45,120,41]
def names : List (List Byte) := [[118,97,114]]
def initial : State := constructor ⟨none,none⟩
def reader (source : List Byte) : Nat → Lexeme := ByteLex.read (fun _ _ => 1) source

def fetch (source : List Byte) (s : State) : State :=
 (PublicNext.native source (reader source) (fun _=>false) names s).state

def prime : State := PublicCache.restore 0 (fetch varInput (PublicCache.save initial))
def late : State := fetch varInput (PublicHistory.begin names prime)

theorem var_name : Name.run false [118,97,114,40,45,45,120,41] = ⟨[118,97,114],3,[40,45,45,120,41],false⟩ := by
 simp only [Name.run]
 decide

theorem var_read : reader varInput 0 = ⟨.function [118,97,114],⟨4,some .parenthesis⟩⟩ := by
 simp only [reader,ByteLex.read,ByteLex.native,ByteLex.identToken,ByteLex.selected,URLDispatch.native,
   URLDispatch.finish,URLDispatch.nativeURL,varInput,List.drop_zero,var_name]
 decide

theorem var_head : varInput[0]?=some 118 := rfl

theorem cold_control : seen (fetch varInput (PublicHistory.begin names initial)).mode=true := by
 simp [fetch,prime,late,initial,PublicNext.native,PublicNext.reference,PublicCleanup.pending,PublicFetch.fetchReady,PublicFetch.freshOutput,PublicSourceOnly.pending,PublicSourceOnly.ready,PublicHistory.begin,PublicHistory.query,PublicCache.constructor,PublicCache.fresh,PublicCache.save,PublicCache.restore,PublicCache.hit,PublicCache.cacheRelevant,PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,names,var_read,var_head]
 all_goals decide

theorem late_enable_byte_counterexample :
 seen late.mode=false ∧ cacheRelevant names prime=true ∧
 (PublicNext.reference varInput (reader varInput) (fun _=>false) prime.cursor).observations.any (relevant names)=true := by
 simp [fetch,prime,late,initial,PublicNext.native,PublicNext.reference,PublicCleanup.pending,PublicFetch.fetchReady,PublicFetch.freshOutput,PublicSourceOnly.pending,PublicSourceOnly.ready,PublicHistory.begin,PublicHistory.query,PublicCache.constructor,PublicCache.fresh,PublicCache.save,PublicCache.restore,PublicCache.hit,PublicCache.cacheRelevant,PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,names,var_read,var_head]
 all_goals decide

def tracked : State := fetch varInput (PublicHistory.begin names (PublicCache.save initial))
def queried : State := (PublicHistory.query tracked).2
def reenabled : State := PublicHistory.begin names (PublicCache.restore 0 queried)

theorem query_reenable_byte_counterexample :
 (PublicHistory.query tracked).1=true ∧ seen (fetch varInput reenabled).mode=false ∧
 cacheRelevant names reenabled=true := by
 simp [tracked,queried,reenabled,fetch,prime,late,initial,PublicNext.native,PublicNext.reference,PublicCleanup.pending,PublicFetch.fetchReady,PublicFetch.freshOutput,PublicSourceOnly.pending,PublicSourceOnly.ready,PublicHistory.begin,PublicHistory.query,PublicCache.constructor,PublicCache.fresh,PublicCache.save,PublicCache.restore,PublicCache.hit,PublicCache.cacheRelevant,PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,names,var_read,var_head]
 all_goals decide

def annotationInput (key : String) : List Byte :=
 CommentDirectives.ascii ("(/*# "++key++"=A */)/*# "++key++"=B */")
def afterOpen (key : String) : State := PublicCache.save (fetch (annotationInput key) initial)
def firstComments (key : String) : State := fetch (annotationInput key) (afterOpen key)
def replayComments (key : String) : State :=
 fetch (annotationInput key) (PublicCache.restore 0 (firstComments key))

theorem source_annotation_byte_counterexample :
 (firstComments "sourceURL").urls.source=some [66] ∧
 (replayComments "sourceURL").urls.source=some [65] ∧
 (replayComments "sourceURL").cursor.position=(annotationInput "sourceURL").length := by
 decide

theorem map_annotation_byte_counterexample :
 (firstComments "sourceMappingURL").urls.sourceMap=some [66] ∧
 (replayComments "sourceMappingURL").urls.sourceMap=some [65] ∧
 (replayComments "sourceMappingURL").cursor.position=(annotationInput "sourceMappingURL").length := by
 decide

end PublicByteWitnesses
