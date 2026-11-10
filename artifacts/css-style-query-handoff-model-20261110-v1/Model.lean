namespace CssQueryHandoff

inductive Bit where
  | unnamedQuery
  | namedQuery
  | font
  | other
  deriving DecidableEq, Repr

abbrev Hints := Bit → Bool

def queryBit : Bit → Bool
  | .unnamedQuery | .namedQuery => true
  | _ => false

def project (hint : Hints) : Hints := fun bit => queryBit bit && hint bit

def union (left right : Hints) : Hints := fun bit => left bit || right bit

structure Tree (count : Nat) where
  root : Fin count
  parent : Fin count → Option (Fin count)
  depth : Fin count → Nat
  root_parent : parent root = none
  next : Fin count → Fin count
  next_edge : ∀ node, node ≠ root → parent node = some (next node)
  decreases : ∀ node ancestor, parent node = some ancestor → depth ancestor < depth node
  children : Fin count → List (Fin count)
  children_exact : ∀ node child, child ∈ children node ↔ parent child = some node

def ancestors (tree : Tree count) (node : Fin count) : List (Fin count) :=
  if _atRoot : node = tree.root then [node]
  else node :: ancestors tree (tree.next node)
termination_by tree.depth node
 decreasing_by exact tree.decreases node (tree.next node) (tree.next_edge node _atRoot)

inductive Ancestor (tree : Tree count) : Fin count → Fin count → Prop where
  | self (node) : Ancestor tree node node
  | parent {node parent ancestor} : tree.parent node = some parent →
      Ancestor tree parent ancestor → Ancestor tree node ancestor

structure Producer (count : Nat) where
  node : Fin count
  childHint : Hints

structure Delivery (count : Nat) where
  child : Fin count
  hint : Hints
  dirty : List (Fin count)

structure State (count : Nat) where
  hints : Fin count → Hints
  dirty : Fin count → Bool

def collected (animationOnly : Bool) (producer : Producer count) : Bool :=
  animationOnly && (producer.childHint .unnamedQuery || producer.childHint .namedQuery)

def plan (tree : Tree count) (styled : Fin count → Bool) (animationOnly : Bool)
    (producers : List (Producer count)) : List (Delivery count) :=
  producers.flatMap fun producer =>
    if collected animationOnly producer then
      (tree.children producer.node).filterMap fun child =>
        if styled child then some ⟨child, project producer.childHint, ancestors tree producer.node⟩
        else none
    else []

def applyDelivery (delivery : Delivery count) (state : State count) : State count :=
  ⟨fun node => if node = delivery.child then union (state.hints node) delivery.hint else state.hints node,
   fun node => state.dirty node || delivery.dirty.contains node⟩

def execute (deliveries : List (Delivery count)) (state : State count) : State count :=
  match deliveries with
  | [] => state
  | delivery :: rest => execute rest (applyDelivery delivery state)

def handoff (tree : Tree count) (styled : Fin count → Bool) (animationOnly : Bool)
    (producers : List (Producer count)) (state : State count) : State count :=
  execute (plan tree styled animationOnly producers) state

inductive Supplies (tree : Tree count) (styled : Fin count → Bool) (animationOnly : Bool)
    (producers : List (Producer count)) (child : Fin count) (bit : Bit) : Prop where
  | producer (producer) : producer ∈ producers → animationOnly = true →
      tree.parent child = some producer.node → styled child = true →
      queryBit bit = true → producer.childHint bit = true →
      Supplies tree styled animationOnly producers child bit

inductive Marks (tree : Tree count) (styled : Fin count → Bool) (animationOnly : Bool)
    (producers : List (Producer count)) (node : Fin count) : Prop where
  | producer (producer child) : producer ∈ producers → animationOnly = true →
      (producer.childHint .unnamedQuery = true ∨ producer.childHint .namedQuery = true) →
      tree.parent child = some producer.node → styled child = true →
      Ancestor tree producer.node node → Marks tree styled animationOnly producers node

structure Certificates (count : Nat) where
  certified : Fin count → Bool
  dirty : Fin count → Bool

def CertificateSound (tree : Tree count) (state : Certificates count) : Prop :=
  ∀ node, state.certified node = true → ∀ ancestor, Ancestor tree node ancestor →
    state.certified ancestor = true ∧ state.dirty ancestor = true

def clippedAncestors (tree : Tree count) (certified : Fin count → Bool)
    (node : Fin count) : List (Fin count) :=
  if certified node then []
  else if _atRoot : node = tree.root then [node]
  else node :: clippedAncestors tree certified (tree.next node)
termination_by tree.depth node
 decreasing_by exact tree.decreases node (tree.next node) (tree.next_edge node _atRoot)

def certify (tree : Tree count) (producer : Fin count) (state : Certificates count) : Certificates count :=
  let path := clippedAncestors tree state.certified producer
  ⟨fun node => state.certified node || path.contains node,
   fun node => state.dirty node || path.contains node⟩

def certifyMany (tree : Tree count) (producers : List (Fin count))
    (state : Certificates count) : Certificates count :=
  match producers with
  | [] => state
  | producer :: rest => certifyMany tree rest (certify tree producer state)

def activeNodes (tree : Tree count) (styled : Fin count → Bool) (animationOnly : Bool)
    (producers : List (Producer count)) : List (Fin count) :=
  producers.filterMap fun producer =>
    if collected animationOnly producer && (tree.children producer.node).any styled then
      some producer.node
    else none

end CssQueryHandoff
