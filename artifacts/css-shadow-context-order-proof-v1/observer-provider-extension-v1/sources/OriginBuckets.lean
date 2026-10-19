import DefaultNormalization
namespace ShadowOrder

def hasOrigin (origin : Nat) (entries : List Entry) : Prop :=
 ∀ entry ∈ entries, entry.origin = origin

theorem tagged_origin_entries (origin tree : Nat) (rules : List Rule) :
 hasOrigin origin (originEntries origin tree rules) := by
 intro entry member
 rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
 rfl

theorem tagged_at_order (order : Int) (rules : List Rule) : hasOrigin 3 (atOrder order rules) := by
 intro entry member
 rcases List.mem_map.mp member with ⟨rule,hr,rfl⟩
 rfl

theorem tagged_append (origin : Nat) (left right : List Entry)
 (a : hasOrigin origin left) (b : hasOrigin origin right) : hasOrigin origin (left ++ right) := by
 intro entry member
 rcases List.mem_append.mp member with hl | hr
 · exact a entry hl
 · exact b entry hr

theorem tagged_host (limit count : Nat) (rules : List Rule) :
 hasOrigin 3 (hostCollector limit count rules) := by
 unfold hostCollector
 cases inner limit count
 · simp [hasOrigin]
 · exact tagged_at_order _ _

theorem tagged_slots (limit index : Nat) (slots : List InnerContext) :
 hasOrigin 3 (reverseSlotCollector limit index slots) := by
 induction slots generalizing index with
 | nil => simp [reverseSlotCollector,hasOrigin]
 | cons slot rest ih =>
   simp only [reverseSlotCollector]
   apply tagged_append
   · exact ih _
   · cases inner limit index
     · simp [hasOrigin]
     · exact tagged_at_order _ _

theorem tagged_outer_reference (limit rank : Nat) (parts : List Nat) (contexts : List Context) :
 hasOrigin 3 (physicalReference limit rank parts contexts) := by
 induction contexts generalizing rank parts with
 | nil => simp [physicalReference,hasOrigin]
 | cons context rest ih =>
   simp only [physicalReference]
   split
   · simp [hasOrigin]
   · apply tagged_append
     · split
       · exact tagged_at_order _ _
       · simp [hasOrigin]
     · exact ih _ _

theorem tagged_outer (limit rank : Nat) (parts : List Nat) (contexts : List Context) :
 hasOrigin 3 (collectParts limit rank parts contexts) := by
 rw [parts_refinement]
 exact tagged_outer_reference limit rank parts contexts

theorem tagged_containing (raw : RawProviderInput) (pseudos : List Nat)
 (target : RawElement) (containing : List Entry × Bool)
 (made : normalizeContaining raw pseudos target = some containing) : hasOrigin 3 containing.1 := by
 cases matching : target.matchesContent with
 | false => simp [normalizeContaining,matching] at made; subst containing; simp [hasOrigin]
 | true =>
   cases identity : target.containingIgnoringSvgUse with
   | none => simp [normalizeContaining,matching,identity] at made; subst containing; simp [hasOrigin]
   | some rootId =>
     cases found : raw.roots[rootId]? with
     | none => simp [normalizeContaining,matching,identity,found] at made
     | some root =>
       simp [normalizeContaining,matching,identity,found] at made
       subst containing
       exact tagged_origin_entries 3 0 _

theorem normalized_author_tag (raw : RawProviderInput) (normalized : RawInput)
 (made : normalizeRawProviders raw = some normalized) : hasOrigin 3 (authorOnlyEntries normalized) := by
 apply raw_author_normalization_property raw normalized (hasOrigin 3) (by simp [hasOrigin]) _ made
 intro target pseudos host slots containing contexts backed hm sm cm om
 unfold normalizedAuthorGroups
 simp only
 apply tagged_append
 · apply tagged_append
   · apply tagged_append
     · apply tagged_append
       · exact tagged_append 3 _ _ (tagged_host _ _ _) (tagged_slots _ _ _)
       · exact tagged_containing raw pseudos target containing cm
     · cases containing.2
       · simp [hasOrigin]
       · exact tagged_origin_entries 3 0 _
   · exact tagged_origin_entries 3 0 _
 · exact tagged_outer _ _ _ _

