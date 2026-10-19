import PublicStorage
set_option linter.unusedSectionVars false
namespace ParseWinners
open AllOrder PublicStorage
variable {ι ν : Type} [DecidableEq ι]
local notation "E" => Entry ι ν

def hasImportant (history : List E) (id : ι) : Bool :=
  history.any (fun e => decide (e.id=id) && e.important)

def preferred (history : List E) : List E :=
  history.filter (fun e => e.important || !hasImportant history e.id)

def lastOnly : List E → List E
  | [] => []
  | e::rest => if rest.any (fun x => decide (x.id=e.id)) then lastOnly rest else e::lastOnly rest

def winners (history : List E) : List E := lastOnly (preferred history)

theorem last_membership (xs : List E) (id : ι) :
    id ∈ (lastOnly xs).map Entry.id ↔ id ∈ xs.map Entry.id := by
  induction xs with
  | nil => rfl
  | cons e rest ih =>
    simp only [lastOnly]
    split
    · next h =>
      have hm : e.id ∈ rest.map Entry.id := by
        obtain ⟨x,hx,hi⟩ := List.any_eq_true.mp h
        exact List.mem_map.mpr ⟨x,hx,of_decide_eq_true hi⟩
      rw [ih]
      simp only [List.map_cons,List.mem_cons]
      constructor
      · exact Or.inr
      · intro h; rcases h with rfl | h
        · exact hm
        · exact h
    · simp [ih]

theorem last_sublist (xs : List E) : (lastOnly xs).Sublist xs := by
  induction xs with
  | nil => exact .slnil
  | cons e rest ih =>
    simp only [lastOnly]
    split
    · exact ih.cons e
    · exact ih.cons_cons e

theorem last_unique (xs : List E) : unique (lastOnly xs) := by
  induction xs with
  | nil => simp [lastOnly,unique]
  | cons e rest ih =>
    simp only [lastOnly]
    split
    · exact ih
    · next h =>
      apply List.nodup_cons.mpr
      refine ⟨?_,ih⟩
      intro hm
      obtain ⟨x,hx,hi⟩ := List.mem_map.mp ((last_membership rest e.id).mp hm)
      exact h (List.any_eq_true.mpr ⟨x,hx,by simp [hi]⟩)

theorem last_append (xs : List E) (new : E) :
    lastOnly (xs++[new]) = (lastOnly xs).filter (fun e => decide (e.id≠new.id)) ++ [new] := by
  induction xs with
  | nil => simp [lastOnly]
  | cons e rest ih =>
    by_cases he : e.id=new.id
    · simp [lastOnly,ih,he,List.filter_cons]
      split <;> simp_all
    · have hn : new.id ≠ e.id := Ne.symm he
      simp only [List.cons_append,lastOnly,List.any_append,List.any_cons,List.any_nil,Bool.or_false]
      simp only [hn,decide_false,Bool.or_false]
      split <;> simp_all

theorem last_filter (xs : List E) (keep : ι → Bool) :
    lastOnly (xs.filter (fun e => keep e.id)) = (lastOnly xs).filter (fun e => keep e.id) := by
  induction xs with
  | nil => rfl
  | cons e rest ih =>
    cases hk : keep e.id
    · simp [List.filter_cons,hk,lastOnly]
      split <;> simp [hk,ih]
    · have he : (rest.filter (fun x => keep x.id)).any (fun x => decide (x.id=e.id)) =
          rest.any (fun x => decide (x.id=e.id)) := by
        apply Bool.eq_iff_iff.mpr
        constructor
        · intro h
          obtain ⟨x,hx,hi⟩ := List.any_eq_true.mp h
          exact List.any_eq_true.mpr ⟨x,(List.mem_filter.mp hx).1,hi⟩
        · intro h
          obtain ⟨x,hx,hi⟩ := List.any_eq_true.mp h
          have hid := of_decide_eq_true hi
          exact List.any_eq_true.mpr ⟨x,List.mem_filter.mpr ⟨hx,by simpa [hid] using hk⟩,hi⟩
      simp [List.filter_cons,hk,lastOnly,he,ih]
      split <;> simp [hk]

def accepted (history : List E) (new : E) : Bool :=
  new.important || !hasImportant history new.id

theorem important_append (history : List E) (new : E) (id : ι) :
    hasImportant (history++[new]) id = (hasImportant history id || (decide (new.id=id) && new.important)) := by
  simp only [hasImportant,List.any_append,List.any_cons,List.any_nil,Bool.or_false]

