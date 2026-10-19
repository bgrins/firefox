# Source correspondence ledger

All source snapshots are complete `servo/components/style/custom_properties_map.rs` files. `SOURCE-PINS.json` records the root-provided final formatted identities. `BINDINGS.json` extracts 16 complete definitions from each of original, count-only and combined; the checker independently regenerates those slices. Full `EMPTY`, field/type declarations and constants are retained in each source file.

| Native operation | Model / result | Remaining bridge |
|---|---|---|
| `EMPTY`, `Default::default` | `initial`, `initial_ready` | LazyLock/Arc allocation and publication |
| `Inner::get` | `ownFind`, `lookup`, `tombstone` | IndexMap/atom representation, finite parent graph |
| `Inner::insert` | `ownInsert`, `nativeInsert`, `count_transition` | Native old read precedes own insertion; container mutation and integer interpretation |
| `Inner::should_expand_chain` | `shouldExpand`, `expansion_depth_bound` | Actual ancestor metadata equals modeled depth |
| `CustomPropertiesMap::do_insert` | `doInsert`, `cow_ready`, `cow_lookup` | Arc branch/read/copy behavior; normal completion; sound successful comparator for value semantics |
| `insert` / `remove` | operation with `Some v` / `None` | Caller-supplied payload and name |
| `len` / `is_empty` | stored count / zero predicate | Native field reading |
| `get_index` | `getIndex`, `filtered_count`, bounds and presence theorems | `RawEnumeration` for the actual raw iterator |
| `Iter::next` | retained only; known original/count-only defect | Separate iterator proof and composition required |
| `shrink_to_fit` | logical identity | Container capacity operation preserves data |
| `Inner::eq` | retained context only | Not proved; count equality alone is not map equality |

The checker confirms combined minus the two iterator control-flow labels is byte-identical to count-only. Thus constructor/count/source binding is shared; iterator semantics are not silently imported. The count diff is exact original-to-count-only bytes. No production file is read during replay.

The source matcher locates the named impl and complete method through its own indentation-level closing brace. It validates exact retained text and hashes; it is a structural source binding, not a Rust parser or proof of behavioral equivalence. No native compilation is claimed here.

Four mutations target effective old presence, new presence, missing decrement, and key-presence-versus-value-presence on resurrection. Each mutated Lean definition must compile; its unchanged correct gate must then be kernel-rejected as false. Concrete Rust edit proposals are retained to explain the source correspondence. They are not compiled native mutants and do not establish compiler-level refinement.
