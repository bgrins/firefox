import AuthorBounds
namespace ShadowOrder

theorem materialized_stylesheet_layer (tree : Nat) (data : RawCascadeData)
 (candidate : RawSelectorResult) (rule : Rule) (valid : rawDataValid data = true)
 (made : materialize tree data.table candidate = some rule) : rule.layer ≤ 65534 := by
 simp only [rawDataValid,Bool.and_eq_true] at valid
 unfold materialize at made
 cases matched : candidate.matched <;> simp only [matched,Bool.not_false,Bool.not_true,↓reduceIte] at made
 · contradiction
 cases found : data.table[candidate.ordinal]? with
 | none => simp [found] at made
 | some block =>
   simp [found] at made
   subst rule
   have h := List.all_eq_true.mp valid.1.1.1.1.2 block (List.mem_of_getElem? found)
   simp only [Bool.and_eq_true,decide_eq_true_eq] at h
   exact Nat.le_of_lt_succ h.2

theorem map_stylesheet_layer (tree : Nat) (data : RawCascadeData)
 (map : Option (List RawSelectorResult)) (valid : rawDataValid data = true) :
 ∀ rule ∈ mapRules tree data map, rule.layer ≤ 65534 := by
 intro rule member
 rcases List.mem_filterMap.mp member with ⟨candidate,hc,made⟩
 exact materialized_stylesheet_layer tree data candidate rule valid made

def defaultUaRules (raw : RawProviderInput) (pseudos : List Nat)
 (elementBacked namedViewTransition : Bool) : List Rule :=
 localSort completeLocalKey
   ((if elementBacked then mapRules 0 raw.ua (pseudoMapLookup raw.ua.normal []) else []) ++
     mapRules 0 raw.ua (pseudoMapLookup raw.ua.normal pseudos)) ++
 if namedViewTransition then raw.dynamicUa.map
   (fun rule => plainRule 0 0 {rule with layer := 65534,flags := 0}) else []

theorem default_ua_numeric (raw : RawProviderInput) (pseudos : List Nat)
 (elementBacked namedViewTransition : Bool) (valid : rawFieldsValid raw = true) :
 ∀ rule ∈ defaultUaRules raw pseudos elementBacked namedViewTransition, ruleNumericBounds rule := by
 simp only [rawFieldsValid,Bool.and_eq_true] at valid
 have dataValid := valid.1.1.1.1.1.2
 have mapValid : rawMapValid raw.ua.table raw.ua.normal = true := by
   simp only [rawDataValid,Bool.and_eq_true] at dataValid
   exact dataValid.1.1.1.2
 intro rule member
 rcases List.mem_append.mp member with styles | dynamic
 · have unsorted := (sort_perm _ _).mem_iff.mp styles
   rcases List.mem_append.mp unsorted with backed | normal
   · cases elementBacked
     · simp at backed
     · exact exact_map_numeric_bounds 0 raw.ua raw.ua.normal [] mapValid rule backed
   · exact exact_map_numeric_bounds 0 raw.ua raw.ua.normal pseudos mapValid rule normal
 · cases namedViewTransition
   · simp at dynamic
   · rcases List.mem_map.mp dynamic with ⟨block,hb,rfl⟩
     simp [ruleNumericBounds,plainRule]

theorem default_ua_layer_order (raw : RawProviderInput) (pseudos : List Nat)
 (elementBacked namedViewTransition : Bool) (valid : rawFieldsValid raw = true) :
 (defaultUaRules raw pseudos elementBacked namedViewTransition).Pairwise (fun a b => a.layer ≤ b.layer) := by
 have numeric := default_ua_numeric raw pseudos elementBacked namedViewTransition valid
 have uaValid : rawDataValid raw.ua = true := by
   simp only [rawFieldsValid,Bool.and_eq_true] at valid
   exact valid.1.1.1.1.1.2
 apply List.pairwise_append.mpr
 refine ⟨?_,?_,?_⟩
 · apply sorted_rule_layers
   intro rule member
   apply numeric rule
   apply List.mem_append_left
   exact (sort_perm _ _).mem_iff.mpr member
 · cases namedViewTransition
   · simp
   · simp [List.pairwise_map,plainRule]
     apply List.pairwise_iff_getElem.mpr
     intro i j hi hj hij
     trivial
 · intro a ha b hb
   have lower : a.layer ≤ 65534 := by
     have unsorted := (sort_perm _ _).mem_iff.mp ha
     rcases List.mem_append.mp unsorted with backed | normal
     · cases elementBacked
       · simp at backed
       · exact map_stylesheet_layer 0 raw.ua _ uaValid a backed
     · exact map_stylesheet_layer 0 raw.ua _ uaValid a normal
   cases namedViewTransition
   · simp at hb
   · rcases List.mem_map.mp hb with ⟨block,hb,rfl⟩
     exact lower

