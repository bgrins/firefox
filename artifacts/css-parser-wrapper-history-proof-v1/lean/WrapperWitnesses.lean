import WrapperBounds
import WrapperEpochs
set_option autoImplicit false
set_option linter.unusedSimpArgs false
set_option maxRecDepth 10000
set_option maxHeartbeats 3000000
namespace WrapperWitnesses
open PublicCache

def names : List (List Byte) := [[118,97,114]]
def read (bytes : List Byte) := ByteLex.read (fun _ _ => 1) bytes
def initial : State := constructor ⟨none,none⟩
def next (bytes : List Byte) (s : State) := WrapperNext.native bytes (read bytes) (fun _ => false) names s

def nested : List Byte := [40,118,97,114,40,41,41,32,58]
def opened : State := (next nested initial).state
def skipped : State := (WrapperSkip.native nested (read nested) names (PublicHistory.begin names opened)).state

theorem nested_var_name : Name.run false [118,97,114,40,41,41,32,58] = ⟨[118,97,114],3,[40,41,41,32,58],false⟩ := by
 simp only [Name.run]
 decide

theorem nested_read0 : read nested 0=⟨.open .parenthesis,⟨1,some .parenthesis⟩⟩ := by decide
theorem nested_read1 : read nested 1=⟨.function [118,97,114],⟨5,some .parenthesis⟩⟩ := by
 simp only [read,ByteLex.read,ByteLex.native,ByteLex.identToken,ByteLex.selected,URLDispatch.native,
   URLDispatch.finish,URLDispatch.nativeURL,nested,List.drop_succ_cons,List.drop_zero,List.tail_cons,nested_var_name]
 decide
theorem nested_read5 : read nested 5=⟨.close .parenthesis,⟨6,none⟩⟩ := by decide
theorem nested_read6 : read nested 6=⟨.close .parenthesis,⟨7,none⟩⟩ := by decide
theorem nested_read8 : read nested 8=⟨.colon,⟨9,none⟩⟩ := by decide

theorem pending_cleanup_observes : seen skipped.mode=true := by
 have h0 := nested_read0
 have h1 := nested_read1
 have h5 := nested_read5
 have h6 := nested_read6
 have h8 := nested_read8
 simp only [nested] at h0 h1 h5 h6 h8
 simp [skipped,opened,next,names,initial,nested,
   WrapperNext.native,WrapperSkip.native,WrapperWhitespace.run,WrapperWhitespace.nativeUnit,WrapperWhitespace.advance,
   PublicNext.native,PublicCleanup.pending,PublicCleanup.run,PublicCleanup.done,PublicCleanup.clear,
   PublicFetch.fetchReady,PublicFetch.freshOutput,PublicHistory.begin,PublicCache.constructor,PublicCache.fresh,
   PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,
   h0,h1,h5,h6,h8,WrapperEntry.expectColon]
 all_goals decide

theorem raw_skip_retains_opener_cache : skipped.cache=opened.cache := by
 have h0 := nested_read0
 have h1 := nested_read1
 have h5 := nested_read5
 have h6 := nested_read6
 have h8 := nested_read8
 simp only [nested] at h0 h1 h5 h6 h8
 simp [skipped,opened,next,names,initial,nested,
   WrapperNext.native,WrapperSkip.native,WrapperWhitespace.run,WrapperWhitespace.nativeUnit,WrapperWhitespace.advance,
   PublicNext.native,PublicCleanup.pending,PublicCleanup.run,PublicCleanup.done,PublicCleanup.clear,
   PublicFetch.fetchReady,PublicFetch.freshOutput,PublicHistory.begin,PublicCache.constructor,PublicCache.fresh,
   PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,
   h0,h1,h5,h6,h8,WrapperEntry.expectColon]
 all_goals decide

theorem raw_skip_stops_at_colon : skipped.cursor=⟨8,none⟩ := by
 have h0 := nested_read0
 have h1 := nested_read1
 have h5 := nested_read5
 have h6 := nested_read6
 have h8 := nested_read8
 simp only [nested] at h0 h1 h5 h6 h8
 simp [skipped,opened,next,names,initial,nested,
   WrapperNext.native,WrapperSkip.native,WrapperWhitespace.run,WrapperWhitespace.nativeUnit,WrapperWhitespace.advance,
   PublicNext.native,PublicCleanup.pending,PublicCleanup.run,PublicCleanup.done,PublicCleanup.clear,
   PublicFetch.fetchReady,PublicFetch.freshOutput,PublicHistory.begin,PublicCache.constructor,PublicCache.fresh,
   PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,
   h0,h1,h5,h6,h8,WrapperEntry.expectColon]
 all_goals decide

