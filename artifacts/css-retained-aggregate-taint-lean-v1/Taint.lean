import Ranges

namespace RetainedAggregateTaint
open TaintRanges

structure Chunk where
  bytes : List UInt8
  separator : List UInt8 := []
  tainted : Bool
  origin : Nat
  deriving DecidableEq, Repr

structure Retained where
  bytes : List UInt8
  ranges : List Span
  aggregate : Bool
  origins : List Nat
  deriving DecidableEq, Repr

structure Direct where
  bytes : List UInt8
  ranges : List Span
  deriving DecidableEq, Repr

structure Custom where
  bytes : List UInt8
  tainted : Bool
  deriving DecidableEq, Repr

def initial : Retained := ⟨[], [], false, []⟩
def chunkOrigins (c : Chunk) : List Nat := if c.tainted then [c.origin] else []
def start (s : Retained) (c : Chunk) := s.bytes.length + c.separator.length
def emitted (s : Retained) (c : Chunk) : List Span :=
  if c.bytes.isEmpty then []
  else if c.tainted then [⟨start s c, start s c + c.bytes.length⟩] else []

def append (s : Retained) (c : Chunk) : Retained :=
  ⟨if c.bytes.isEmpty then s.bytes else s.bytes ++ c.separator ++ c.bytes,
   s.ranges ++ emitted s c, s.aggregate || c.tainted, s.origins ++ chunkOrigins c⟩

def push (limit : Nat) (s : Retained) (c : Chunk) : Option Retained :=
  if s.bytes.length + c.bytes.length ≤ limit then some (append s c) else none

def run : Retained → List Chunk → Retained
  | s, [] => s
  | s, c :: cs => run (append s c) cs

def provenance (chunks : List Chunk) : List Nat := chunks.flatMap chunkOrigins

def toDirect (s : Retained) : Direct := ⟨s.bytes, s.ranges⟩
def publish (s : Retained) : Custom := ⟨s.bytes, s.aggregate⟩
def oldPublish (s : Retained) : Custom := ⟨s.bytes, !s.ranges.isEmpty⟩
def alias (c : Custom) (origin : Nat) : Chunk := ⟨c.bytes, [], c.tainted, origin⟩
def directBlocked (s : Retained) (url : Span) := blocked (toDirect s).ranges url

def Sound (s : Retained) : Prop :=
  s.aggregate = !s.origins.isEmpty ∧
  ∀ r ∈ s.ranges, r.start < r.finish ∧ r.finish ≤ s.bytes.length

theorem initial_sound : Sound initial := by simp [Sound, initial]

theorem empty_retains_provenance (s : Retained) (c : Chunk) (empty : c.bytes = []) :
    (append s c).bytes = s.bytes ∧ (append s c).ranges = s.ranges ∧
    (append s c).aggregate = (s.aggregate || c.tainted) ∧
    (append s c).origins = s.origins ++ chunkOrigins c := by
  simp [append, emitted, empty]

theorem append_origins (s : Retained) (c : Chunk) :
    (append s c).origins = s.origins ++ chunkOrigins c := rfl

theorem append_aggregate (s : Retained) (c : Chunk) :
    (append s c).aggregate = (s.aggregate || c.tainted) := rfl

theorem append_byte_length (s : Retained) (c : Chunk) :
    (append s c).bytes.length =
      if c.bytes.isEmpty then s.bytes.length else start s c + c.bytes.length := by
  by_cases h : c.bytes.isEmpty <;> simp [append, start, h, Nat.add_assoc]

theorem append_sound (s : Retained) (c : Chunk) (sound : Sound s) : Sound (append s c) := by
  constructor
  · have bit := sound.1
    cases ht : c.tainted <;> simp [append, chunkOrigins, ht, bit]
  · intro r member
    have old_le : s.bytes.length ≤ (append s c).bytes.length := by
      rw [append_byte_length]; unfold start; split <;> omega
    rcases List.mem_append.mp member with old | fresh
    · obtain ⟨nonempty, bound⟩ := sound.2 r old
      exact ⟨nonempty, by omega⟩
    · by_cases empty : c.bytes.isEmpty = true
      · simp [emitted, empty] at fresh
      · have length : 0 < c.bytes.length := by
          cases hb : c.bytes with
          | nil => simp [hb] at empty
          | cons b bs => simp
        cases ht : c.tainted with
        | false => simp [emitted, empty, ht] at fresh
        | true =>
            have eq : r = ⟨start s c, start s c + c.bytes.length⟩ := by
              simpa [emitted, empty, ht] using fresh
            subst r
            simp only [append_byte_length, empty, Bool.false_eq_true, ↓reduceIte]
            constructor <;> omega

