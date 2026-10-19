import RawDOM
namespace ShadowOrder

inductive OuterTrace (raw : RawProviderInput) (pseudos : List Nat) : Nat → List Context → Prop
 | document (identity : Nat) (inner : RawShadowRoot) (host : RawElement)
   (rootFound : raw.roots[identity]? = some inner)
   (hostFound : raw.elements[inner.host]? = some host)
   (outside : host.containingShadow = none) :
   OuterTrace raw pseudos identity [documentOuterContext raw pseudos host]
 | shadow (identity outerIdentity : Nat) (inner outer : RawShadowRoot) (host : RawElement)
   (rest : List Context)
   (rootFound : raw.roots[identity]? = some inner)
   (hostFound : raw.elements[inner.host]? = some host)
   (outside : host.containingShadow = some outerIdentity)
   (outerFound : raw.roots[outerIdentity]? = some outer)
   (tail : OuterTrace raw pseudos outerIdentity rest) :
   OuterTrace raw pseudos identity (shadowOuterContext pseudos outerIdentity outer host::rest)

theorem outer_normalization_sound (raw : RawProviderInput) (pseudos : List Nat)
 (fuel identity : Nat) (contexts : List Context)
 (normalized : normalizeOuter raw pseudos fuel identity = some contexts) :
 OuterTrace raw pseudos identity contexts := by
 induction fuel generalizing identity contexts with
 | zero => simp [normalizeOuter] at normalized
 | succ fuel ih =>
   cases rootFound : raw.roots[identity]? with
   | none => simp [normalizeOuter,rootFound] at normalized
   | some inner =>
     cases hostFound : raw.elements[inner.host]? with
     | none => simp [normalizeOuter,rootFound,hostFound] at normalized
     | some host =>
       cases outside : host.containingShadow with
       | none =>
         simp [normalizeOuter,rootFound,hostFound,outside] at normalized
         subst contexts
         exact OuterTrace.document identity inner host rootFound hostFound outside
       | some outerIdentity =>
         cases outerFound : raw.roots[outerIdentity]? with
         | none => simp [normalizeOuter,rootFound,hostFound,outside,outerFound] at normalized
         | some outer =>
           cases tail : normalizeOuter raw pseudos fuel outerIdentity with
           | none => simp [normalizeOuter,rootFound,hostFound,outside,outerFound,tail] at normalized
           | some rest =>
             simp [normalizeOuter,rootFound,hostFound,outside,outerFound,tail] at normalized
             subst contexts
             exact OuterTrace.shadow identity outerIdentity inner outer host rest
               rootFound hostFound outside outerFound (ih _ _ tail)

theorem outer_normalization_complete (raw : RawProviderInput) (pseudos : List Nat)
 (identity : Nat) (contexts : List Context) (meaning : OuterTrace raw pseudos identity contexts)
 (fuel : Nat) (enough : contexts.length ≤ fuel) :
 normalizeOuter raw pseudos fuel identity = some contexts := by
 induction meaning generalizing fuel with
 | document identity inner host rootFound hostFound outside =>
   cases fuel
   · simp at enough
   · simp [normalizeOuter,rootFound,hostFound,outside]
 | shadow identity outerIdentity inner outer host rest rootFound hostFound outside outerFound tail ih =>
   cases fuel with
   | zero => simp at enough
   | succ fuel =>
     have enoughRest : rest.length ≤ fuel := by simpa using enough
     simp [normalizeOuter,rootFound,hostFound,outside,outerFound,ih fuel enoughRest]

theorem outer_trace_unique (raw : RawProviderInput) (pseudos : List Nat) (identity : Nat)
 (a b : List Context) (ha : OuterTrace raw pseudos identity a) (hb : OuterTrace raw pseudos identity b) :
 a = b := by
 have left := outer_normalization_complete raw pseudos identity a ha (a.length+b.length) (by omega)
 have right := outer_normalization_complete raw pseudos identity b hb (a.length+b.length) (by omega)
 rw [left] at right
 exact Option.some.inj right

def rawPartReference (raw : RawProviderInput) (pseudos parts : List Nat)
 (identity limit : Nat) (result : List Entry) : Prop :=
 ∃ contexts, OuterTrace raw pseudos identity contexts ∧
   result = physicalReference limit 1 parts contexts

theorem raw_part_collection_refinement (raw : RawProviderInput) (pseudos parts : List Nat)
 (identity limit fuel : Nat) (contexts : List Context)
 (normalized : normalizeOuter raw pseudos fuel identity = some contexts) :
 rawPartReference raw pseudos parts identity limit (collectParts limit 1 parts contexts) := by
 exact ⟨contexts,outer_normalization_sound raw pseudos fuel identity contexts normalized,
   parts_refinement contexts limit 1 parts⟩

theorem raw_part_reference_unique (raw : RawProviderInput) (pseudos parts : List Nat)
 (identity limit : Nat) (a b : List Entry)
 (ha : rawPartReference raw pseudos parts identity limit a)
 (hb : rawPartReference raw pseudos parts identity limit b) : a = b := by
 rcases ha with ⟨ca,ta,ea⟩
 rcases hb with ⟨cb,tb,eb⟩
 have same := outer_trace_unique raw pseudos identity ca cb ta tb
 subst cb
 exact ea.trans eb.symm