theorem next_colon_entry : (WrapperEntry.expectColon nested (read nested) (fun _=>false) names skipped).1=true := by
 have h0 := nested_read0
 have h1 := nested_read1
 have h5 := nested_read5
 have h6 := nested_read6
 have h8 := nested_read8
 simp only [nested] at h0 h1 h5 h6 h8
 simp [skipped,opened,next,names,initial,nested,
   WrapperNext.native,WrapperSkip.native,WrapperWhitespace.run,WrapperWhitespace.nativeUnit,WrapperWhitespace.advance,
   PublicNext.native,PublicCleanup.pending,PublicCleanup.run,PublicCleanup.done,PublicCleanup.clear,
   PublicFetch.fetchReady,PublicFetch.freshOutput,PublicHistory.begin,PublicCache.constructor,PublicCache.fresh,
   PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,
   h0,h1,h5,h6,h8,WrapperEntry.expectColon]
 all_goals decide

def lateBytes : List Byte := [118,97,114,40,41]
def cached : State := (next lateBytes (save initial)).state
def late : State := PublicHistory.begin names (restore 0 cached)

theorem wrapper_late_enable_still_misses : seen (next lateBytes late).state.mode=false := by
 simp [skipped,opened,next,nested,read,initial,names,lateBytes,cached,late,
   WrapperNext.native,WrapperNext.reference,WrapperSkip.native,WrapperSkip.reference,
   WrapperWhitespace.run,WrapperWhitespace.reference,WrapperWhitespace.nativeUnit,WrapperWhitespace.referenceUnit,WrapperWhitespace.advance,
   PublicNext.native,PublicNext.reference,PublicCleanup.pending,PublicCleanup.run,PublicCleanup.done,PublicCleanup.clear,
   PublicFetch.fetchReady,PublicFetch.freshOutput,PublicSourceOnly.pending,PublicSourceOnly.ready,PublicSourceOnly.cleanup,
   PublicHistory.begin,PublicHistory.query,PublicCache.constructor,PublicCache.fresh,PublicCache.save,PublicCache.restore,PublicCache.hit,
   PublicCache.cacheRelevant,PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,
   ByteLex.read,ByteLex.native,ByteLex.selected,ByteLex.other,ByteLex.identToken,ByteLex.pending,
   IdentifierStart.nativeAscii,URLDispatch.native,URLDispatch.finish,URLDispatch.nativeURL,Name.run,Name.ordinary,Name.simple,Name.continuation,Name.fourIntro,
   WrapperEntry.expectColon]
 all_goals decide
theorem wrapper_reference_sees_late_function :
 (WrapperNext.reference lateBytes (read lateBytes) (fun _=>false) late.cursor).observations.any (relevant names)=true := by
 simp [skipped,opened,next,nested,read,initial,names,lateBytes,cached,late,
   WrapperNext.native,WrapperNext.reference,WrapperSkip.native,WrapperSkip.reference,
   WrapperWhitespace.run,WrapperWhitespace.reference,WrapperWhitespace.nativeUnit,WrapperWhitespace.referenceUnit,WrapperWhitespace.advance,
   PublicNext.native,PublicNext.reference,PublicCleanup.pending,PublicCleanup.run,PublicCleanup.done,PublicCleanup.clear,
   PublicFetch.fetchReady,PublicFetch.freshOutput,PublicSourceOnly.pending,PublicSourceOnly.ready,PublicSourceOnly.cleanup,
   PublicHistory.begin,PublicHistory.query,PublicCache.constructor,PublicCache.fresh,PublicCache.save,PublicCache.restore,PublicCache.hit,
   PublicCache.cacheRelevant,PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,
   ByteLex.read,ByteLex.native,ByteLex.selected,ByteLex.other,ByteLex.identToken,ByteLex.pending,
   IdentifierStart.nativeAscii,URLDispatch.native,URLDispatch.finish,URLDispatch.nativeURL,Name.run,Name.ordinary,Name.simple,Name.continuation,Name.fourIntro,
   WrapperEntry.expectColon]
 all_goals decide
