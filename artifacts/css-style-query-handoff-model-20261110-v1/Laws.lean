import Model

namespace CssQueryHandoff

theorem project_exact (hint bit) : project hint bit = true ↔ queryBit bit = true ∧ hint bit = true := by
  simp [project]

theorem project_font (hint) : project hint .font = false := by rfl

theorem project_other (hint) : project hint .other = false := by rfl

theorem ancestor_depth {tree : Tree count} {node ancestor}
    (path : Ancestor tree node ancestor) : tree.depth ancestor ≤ tree.depth node := by
  induction path with
  | self node => exact Nat.le_refl _
  | parent edge path ih => exact Nat.le_trans ih (Nat.le_of_lt (tree.decreases _ _ edge))

theorem root_ancestor {tree : Tree count} {node} : Ancestor tree tree.root node ↔ node = tree.root := by
  constructor
  · intro path
    cases path with
    | self => rfl
    | parent edge _ => simp [tree.root_parent] at edge
  · intro equality
    subst node
    exact .self _

theorem ancestor_step {tree : Tree count} {node parent ancestor}
    (edge : tree.parent node = some parent) :
    Ancestor tree node ancestor ↔ ancestor = node ∨ Ancestor tree parent ancestor := by
  constructor
  · intro path
    cases path with
    | self => exact Or.inl rfl
    | parent other prior =>
      have same := Option.some.inj (other.symm.trans edge)
      subst same
      exact Or.inr prior
  · intro path
    cases path with
    | inl equality => subst ancestor; exact .self _
    | inr prior => exact .parent edge prior

theorem ancestors_exact (tree : Tree count) (node ancestor) :
    ancestor ∈ ancestors tree node ↔ Ancestor tree node ancestor := by
  by_cases atRoot : node = tree.root
  · subst node
    rw [ancestors]
    simp [root_ancestor]
  · rw [ancestors]
    simp only [dite_eq_right atRoot, List.mem_cons]
    rw [ancestors_exact tree (tree.next node) ancestor, ancestor_step (tree.next_edge node atRoot)]
termination_by tree.depth node
 decreasing_by exact tree.decreases node (tree.next node) (tree.next_edge node atRoot)

theorem ancestor_root_reached (tree : Tree count) (node) : Ancestor tree node tree.root := by
  by_cases atRoot : node = tree.root
  · subst node
    exact .self _
  · exact .parent (tree.next_edge node atRoot) (ancestor_root_reached tree (tree.next node))
termination_by tree.depth node
 decreasing_by exact tree.decreases node (tree.next node) (tree.next_edge node atRoot)

theorem ancestors_reach_root (tree : Tree count) (node) : tree.root ∈ ancestors tree node := by
  exact (ancestors_exact _ _ _).mpr (ancestor_root_reached _ _)

theorem ancestors_exclude_child {tree : Tree count} {producer child}
    (edge : tree.parent child = some producer) : child ∉ ancestors tree producer := by
  intro member
  have bound := ancestor_depth ((ancestors_exact _ _ _).mp member)
  have strict := tree.decreases _ _ edge
  exact (Nat.not_lt_of_ge bound) strict

theorem execute_hints (deliveries : List (Delivery count)) (state : State count) (node bit) :
    (execute deliveries state).hints node bit = true ↔
      state.hints node bit = true ∨
      ∃ delivery ∈ deliveries, node = delivery.child ∧ delivery.hint bit = true := by
  induction deliveries generalizing state with
  | nil => simp [execute]
  | cons delivery rest ih =>
    rw [execute, ih]
    by_cases same : node = delivery.child
    · simp [applyDelivery, same, union, List.mem_cons, or_assoc]
    · simp [applyDelivery, same, List.mem_cons]

theorem execute_dirty (deliveries : List (Delivery count)) (state : State count) (node) :
    (execute deliveries state).dirty node = true ↔
      state.dirty node = true ∨ ∃ delivery ∈ deliveries, node ∈ delivery.dirty := by
  induction deliveries generalizing state with
  | nil => simp [execute]
  | cons delivery rest ih =>
    rw [execute, ih]
    simp [applyDelivery, List.mem_cons, or_assoc, or_left_comm, or_comm]

theorem plan_member (tree : Tree count) styled animationOnly producers delivery :
    delivery ∈ plan tree styled animationOnly producers ↔
      ∃ producer ∈ producers, collected animationOnly producer = true ∧
        ∃ child ∈ tree.children producer.node, styled child = true ∧
          (⟨child, project producer.childHint, ancestors tree producer.node⟩ : Delivery count) = delivery := by
  simp [plan, List.mem_flatMap, List.mem_filterMap]

