# Candidate replay

The root applied the exact `proposed-dispatch.rs` helper. On 18 October 2026,
the producer reran the unchanged Lean gate against that live helper:

- Process 46648 reached exit 0: twelve theorem audits, four separately compiled
  mutations, thirteen record guards, `live_candidate_verified: true`.
- Process 86926 reached exit 0: two accepted source fixtures and ten rejected
  source tamper/downgrade controls, plus the live candidate check.
- Complete live `calc.rs` SHA-256 during both gates was
  `f20421f8015d55ff6b3fb090961e3a9e29cf6508163becbfc7d5f7cee259d49d`.
- Input hashes were unchanged across each gate. The 31 pins in the preparatory
  `PROOF-v1.json` still match; the separate `PROOF-v2.json` records this replay.

The model, theorem statements, finite arithmetic premise, and formula category
premise have not changed. Candidate acceptance means the live Rust helper
matches the manually reviewed native-shaped dispatch. It does not prove finite
IEEE arithmetic, extraction from Rust, browser behavior, or WPT outcomes.

## Source controls

`source_controls.py` copies the source snippets and authenticated specification
excerpts into isolated fixtures under its new output directory. It calls the
same `source_binding` function used by the proof gate. The old helper must be
classified as old, and the proposed helper as candidate. Candidate-mode checks
reject downgrading to the old helper, removing the finite-dividend guard,
returning zero instead of the dividend, and applying the sign exception to rem.
They also reject missing/duplicate helpers, either changed source snapshot,
and either changed specification excerpt.

These are drift and classification guards. Exact source matching does not
itself establish semantic correspondence; that bridge remains the review in
`REVIEW.md`. Fixture checks modify no production source.

## Independent replay and commit ordering

```
python3 artifacts/css-mod-rem-infinity-proof-v1/check.py /tmp/mod-rem-root-new
python3 artifacts/css-mod-rem-infinity-proof-v1/source_controls.py /tmp/mod-rem-source-root-new
```

`check.py` deliberately accepts either authenticated helper, recording which
one is live. Thus the source-only companion remains usable before the native
fix commit. This was executed against the real old helper in the preserved
preparatory gate and is additionally exercised by the old-helper fixture.
`source_controls.py` is a candidate-only follow-up and requires the patched
helper. It is not a prerequisite for using the preceding companion commit.

`tooling-paths-v2.txt` lists the thirteen proposed companion sources. Generated
proof objects, fixture directories, logs, capsules, and browser/WPT evidence
are excluded. Root still owns independent proof review, browser validation,
the production/WPT commit, and the commit index.
