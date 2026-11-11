# Text-transform browser differential preparation

Open `probe.html` in an ordinary browser tab, optionally enter the build identity, click Run, and save JSON. The page is self-contained and makes no network requests. It uses detached style declarations and performs no rendering/layout queries. It is research tooling, not a Firefox product UI.

Then validate the saved observation:

```sh
python3 -I -B artifacts/css-text-transform-browser-probe-20261110-v1/analyze.py /path/to/text-transform-observations.json
```

Exit 0 means MATCH; exit 1 means MISMATCH or SETUP_FAILED; exit 2 means malformed/incomplete capture. A mismatch is an investigation candidate, not an automatic specification violation. Retain browser/version/build/preferences separately; the page records exposed user-agent fields and an optional supplied label but cannot authenticate the browser binary or preference state.

The corpus is exactly all 1,555 sequences of length zero through four over `none`, `capitalize`, `uppercase`, `lowercase`, `full-width`, `full-size-kana`. Its expected membership comes from the independently frozen 38-sequence oracle, not either browser API. It matches the first 1,555 cases of the accepted Lean milestone. The formal theorem covers arbitrary normalized-token input; this browser experiment is bounded and observes concrete API behavior only.

Both CSS.supports and a fresh CSSStyleDeclaration are checked per row. Empty input has a separate seeded-removal observation and is never counted as a supported grammar value. Four setup controls check accepted singles, invalid assignment preservation and empty removal. Observed serializations are retained without asserting ordering. The page's quick difference count is provisional; `analyze.py` performs the strict identity/schema/setup checks.

`inputs` copies the frozen oracle, source manifest, fixture, correspondence laws, extraction map and source metadata. `ORIGINS.json` pins the complete CSS Text 3 source and exact contextual excerpt plus the original paths/hashes. This capsule relies on the separately reviewed Lean milestone; it does not rerun Lean or claim independent model proof. The spec source was pinned at CSS Text 3 revision e2a76bde01e77f714a8f22e9866d8c636b482a6f. No later-level keywords, CSS-wide values, var(), escapes/case folding, arbitrary whitespace or full raw CSS tokenization are covered.

Run `python3 -I -B .../check.py` for source preparation checks. It reconstructs the exhaustive corpus and self-contained page, checks provenance hashes and JavaScript syntax, and uses an explicitly fake Node collector to exercise row collection/analyzer behavior. Reversed mock serialization is deliberately accepted; overacceptance, broken empty removal and malformed captures are detected. These checks do not execute a browser or establish parser agreement. No browser observation is included in this preparation capsule.
