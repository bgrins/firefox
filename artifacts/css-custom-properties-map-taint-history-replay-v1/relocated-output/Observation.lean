import Laws
namespace TaintShortcut
structure Range where
  start : Nat
  finish : Nat

def overlaps (a b : Range) : Bool := decide (a.start ≤ b.finish ∧ a.finish ≥ b.start)
def observeAt (parse : P → Option U) (region query : Range) : State P → Option U
  | none => none
  | some v => if v.attr && overlaps region query then none else parse v.payload

theorem contained_overlaps (base len : Nat) (query : Range)
    (valid : query.start ≤ query.finish) (lower : base ≤ query.start)
    (upper : query.finish ≤ base + len) : overlaps ⟨base,base+len⟩ query = true := by
  simp only [overlaps, decide_eq_true_eq]
  constructor <;> omega

theorem contained_url_projection (parse : P → Option U) (base len : Nat) (query : Range)
    (valid : query.start ≤ query.finish) (lower : base ≤ query.start)
    (upper : query.finish ≤ base + len) (value : State P) :
    observeAt parse ⟨base,base+len⟩ query value = observeURL parse value := by
  cases value with
  | none => rfl
  | some v => simp [observeAt, observeURL, contained_overlaps base len query valid lower upper]

theorem pipeline_range_correct (cmp : P → P → Bool) (sound : PayloadSound cmp)
    (resolve : Incoming P → State P) (provider : ReferenceFreeProvider resolve)
    (unique : Bool) (old : State P) (d : Incoming P) (domain : EligibleDomain d)
    (parse : P → Option U) (region query : Range) :
    observeAt parse region query (pipeline (metadataSame cmp) (metadataSame cmp) resolve unique old d) =
      observeAt parse region query (resolve d) := by
  rw [pipeline_correct cmp sound resolve provider unique old d domain]
end TaintShortcut