theorem late_cache_not_safe : cacheRelevant names late=true := by
 simp [skipped,opened,next,nested,read,initial,names,lateBytes,cached,late,
   WrapperNext.native,WrapperNext.reference,WrapperSkip.native,WrapperSkip.reference,
   WrapperWhitespace.run,WrapperWhitespace.reference,WrapperWhitespace.nativeUnit,WrapperWhitespace.referenceUnit,WrapperWhitespace.advance,
   PublicNext.native,PublicNext.reference,PublicCleanup.pending,PublicCleanup.run,PublicCleanup.done,PublicCleanup.clear,
   PublicFetch.fetchReady,PublicFetch.freshOutput,PublicSourceOnly.pending,PublicSourceOnly.ready,PublicSourceOnly.cleanup,
   PublicHistory.begin,PublicHistory.query,PublicCache.constructor,PublicCache.fresh,PublicCache.save,PublicCache.restore,PublicCache.hit,
   PublicCache.cacheRelevant,PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,
   ByteLex.read,ByteLex.native,ByteLex.selected,ByteLex.other,ByteLex.identToken,ByteLex.pending,
   IdentifierStart.nativeAscii,URLDispatch.native,URLDispatch.finish,URLDispatch.nativeURL,Name.run,Name.ordinary,Name.simple,Name.continuation,Name.fourIntro,
   WrapperEntry.expectColon]
 all_goals decide
theorem failed_colon_not_safe :
 (WrapperEntry.expectColon lateBytes (read lateBytes) (fun _=>false) names initial).1=false ∧
 cacheRelevant names (WrapperEntry.expectColon lateBytes (read lateBytes) (fun _=>false) names initial).2=true := by
 simp [skipped,opened,next,nested,read,initial,names,lateBytes,cached,late,
   WrapperNext.native,WrapperNext.reference,WrapperSkip.native,WrapperSkip.reference,
   WrapperWhitespace.run,WrapperWhitespace.reference,WrapperWhitespace.nativeUnit,WrapperWhitespace.referenceUnit,WrapperWhitespace.advance,
   PublicNext.native,PublicNext.reference,PublicCleanup.pending,PublicCleanup.run,PublicCleanup.done,PublicCleanup.clear,
   PublicFetch.fetchReady,PublicFetch.freshOutput,PublicSourceOnly.pending,PublicSourceOnly.ready,PublicSourceOnly.cleanup,
   PublicHistory.begin,PublicHistory.query,PublicCache.constructor,PublicCache.fresh,PublicCache.save,PublicCache.restore,PublicCache.hit,
   PublicCache.cacheRelevant,PublicCache.track,PublicCache.annotate,PublicCache.relevant,PublicCache.seen,
   ByteLex.read,ByteLex.native,ByteLex.selected,ByteLex.other,ByteLex.identToken,ByteLex.pending,
   IdentifierStart.nativeAscii,URLDispatch.native,URLDispatch.finish,URLDispatch.nativeURL,Name.run,Name.ordinary,Name.simple,Name.continuation,Name.fourIntro,
   WrapperEntry.expectColon]
 all_goals decide

def annotated : List Byte := [40,47,42,35,32,115,111,117,114,99,101,77,97,112,112,105,110,103,85,82,76,61,65,32,42,47,41,47,42,35,32,115,111,117,114,99,101,77,97,112,112,105,110,103,85,82,76,61,66,32,42,47]
def annotationOpen := (PublicNext.native annotated (read annotated) (fun _=>false) [] initial).state
def annotationSaved := save annotationOpen
def annotationCached := (PublicNext.native annotated (read annotated) (fun _=>false) [] annotationSaved).state
def annotationReset := restore 0 annotationCached

theorem primary_replay_leaves_A :
 (PublicNext.native annotated (read annotated) (fun _=>false) [] annotationReset).state.urls.sourceMap=
 some ([65]) := by decide
theorem next_raw_comment_restores_B :
 (WrapperNext.native annotated (read annotated) (fun _=>false) [] annotationReset).state.urls.sourceMap=
 some ([66]) := by decide

theorem exact_whitespace_set_and_CRLF :
 (WrapperWhitespace.reference [32,9,13,10,12,10,58] 8 0).position=6 ∧
 (WrapperWhitespace.reference [11,58] 3 0).position=0 := by decide

end WrapperWitnesses
