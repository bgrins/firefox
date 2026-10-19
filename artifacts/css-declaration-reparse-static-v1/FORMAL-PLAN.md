# Proposed declaration component validation contract

This is a follow-up design, not an implemented proof.

## Independent specification

Use finite recursive CSS component values: ordinary atom, function with a name
and child sequence, and simple block with a delimiter kind and child sequence.
Whitespace/comments are represented explicitly in the lexical-to-component
bridge and erased only for significant-component classification. Define normal
declaration structural validity independently as: no top-level curly block, or
exactly one significant top-level component which is that curly block. Custom
properties bypass this normal-property restriction. Function interiors never
count as top-level blocks.

Define an associative summary for concatenation: significant component count
saturated at two, and existence of a top-level curly block. Prove summary
composition, scan invariant for every prefix, and equivalence to the declarative
predicate for arbitrary finite recursive inputs. This provides a reusable
full-list contract and a small real counterexample to suffix-only validation.

## Native-shaped control flow

Model the property callback as a transition with success/error, consumed
prefix, pending block, tracker state and scratch declarations. The callback may
consume the entire current item on error. Derive whole-value validation after
reset for every admitted cursor; do not assume failure leaves the invalid token
unconsumed. Include whitespace-only and empty input, curly-only, repeated curly,
curly in functions/square blocks, and arbitrary component prefixes/suffixes.

Separate the observer's current enabled/seen state from a saved positive query
result. Reuse or explicitly authenticate the separate cache epoch contract:
reset restores parser state but does not erase seen-function history; a prior
positive query can disable tracking without losing the saved fact. Fresh/colon
entry and cache admission are premises until linked to complete source callers.

Prove publication follows structural validation plus successful arbitrary-value
parsing. A callback's ordinary successful parse needs the explicit premise that
its accepted property grammar satisfies declaration structure; this premise is
not replaced by a proof that arbitrary callbacks are valid. The unchanged fast
success path follows under that premise. Empty/custom/wide keyword paths and
malformed important suffixes must retain their separate contracts.

## Native bridge and costs

Keep the full helper, complete cssparser reset/next/block-skip/parse_until and
comma parser. Extend the current adapter witness with complete FontFamily and
SingleFontFamily parsing plus explicit atom/generic-family providers, or compile
the whole Style crate. Include actual VariableValue scanning and its rejecting
paths before claiming complete declaration acceptance. The current accepting
VariableValue adapter proves only that the fallback gateway is reached.

For universal byte/native claims, connect tokenization and parser cursor/pending
state to the recursive component projection, including EOF, mismatched closing
tokens, nesting limit, delimiters and observer cache behavior. Existing token
and recovery proofs can be composed only with explicit provider correspondence.
This is the expensive obligation; finite native rows do not discharge it.

Useful compiled mutants: omit reset, reset only on failed callback, discard the
saved successful observation, reject all curly blocks, permit repeated curly
blocks, or descend into inner blocks when counting top-level curly components.
Each needs an executed witness; the successful-callback mutation may require a
contract-level callback fixture clearly separated from a production-property
reachability claim. Pair Lean counterexamples with the same distinctions.

Preserve root's browser cases plus invalid important/trailing-token controls.
Assess linear rescan cost on fallback/error paths separately from ordinary
success, with measured costs labelled as finite benchmarks. No theorem of CSS
substitution evaluation or the complete C++/Rust compiler is implied.
