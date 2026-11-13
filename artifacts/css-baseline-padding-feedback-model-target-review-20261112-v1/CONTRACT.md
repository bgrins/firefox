# Baseline padding across cached reflows

Draft ten-clause target, awaiting independent review and definition compilation.
No proof or native correctness is claimed.

This model isolates one padding side after acquisition and baseline side selection.
`raw` is the acquired padding before that side's baseline contribution;
`adjustment` is the contribution; `used` is the cached result. A parent event
replaces all three values. A child event represents the non-root PresShell path
supplying that already-adjusted cache back to initialization. The old transition
adds the contribution again; the proposed transition preserves the used value.

The invariant is a separate equation relating cached output to its two sources.
The target quantifies over arbitrary finite parent/child histories and arbitrary
integer values; it does not presume that an input history is already correct.
Only the initial state must satisfy the invariant. Separate obligations quantify
over arbitrary initial states to characterize repeated child events and parent
reset independence. Concrete nonzero and zero-adjustment witnesses are included.

The browser probe reports 18px repeated movement with author padding 3px. The
numeric witness models that padding contribution; the additional 2px border is
outside this scalar model. It does not model DOM measurement or establish that
the old browser executes these transitions. Browser evidence is retained in
`../css-grid-baseline-padding-reflow-probe-20261112-v1` and the repair capsule.

Native correspondence remains separate: acquisition precedence (theme, SVG,
explicit override, style), both axis suppression flags, property lifetime,
frame-state bookkeeping, parent baseline recalculation and representability
must be checked against the actual source. Integers here have no overflow. This
model does not resolve the separate dynamic peer-font discrepancy or the wider
padding/border overflow work. A parent event describes correct cache replacement;
the implementation's ability to realize it is not assumed proved.