theorem normalized_defaults_tag (raw : RawProviderInput) (normalized : RawInput)
 (made : normalizeRawProviders raw = some normalized) :
 hasOrigin 0 normalized.ua ∧ hasOrigin 1 normalized.user := by
 apply raw_defaults_normalization_property raw normalized
   (fun ua user => hasOrigin 0 ua ∧ hasOrigin 1 user) _ made
 intro pseudos backed named matching
 exact ⟨tagged_origin_entries 0 0 _,tagged_origin_entries 1 0 _⟩

theorem filter_tagged_origin (origin : Nat) (entries : List Entry) (tagged : hasOrigin origin entries)
 (wanted : Nat) : entries.filter (fun entry => entry.origin == wanted) =
 if origin = wanted then entries else [] := by
 by_cases same : origin = wanted
 · simp only [same,↓reduceIte]
   apply List.filter_eq_self.mpr
   intro entry member
   simp [tagged entry member,same]
 · simp only [same,↓reduceIte]
   apply List.filter_eq_nil_iff.mpr
   intro entry member
   simp [tagged entry member,same]

def importantOrigin (origin : Nat) (entries : List Entry) : List Entry :=
 entries.filter fun entry => hasImportant entry && entry.origin == origin

theorem important_tagged_origin (origin : Nat) (entries : List Entry) (tagged : hasOrigin origin entries)
 (wanted : Nat) : importantOrigin wanted entries =
 if origin = wanted then entries.filter hasImportant else [] := by
 have factor : importantOrigin wanted entries =
   (entries.filter (fun entry => entry.origin == wanted)).filter hasImportant := by
   simp only [importantOrigin,List.filter_filter]

 rw [factor,filter_tagged_origin origin entries tagged wanted]
 split <;> simp

def normalizedOtherShape (normalized : RawInput) : Prop :=
 hasOrigin 2 normalized.presHints ∧
 (∀ entry ∈ normalized.animations, 5 ≤ entry.origin) ∧
 (normalized.defaultOnly = true ∨ normalized.authorEnabled = false → authorOnlyEntries normalized = [])

theorem normalized_other_shape (raw : RawProviderInput) (normalized : RawInput)
 (made : normalizeRawProviders raw = some normalized) : normalizedOtherShape normalized := by
 cases pseudoResult : nativePseudo (rawPseudoNodes raw) (raw.elements.length+1)
     raw.element raw.explicitPseudo.toList with
 | none => simp only [bind,pure,Option.bind_some,Option.bind_none,normalizeRawProviders,pseudoResult] at made; contradiction
 | some pseudo =>
   cases targetFound : raw.elements[pseudo.1]? with
   | none => simp only [bind,pure,Option.bind_some,Option.bind_none,normalizeRawProviders,pseudoResult,targetFound] at made; contradiction
   | some target =>
     cases defaults : raw.defaultOnly with
     | true =>
       simp only [bind,pure,Option.bind_some,Option.some.injEq,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults] at made
       subst normalized
       simp [normalizedOtherShape,hasOrigin,originEntries,authorOnlyEntries,hostCollector,inner,reverseSlotCollector,collectParts,atOrder,maxOrder] <;> grind
     | false =>
       cases enabled : raw.authorEnabled with
       | false =>
         simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_false,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled] at made
         subst normalized
         simp [normalizedOtherShape,hasOrigin,originEntries,authorOnlyEntries,hostCollector,inner,reverseSlotCollector,collectParts,atOrder,maxOrder] <;> grind
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
                 simp [normalizedOtherShape,hasOrigin,originEntries,authorOnlyEntries,hostCollector,inner,reverseSlotCollector,collectParts,atOrder,maxOrder] <;> grind
               | true =>
                 cases outerRoot : target.containingShadow with
                 | none =>
                   simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot] at made
                   subst normalized
                   simp [normalizedOtherShape,hasOrigin,originEntries,authorOnlyEntries,hostCollector,inner,reverseSlotCollector,collectParts,atOrder,maxOrder] <;> grind
                 | some root =>
                   cases outerMade : normalizeOuter raw pseudo.2 (raw.roots.length+1) root with
                   | none => simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot,outerMade] at made; contradiction
                   | some contexts =>
                     simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot,outerMade] at made
                     subst normalized
                     simp [normalizedOtherShape,hasOrigin,originEntries,authorOnlyEntries,hostCollector,inner,reverseSlotCollector,collectParts,atOrder,maxOrder] <;> grind

