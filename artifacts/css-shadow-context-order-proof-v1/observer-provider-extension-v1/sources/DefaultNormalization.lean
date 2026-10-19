import DefaultProviderOrder
namespace ShadowOrder
theorem raw_defaults_normalization_property (raw : RawProviderInput) (normalized : RawInput)
 (P : List Entry → List Entry → Prop)
 (constructed : ∀ pseudos elementBacked namedViewTransition matchesContent,
   P (originEntries 0 0 (defaultUaRules raw pseudos elementBacked namedViewTransition))
     (originEntries 1 0 (defaultUserRules raw pseudos matchesContent)))
 (made : normalizeRawProviders raw = some normalized) : P normalized.ua normalized.user := by
 cases pseudoResult : nativePseudo (rawPseudoNodes raw) (raw.elements.length+1)
     raw.element raw.explicitPseudo.toList with
 | none => simp only [bind,pure,Option.bind_some,Option.bind_none,normalizeRawProviders,pseudoResult] at made; contradiction
 | some pseudo =>
   cases targetFound : raw.elements[pseudo.1]? with
   | none => simp only [bind,pure,Option.bind_some,Option.bind_none,normalizeRawProviders,pseudoResult,targetFound] at made; contradiction
   | some target =>
     have defaultsProperty := constructed pseudo.2
       (pseudo.1 != raw.element && pseudo.2.length == 1 &&
         (pseudo.2.head?.map fun p => raw.elementBackedPseudos.contains p).getD false)
       ((pseudo.2.head?.map fun p => raw.namedViewTransitionPseudos.contains p).getD false)
       target.matchesContent
     cases defaults : raw.defaultOnly with
     | true =>
       simp only [bind,pure,Option.bind_some,Option.some.injEq,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults] at made
       subst normalized
       simpa [defaultUaRules,defaultUserRules] using defaultsProperty
     | false =>
       cases enabled : raw.authorEnabled with
       | false =>
         simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_false,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled] at made
         subst normalized
         simpa [defaultUaRules,defaultUserRules] using defaultsProperty
       | true =>
         let elementBacked := pseudo.1 != raw.element && pseudo.2.length == 1 &&
           (pseudo.2.head?.map fun p => raw.elementBackedPseudos.contains p).getD false
         cases slotsMade : normalizeSlots raw pseudo.2 (raw.elements.length+1) target.assignedSlot with
         | none => simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade] at made; contradiction
         | some slots =>
           cases hostMade : normalizeOwnHost raw pseudo.2 target elementBacked with
           | none =>
             simp only [elementBacked] at hostMade
             simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade] at made; contradiction
           | some host =>
             simp only [elementBacked] at hostMade
             cases containingMade : normalizeContaining raw pseudo.2 target with
             | none => simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade] at made; contradiction
             | some containing =>
               cases partFlag : target.hasPartAttribute with
               | false =>
                 simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag] at made
                 subst normalized
                 simpa [defaultUaRules,defaultUserRules] using defaultsProperty
               | true =>
                 cases outerRoot : target.containingShadow with
                 | none =>
                   simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot] at made
                   subst normalized
                   simpa [defaultUaRules,defaultUserRules] using defaultsProperty
                 | some root =>
                   cases outerMade : normalizeOuter raw pseudo.2 (raw.roots.length+1) root with
                   | none => simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot,outerMade] at made; contradiction
                   | some contexts =>
                     simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot,outerMade] at made
                     subst normalized
                     simpa [defaultUaRules,defaultUserRules] using defaultsProperty

theorem normalized_default_important_skip (raw : RawProviderInput) (normalized : RawInput)
 (valid : rawFieldsValid raw = true) (made : normalizeRawProviders raw = some normalized) :
 (skipSort entryPriorityIdentity entryImportantKey (normalized.ua.filter hasImportant) =
   localSort entryImportantKey (normalized.ua.filter hasImportant)) ∧
 (skipSort entryPriorityIdentity entryImportantKey (normalized.user.filter hasImportant) =
   localSort entryImportantKey (normalized.user.filter hasImportant)) := by
 apply raw_defaults_normalization_property raw normalized
   (fun ua user =>
     skipSort entryPriorityIdentity entryImportantKey (ua.filter hasImportant) =
       localSort entryImportantKey (ua.filter hasImportant) ∧
     skipSort entryPriorityIdentity entryImportantKey (user.filter hasImportant) =
       localSort entryImportantKey (user.filter hasImportant)) _ made
 intro pseudos backed named matching
 exact ⟨raw_ua_important_skip raw pseudos backed named valid,
   raw_user_important_skip raw pseudos matching valid⟩

theorem normalized_three_groups_skip (raw : RawProviderInput) (normalized : RawInput)
 (valid : rawFieldsValid raw = true) (made : normalizeRawProviders raw = some normalized) :
 ∀ group ∈ [authorOnlyEntries normalized,normalized.user,normalized.ua],
 skipSort entryPriorityIdentity entryImportantKey (group.filter hasImportant) =
 localSort entryImportantKey (group.filter hasImportant) := by
 intro group member
 simp only [List.mem_cons,List.not_mem_nil,or_false] at member
 rcases member with author | user | ua
 · subst group
   exact raw_author_important_partition_skip raw normalized valid made
 · subst group
   exact (normalized_default_important_skip raw normalized valid made).2
 · subst group
   exact (normalized_default_important_skip raw normalized valid made).1

#print axioms normalized_default_important_skip
#print axioms normalized_three_groups_skip
end ShadowOrder
