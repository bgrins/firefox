# Shorthand cache provenance contract

This proof follows static source analysis and a browser reproduction. It did not
find the original partial `revert-layer` bug independently. It establishes a
bounded cache contract and tests that both native provenance guards are necessary.

## Independent semantics and theorem

The reference selects the first eligible declaration separately for each physical
side, then expands that declaration. It never consults a cache. A candidate scan
is any finite ordered list of declaration/side/eligibility records. This makes
rollback selection explicit input; the model does not prove the cascade computes
those eligibility bits correctly.

The source-shaped evaluator scans candidates in order, skips ineligible and
already-set sides, and consults a direct-mapped cache keyed by shorthand and side.
Each cache entry contains the retained declaration identity and a value. Both
initial lookup and lookup after population require identity equality. On a miss,
expansion populates every available side. Omitted sides leave older entries in
place, so the second check is necessary.

`CacheSound` records that each cached value belongs to the meaning of its tagged
source. `populate_sound` proves preservation; `lookup_sound` proves hit provenance;
`populated_lookup` proves post-population lookup equals the current source's
expansion even for omitted sides. `scan_refinement` uses induction over arbitrary
finite scans and arbitrary sound initial caches/partial outputs to prove agreement
with independent selection. `fresh_scan_refinement` specializes to an empty cache.

Two kernel-evaluated witnesses accompany the induction. The partial rollback
witness selects high-source margins 10/20/10 and low-source left 40. The old cache
returns left 20; the guarded cache returns 40. The omitted-entry witness retains
high-source left 20 in a reused bucket after the low source omits that side. A
post-parse unchecked lookup returns 20; the guarded lookup returns no value.

## Native bridge and assumptions

The reviewed native implementation stores an owning `Arc<UnparsedValue>` beside
each declaration and compares with `Arc::ptr_eq`. Retention prevents pointer reuse
while an entry exists. `Declaration.identity` represents that allocation identity,
not source text, payload hash, shorthand kind, layer, or current longhand.

The explicit `Admitted` premise requires every declaration sharing an identity to
have the same optional expansion under one fixed environment throughout the scan.
`Meaning` is the interpretation of those stable source identities. The model does
not prove the lifetime behavior of Arc, immutability of native values, or that all
parse/substitution-affecting native context remains compatible across cache use.
A later audit must check those conditions separately if cache lifetime expands.

`Environment`, payloads, shorthand IDs, and expansion are abstract. The model has
four physical sides and integer values, with `none` representing an omitted or
invalid value. Outputs distinguish an unprocessed side from a processed missing
value. Native invalid-at-computed-value-time defaulting is outside this model.

Logical-to-physical alias insertion, parser correctness, variable substitution,
CSS-wide keyword handling, attr taint, conditionals, animation, origins, computed
font state, and dynamic environment changes are not proved. An abstract eligible
scan can represent their already-resolved outcome; that does not verify those
native subsystems. There is no extracted Rust semantics, general Stylo refinement,
or complete CSS conformance claim.

## Gate

Run `python3 artifacts/css-shorthand-cache-proof-v1/check.py /tmp/new-cache-proof`
with a nonexistent output directory. It uses a fresh directory and fresh Lean
invocation, checks all eight exact axiom audits, and compiles three mutations:
remove the first source check, remove the second, and store the wrong identity.
Failures must occur in the intended theorem bodies with the exact diagnostic
inventory; syntax errors, unknown symbols, and arbitrary tool failures do not count.
Validator-corruption controls test that rejection policy.

The source guard binds the full changed native file, old snapshot, exact reviewed
cache/method snippets, Lean binary, and proof inputs. It rejects drift and altered
bridge snippets. This is an authenticated manual correspondence, not automatic
extraction or a proof of Rust/Arc semantics. Toolchain library closure is not pinned.

The discovery full-key model and initial deprecated-tactic diagnostics are retained
as history and excluded from accepted evidence. The final model represents the
actual tagged direct-mapped design.