theorem collected_exact (animationOnly) (producer : Producer count) :
    collected animationOnly producer = true ↔ animationOnly = true ∧
      (producer.childHint .unnamedQuery = true ∨ producer.childHint .namedQuery = true) := by
  simp [collected]

theorem supplies_plan (tree : Tree count) styled animationOnly producers node bit :
    (∃ delivery ∈ plan tree styled animationOnly producers,
      node = delivery.child ∧ delivery.hint bit = true) ↔
      Supplies tree styled animationOnly producers node bit := by
  constructor
  · rintro ⟨delivery, member, same, hint⟩
    obtain ⟨producer, present, active, child, childMember, eligible, equality⟩ :=
      (plan_member _ _ _ _ _).mp member
    subst delivery
    change node = child at same
    subst node
    obtain ⟨query, source⟩ := (project_exact _ _).mp hint
    have animation : animationOnly = true := by
      cases animationOnly <;> simp_all [collected]
    exact .producer producer present animation
      ((tree.children_exact _ _).mp childMember) eligible query source
  · intro supplied
    cases supplied with
    | producer producer present animation edge eligible query source =>
      have active : collected animationOnly producer = true := by
        cases bit <;> simp_all [collected, queryBit]
      refine ⟨⟨node, project producer.childHint, ancestors tree producer.node⟩, ?_, rfl, ?_⟩
      · exact (plan_member _ _ _ _ _).mpr
          ⟨producer, present, active, node, (tree.children_exact _ _).mpr edge, eligible, rfl⟩
      · exact (project_exact _ _).mpr ⟨query, source⟩

theorem marks_plan (tree : Tree count) styled animationOnly producers node :
    (∃ delivery ∈ plan tree styled animationOnly producers, node ∈ delivery.dirty) ↔
      Marks tree styled animationOnly producers node := by
  constructor
  · rintro ⟨delivery, member, dirty⟩
    obtain ⟨producer, present, active, child, childMember, eligible, equality⟩ :=
      (plan_member _ _ _ _ _).mp member
    subst delivery
    obtain ⟨animation, query⟩ := (collected_exact _ _).mp active
    exact .producer producer child present animation query ((tree.children_exact _ _).mp childMember)
      eligible ((ancestors_exact _ _ _).mp dirty)
  · intro marked
    cases marked with
    | producer producer child present animation query edge eligible ancestry =>
      have active := (collected_exact _ _).mpr ⟨animation, query⟩
      refine ⟨⟨child, project producer.childHint, ancestors tree producer.node⟩, ?_, ?_⟩
      · exact (plan_member _ _ _ _ _).mpr
          ⟨producer, present, active, child, (tree.children_exact _ _).mpr edge, eligible, rfl⟩
      · exact (ancestors_exact _ _ _).mpr ancestry

theorem handoff_hints (tree : Tree count) styled animationOnly producers state node bit :
    (handoff tree styled animationOnly producers state).hints node bit = true ↔
      state.hints node bit = true ∨ Supplies tree styled animationOnly producers node bit := by
  rw [handoff, execute_hints, supplies_plan]

theorem handoff_dirty (tree : Tree count) styled animationOnly producers state node :
    (handoff tree styled animationOnly producers state).dirty node = true ↔
      state.dirty node = true ∨ Marks tree styled animationOnly producers node := by
  rw [handoff, execute_dirty, marks_plan]

theorem existing_hint_preserved (tree : Tree count) styled animationOnly producers state node bit
    (existing : state.hints node bit = true) :
    (handoff tree styled animationOnly producers state).hints node bit = true := by
  exact (handoff_hints _ _ _ _ _ _ _).mpr (Or.inl existing)

theorem existing_dirty_preserved (tree : Tree count) styled animationOnly producers state node
    (existing : state.dirty node = true) :
    (handoff tree styled animationOnly producers state).dirty node = true := by
  exact (handoff_dirty _ _ _ _ _ _).mpr (Or.inl existing)

theorem no_invented_bits {tree : Tree count} {styled animationOnly producers state node bit}
    (absent : state.hints node bit = false)
    (present : (handoff tree styled animationOnly producers state).hints node bit = true) :
    ∃ producer ∈ producers, tree.parent node = some producer.node ∧
      styled node = true ∧ queryBit bit = true ∧ producer.childHint bit = true := by
  obtain old | supplied := (handoff_hints _ _ _ _ _ _ _).mp present
  · simp [absent] at old
  · cases supplied with
    | producer producer member _ edge eligible query hint =>
      exact ⟨producer, member, edge, eligible, query, hint⟩

