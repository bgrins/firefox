# Initial trace interpretation: enum and delivery boundaries

**`pseudo=44` is `PseudoStyleType::Before`; `pseudo=95` is `NotPseudo`.** `After=43`, `MAX=96`. The e86 `PseudoStyleType.h` enum expands `PseudoStyleTypeList.h`, then appends `NotPseudo` and `MAX`. `GeneratePseudoStyleTypeList.py` emits `PseudoElementData.all_pseudos()`: stable-sorted anonymous boxes by `inherits`, followed by pseudo-elements in TOML order. Preferences affect flags, not enumeration order. `ENUM.json` retains the five exact e86 source objects and computed ordinal list.

The read-only generated headers at `objdir-full.noindex/layout/style/PseudoStyleTypeList.h` and `dist/include/mozilla/PseudoStyleTypeList.h` agree byte-for-byte: SHA256 `2da6c33daeca769554244944b2418891754db113ecb8cad518ad56ba15007d44`,95 emitted entries,Before at44. A copy is retained. This is a current generated-context cross-check, not a separately archived compiler-input receipt. The saved build RESULT identifies e86, successful compilation, and all five exact instrumentation-v3 candidate source hashes.

Discovery reference: [PseudoStyleType declaration](https://searchfox.org/firefox-main/rev/7a315fc898bbd3e61ba7dd220a8fb1d0721a1eb7/layout/style/PseudoStyleType.h#54). Exact conclusions use the pinned e86 source objects, not an assumed match to indexed tip.

## What the saved WPT actually observed

`raw.jsonl` SHA256 `0075abb630e14771faf7ede4ff6b023ef5cd13b69ba79089bc051fb3e2047fc9` has4733 records. Eight callbacks completed: sixPASS and twoFAIL, oneOK ending. The failures are `existing-child rem keyframes after root em cancellation with none` and `root-pseudo rem keyframes after root em cancellation with none`, both at the first-value assertion64 versus46. Their settled values are not present in these raw failure messages. The script records settled values in a JS array, but that array is not recovered by this analysis. No full34 reproduction or new failure count is claimed.

There are eight distinct root-address/device cohorts with root writes23→32→23, all tagged RustThreadId(4). `TRACE.json` records the exact selected rows and bounded excerpts; row numbers are zero-based positions in the pinned JSONL, not timestamps or source-code citations. These cohort ordinals follow fixture case order plausibly, but there are no per-case trace markers or getter events. The fixture's promise-test ordering and unique addresses are useful inference, not a direct case-name/DOM-address join. Other browser activity is interleaved.

| Cohort | Root/device | Concrete saved sequence |
|---|---|---|
|1|`0x10ed08bb0` / `0x105d79820`|Root restores23 in AnimationOnly at3618; ancestor-font hint propagates and descendants log animation-only-skip; normal pre-traverse3641 declines entry with hint0,dirtyfalse,animation_dirtytrue.|
|5|`0x10ed2dae0` / `0x10fa11820`|Analogous restore23 at4226 and normal pre-traverse4248 declines entry. This is a separate cohort, not merged with1 merely because the expected failing value is the same.|
|3|`0x10ed0b430` / `0x105d87820`|A contrasting normal traversal enters at3937. Child `0x10ed0baf0` has member_operand=true at3951, queues task0x4 at3952, normalizes to itself/pseudo95/task4 at3954, and reaches the same non-null EffectSet/effect UpdateProperties entry and return at3955–3957.|

These observations make missing normal-traversal entry worth testing before instrumenting arithmetic. They do not prove that any particular keyframe conversion read32, that the logged restore23 preceded that conversion, or that a missed UpdateProperties call caused the failing first getter. Cohort3 also has an initial task0xc/delivery during AnimationOnly, consistent with the early-return guard applying only when an old style exists; AnimationOnly is not an unconditional ban on every update task.

The nine observed pseudo44 normalization records use other address cohorts, such as input`0x3158bc3d0`→host`0x3158a3670`, rather than the eight23→32→23 root/device addresses. They are not evidence that the failing root::before received an update. For pseudo attribution, require a normalization record joining the actual Rust input node to the expected host and44, then the same host/pseudo/style delivery record; do not infer it from44 alone. No global absence of pseudo updates is proved by this bounded projection.

## Exact marker meanings

`root-write` is emitted after the existing Device setter with its existing argument; it records a publication attempt/value, not a later consumer read. `root-hint` records accumulated child hints before later traversal-specific handling. `propagate` records returned/combined hints, not proof of normal scheduling. `child-decision` records the existing traversal predicate and stored hint at that boundary.

`admission.member_operand` is the cached complete short-circuit expression: normal traversal, relevant hint, and animation membership. False during AnimationOnly does not mean no animation or EffectSet. `kind` reports the resulting restyle-kind decision. `animation-only-skip` means the existing early-return branch with old style was taken. `animation-task` is queued work, not delivery; tasks0x4 is EffectProperties and0xc includes that bit.

`normalize` joins an existing input node to its normalized host/pseudo and reports the numeric mask and style pointer. A null style or absent EffectProperties bit would not establish property delivery. `delivery` occurs after the existing EffectSet lookup; null means that call returned before iterating effects. `deliver-effect`/`delivered-effect` bracket UpdateProperties, but do not reveal computed endpoints or final installed animation values. Rust hexadecimal masks and C++ decimal masks must be compared numerically.

Opaque pointers may be reused across documents or processes. Rust thread IDs are not OS/process-global IDs; C++ main=1 is not a unique thread identity. The WPT process-output envelope names the launching browser process and is not proof of which child produced every stderr line. Mixed Rust/C++ output and collector timestamps provide no global happens-before relation. The short same-target task/normalization/delivery runs above are candidate joins, bounded by these limitations.

Next: execute the unchanged34 diagnostic on the verified trace archive and require the same behavioral failures under logging. If episode identity is ambiguous, use the already prepared one-case scripts separately; do not add getters, flushes or markers to the histories. Only then use the missing-normal-entry versus delivered-with-stale-input distinction to guide a targeted next instrument. No source change, browser execution, audit acceptance or new cause claim was made here.
