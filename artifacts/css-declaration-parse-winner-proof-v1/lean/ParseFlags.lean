import ParseWinners
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false
namespace ParseFlags
open AllOrder PublicStorage ParseWinners
variable {ι ν : Type} [DecidableEq ι]
local notation "E" => Entry ι ν

def pushFlag : List E → E → Bool
  | [], _ => true
  | old::rest, new =>
    if old.id=new.id then !(old.important && !new.important) else pushFlag rest new

theorem push_flag_exact (xs : List E) (new : E) (hu : unique xs) :
    pushFlag xs new = accepted xs new := by
  induction xs with
  | nil => simp [pushFlag,accepted,hasImportant]
  | cons old rest ih =>
    have ht : unique rest := (List.nodup_cons.mp hu).2
    by_cases hi : old.id=new.id
    · have ha : absent new.id rest := by
        intro e he hid
        exact (List.nodup_cons.mp hu).1 (List.mem_map.mpr ⟨e,he,hid.trans hi.symm⟩)
      have hnone := important_absent rest new.id ha
      simp only [pushFlag,hi,ite_true,accepted,hasImportant,List.any_cons,decide_true,Bool.true_and]
      change (!(old.important && !new.important)) = (new.important || !(old.important || hasImportant rest new.id))
      rw [hnone]
      cases old.important <;> cases new.important <;> rfl
    · simp [pushFlag,hi,ih ht,accepted,hasImportant]

def changed : List E → List E → Bool
  | _, [] => false
  | xs,new::rest => pushFlag xs new || changed (parseSet xs new) rest

def pushResult (state : List E × Bool) (new : E) : List E × Bool :=
  (parseSet state.1 new,state.2 || pushFlag state.1 new)

def extendResult (xs actions : List E) : List E × Bool := actions.foldl pushResult (xs,false)

theorem accumulate_exact (xs actions : List E) (flag : Bool) :
    actions.foldl pushResult (xs,flag) = (parseExtend xs actions,flag || changed xs actions) := by
  induction actions generalizing xs flag with
  | nil => simp [parseExtend,changed]
  | cons new rest ih =>
    simp only [List.foldl_cons,pushResult]
    rw [ih]
    simp [parseExtend,changed,Bool.or_assoc]

theorem returned_flag_and_state (xs actions : List E) :
    extendResult xs actions = (parseExtend xs actions,changed xs actions) := by
  simpa [extendResult] using accumulate_exact xs actions false

theorem exact_change_bit (xs actions : List E) (hu : unique xs) :
    changed xs actions = actions.any (fun new => new.important || !hasImportant xs new.id) := by
  induction actions with
  | nil => rfl
  | cons new rest ih =>
    rw [changed,push_flag_exact xs new hu]
    cases ha : accepted xs new
    · have hstate : parseSet xs new = xs := by rw [parse_set_formula xs new hu,ha]; rfl
      simp only [Bool.false_or,hstate,List.any_cons]
      change changed xs rest = (accepted xs new || _)
      rw [ha]
      simpa using ih
    · simp only [Bool.true_or,List.any_cons]
      change true = (accepted xs new || _)
      rw [ha];rfl

theorem rejected_push_retains_all (xs : List E) (new : E) (hu : unique xs)
    (h : pushFlag xs new = false) : parseSet xs new = xs := by
  rw [push_flag_exact xs new hu] at h
  rw [parse_set_formula xs new hu,h]
  rfl

theorem all_rejected_retains_all (xs actions : List E) (hu : unique xs)
    (h : changed xs actions = false) : parseExtend xs actions = xs := by
  induction actions generalizing xs with
  | nil => rfl
  | cons new rest ih =>
    have hc : pushFlag xs new=false ∧ changed (parseSet xs new) rest=false := by simpa [changed] using h
    have he := rejected_push_retains_all xs new hu hc.1
    change parseExtend (parseSet xs new) rest = xs
    rw [he]
    apply ih xs hu
    simpa [he] using hc.2

theorem full_winner_and_flag (initial actions : List E) (hu : unique initial) :
    extendResult initial actions =
      (winners (initial++actions),actions.any (fun new => new.important || !hasImportant initial new.id)) := by
  rw [returned_flag_and_state,arbitrary_initial_prefix initial actions hu,exact_change_bit initial actions hu]

end ParseFlags