theorem collected_origin_groups (normalized : RawInput) :
 nativeCollected normalized = normalized.ua ++ normalized.user ++
   (if normalized.defaultOnly then [] else normalized.presHints ++
     if normalized.authorEnabled then authorOnlyEntries normalized ++ normalized.animations else []) := by
 cases hd : normalized.defaultOnly <;> cases he : normalized.authorEnabled <;>
   simp [nativeCollected,authorOnlyEntries,List.append_assoc,hd,he]

theorem important_origin_append (origin : Nat) (left right : List Entry) :
 importantOrigin origin (left ++ right) = importantOrigin origin left ++ importantOrigin origin right := by
 simp [importantOrigin,List.filter_append]

theorem important_origin_absent (origin : Nat) (entries : List Entry)
 (absent : ∀ entry ∈ entries, entry.origin ≠ origin) : importantOrigin origin entries = [] := by
 apply List.filter_eq_nil_iff.mpr
 intro entry member
 simp [absent entry member]

def normalizedBucket (normalized : RawInput) (origin : Nat) : List Entry :=
 if origin = 0 then normalized.ua.filter hasImportant
 else if origin = 1 then normalized.user.filter hasImportant
 else (authorOnlyEntries normalized).filter hasImportant

theorem normalized_collected_bucket (raw : RawProviderInput) (normalized : RawInput)
 (made : normalizeRawProviders raw = some normalized) (origin : Nat)
 (supported : origin = 0 ∨ origin = 1 ∨ origin = 3) :
 importantOrigin origin (nativeCollected normalized) = normalizedBucket normalized origin := by
 have tags := normalized_defaults_tag raw normalized made
 have authorTag := normalized_author_tag raw normalized made
 have others := normalized_other_shape raw normalized made
 have animationAbsent : importantOrigin origin normalized.animations = [] := by
   apply important_origin_absent
   intro entry member
   have lower := others.2.1 entry member
   rcases supported with h | h | h <;> omega
 have disabled : normalized.defaultOnly = true ∨ normalized.authorEnabled = false →
   (authorOnlyEntries normalized).filter hasImportant = [] := by
   intro h
   rw [others.2.2 h]
   rfl
 rw [collected_origin_groups]
 rcases supported with h | h | h <;> subst origin
 all_goals
   cases defaults : normalized.defaultOnly <;> cases enabled : normalized.authorEnabled
   all_goals
     simp only [defaults,enabled,Bool.false_eq_true,↓reduceIte,important_origin_append]
     simp only [important_tagged_origin 0 normalized.ua tags.1,
       important_tagged_origin 1 normalized.user tags.2,
       important_tagged_origin 3 (authorOnlyEntries normalized) authorTag,
       important_tagged_origin 2 normalized.presHints others.1,
       animationAbsent]
     simp [normalizedBucket,importantOrigin]
       <;> simpa using disabled (by simp [defaults,enabled])

theorem normalized_collected_buckets_skip (raw : RawProviderInput) (normalized : RawInput)
 (valid : rawFieldsValid raw = true) (made : normalizeRawProviders raw = some normalized)
 (origin : Nat) (supported : origin = 0 ∨ origin = 1 ∨ origin = 3) :
 skipSort entryPriorityIdentity entryImportantKey (importantOrigin origin (nativeCollected normalized)) =
 localSort entryImportantKey (importantOrigin origin (nativeCollected normalized)) := by
 rw [normalized_collected_bucket raw normalized made origin supported]
 rcases supported with h | h | h <;> subst origin
 · simpa [normalizedBucket] using (normalized_default_important_skip raw normalized valid made).1
 · simpa [normalizedBucket] using (normalized_default_important_skip raw normalized valid made).2
 · simpa [normalizedBucket] using raw_author_important_partition_skip raw normalized valid made

#print axioms normalized_collected_bucket
#print axioms normalized_collected_buckets_skip
#print axioms normalized_author_tag
#print axioms normalized_defaults_tag
end ShadowOrder