theorem preferred_away (history : List E) (new : E) :
    ((history.filter (fun e => e.important || !hasImportant (history++[new]) e.id)).filter
      (fun e => decide (e.id≠new.id))) =
    (preferred history).filter (fun e => decide (e.id≠new.id)) := by
  simp only [preferred,List.filter_filter]
  congr 1
  funext e
  by_cases he : e.id=new.id
  · simp [he]
  · simp [important_append,he,Ne.symm he]

theorem winners_append_accepted (history : List E) (new : E) (ha : accepted history new = true) :
    winners (history++[new]) = (winners history).filter (fun e => decide (e.id≠new.id)) ++ [new] := by
  have hn : (new.important || !hasImportant (history++[new]) new.id) = true := by
    cases hi : new.important <;> simp_all [accepted,important_append]
  unfold winners
  simp only [preferred,List.filter_append,List.filter_cons,List.filter_nil,hn,ite_true]
  rw [last_append,←last_filter _ (fun id => decide (id≠new.id)),preferred_away,last_filter _ (fun id => decide (id≠new.id))]
  rfl

theorem winners_append_rejected (history : List E) (new : E) (ha : accepted history new = false) :
    winners (history++[new]) = winners history := by
  have hn : new.important = false ∧ hasImportant history new.id = true := by simpa [accepted] using ha
  have he : ∀ id, hasImportant (history++[new]) id = hasImportant history id := by
    intro id; simp [important_append,hn.1]
  simp [winners,preferred,he,hn.1,hn.2]

theorem last_filter_exists (xs : List E) (keep : ι → Bool) :
    ((lastOnly xs).filter (fun e => keep e.id)).isEmpty =
      (xs.filter (fun e => keep e.id)).isEmpty := by
  have he : (lastOnly xs).filter (fun e => keep e.id) = lastOnly (xs.filter (fun e => keep e.id)) := (last_filter xs keep).symm
  rw [he]
  cases h : xs.filter (fun e => keep e.id) with
  | nil => rfl
  | cons e rest =>
    have hm : e.id ∈ (lastOnly (e::rest)).map Entry.id := (last_membership _ _).mpr (by simp)
    cases ht : lastOnly (e::rest) with
    | nil => simp [ht] at hm
    | cons x tail => rfl

theorem important_absent (xs : List E) (id : ι) (ha : absent id xs) :
    hasImportant xs id = false := by
  apply List.any_eq_false.mpr
  intro e he
  simp [ha e he]

theorem winners_sublist (history : List E) : (winners history).Sublist history :=
  (last_sublist _).trans List.filter_sublist

theorem winners_unique (history : List E) : unique (winners history) := last_unique _

theorem preferred_important (history : List E) (e : E) (hm : e ∈ preferred history)
    (hi : hasImportant history e.id = true) : e.important = true := by
  have h := (List.mem_filter.mp hm).2
  simpa [hi] using h

theorem important_winners (history : List E) (id : ι) :
    hasImportant (winners history) id = hasImportant history id := by
  apply Bool.eq_iff_iff.mpr
  constructor
  · intro h
    obtain ⟨e,he,hi⟩ := List.any_eq_true.mp h
    exact List.any_eq_true.mpr ⟨e,(winners_sublist history).subset he,hi⟩
  · intro h
    obtain ⟨e,he,hi⟩ := List.any_eq_true.mp h
    have hib : e.id=id ∧ e.important=true := by simpa using hi
    have hid := hib.1
    have himp := hib.2
    have hep : e ∈ preferred history := List.mem_filter.mpr ⟨he,by simp [himp]⟩
    have hmp : id ∈ (preferred history).map Entry.id := List.mem_map.mpr ⟨e,hep,hid⟩
    have hmw := (last_membership (preferred history) id).mpr hmp
    obtain ⟨winner,hw,hwid⟩ := List.mem_map.mp hmw
    have hwp : winner ∈ preferred history := (last_sublist _).subset hw
    have hwi := preferred_important history winner hwp (by simpa [hwid] using h)
    exact List.any_eq_true.mpr ⟨winner,hw,by simp [hwid,hwi]⟩

