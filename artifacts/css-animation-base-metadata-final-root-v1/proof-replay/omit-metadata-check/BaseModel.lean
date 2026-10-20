import EndpointModel
namespace BaseMetadata
open EndpointTaint
abbrev Entry (K P : Type) := K × Endpoint P
abbrev Lookup (K P : Type) := K → Endpoint P

def oldChanged (cmp : P → P → Bool) (old : Lookup K P) (entries : List (Entry K P)) : Bool :=
  entries.any fun entry => !endpointSame cmp entry.2 (old entry.1)

def metaChanged (custom : K → Bool) (old : Lookup K P) (entries : List (Entry K P)) : Bool :=
  entries.any fun entry => custom entry.1 && !(tainted entry.2 == tainted (old entry.1))

def entryChanged (cmp : P → P → Bool) (custom : K → Bool) (old : Lookup K P)
    (entry : Entry K P) : Bool :=
  !endpointSame cmp entry.2 (old entry.1)

def changed (cmp : P → P → Bool) (custom : K → Bool)
    (old : Lookup K P) (entries : List (Entry K P)) : Bool :=
  entries.any (entryChanged cmp custom old)

def baseFlag (target compare : Bool) (delta : Bool) : Bool := target && compare && delta

def requestsRestyle (propertiesChanged target delta : Bool) : Bool :=
  propertiesChanged || baseFlag target (!propertiesChanged) delta

structure SampleState (P : Type) where
  base : Endpoint P
  sampled : Endpoint P

-- A deliberately small synchronous scheduling model, not Gecko's scheduler.
def tick (notify force : Bool) (published : Endpoint P) (state : SampleState P) : SampleState P :=
  ⟨published, if notify || force then published else state.sampled⟩

end BaseMetadata