def defaultUserRules (raw : RawProviderInput) (pseudos : List Nat) (matchesContent : Bool) : List Rule :=
 if matchesContent then sortedMapRules 0 raw.user (pseudoMapLookup raw.user.normal pseudos) else []

theorem default_user_numeric (raw : RawProviderInput) (pseudos : List Nat)
 (matchesContent : Bool) (valid : rawFieldsValid raw = true) :
 ∀ rule ∈ defaultUserRules raw pseudos matchesContent, ruleNumericBounds rule := by
 simp only [rawFieldsValid,Bool.and_eq_true] at valid
 have dataValid := valid.1.1.1.1.2
 simp only [rawDataValid,Bool.and_eq_true] at dataValid
 cases matchesContent
 · simp [defaultUserRules]
 · intro rule member
   exact exact_map_numeric_bounds 0 raw.user raw.user.normal pseudos dataValid.1.1.1.2 rule
     ((sort_perm _ _).mem_iff.mp member)

theorem default_user_layer_order (raw : RawProviderInput) (pseudos : List Nat)
 (matchesContent : Bool) (valid : rawFieldsValid raw = true) :
 (defaultUserRules raw pseudos matchesContent).Pairwise (fun a b => a.layer ≤ b.layer) := by
 simp only [rawFieldsValid,Bool.and_eq_true] at valid
 have dataValid := valid.1.1.1.1.2
 simp only [rawDataValid,Bool.and_eq_true] at dataValid
 cases matchesContent
 · simp [defaultUserRules]
 · exact sorted_exact_map_layer_order 0 raw.user raw.user.normal pseudos dataValid.1.1.1.2

theorem origin_group_important_skip (origin tree : Nat) (rules : List Rule)
 (numeric : ∀ rule ∈ rules, ruleNumericBounds rule)
 (sorted : rules.Pairwise (fun a b => a.layer ≤ b.layer)) :
 skipSort entryPriorityIdentity entryImportantKey ((originEntries origin tree rules).filter hasImportant) =
 localSort entryImportantKey ((originEntries origin tree rules).filter hasImportant) := by
 apply bounded_important_skip
 · intro entry member
   rcases List.mem_map.mp (List.mem_filter.mp member).1 with ⟨rule,hr,rfl⟩
   have layer := (numeric rule hr).1
   unfold entryBounds
   simp only
   exact ⟨by omega,by omega,by omega⟩
 · have order : (originEntries origin tree rules).Pairwise contextLayerLE := by
     simpa [originEntries,List.pairwise_map,contextLayerLE] using sorted
   exact order.filter _

theorem raw_ua_important_skip (raw : RawProviderInput) (pseudos : List Nat)
 (elementBacked namedViewTransition : Bool) (valid : rawFieldsValid raw = true) :
 skipSort entryPriorityIdentity entryImportantKey
   ((originEntries 0 0 (defaultUaRules raw pseudos elementBacked namedViewTransition)).filter hasImportant) =
 localSort entryImportantKey
   ((originEntries 0 0 (defaultUaRules raw pseudos elementBacked namedViewTransition)).filter hasImportant) :=
 origin_group_important_skip 0 0 _ (default_ua_numeric raw pseudos elementBacked namedViewTransition valid)
   (default_ua_layer_order raw pseudos elementBacked namedViewTransition valid)

theorem raw_user_important_skip (raw : RawProviderInput) (pseudos : List Nat)
 (matchesContent : Bool) (valid : rawFieldsValid raw = true) :
 skipSort entryPriorityIdentity entryImportantKey
   ((originEntries 1 0 (defaultUserRules raw pseudos matchesContent)).filter hasImportant) =
 localSort entryImportantKey
   ((originEntries 1 0 (defaultUserRules raw pseudos matchesContent)).filter hasImportant) :=
 origin_group_important_skip 1 0 _ (default_user_numeric raw pseudos matchesContent valid)
   (default_user_layer_order raw pseudos matchesContent valid)

#print axioms default_ua_layer_order
end ShadowOrder