theorem font_hint_preserved_exactly (tree : Tree count) styled animationOnly producers state node :
    (handoff tree styled animationOnly producers state).hints node .font = state.hints node .font := by
  have equivalence := handoff_hints tree styled animationOnly producers state node .font
  have impossible : ¬ Supplies tree styled animationOnly producers node .font := by
    intro supplied
    cases supplied with
    | producer _ _ _ _ _ query _ => simp [queryBit] at query
  cases old : state.hints node .font <;>
    cases updated : (handoff tree styled animationOnly producers state).hints node .font <;>
    simp_all

theorem eligible_child_coverage {tree : Tree count} {styled producers state producer child bit}
    (member : producer ∈ producers) (edge : tree.parent child = some producer.node)
    (eligible : styled child = true) (query : queryBit bit = true)
    (hint : producer.childHint bit = true) :
    (handoff tree styled true producers state).hints child bit = true := by
  exact (handoff_hints _ _ _ _ _ _ _).mpr
    (Or.inr (.producer producer member rfl edge eligible query hint))

theorem eligible_child_root_reachable {tree : Tree count} {styled producers state producer child}
    (member : producer ∈ producers) (active : collected true producer = true)
    (edge : tree.parent child = some producer.node) (eligible : styled child = true) :
    (handoff tree styled true producers state).dirty tree.root = true := by
  exact (handoff_dirty _ _ _ _ _ _).mpr
    (Or.inr (.producer producer child member rfl ((collected_exact _ _).mp active).2
      edge eligible (ancestor_root_reached _ _)))

theorem ancestor_trans {tree : Tree count} {start middle finish}
    (first : Ancestor tree start middle) (second : Ancestor tree middle finish) :
    Ancestor tree start finish := by
  induction first with
  | self => exact second
  | parent edge prior ih => exact .parent edge (ih second)

theorem clipped_exact (tree : Tree count) (state : Certificates count)
    (sound : CertificateSound tree state) (producer node) :
    node ∈ clippedAncestors tree state.certified producer ↔
      Ancestor tree producer node ∧ state.certified node = false := by
  by_cases certified : state.certified producer = true
  · rw [clippedAncestors]
    simp only [certified, ↓reduceIte, List.not_mem_nil, false_iff, not_and]
    intro path
    have known := (sound producer certified node path).1
    simp [known]
  · have uncertified : state.certified producer = false := by
      cases value : state.certified producer <;> simp_all
    rw [clippedAncestors]
    simp only [uncertified, Bool.false_eq_true, ↓reduceIte]
    by_cases atRoot : producer = tree.root
    · subst producer
      simp [root_ancestor]
      intro same
      subst node
      exact uncertified
    · simp only [dite_eq_right atRoot, List.mem_cons]
      rw [clipped_exact tree state sound (tree.next producer) node,
        ancestor_step (tree.next_edge producer atRoot)]
      constructor
      · rintro (equal | ⟨path, clean⟩)
        · subst node; exact ⟨Or.inl rfl, uncertified⟩
        · exact ⟨Or.inr path, clean⟩
      · rintro ⟨equal | path, clean⟩
        · exact Or.inl equal
        · exact Or.inr ⟨path, clean⟩
termination_by tree.depth producer
 decreasing_by exact tree.decreases producer (tree.next producer) (tree.next_edge producer atRoot)

theorem certify_dirty_equivalent (tree : Tree count) (state : Certificates count)
    (sound : CertificateSound tree state) (producer node) :
    (certify tree producer state).dirty node =
      (state.dirty node || (ancestors tree producer).contains node) := by
  have full := ancestors_exact tree producer node
  have clipped := clipped_exact tree state sound producer node
  have known : state.certified node = true → Ancestor tree producer node → state.dirty node = true := by
    intro certified _
    exact (sound node certified node (.self node)).2
  unfold certify
  cases old : state.dirty node <;>
    cases marked : (ancestors tree producer).contains node <;>
    cases fresh : (clippedAncestors tree state.certified producer).contains node <;>
    simp_all