inductive SlotTrace (raw : RawProviderInput) (pseudos : List Nat) :
 Option Nat → List InnerContext → Prop
 | endPath : SlotTrace raw pseudos none []
 | slot (identity rootIdentity : Nat) (element : RawElement) (root : RawShadowRoot)
   (rest : List InnerContext)
   (elementFound : raw.elements[identity]? = some element)
   (containing : element.containingShadow = some rootIdentity)
   (rootFound : raw.roots[rootIdentity]? = some root)
   (tail : SlotTrace raw pseudos element.assignedSlot rest) :
   SlotTrace raw pseudos (some identity) (slotContext pseudos rootIdentity root::rest)

theorem slot_normalization_sound (raw : RawProviderInput) (pseudos : List Nat)
 (fuel : Nat) (start : Option Nat) (slots : List InnerContext)
 (normalized : normalizeSlots raw pseudos fuel start = some slots) :
 SlotTrace raw pseudos start slots := by
 induction fuel generalizing start slots with
 | zero =>
   cases start
   · simp [normalizeSlots] at normalized; subst slots; exact SlotTrace.endPath
   · simp [normalizeSlots] at normalized
 | succ fuel ih =>
   cases start with
   | none => simp [normalizeSlots] at normalized; subst slots; exact SlotTrace.endPath
   | some identity =>
     cases elementFound : raw.elements[identity]? with
     | none => simp [normalizeSlots,elementFound] at normalized
     | some element =>
       cases containing : element.containingShadow with
       | none => simp [normalizeSlots,elementFound,containing] at normalized
       | some rootIdentity =>
         cases rootFound : raw.roots[rootIdentity]? with
         | none => simp [normalizeSlots,elementFound,containing,rootFound] at normalized
         | some root =>
           cases tail : normalizeSlots raw pseudos fuel element.assignedSlot with
           | none => simp [normalizeSlots,elementFound,containing,rootFound,tail] at normalized
           | some rest =>
             simp [normalizeSlots,elementFound,containing,rootFound,tail] at normalized
             subst slots
             exact SlotTrace.slot identity rootIdentity element root rest
               elementFound containing rootFound (ih _ _ tail)

theorem slot_normalization_complete (raw : RawProviderInput) (pseudos : List Nat)
 (start : Option Nat) (slots : List InnerContext) (meaning : SlotTrace raw pseudos start slots)
 (fuel : Nat) (enough : slots.length ≤ fuel) :
 normalizeSlots raw pseudos fuel start = some slots := by
 induction meaning generalizing fuel with
 | endPath => simp [normalizeSlots]
 | slot identity rootIdentity element root rest elementFound containing rootFound tail ih =>
   cases fuel with
   | zero => simp at enough
   | succ fuel =>
     have enoughRest : rest.length ≤ fuel := by simpa using enough
     simp [normalizeSlots,elementFound,containing,rootFound,ih fuel enoughRest]

theorem slot_trace_unique (raw : RawProviderInput) (pseudos : List Nat) (start : Option Nat)
 (a b : List InnerContext) (ha : SlotTrace raw pseudos start a) (hb : SlotTrace raw pseudos start b) :
 a = b := by
 have left := slot_normalization_complete raw pseudos start a ha (a.length+b.length) (by omega)
 have right := slot_normalization_complete raw pseudos start b hb (a.length+b.length) (by omega)
 rw [left] at right
 exact Option.some.inj right

def rawSlotReference (raw : RawProviderInput) (pseudos : List Nat) (start : Option Nat)
 (limit : Nat) (result : List Entry) : Prop :=
 ∃ slots, SlotTrace raw pseudos start slots ∧ result = (slotReference limit 0 slots).reverse.flatten

theorem raw_slot_collection_refinement (raw : RawProviderInput) (pseudos : List Nat)
 (start : Option Nat) (limit fuel : Nat) (slots : List InnerContext)
 (normalized : normalizeSlots raw pseudos fuel start = some slots) :
 rawSlotReference raw pseudos start limit (reverseSlotCollector limit 0 slots) := by
 exact ⟨slots,slot_normalization_sound raw pseudos fuel start slots normalized,
   slots_refinement slots limit 0⟩

theorem raw_slot_reference_unique (raw : RawProviderInput) (pseudos : List Nat)
 (start : Option Nat) (limit : Nat) (a b : List Entry)
 (ha : rawSlotReference raw pseudos start limit a)
 (hb : rawSlotReference raw pseudos start limit b) : a = b := by
 rcases ha with ⟨sa,ta,ea⟩
 rcases hb with ⟨sb,tb,eb⟩
 have same := slot_trace_unique raw pseudos start sa sb ta tb
 subst sb
 exact ea.trans eb.symm

#print axioms outer_normalization_sound
#print axioms outer_normalization_complete
#print axioms raw_part_collection_refinement
#print axioms raw_part_reference_unique
#print axioms slot_normalization_sound
#print axioms slot_normalization_complete
#print axioms raw_slot_collection_refinement
#print axioms raw_slot_reference_unique
end ShadowOrder