theorem parse_set_formula (xs : List E) (new : E) (hu : unique xs) :
    parseSet xs new = if accepted xs new then xs.filter (fun e => decide (e.id≠new.id)) ++ [new] else xs := by
  classical
  rcases unique_split xs new hu with ha | ⟨pre,old,post,rfl,he,hp,ht⟩
  · have hf : xs.filter (fun e => decide (e.id≠new.id)) = xs := by
      apply List.filter_eq_self.mpr
      intro e hm; simp [ha e hm]
    have hac : accepted xs new = true := by simp [accepted,important_absent xs new.id ha]
    rw [parse_absent xs new ha,hac]
    simp only [ite_true]
    rw [hf]
  · have hi : hasImportant (pre++old::post) new.id = old.important := by
      have a := important_absent pre new.id hp
      have b := important_absent post new.id ht
      simp only [hasImportant,List.any_append,List.any_cons,he,decide_true,Bool.true_and]
      change (hasImportant pre new.id || (old.important || hasImportant post new.id)) = old.important
      rw [a,b];simp
    have hf : (pre++old::post).filter (fun e => decide (e.id≠new.id)) = pre++post := by
      have a : pre.filter (fun e => decide (e.id≠new.id)) = pre := List.filter_eq_self.mpr (by intro e hm; simp [hp e hm])
      have b : post.filter (fun e => decide (e.id≠new.id)) = post := List.filter_eq_self.mpr (by intro e hm; simp [ht e hm])
      simp only [List.filter_append,List.filter_cons,he,ne_self_iff_false,decide_false,Bool.false_eq_true,ite_false]
      rw [a,b]
    rw [parse_split pre post old new hp he,hf]
    cases hnew : new.important <;> cases hold : old.important <;> simp [accepted,hi,hnew,hold]

theorem winners_append (history : List E) (new : E) :
    winners (history++[new]) = parseSet (winners history) new := by
  rw [parse_set_formula _ _ (winners_unique history)]
  have ha : accepted (winners history) new = accepted history new := by simp [accepted,important_winners]
  rw [ha]
  cases h : accepted history new
  · exact winners_append_rejected history new h
  · exact winners_append_accepted history new h

theorem extend_winners (history actions : List E) :
    parseExtend (winners history) actions = winners (history++actions) := by
  induction actions generalizing history with
  | nil => simp [parseExtend]
  | cons new rest ih =>
    change parseExtend (parseSet (winners history) new) rest = _
    rw [←winners_append,ih]
    simp

theorem empty_extend_winners (actions : List E) : parseExtend [] actions = winners actions := by
  simpa [winners,preferred,lastOnly] using extend_winners ([] : List E) actions

theorem last_unique_input (xs : List E) (hu : unique xs) : lastOnly xs = xs := by
  induction xs with
  | nil => rfl
  | cons e rest ih =>
    have hn := (List.nodup_cons.mp hu).1
    have ht := (List.nodup_cons.mp hu).2
    have ha : rest.any (fun x => decide (x.id=e.id)) = false := by
      apply List.any_eq_false.mpr
      intro x hx
      have hne : x.id ≠ e.id := by
        intro he; exact hn (List.mem_map.mpr ⟨x,hx,he⟩)
      simp [hne]
    simp [lastOnly,ha,ih ht]

theorem preferred_unique_input (xs : List E) (hu : unique xs) : preferred xs = xs := by
  apply List.filter_eq_self.mpr
  intro e he
  cases hi : e.important
  · have hn : hasImportant xs e.id = false := by
      apply List.any_eq_false.mpr
      intro other ho
      by_cases hid : other.id=e.id
      · have heq : other=e := by
          have hnodup := hu
          induction xs with
          | nil => simp at he
          | cons first rest ih =>
            rcases List.mem_cons.mp he with hfirst | her
            · subst first
              rcases List.mem_cons.mp ho with hother | hor
              · exact hother
              · exact False.elim ((List.nodup_cons.mp hnodup).1 (List.mem_map.mpr ⟨other,hor,hid⟩))
            · rcases List.mem_cons.mp ho with hother | hor
              · subst first
                exact False.elim ((List.nodup_cons.mp hnodup).1 (List.mem_map.mpr ⟨e,her,hid.symm⟩))
              · exact ih (List.nodup_cons.mp hu).2 her hor (List.nodup_cons.mp hnodup).2
        simp [heq,hi]
      · simp [hid]
    simp [hi,hn]
  · simp [hi]

theorem winners_unique_input (xs : List E) (hu : unique xs) : winners xs = xs := by
  rw [winners,preferred_unique_input xs hu,last_unique_input xs hu]

theorem arbitrary_initial_prefix (initial actions : List E) (hu : unique initial) :
    parseExtend initial actions = winners (initial++actions) := by
  rw [←winners_unique_input initial hu]
  rw [extend_winners,winners_unique_input initial hu]

