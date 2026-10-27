# Non-type attribute contents must not create substitution cycles

Concrete artifact-only proposal, pending compilation and browser comparison. The native change removes the parent-Attr exception from visit_value_references: only type() attribute reads traverse their contents. All non-type occurrences use the prior fix's actual-primary classifier and retain traversal of a used fallback. The now-unused parent-node parameter and its two call arguments are removed.

The three-path patch contains cascade.rs, two explicit oracle corrections in the existing attr-cycle.html, and the new attr-raw-nested-cycle.html. The used-fallback helper itself is unchanged. ORACLE-ADJUDICATION.md explains both expectation corrections; they are not silent metadata changes.

## Dependency and transport

This patch depends on css-attr-non-type-fallback-repair-v3's non_type_primary_is_valid helper and used-fallback traversal. Its base is that proposal's reviewed candidate-live cascade, not the active live tree. The v3 helper uses direct ParsedNamespace matching. BASE.json pins its exact source and the corresponding candidate-head helper. Applying this raw patch without that prerequisite is not supported.

A candidate-head equivalent is supplied to establish that no typed-demand prototype change belongs to this fix. verify_transport.py applies the exact same fix.patch to fresh copies of both used-fallback bases, checks exact postimages and three-file inventory, reverses to exact preimages, and reapplies. Scratch directories are removed. It never targets the live checkout or index.

```sh
python3 -I -S -B artifacts/css-attr-raw-nested-repair-v1/verify_transport.py
```

## Tests and confidence

The new fixture has 29 tests: 26 fixed cases and three mutation sequences. Its first 13 data rows are identical to the earlier release/local raw probe (five observed disagreements, eight passing controls). Added coverage includes the earlier existing-WPT oracle, genuine typed mutual cycles, used raw/unit fallbacks reaching typed or property cycles, present empty raw values, namespace separation/aliases/unknown outer prefixes, and mutations switching between raw reads and typed cycles or selected fallbacks.

Namespace coverage uses a known namespaced outer attr() with null-namespace inner reads. It deliberately does not assume support for namespace prefixes interpreted inside typed attribute text, the separate existing bug 2021110 limitation. Raw strings containing prefix text stay opaque.

The native change also corrects the same distinction for primitive numeric reads inside typed attribute text. Those new cases have spec-derived predictions but have not yet been observed independently; no separate bug count is claimed. Actual typed cycles and used-fallback edges must continue working.

Confidence is high in the two raw oracle traces and the targeted removal of false edges, supported by the current spec, independent root review, prior release/branch observations and guard-model laws. Confidence in full native behavior remains conditional on the proposed comparison: no Rust type check, candidate browser run, namespace/mutation run or native refinement proof has occurred. Static Rust parsing, JavaScript syntax and exact transport are the present implementation checks.

## Acceptance gates

First complete the separate used-fallback comparison. Then run the corrected attr-cycle fixture and the new fixture on both the used-fallback baseline and raw candidate; require all new assertions to pass and exactly the documented old-oracle changes. Preserve the 34-test used-fallback fixture, numeric-token, typed-preparation/eligibility, namespace-cache/namespace variants, non-custom-cycle, all-types, no-type-fallback and existing order regressions. Retain the root's native demand-resolver regression gates as applicable. No unexplained regression may be hidden by changing expected metadata.

Only the native file and WPT files belong in the eventual standalone fix commit, after its used-fallback prerequisite. This package's snapshots, trace, model discussion and verifier are research material. No browser/build, canonical Lean edit, live source/WPT/runtime edit, index/HEAD mutation or commit was performed by this proposal.
