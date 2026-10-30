Uninstalled MinMax guard proposal against accepted pow source b291d6e9.

The existing comparison loop may identify a winner from unresolved relative-length coefficients. Before replacing the MinMax node, the proposal checks every child for an infinite coefficient without a canonical value and defers simplification. A zero font basis can make such an operand NaN; discarding it would lose NaN propagation. The existing explicit-NaN returns remain before this guard.

The candidate is conservative: even cases that would safely retain the infinite operand may stay unsimplified. Specified serialization can therefore change. No runtime algorithm, numeric type, parser or unrelated operator is modified. The current source remains unchanged.

Current branch reproduction is18 callbacks: eight failures and ten passing controls. The companion Lean model explains a sufficient abstract defer condition, not correctness of this full Rust implementation. Compilation, candidate browser comparison and broader regression tests remain pending. No accepted fix ID is assigned.