theorem run_sound (s : Retained) (chunks : List Chunk) (sound : Sound s) :
    Sound (run s chunks) := by
  induction chunks generalizing s with
  | nil => exact sound
  | cons c cs ih => exact ih (append s c) (append_sound s c sound)

theorem run_origins (s : Retained) (chunks : List Chunk) :
    (run s chunks).origins = s.origins ++ provenance chunks := by
  induction chunks generalizing s with
  | nil => simp [run, provenance]
  | cons c cs ih => simp [run, ih, provenance, append, List.append_assoc]

theorem publication_conserves_trace (chunks : List Chunk) :
    (publish (run initial chunks)).tainted = !(provenance chunks).isEmpty := by
  have sound := run_sound initial chunks initial_sound
  simpa [publish, run_origins, initial] using sound.1

theorem direct_projection_exact (s : Retained) :
    (toDirect s).bytes = s.bytes ∧ (toDirect s).ranges = s.ranges := ⟨rfl, rfl⟩

theorem alias_preserves_custom_aggregate (s : Retained) (origin : Nat) :
    (alias (publish s) origin).tainted = s.aggregate := rfl

theorem append_direct_ranges (s : Retained) (c : Chunk) (url : Span) :
    directBlocked (append s c) url =
      (directBlocked s url || blocked (emitted s c) url) := by
  exact append_taints s.ranges (emitted s c) url

theorem earlier_url_unchanged (s : Retained) (c : Chunk) (url : Span)
    (earlier : url.finish ≤ s.bytes.length) :
    directBlocked (append s c) url = directBlocked s url := by
  rw [append_direct_ranges]
  have noNew : blocked (emitted s c) url = false := by
    unfold emitted
    split
    · rfl
    · split
      · have disjoint : overlaps ⟨start s c, start s c + c.bytes.length⟩ url = false := by
          rw [symmetry]
          apply separated
          simp only [start]
          omega
        simp [blocked, disjoint]
      · rfl
  simp [noNew]

theorem interior_new_url_blocked (s : Retained) (c : Chunk) (url : Span)
    (nonempty : c.bytes.isEmpty = false) (tainted : c.tainted = true)
    (lower : start s c ≤ url.start) (upper : url.finish ≤ start s c + c.bytes.length)
    (width : url.start < url.finish) : directBlocked (append s c) url = true := by
  rw [append_direct_ranges]
  have overlap := contained_nonempty ⟨start s c, start s c + c.bytes.length⟩ url lower upper width
  simp [emitted, nonempty, tainted, blocked, overlap]

theorem successful_push_exact (limit : Nat) (s : Retained) (c : Chunk) (out : Retained)
    (success : push limit s c = some out) : out = append s c := by
  unfold push at success
  split at success
  · exact Option.some.inj success.symm
  · contradiction

theorem successful_push_sound (limit : Nat) (s : Retained) (c : Chunk) (out : Retained)
    (sound : Sound s) (success : push limit s c = some out) : Sound out := by
  rw [successful_push_exact limit s c out success]
  exact append_sound s c sound

def emptyDirty : Chunk := ⟨[], [], true, 1⟩
def literal : Chunk := ⟨[102, 111, 111], [], false, 2⟩
def cleanWitness := run initial [literal]
def dirtyWitness := run initial [emptyDirty, literal]

theorem equal_bytes_ranges_different_provenance :
    toDirect cleanWitness = toDirect dirtyWitness ∧
    (publish cleanWitness).tainted = false ∧ (publish dirtyWitness).tainted = true := by decide

theorem no_reconstruction_from_bytes_and_ranges :
    ¬∃ recover : Direct → Bool, ∀ chunks,
      recover (toDirect (run initial chunks)) = (publish (run initial chunks)).tainted := by
  rintro ⟨recover, all⟩
  have clean := all [literal]
  have dirty := all [emptyDirty, literal]
  change recover (toDirect cleanWitness) = false at clean
  change recover (toDirect dirtyWitness) = true at dirty
  rw [equal_bytes_ranges_different_provenance.1] at clean
  rw [clean] at dirty
  contradiction

theorem old_reconstruction_loses_empty :
    (oldPublish dirtyWitness).tainted = false ∧ (publish dirtyWitness).tainted = true := by decide

theorem direct_literal_remains_unblocked :
    directBlocked dirtyWitness ⟨0, 3⟩ = false := by decide

theorem empty_alias_retains_provenance :
    (publish (run initial [alias (publish (run initial [emptyDirty])) 3, literal])).tainted = true := by decide

end RetainedAggregateTaint