def lastFor : List E → ι → Option E
  | [], _ => none
  | e::rest, id => (lastFor rest id).or (if e.id=id then some e else none)

theorem last_for_none (xs : List E) (id : ι) : lastFor xs id = none ↔ absent id xs := by
  induction xs with
  | nil => simp [lastFor,absent]
  | cons e rest ih =>
    by_cases he : e.id=id
    · simp [lastFor,he,absent]
    · simp [lastFor,he,ih,absent] at *

theorem last_for_some_member (xs : List E) (id : ι) (e : E) (h : lastFor xs id = some e) :
    e ∈ xs ∧ e.id=id := by
  induction xs with
  | nil => simp [lastFor] at h
  | cons first rest ih =>
    cases ht : lastFor rest id with
    | some winner =>
      have he : winner=e := by simpa [lastFor,ht] using h
      subst winner
      have hi := ih ht
      exact ⟨by simp [hi.1],hi.2⟩
    | none =>
      by_cases he : first.id=id
      · have hf : first=e := by simpa [lastFor,ht,he] using h
        subst first
        exact ⟨by simp,he⟩
      · simp [lastFor,ht,he] at h

theorem last_for_filter_congruence (xs : List E) (id : ι) (keep other : E → Bool)
    (hc : ∀ e ∈ xs, e.id=id → keep e=other e) :
    lastFor (xs.filter keep) id = lastFor (xs.filter other) id := by
  induction xs with
  | nil => rfl
  | cons e rest ih =>
    have ht := ih (by intro x hx hi; exact hc x (by simp [hx]) hi)
    by_cases he : e.id=id
    · have hk := hc e (by simp) he
      cases hother : other e <;> simp [List.filter_cons,hk,hother,lastFor,ht]
    · cases hk : keep e <;> cases ho : other e <;> simp [List.filter_cons,hk,ho,lastFor,he,ht]

theorem last_for_lastOnly (xs : List E) (id : ι) : lastFor (lastOnly xs) id = lastFor xs id := by
  induction xs with
  | nil => rfl
  | cons e rest ih =>
    simp only [lastOnly]
    split
    · next h =>
      rw [ih]
      cases ht : lastFor rest id with
      | some winner => simp [lastFor,ht]
      | none =>
        have ha := (last_for_none rest id).mp ht
        have he : e.id ≠ id := by
          intro he
          obtain ⟨other,ho,hi⟩ := List.any_eq_true.mp h
          exact ha other ho ((of_decide_eq_true hi).trans he)
        simp [lastFor,ht,he]
    · simp [lastFor,ih]

def sourceWinner (history : List E) (id : ι) : Option E :=
  if hasImportant history id then lastFor (history.filter Entry.important) id else lastFor history id

theorem winner_per_identity (history : List E) (id : ι) :
    lastFor (winners history) id = sourceWinner history id := by
  rw [winners,last_for_lastOnly]
  unfold sourceWinner
  cases hi : hasImportant history id
  · have h := last_for_filter_congruence history id
      (fun e => e.important || !hasImportant history e.id) (fun _ => true)
      (by intro e he hid; simp [hid,hi])
    have hf : history.filter (fun _ => true) = history := List.filter_eq_self.mpr (by intros; rfl)
    rw [hf] at h
    exact h
  · exact last_for_filter_congruence history id _ _ (by intro e he hid; simp [hid,hi])

theorem last_for_occurrence (history : List E) (id : ι) (e : E) :
    lastFor history id = some e ↔
      ∃ pre post, history=pre++e::post ∧ e.id=id ∧ absent id post := by
  induction history with
  | nil => simp [lastFor]
  | cons first rest ih =>
    constructor
    · intro h
      cases ht : lastFor rest id with
      | some winner =>
        have he : winner=e := by simpa [lastFor,ht] using h
        subst winner
        obtain ⟨pre,post,hr,hi,ha⟩ := ih.mp ht
        exact ⟨first::pre,post,by simp [hr],hi,ha⟩
      | none =>
        by_cases hi : first.id=id
        · have he : first=e := by simpa [lastFor,ht,hi] using h
          subst first
          exact ⟨[],rest,rfl,hi,(last_for_none rest id).mp ht⟩
        · simp [lastFor,ht,hi] at h
    · rintro ⟨pre,post,hist,hi,ha⟩
      cases pre with
      | nil =>
        simp only [List.nil_append,List.cons.injEq] at hist
        obtain ⟨rfl,rfl⟩ := hist
        simp [lastFor,hi,(last_for_none rest id).mpr ha]
      | cons p pre =>
        simp only [List.cons_append,List.cons.injEq] at hist
        have hr := ih.mpr ⟨pre,post,hist.2,hi,ha⟩
        simp [lastFor,hr]

