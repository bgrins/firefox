# Upstream independence audit and two review variants

The branch repair has one real semantic prerequisite: `499c0c6b72ac4bc0a6396bffa3fa0d71665409ce` (Require a complete number token for attr units). This is stronger than independence from the animation prototype. The current upstream implementation still accepts a numeric prefix and appends a unit to the entire original attribute text; the reviewed branch implementation already has the whole-token correction.

The audit pins upstream `refs/heads/main` to `ff3b300c151f45f09f300284659f24f5d95b0f25` using a read-only `git ls-remote`, then fetches the two exact Rust bodies at that revision. No upstream clone or build was made. The proposed WPT path returned HTTP 404 at the same revision. File hashes and fetch provenance are recorded in SOURCE-PINS.json and EXECUTION.json.

## Dependency distinction

| Component | Pinned upstream | Consequence |
| --- | --- | --- |
| `visit_value_references`, `can_chain`, existing SCC/fallback stack | Present | The used non-type fallback repair can use the existing walker; it does not require importing the branch's whole cascade changes. |
| `AttributeData::parse_typed_value` | Absent | Merely an insertion anchor in the branch patch. This new fix never calls it. The upstream variant creates its own small AttributeData impl instead. |
| `AttributeData::namespace` and namespace-keyed typed-provider cache | Absent | The new classifier uses the existing ParsedNamespace::Known/Unknown field directly. No namespace-cache repair is included. |
| Numeric whitespace/token-slice/exhaustion correction | Absent | A genuine semantic prerequisite of the shared classifier/substituter primitive. The self-contained variant includes its minimal correction explicitly. |
| Attribute-only NonCustom collection without an authored var() | Still skips after preparation | The four added NonCustom cases all contain an authored var() in the attr fallback, so they enter the upstream VAR dependency path. They do not require the separate attr-only collection repair. |

For example, upstream numeric substitution accepts the first token of `5 6` and uses the whole attribute string. A strict whole-token classifier would reject it. Merely importing the classifier without updating substitution would make graph admission and substitution disagree. With a unit and surrounding whitespace, upstream appends the unit to the whole original string instead of the captured numeric token, which likewise differs from the corrected operation. The v2 extra-token and unit-with-whitespace cases detect these distinctions. Dimension-token rejection already exists upstream; it is not part of this prerequisite finding.

## Reviewable artifacts

`upstream-self-contained.patch` is the requested single upstream-compatible review unit: two Rust files and the unchanged 34-test WPT. It adds the used-fallback graph edges and includes the minimal existing whole-number-token correction, shared through exactly one `parse_attr_number` primitive. It uses ParsedNamespace directly and includes no typed parse helper, namespace-cache fix, animation prototype, raw-nested cycle repair or unrelated cascade change.

This variant overlaps the existing numeric bugfix `499c0c6b72ac4bc0a6396bffa3fa0d71665409ce`; it is not a second discovery of that bug. If that prerequisite is absent upstream, the alternative lets a reviewer evaluate the necessary combined native behavior in one patch. It must not be represented as only the incremental delta used in the branch comparison.

`prerequisite-native.patch` is the exact native hunk extracted from that earlier commit. `repair-after-number-fix.patch` is the used-fallback repair adapted to upstream after that native prerequisite. These two patches produce byte-for-byte identical final source and WPT bodies to `upstream-self-contained.patch`. The predecessor's existing WPT is not duplicated in this native-only prerequisite view; the actual earlier commit remains the source of that separate bug and test.

The full v2 WPT is retained unchanged at SHA-256 `6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3`. No case, namespace control, numeric rejection or NonCustom oracle was weakened to fit upstream. The original/candidate repair-v2 patch used by root remains untouched, as does the branch's intended incremental bugfix commit.

## Validation limits

Six exact scratch apply/reverse operations passed: self-contained forward/reverse, prerequisite forward, adapted repair forward/reverse, prerequisite reverse. Both paths yielded identical three-file candidate inventories and exact original restoration, including removal of the newly added WPT. Scratch was removed. `check.py` replays this without using the live index or tree.

Rustfmt parsed the two copied native candidate files successfully; its temporary full formatting outputs were hashed and removed. This is syntax evidence only. Neither upstream variant has been compiled, linked, run in a browser, or tested in WPT. Passing the branch original/candidate comparison would validate that branch environment, not this independently captured upstream environment. Upstream build and the unchanged 34-case fixture plus numeric regression coverage remain required before claiming the self-contained variant is validated or landable.
