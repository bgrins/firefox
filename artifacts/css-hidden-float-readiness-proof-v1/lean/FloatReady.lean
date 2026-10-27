import LineReady

namespace FloatReady
open Subtree

def skipLine (w : World) : World :=
  {w with principal := (LineReady.newSkip ⟨true, w.principal⟩).children}

def markEntry (isPushed : Tree → Bool) (t : Tree) : Tree :=
  if isPushed t then t else markRoot t

def markOwner (hidden ownsAnonymous : Bool) (isPushed : Tree → Bool)
    (w : World) : World :=
  if hidden && !ownsAnonymous then
    {w with otherLists := w.otherLists.map (markEntry isPushed)}
  else w

def floatEligible (n : Nat) (path : List Nat) (w : World) : Bool :=
  (w.otherLists[n]?).any (eligibleAt path)

theorem line_projection (w : World) :
    (skipLine w).principal = (markPrincipal w).principal := rfl

theorem line_does_not_follow_float_pointer (w : World) :
    (skipLine w).otherLists = w.otherLists := rfl

theorem line_cannot_change_float_readiness (w : World) (n : Nat) (path : List Nat) :
    floatEligible n path (skipLine w) = floatEligible n path w := rfl

theorem visible_owner_unchanged (owns : Bool) (pushed : Tree → Bool) (w : World) :
    markOwner false owns pushed w = w := by simp [markOwner]

theorem anonymous_owner_unchanged (hidden : Bool) (pushed : Tree → Bool) (w : World) :
    markOwner hidden true pushed w = w := by simp [markOwner]

theorem owner_preserves_nonselected_storage (hidden owns : Bool)
    (pushed : Tree → Bool) (w : World) :
    (markOwner hidden owns pushed w).principal = w.principal ∧
    (markOwner hidden owns pushed w).ownDirty = w.ownDirty ∧
    (markOwner hidden owns pushed w).externalOutOfFlow = w.externalOutOfFlow ∧
    (markOwner hidden owns pushed w).nextContinuation = w.nextContinuation := by
  simp [markOwner]; split <;> simp

theorem current_list_length_preserved (hidden owns : Bool)
    (pushed : Tree → Bool) (w : World) :
    (markOwner hidden owns pushed w).otherLists.length = w.otherLists.length := by
  simp [markOwner]; split <;> simp

theorem selected_root_lookup (pushed : Tree → Bool) (w : World) (n : Nat)
    (t : Tree) (found : w.otherLists[n]? = some t) (notPushed : pushed t = false) :
    (markOwner true false pushed w).otherLists[n]? = some (markRoot t) := by
  simp [markOwner, List.getElem?_map, found, markEntry, notPushed]

theorem pushed_root_untouched (pushed : Tree → Bool) (w : World) (n : Nat)
    (t : Tree) (found : w.otherLists[n]? = some t) (isPushed : pushed t = true) :
    (markOwner true false pushed w).otherLists[n]? = some t := by
  simp [markOwner, List.getElem?_map, found, markEntry, isPushed]

theorem selected_root_ready (pushed : Tree → Bool) (w : World) (n : Nat)
    (t : Tree) (found : w.otherLists[n]? = some t) (notPushed : pushed t = false) :
    floatEligible n [] (markOwner true false pushed w) = true := by
  simp [floatEligible, selected_root_lookup pushed w n t found notPushed,
    eligibleAt, locate, root_is_eligible]

theorem selected_path_ready (pushed : Tree → Bool) (w : World) (n : Nat)
    (path : List Nat) (t : Tree) (found : w.otherLists[n]? = some t)
    (notPushed : pushed t = false) (clear : clearRootPath path t = true) :
    floatEligible n path (markOwner true false pushed w) = true := by
  simpa [floatEligible, selected_root_lookup pushed w n t found notPushed] using
    clear_root_path_marks path t clear

theorem selected_root_coverage (pushed : Tree → Bool) (t : Tree)
    (notPushed : pushed t = false) :
    allDirty (markEntry pushed t) = rootClosure t := by
  simp [markEntry, notPushed, root_coverage_exact]

theorem selected_closed_descendant_ready (pushed : Tree → Bool) (t target : Tree)
    (path : List Nat) (notPushed : pushed t = false)
    (closure : rootClosure t = true)
    (found : locate path (markEntry pushed t) = some target) :
    eligible target = true :=
  LineReady.allDirty_locate path (markEntry pushed t) target
    (by rw [selected_root_coverage pushed t notPushed, closure]) found

