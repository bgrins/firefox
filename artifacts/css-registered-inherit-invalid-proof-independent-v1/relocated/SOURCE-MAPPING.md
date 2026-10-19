# Source correspondence ledger

`SOURCE-BINDINGS.json` retains twelve complete definition records, with complete-file hashes authenticated by the capsule. The extraction uses exact indentation-delimited Rust method definitions, not a general Rust parser; these definitions were read in full. A brace-count check is supplementary, not the basis of semantic translation. The checker reextracts and compares all complete bodies before kernel work.

| Native stage | Selected model | Admission |
| --- | --- | --- |
| Cascade::init_custom_properties | seed / Ready first conjunct | Reset map comes from computed initial cache; nonroot inherited map comes from parent; root inherited map from initial. Full map preparation/scheduler is not proved. |
| Cascade::value_may_affect_style, CSSWideKeyword::Inherit | gate false / gate true | Source first skips inherited properties; if selected current value is absent it proceeds. Otherwise original skips absent reset parent, candidate skips root. Other declaration kinds and all outer caller filters excluded. |
| Cascade::cascade_custom_property, Inherit branch | update false / update true | Actual source sets INHERITS_RESET_STYLE, reads parent non_inherited, clones Some, then inserts. Candidate additionally removes on None. Clones preserve abstract Value, including taint/URL fields; compiler/map-provider correctness admitted. |
| ComputedCustomProperties::{get,insert,remove,map_mut} | values indexed by inherited Bool; selected; put | True is inherited bucket, false is reset bucket. None abstracts getter absence including guaranteed-invalid tombstones; physical persistent-map/COW implementation is outside model. |
| ComputedSubstitutionFunctions::{insert_var,remove_var} | put | Only custom properties are forwarded to the selected bucket. Attributes and unrelated state are part of the frame/preservation admission. |
| add_flags(INHERITS_RESET_STYLE) | setting one Bool; arbitrary otherFlags unchanged | Bitwise flag API is represented by its intended OR semantics, not independently proved. Existing true bit is never cleared. |
| Root inherited-style representation | Ready second conjunct | Actual root-parent reset getter is None; this is required for root/no-initial branch, not inferred solely from the initial seed. |

No native arithmetic/index operations occur in this selected projection. Actual container capacity, key/atom identity, clone/allocation normal completion, compiler execution and caller root/registration coherence remain admitted. The proof imposes DecidableEq only on keys, never abstract payload equality; NaN payload equality is not assumed.

The independent expected value is defined before the gate/update code: root selects the computed registration initial; nonroot selects the actual parent map using the registration bucket. Its correctness theorem is not stated as equality between two copies of the implementation gate.

Root candidate snapshot SHA256 7cf543c5f258c577568df72b892dd0a39e97578b59390752e8c63a77ee501a8c matches this exact proposed full cascade.rs. The one-file native.patch is the source delta, while root's separate final patch adds the corrected twelve-case WPT. Browser receipts under runtime-context are contextual root evidence, not part of the Lean premises or a new browser execution.
