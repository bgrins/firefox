import QualifiedHistories
namespace QualifiedAttributes

inductive Node where
 | custom (name : Nat)
 | attr (key : Key)
 | nonCustom (property : Nat)
 deriving DecidableEq, Repr

theorem attribute_node_identity (left right : Key) : Node.attr left = Node.attr right ↔ left = right := by
 simp

theorem attribute_and_custom_nodes_are_distinct (key : Key) (name : Nat) :
 Node.attr key ≠ Node.custom name := by simp

theorem distinct_namespace_nodes_are_distinct (name left right : Nat) (different : left ≠ right) :
 Node.attr ⟨name,left⟩ ≠ Node.attr ⟨name,right⟩ := by
 intro same
 exact different_namespaces_are_distinct name left right different (Node.attr.inj same)

inductive Reach (edge : Vertex → Vertex → Prop) : Vertex → Vertex → Prop where
 | refl (vertex : Vertex) : Reach edge vertex vertex
 | step {first next last : Vertex} : edge first next → Reach edge next last → Reach edge first last

def stronglyConnected (edge : Vertex → Vertex → Prop) (left right : Vertex) :=
 Reach edge left right ∧ Reach edge right left

def encodedEdge (encode : Vertex → Code) (edge : Vertex → Vertex → Prop) (left right : Code) : Prop :=
 ∃ first next, encode first = left ∧ encode next = right ∧ edge first next

theorem encoding_preserves_reach (encode : Vertex → Code) (edge : Vertex → Vertex → Prop)
 (first last : Vertex) (path : Reach edge first last) :
 Reach (encodedEdge encode edge) (encode first) (encode last) := by
 induction path with
 | refl vertex => exact .refl _
 | @step first next last link path ih => exact .step ⟨first,next,rfl,rfl,link⟩ ih

theorem injective_encoding_reflects_path_endpoint (encode : Vertex → Code)
 (injective : Function.Injective encode) (edge : Vertex → Vertex → Prop)
 (first last : Code) (path : Reach (encodedEdge encode edge) first last) :
 ∀ original, first = encode original → ∃ terminal, last = encode terminal ∧ Reach edge original terminal := by
 induction path with
 | refl vertex =>
   intro original same
   exact ⟨original,same,.refl _⟩
 | @step first next last link path ih =>
   intro original same
   rcases link with ⟨a,b,ea,eb,ab⟩
   have equal : a = original := injective (ea.trans same)
   subst a
   rcases ih b eb.symm with ⟨terminal,lastEquals,reachable⟩
   exact ⟨terminal,lastEquals,.step ab reachable⟩

theorem injective_encoding_preserves_and_reflects_reach (encode : Vertex → Code)
 (injective : Function.Injective encode) (edge : Vertex → Vertex → Prop) (left right : Vertex) :
 Reach (encodedEdge encode edge) (encode left) (encode right) ↔ Reach edge left right := by
 constructor
 · intro path
   rcases injective_encoding_reflects_path_endpoint encode injective edge _ _ path left rfl with
     ⟨terminal,same,originalPath⟩
   have equality : right = terminal := injective same
   subst terminal
   exact originalPath
 · exact encoding_preserves_reach encode edge left right

theorem injective_encoding_preserves_scc_membership (encode : Vertex → Code)
 (injective : Function.Injective encode) (edge : Vertex → Vertex → Prop) (left right : Vertex) :
 stronglyConnected (encodedEdge encode edge) (encode left) (encode right) ↔
 stronglyConnected edge left right := by
 simp only [stronglyConnected,injective_encoding_preserves_and_reflects_reach encode injective]

def nameOnlyNode : Node → Nat × Nat
 | .custom name => (0,name)
 | .attr key => (1,key.name)
 | .nonCustom property => (2,property)

theorem name_only_encoding_creates_false_self_edge (name left right : Nat) (different : left ≠ right) :
 let source := Node.attr ⟨name,left⟩
 let target := Node.attr ⟨name,right⟩
 let edge := fun a b => a = source ∧ b = target
 ¬ edge source source ∧
 encodedEdge nameOnlyNode edge (nameOnlyNode source) (nameOnlyNode source) := by
 dsimp
 constructor
 · intro same
   exact distinct_namespace_nodes_are_distinct name left right different same.2
 · exact ⟨Node.attr ⟨name,left⟩,Node.attr ⟨name,right⟩,rfl,rfl,⟨rfl,rfl⟩⟩

def invalidateNode (values : AttributeMap Value) : Node → AttributeMap Value
 | .attr key => invalidate values key
 | _ => values

def invalidateComponent (values : AttributeMap Value) (nodes : List Node) :=
 nodes.foldl invalidateNode values

theorem component_invalidation_preserves_nonmember (values : AttributeMap Value)
 (nodes : List Node) (key : Key) (outside : Node.attr key ∉ nodes) :
 invalidateComponent values nodes key = values key := by
 induction nodes generalizing values with
 | nil => rfl
 | cons node rest ih =>
   have outsideRest : Node.attr key ∉ rest := fun h => outside (List.mem_cons_of_mem _ h)
   simp only [invalidateComponent,List.foldl_cons]
   rw [← invalidateComponent,ih _ outsideRest]
   cases node with
   | custom name => rfl
   | nonCustom property => rfl
   | attr other =>
     apply write_preserves_other
     intro same
     subst other
     exact outside (by simp)

theorem component_invalidation_exact (values : AttributeMap Value)
 (nodes : List Node) (key : Key) :
 invalidateComponent values nodes key =
   if Node.attr key ∈ nodes then some none else values key := by
 induction nodes generalizing values with
 | nil => simp [invalidateComponent]
 | cons node rest ih =>
   simp only [invalidateComponent,List.foldl_cons]
   rw [← invalidateComponent,ih]
   by_cases inRest : Node.attr key ∈ rest
   · simp [inRest]
   · simp only [inRest,ite_false,List.mem_cons,or_false]
     cases node with
     | custom name => simp [invalidateNode]
     | nonCustom property => simp [invalidateNode]
     | attr other => simp [invalidateNode,invalidate,write]

theorem component_invalidation_depends_only_on_membership (values : AttributeMap Value)
 (left right : List Node) (same : ∀ key, Node.attr key ∈ left ↔ Node.attr key ∈ right) :
 invalidateComponent values left = invalidateComponent values right := by
 funext key
 simp only [component_invalidation_exact,same]

theorem repeated_component_invalidation_is_idempotent (values : AttributeMap Value)
 (nodes : List Node) :
 invalidateComponent (invalidateComponent values nodes) nodes = invalidateComponent values nodes := by
 funext key
 simp only [component_invalidation_exact]
 split <;> rfl

end QualifiedAttributes