theorem certify_sound (tree : Tree count) (state : Certificates count)
    (sound : CertificateSound tree state) (producer) :
    CertificateSound tree (certify tree producer state) := by
  intro node marked ancestor path
  have markedCases : state.certified node = true ∨ node ∈ clippedAncestors tree state.certified producer := by
    simpa [certify] using marked
  cases markedCases with
  | inl existing =>
    obtain ⟨certified, dirty⟩ := sound node existing ancestor path
    simp [certify, certified, dirty]
  | inr fresh =>
    have sourcePath := ((clipped_exact tree state sound producer node).mp fresh).1
    have rootPath := ancestor_trans sourcePath path
    by_cases certified : state.certified ancestor = true
    · have dirty := (sound ancestor certified ancestor (.self ancestor)).2
      simp [certify, certified, dirty]
    · have clean : state.certified ancestor = false := by
        cases value : state.certified ancestor <;> simp_all
      have included := (clipped_exact tree state sound producer ancestor).mpr ⟨rootPath, clean⟩
      simp [certify, included]

theorem empty_certificate_sound (tree : Tree count) (dirty) :
    CertificateSound tree ⟨fun _ => false, dirty⟩ := by
  intro node certified
  simp at certified

theorem certify_many_sound (tree : Tree count) (producers) (state : Certificates count)
    (sound : CertificateSound tree state) :
    CertificateSound tree (certifyMany tree producers state) := by
  induction producers generalizing state with
  | nil => exact sound
  | cons producer rest ih => exact ih _ (certify_sound _ _ sound producer)

theorem certify_many_equivalent (tree : Tree count) (producers) (state : Certificates count)
    (sound : CertificateSound tree state) (node) :
    (certifyMany tree producers state).dirty node =
      (state.dirty node || producers.any (fun producer => (ancestors tree producer).contains node)) := by
  induction producers generalizing state with
  | nil => simp [certifyMany]
  | cons producer rest ih =>
    rw [certifyMany, ih _ (certify_sound _ _ sound producer),
      certify_dirty_equivalent _ _ sound producer]
    simp [Bool.or_assoc]

theorem project_ignores_font (hint : Hints) (font : Bool) :
    project (fun bit => if bit = .font then font else hint bit) = project hint := by
  funext bit
  cases bit <;> rfl

theorem collection_ignores_font (producer : Producer count) (font : Bool) (animationOnly) :
    collected animationOnly
      { producer with childHint := fun bit => if bit = .font then font else producer.childHint bit } =
      collected animationOnly producer := by
  rfl

theorem active_node_member (tree : Tree count) styled animationOnly producers node :
    node ∈ activeNodes tree styled animationOnly producers ↔
      ∃ producer ∈ producers, collected animationOnly producer = true ∧
        (∃ child ∈ tree.children producer.node, styled child = true) ∧ producer.node = node := by
  simp [activeNodes, List.mem_filterMap, List.any_eq_true, and_assoc]

theorem active_nodes_marks (tree : Tree count) styled animationOnly producers node :
    (activeNodes tree styled animationOnly producers).any
        (fun producer => (ancestors tree producer).contains node) = true ↔
      Marks tree styled animationOnly producers node := by
  constructor
  · intro marked
    obtain ⟨producerNode, member, contains⟩ := List.any_eq_true.mp marked
    obtain ⟨producer, present, active, ⟨child, childMember, eligible⟩, equal⟩ :=
      (active_node_member _ _ _ _ _).mp member
    obtain ⟨animation, query⟩ := (collected_exact _ _).mp active
    subst producerNode
    have ancestry : Ancestor tree producer.node node := by
      apply (ancestors_exact _ _ _).mp
      simpa using contains
    exact .producer producer child present animation query
      ((tree.children_exact _ _).mp childMember) eligible ancestry
  · intro marked
    cases marked with
    | producer producer child present animation query edge eligible ancestry =>
      apply List.any_eq_true.mpr
      refine ⟨producer.node, ?_, ?_⟩
      · exact (active_node_member _ _ _ _ _).mpr
          ⟨producer, present, (collected_exact _ _).mpr ⟨animation, query⟩,
            ⟨child, (tree.children_exact _ _).mpr edge, eligible⟩, rfl⟩
      · have member := (ancestors_exact _ _ _).mpr ancestry
        simpa using member

theorem boolean_ext (left right : Bool) (equivalence : left = true ↔ right = true) : left = right := by
  cases left <;> cases right <;> simp_all

theorem optimized_handoff_equivalent (tree : Tree count) styled animationOnly producers hints
    (state : Certificates count) (sound : CertificateSound tree state) (node) :
    (certifyMany tree (activeNodes tree styled animationOnly producers) state).dirty node =
      (handoff tree styled animationOnly producers ⟨hints, state.dirty⟩).dirty node := by
  rw [certify_many_equivalent _ _ _ sound]
  apply boolean_ext
  rw [handoff_dirty]
  have relation := active_nodes_marks tree styled animationOnly producers node
  cases old : state.dirty node <;> simp_all

end CssQueryHandoff