theorem raw_winner_refinement (raw : Storage ι ν) (initial actions : List E)
    (hu : unique initial) (hr : Represents raw initial) :
    Represents (rawExtend raw actions) (winners (initial++actions)) := by
  rw [←arbitrary_initial_prefix initial actions hu]
  exact raw_extend_refinement raw initial actions hu hr

theorem winner_identities (history : List E) (id : ι) :
    id ∈ (winners history).map Entry.id ↔ id ∈ history.map Entry.id := by
  rw [winners,last_membership]
  constructor
  · intro h
    obtain ⟨e,he,hi⟩ := List.mem_map.mp h
    exact List.mem_map.mpr ⟨e,(List.mem_filter.mp he).1,hi⟩
  · intro h
    obtain ⟨e,he,hi⟩ := List.mem_map.mp h
    cases hp : hasImportant history id
    · exact List.mem_map.mpr ⟨e,List.mem_filter.mpr ⟨he,by simp [hi,hp]⟩,hi⟩
    · obtain ⟨other,ho,hi⟩ := List.any_eq_true.mp hp
      have hid : other.id=id ∧ other.important=true := by simpa using hi
      exact List.mem_map.mpr ⟨other,List.mem_filter.mpr ⟨ho,by simp [hid.2]⟩,hid.1⟩

def tagged (history : List E) : List (Entry ι (Nat × ν)) :=
  history.zipIdx.map (fun (e,n) => ⟨e.id,(n,e.value),e.important⟩)

theorem tagged_positions (history : List E) :
    (tagged history).map (fun e => e.value.1) = List.range history.length := by
  simpa [tagged,List.map_map,Function.comp_def,List.range_eq_range'] using List.zipIdx_map_snd (l := history) 0

theorem winning_positions_source_order (history : List E) :
    ((winners (tagged history)).map (fun e => e.value.1)).Sublist (List.range history.length) := by
  have h := (winners_sublist (tagged history)).map (fun e => e.value.1)
  rw [tagged_positions] at h
  exact h

def mapValue (f : ν → μ) (e : Entry ι ν) : Entry ι μ := ⟨e.id,f e.value,e.important⟩

theorem important_map (f : ν → μ) (history : List E) (id : ι) :
    hasImportant (history.map (mapValue f)) id = hasImportant history id := by
  simp only [hasImportant,List.any_map,Function.comp_def,mapValue]
  rfl

theorem last_map (f : ν → μ) (history : List E) :
    lastOnly (history.map (mapValue f)) = (lastOnly history).map (mapValue f) := by
  induction history with
  | nil => rfl
  | cons e rest ih =>
    simp only [List.map_cons,lastOnly]
    simp only [List.any_map,Function.comp_def,mapValue]
    change (if rest.any (fun x => decide (x.id=e.id)) then lastOnly (rest.map (mapValue f)) else mapValue f e :: lastOnly (rest.map (mapValue f))) =
      (if rest.any (fun x => decide (x.id=e.id)) then lastOnly rest else e::lastOnly rest).map (mapValue f)
    rw [ih]
    cases rest.any (fun x => decide (x.id=e.id)) <;> rfl

theorem preferred_map (f : ν → μ) (history : List E) :
    preferred (history.map (mapValue f)) = (preferred history).map (mapValue f) := by
  simp only [preferred,important_map,List.filter_map]
  rfl

theorem winners_map (f : ν → μ) (history : List E) :
    winners (history.map (mapValue f)) = (winners history).map (mapValue f) := by
  rw [winners,preferred_map,last_map]
  rfl

theorem tagged_values (history : List E) :
    (tagged history).map (mapValue Prod.snd) = history := by
  have hf : (fun pair : E × Nat => mapValue Prod.snd (⟨pair.1.id,(pair.2,pair.1.value),pair.1.important⟩ : Entry ι (Nat × ν))) = Prod.fst := by
    funext pair;cases pair; rfl
  simp only [tagged,List.map_map,Function.comp_def]
  simpa only [hf] using List.zipIdx_map_fst 0 history

theorem tagged_winners_exact (history : List E) :
    (winners (tagged history)).map (mapValue Prod.snd) = winners history := by
  rw [←winners_map,tagged_values]

end ParseWinners