theorem selected_query_recovers_provider (pushed : Tree → Bool) (w : World)
    (n : Nat) (path : List Nat) (t target : Tree)
    (frame : Hidden.Frame) (layout : Hidden.Key → Hidden.Size) (key : Hidden.Key)
    (member : w.otherLists[n]? = some t) (notPushed : pushed t = false)
    (clear : clearRootPath path t = true)
    (targetFound : (markOwner true false pushed w).otherLists[n]?.bind (locate path) = some target) :
    (Hidden.geometryQuery true layout key {frame with dirty := eligible target}).geometry = layout key := by
  have found : locate path (markRoot t) = some target := by
    simpa [selected_root_lookup pushed w n t member notPushed] using targetFound
  exact selected_query_recovery path t target frame layout key clear found

def clean (id : Nat) : Tree := .node id false false false []
def placeholder : Tree := clean 1
def realFloat : Tree := .node 2 false false false [clean 3]
def fixture : World := ⟨false, [placeholder], [realFloat], [clean 4], [clean 5]⟩
def noPushed : Tree → Bool := fun _ => false

theorem placeholder_marked_float_and_leaf_clean :
    ((skipLine fixture).principal[0]?).any eligible = true ∧
    floatEligible 0 [] (skipLine fixture) = false ∧
    floatEligible 0 [0] (skipLine fixture) = false := by
  simp [floatEligible, skipLine, LineReady.newSkip, fixture, placeholder, realFloat, clean, markRoot, eligibleAt, locate, eligible]
  all_goals decide

theorem owner_mark_recovers_float_and_leaf :
    floatEligible 0 [] (markOwner true false noPushed (skipLine fixture)) = true ∧
    floatEligible 0 [0] (markOwner true false noPushed (skipLine fixture)) = true := by
  simp [floatEligible, markOwner, markEntry, skipLine, LineReady.newSkip, fixture, placeholder, realFloat, clean, noPushed, markRoot, markDesc, eligibleAt, locate, eligible]
  all_goals decide

theorem nested_inline_placeholder_still_cannot_reach_float :
    let w := {fixture with principal := [.node 10 false false false [placeholder]]}
    ((skipLine w).principal[0]?).any (eligibleAt [0]) = true ∧
    floatEligible 0 [0] (skipLine w) = false := by
  simp [floatEligible, skipLine, LineReady.newSkip, fixture, placeholder, realFloat, clean, markRoot, markDesc, eligibleAt, locate, eligible]
  all_goals decide

theorem ordinary_owner_subtree_can_reach_its_float :
    eligibleAt [1, 0] (markRoot (.node 10 false false false [placeholder, realFloat])) = true := by
  simp [placeholder, realFloat, clean, markRoot, markDesc, eligibleAt, locate, eligible]
  all_goals decide

theorem dirty_float_root_does_not_restore_clean_leaf :
    let w := {fixture with otherLists := [.node 2 true false false [clean 3]]}
    floatEligible 0 [] (markOwner true false noPushed w) = true ∧
    floatEligible 0 [0] (markOwner true false noPushed w) = false := by
  simp [floatEligible, markOwner, markEntry, fixture, placeholder, realFloat, clean, noPushed, markRoot, eligibleAt, locate, eligible]
  all_goals decide

theorem pushed_float_excluded_witness :
    floatEligible 0 [] (markOwner true false (fun _ => true) fixture) = false ∧
    floatEligible 0 [0] (markOwner true false (fun _ => true) fixture) = false := by
  simp [floatEligible, markOwner, markEntry, fixture, placeholder, realFloat, clean, eligibleAt, locate, eligible]
  all_goals decide

theorem external_and_continuation_stay_clean :
    ((markOwner true false noPushed fixture).externalOutOfFlow[0]?).any eligible = false ∧
    ((markOwner true false noPushed fixture).nextContinuation[0]?).any eligible = false := by
  simp [markOwner, markEntry, fixture, placeholder, realFloat, clean, noPushed, markRoot, markDesc, eligible]
  all_goals decide

theorem placeholder_query_stale_float_query_then_provider :
    let target := {Hidden.warm with dirty := floatEligible 0 [0] (skipLine fixture)}
    let key := {Hidden.key 32 with computed := ⟨24, 50⟩}
    (Hidden.geometryQuery true Hidden.fixedBlock key target).geometry = ⟨24, 32⟩ ∧
    (Hidden.geometryQuery true Hidden.fixedBlock key
      {target with dirty := floatEligible 0 [0] (markOwner true false noPushed (skipLine fixture))}).geometry = ⟨24, 50⟩ := by
  simp [floatEligible, markOwner, markEntry, skipLine, LineReady.newSkip,
    fixture, placeholder, realFloat, clean, noPushed, markRoot, markDesc,
    eligibleAt, locate, eligible, Hidden.geometryQuery, Hidden.measure,
    Hidden.canReuse, Hidden.fixedBlock, Hidden.warm, Hidden.key]
  all_goals decide

end FloatReady
