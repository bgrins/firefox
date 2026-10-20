import TypeMutations
namespace AtomProvider
open OrderedTypes TypeMutations
abbrev DOMString := List UInt16
variable {α β : Type} [DecidableEq α] [DecidableEq β]

theorem encoded_member (f : α → β) (hf : Function.Injective f) (x : α) (xs : List α) :
    f x ∈ xs.map f ↔ x ∈ xs := by
  constructor
  · intro h
    obtain ⟨a, ha, he⟩ := List.mem_map.mp h
    have := hf he
    simpa [this] using ha
  · exact fun h => List.mem_map.mpr ⟨x, h, rfl⟩

theorem firsts_map (f : α → β) (hf : Function.Injective f) (seen xs : List α) :
    firsts (seen.map f) (xs.map f) = (firsts seen xs).map f := by
  induction xs generalizing seen with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.map_cons, firsts, encoded_member f hf]
    split
    · exact ih seen
    · simp only [List.map_cons]
      congr 1
      exact ih (x :: seen)

theorem appendNew_map (f : α → β) (hf : Function.Injective f) (xs : List α) (x : α) :
    appendNew (xs.map f) (f x) = (appendNew xs x).map f := by
  simp only [appendNew, encoded_member f hf]
  split <;> simp

theorem removeAll_map (f : α → β) (hf : Function.Injective f) (xs : List α) (x : α) :
    (xs.map f).filter (fun a => decide (a ≠ f x)) =
      (xs.filter (fun a => decide (a ≠ x))).map f := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    have he : f a = f x ↔ a = x := ⟨fun h => hf h, congrArg f⟩
    simp only [List.map_cons, List.filter_cons, ne_eq, he]
    split <;> simp_all

def mapOp (f : α → β) : Op α → Op β
  | .add x => .add (f x)
  | .delete x => .delete (f x)
  | .clear => .clear
  | .observe => .observe

theorem reference_map (f : α → β) (hf : Function.Injective f)
    (id : Nat) (xs : List α) (op : Op α) :
    reference id (xs.map f) (mapOp f op) =
      ((reference id xs op).1.map f, (reference id xs op).2) := by
  cases op <;> simp only [mapOp, reference, appendNew_map f hf, removeAll_map f hf,
    encoded_member f hf, List.map_nil]

theorem history_map (f : α → β) (hf : Function.Injective f)
    (id : Nat) (xs : List α) (ops : List (Op α)) :
    referenceHistory id (xs.map f) (ops.map (mapOp f)) =
      ((referenceHistory id xs ops).1.map f, (referenceHistory id xs ops).2) := by
  induction ops generalizing xs with
  | nil => rfl
  | cons op ops ih =>
    simp only [List.map_cons, referenceHistory, reference_map f hf, ih]

structure Provider (Atom : Type) where
  intern : DOMString → Atom
  text : Atom → DOMString
  text_intern : ∀ s, text (intern s) = s

theorem intern_injective {Atom : Type} (p : Provider Atom) : Function.Injective p.intern := by
  intro a b he
  have := congrArg p.text he
  simpa only [p.text_intern] using this

theorem atom_equality {Atom : Type} (p : Provider Atom) (a b : DOMString) :
    p.intern a = p.intern b ↔ a = b :=
  ⟨fun h => intern_injective p h, congrArg p.intern⟩

theorem map_decode {Atom : Type} (p : Provider Atom) (xs : List DOMString) :
    (xs.map p.intern).map p.text = xs := by
  simp only [List.map_map]
  have he : p.text ∘ p.intern = id := funext p.text_intern
  rw [he, List.map_id]

theorem three_representations {Atom : Type} [DecidableEq Atom] (p : Provider Atom)
    (input : List DOMString) (ops : List (Op DOMString)) (tid doc : Nat) :
    let result := history (start (input.map p.intern) tid doc) (ops.map (mapOp p.intern))
    let spec := referenceHistory tid (firsts [] input) ops
    result.1.native = spec.1.map p.intern ∧
    (observed result.1).map p.text = spec.1 ∧ result.2 = spec.2 := by
  dsimp only
  have hg := history_good (start (input.map p.intern) tid doc) (ops.map (mapOp p.intern))
    (start_good (input.map p.intern) tid doc)
  have hr := arbitrary_successful_observations (input.map p.intern)
    (ops.map (mapOp p.intern)) tid doc
  have hi := intern_injective p
  have hm := firsts_map p.intern hi [] input
  simp only [List.map_nil] at hm
  rw [hm, history_map p.intern hi] at hr
  rw [public_native _ hg] at hr
  refine ⟨hr.1, ?_, hr.2⟩
  rw [public_native _ hg, hr.1, map_decode]

theorem no_case_folding {Atom : Type} (p : Provider Atom) :
    p.intern [97] ≠ p.intern [65] := by
  intro he
  have := (atom_equality p [97] [65]).mp he
  contradiction

theorem surrogate_units_preserved {Atom : Type} (p : Provider Atom) :
    p.text (p.intern [0, 0xD800, 0xDC00, 0xFFFF]) = [0, 0xD800, 0xDC00, 0xFFFF] :=
  p.text_intern _

end AtomProvider
