# Wrapped flex line cross-size sum discovery

The existing baseline-maxima review exposed a separate outer accumulation witness. The old DoFlexLayout initializes the gap sum with a size_t product narrowed to nscoord, then adds each line size in signed32. Neither expression caps a large result before ComputeCrossSize applies the container maximum.

A private-profile 40-case probe gives identical installed-release and shared-development observations. Eleven supported-input cases produce zero height instead of 100px; all fixed-height controls are 100px and all auto-size restorations are stable. Three plain 12,000,000px lines suffice without baseline alignment, margins or descendants. Four 20px lines separated by 12,000,000px gaps expose the initial product independently. The phase named candidate is pre-repair discovery, not fixed behavior.

The Flexbox cross-axis algorithm sums line cross sizes for a content-based container cross size, and the containing formatting context applies its min/max constraints. Gaps contribute fixed inter-line spacing. The bounded 100px result is the observer; CSS Values does not require all engines to support the huge inputs. Primary sources are retained in spec/; new WPT cases therefore admit the numeric range explicitly before the unconditional final-size assertion.

Eleven fresh Lean audits prove an arbitrary-list capped accumulation identity, initial/step machine bounds, exact identity within nscoord_MAX, and preservation of a bounded min/max observer. The two signed32 bound witnesses and the capped 100px observer are kernel checked. These primitive results do not certify gap providers, all optional min/max branches, other layout arithmetic, C++ compilation, or browser reachability beyond the retained probes. The reviewed earlier baseline-group sum repair is separate and remains necessary for its own cases.

Searchfox and exact HEAD-equals-live snapshots bind the uint32 array length, gap resolver and min/max observer. GenerateFlexLines supplies an initial line, so count minus one has no empty-list underflow. The array-length return type is size_t but its backing field is uint32. Optional min/max and aspect-ratio branches require separate source review; absent maximum intentionally exposes supported-range saturation above nscoord_MAX rather than universal old-defined identity.

The existing webspec-index command remains unavailable; primary source retrieval was used. No Firefox production source was changed by the discovery probe. All disposable browser profiles were removed by the runner.
