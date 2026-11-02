# Native diagnostic confirms the missing size-readiness action

The diagnostic candidate builds successfully, then crashes on the unchanged typed-attribute page before reporting any of its four callbacks. The 23 captured `CSS_METRIC_PENDING` process-output records identify the retained state:

- Root `Custom(len)`, node 0, phase Publish, flags 1 (`FONT_UNITS`), one completed unit link, no waiting reference.
- `ComputationPending(0)`, no metric action, progress `not-driven`.
- Empty semantic stack; node 1 is Complete while node 0 remains computation-pending.
- Appearance is ensured, dynamic, and uncertified. FontFamily, XTextScale and FontSize are ensured and non-dynamic, but uncertified in both completion sets. Their other logged generated prerequisites are complete.

This confirms the sealed extracted witness's no-action computed-size route in this native diagnostic run: the missing Appearance completion propagates through FontFamily and text scaling to FontSize, and `font_publication_demand` cannot provide an action when size completion is absent. The root has already closed its semantic component; this is not a logged semantic-cycle result. No claimed-Weight or LineHeight action appears in this snapshot. The separately established LineHeight reentry issue is not the explanation recorded here.

The native logger does not record actual computed Appearance, FontFamily or FontSize values, the selected declaration text, or the DOM element identity. It therefore does not establish which numerical value was published or whether an attribute fallback was used. The source has a conservative dynamic-declaration predicate, not a certificate of successful selected evaluation. Treating ensured as complete or deleting that predicate is not a supported repair. The next missing producer must resolve and certify the actual selected prerequisite while preserving ownership and finality.

The build binds cascade `b85af8e8b5ab6ee9f3b76ea7d87742b5b791f088a9dbeb494d38783b48db4e4a`, provider `90acb505`, BuildID `20261102131931`, and HEAD `70d9abdf9784cf84732aed747cbec87fe0589d95`. This is diagnostic-only v2, without the ordinary-ownership successor. Its XUL hash is `122af7faf12071c57272e1d7ed13bfaee28c85037422e536b01f68a8ab9d2877`.

Saved replay `d0019d/0` independently joins the new build, application metadata, binaries, source roles, consumed inputs, staged resources, genuine manifests, saved pre/post snapshots, raw assessment and comparison. The unchanged fixture has no added pref or expected-FAIL metadata; standard harness profiles remain in use. The comparator's original is explicitly the historical 3 PASS/1 FAIL/1 OK result from the earlier paired runtime, not a fresh original build in this run. Candidate observations are zero callbacks and one CRASH ending, with an incomplete assessment and false observation gate. No candidate aggregate exists.

Owner terminal `31469 / 7d42b5 / d0cca4`, exit 1, binds RESULT `17b2a79f121bdbfe9fcf873ab5e159090c7e17c9ee410414d1abc78c8892206b`. The owner reports restoration verified and no publication errors. Root's independent live restoration/backup audit is separate and is not claimed here. The unsuccessful top-level result has an empty phase aggregate; the incomplete lane's raw data remains available.

This is useful native correspondence evidence, not a repair, normative verdict, new release-bug classification, or browser acceptance. `OBSERVATIONS.json` retains all 23 diagnostic events and the build/terminal identities; REFERENCES.json pins 45 completed regular files. The first review replay invocation was rejected by the required Python isolation guard (`5dd159/1`); its `-I -S -B` retry passed. No live runtime or native files were changed by this review.
