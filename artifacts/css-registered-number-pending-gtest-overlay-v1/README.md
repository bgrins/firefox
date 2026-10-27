# Pending registered-number regression overlay

This one-file GTest overlay validates the unaccepted pending-demand prototype together with the live registered-number preparation/collector proposal. It is separate from the standalone committed-HEAD native fix and WPT. Do not apply or compile it during the clean-HEAD comparison.

The base `TestKeyframePresentation.cpp` comes from `css-registered-number-native-runtime-v1/prototype-original`, not the currently restored tracked checkout. Its hash matches both the restoration plan and the source pins preserved by signing checkpoint v8. The preserved glue/build integration and the actual unchanged untracked Rust GTest bridge sources are likewise authenticated. `SOURCE-PINS.json` records all 17 relevant bodies; `REFERENCES.json` binds their signed checkpoint, the restoration plan and the native proposals.

The overlay appends two tests to the existing fixture and leaves its original prefix byte-identical. It changes no Rust bridge, binding, build manifest or production source. The existing test-only endpoint resolver supplies status, demanded name, returned value and attribute-tracking status. That API is why these assertions belong in native GTests: WPT cannot observe a pending provider or prioritary demand directly. Web-facing correctness remains covered by the separate WPT proposal.

`RegisteredNumberAdmissionDemand` runs nine labeled rows while font-size is pending. The registered non-inheriting number has the existing fixture's initial value 10:

| Row | Required result |
| --- | --- |
| Invalid direct `1em` | Resolved initial 10, no demand |
| Missing provider selects invalid `1em` | Resolved initial 10, no demand |
| Ready primary 5, unused `1em` fallback | Resolved 5, no demand |
| Ready wrong-type primary, unused `1em` fallback | Resolved initial 10, no demand |
| Nested missing/ready fallback | Resolved 5, no demand |
| Ready primary with unused admitted length-ratio fallback | Resolved 5, no demand |
| Pending provider whose stored value is ready | Provider demand, no returned value; no fallback or font-demand substitution |
| Substituted `inherit` on a non-inheriting registration | Resolved parent's 17, no demand |
| Substituted `initial` | Resolved initial 10, no demand |

`RegisteredNumberMathDemandCompletion` retains one `calc(1em / 1px)` endpoint after releasing its source keyframe arrays. With font-size pending it must demand `font-size` and return no value. After that demand is removed, the same endpoint resolves to 20; after changing the target's font it resolves to 30. Both completion calls retain an unrelated pending provider, forcing the pending resolver instead of its empty-pending ordinary-path shortcut. The original captured animation value must still serialize to 20 after mutation.

Every new resolution checks that the attribute flag is false. The CSS-wide inheritance row checks value behavior only. `INHERITS_RESET_STYLE` is not exposed by this bridge: the resolver consumes its local computed context and returns an animation value. No claim is made that this internal effect flag has been observed. Adding a dedicated effect-observation API would be separate work; the proposal's static CSS-wide preservation check remains the current evidence for that effect.

`ROSTER.json` derives the original 20 and candidate 22 GTest names from the captured two C++ test files. It preserves all original 22 pending-demand table rows, adds nine table rows and three math calls, for an expected 34 pending bridge calls if all tests reach completion. These are expected source counts, not executed counts. The runtime's exact-name acceptance gate must add the two new names rather than reuse the old 20-name roster.

Validation in this artifact is limited to authenticated captures, appended-only source preservation, exact patch apply/reverse/reapply in owned scratch, roster checks and formatting of the new lines. A working Mozilla clang-format was used after the PATH entry proved to be a Chromium wrapper without a checkout. No C++ compile, GTest, browser, Mach command, source epoch or live native mutation occurred. Read-tool metadata exposed no dedicated Read tool; scoped Python reads were used for `layout/AGENTS.md` and the required layout documentation.

Before execution, restore the full preserved prototype, install the live native preparation/collector candidate, then apply this test overlay and build GTests. Keep the ordinary HEAD+WPT acceptance separate. Use the existing controlled GTest execution machinery with the candidate 22-name roster, inspect every terminal status, and preserve raw logs. A failed setup or early assertion does not constitute completion of the remaining table rows or resolver calls.

Run `python3 -I -S -B artifacts/css-registered-number-pending-gtest-overlay-v1/check.py` to repeat the artifact-only transport and roster checks. It removes its temporary directory. It does not compile or launch Firefox.
