# Independent endpoint taint review

## Verdict

Approve the three-file source proposal and six-case CSS-wide WPT for root integration, subject to generated-binding compilation and paired runtime validation. This is a static source/test review plus independent artifact replay; it is not a universal animation proof or an all-platform compile claim. The upstream standalone alternative must include the separately identified one-site map publication prerequisite. No production edits or browser/build runs were performed by this reviewer.

## Authentication and replay

The externally supplied proposal FREEZE and MANIFEST were matched before executing its checker. All 49 inputs were hashed, duplicate JSON keys and unsafe names rejected, and an exact file roster/no-symlink check applied. A manifest-only copy in /private/tmp was replayed with Python -I -S and without PYTHON/LEAN environment overrides. The retained stdout records successful Node syntax checks and zero-fuzz patch application/reversal on current originals and upstream originals, including exact five-file standalone output. This is source application evidence, not upstream runtime evidence. Node, patch, Python, OS and filesystem remain trusted tools. No native compiler was invoked.

## Shape, identity, lifetime and publication

The full nsTArray equality implementation first checks length, then compares corresponding entries. AnimationProperty equality checks CSSPropertyId and segment arrays. CSSPropertyId equality includes the custom-property atom, not just the generic custom-property numeric ID. Segment equality checks offsets, timing/composite fields and both endpoint AnimationValues. AnimationValue equality distinguishes null from nonnull and otherwise delegates to Servo_AnimationValue_DeepEqual. Thus entering the new scan after ordinary equality establishes equal array and segment lengths, aligned property identity and matching null shape; no unchecked assumption of equal lengths is introduced.

The lambda short-circuits a null mServo before passing a borrowed value to Rust. The accessor reads the outer computed-value attr_tainted bit; absent guaranteed-invalid values yield false. The FFI matches only the Custom variant and returns false otherwise. It does not allocate, transfer ownership, retain references, call script or change state. The arrays hold their endpoint references throughout the scan. The existing property construction/provider relationship remains a native admission, not a new Rust type-level proof that every custom property has a Custom variant.

Both from and to endpoints are compared for each custom-property segment, including later properties and segments. Noncustom properties are skipped. Ordinary inequality takes the original changed path without the added scan. Equal payload but unequal taint now takes that same path: EnsureBaseStyles, replacement of mProperties, effect-set/cascade invalidation, cumulative-change recomputation, notifications and layer restyle. EnsureBaseStyles was already unconditional. Nothing in the new scan introduces reentry between the equality and indexed reads. BuildProperties performs its existing keyframe cloning before this point; that broader provider/reentry contract is unchanged.

The deliberate payload-only equality remains unchanged. Changing global DeepEqual, AnimationProperty or AnimationPropertySegment equality would affect other comparisons, including CSS-animation mutation-notification decisions. The local UpdateProperties check is the narrower retention/publication boundary. This does not establish that every other metadata consumer is complete, nor does it repair other provenance such as URL data.

## Bindings and cost

KeyframeEffect.cpp already includes ServoBindings.h, which includes generated ServoStyleConsts declarations. The new no_mangle Rust function follows adjacent AnimationValue borrowed-reference/bool conventions; cbindgen configuration exports functions and does not exclude this symbol. No handwritten declaration appears necessary. Actual generated C++ signature/linkage compilation remains a root gate.

The added work is a property scan only when ordinary equality succeeded, with at most four constant-time borrowed FFI queries per examined custom segment and early exit on difference. There is no allocation or refcount churn in this scan. This is a source complexity bound, not a measured performance claim.

## Independent test oracle and baseline

The test uses registered inheriting <string> values. A literal registration initial value is clean; the parent obtains the same string through attr(), so inheritance carries taint. It replaces initial with inherit and vice versa using two equal endpoints at an interior time. Both endpoints in each effect have the same provenance, avoiding an oracle assumption about mixed-provenance interpolation. The parent payload, parent rejection, literal URL reference, raw replaced keyframe, initial observation, different-payload replacements and fresh-effect controls calibrate the tested paths. The grandparent has a different payload so parent attr publication is not itself hidden by the old equal-payload map shortcut. The comparison is computed image-set serialization, not successful network loading.

The separately copied root CSS-wide baseline has exactly six identities: the two same-payload directions fail only at Updated effect URL taint; both different-payload cases and both fresh controls pass. The initial-to-inherit failure retains an allowed image; the reverse retains none. Harness status is OK, receipt stable_after is true, and the test pin equals the sealed proposal. These are root-executed baseline observations, not candidate success. The producer original-six evidence is a separate typed-keyframe diagnostic and is not substituted for this CSS-wide baseline.

## Standalone boundary and provenance

The upstream from_declaration CSSWideKeyword branch already reads the registered computed initial cache and inherited computed map. This WPT has no typed Unparsed keyframe attr()/var() values, so it does not require repair70's completed-map provider. It does not use repair71's ordinary substituted-initial reconstruction, invalid/missing inherited registration paths of72/73, or indexed/count enumeration paths of74/75. It uses a full tainted string as the URL source, not the adjacent-range boundary repaired later.

Publication still goes through the custom-property map. Returning clean initial A over inherited tainted A can be discarded by the original do_insert payload-only shortcut. The five-file standalone patch therefore includes exactly the existing map-support change to can_deduplicate_values, plus the three endpoint files and WPT. It omits fix76's separate universal cascade shortcut: this fixture uses parsed typed publication. This prerequisite is already known work, not another newly discovered bug. The three-file endpoint patch plus WPT alone is not claimed to pass on upstream.

The corrected upstream revision is 976279105b2e78b8666a959eb3f25c9176cefaf8. The imported historical attribution had a 41-character typo; IMPORT-AUTHENTICATION records the correction and root's separately supplied byte confirmation. This reviewer validates retained bytes and apply/reverse, not a fresh git lookup. Supplemental upstream cascade/custom-property context is not promoted to newly verified Git provenance. Actual standalone runtime is still open.

## Focused regressions and coverage limits

Recommend web-animations/interfaces/KeyframeEffect/setKeyframes.html: empty replacement, valid/invalid shared keyframe corpus, and immediate left midpoint replacement150px→250px. Searchfox discovery and the exact local test are retained. Its missing per-test metadata is not execution evidence.

css/css-values/attr-security-animation.html has one meaningful string/image-set case. Five other cases use if(style(...)); unsupported if() can make background:none assertions vacuous, although some also assert numeric values. Keep any run separately classified, not six strong URL-taint controls. Per-test metadata was absent at review time.

Not covered by this six-case WPT: asymmetric endpoint taint, multiple properties/segments, neutral endpoints, additive composition, compositor execution and all other metadata consumers. The source shape/loop review covers index safety and both endpoint checks; finite tests do not prove those universally. A separate conditional endpoint-retention Lean component is being reviewed independently and is not accepted by this report.

## Primary requirements

Retrieved through the web tool on 2026-10-19; these are current draft readings, not immutable full-spec snapshots:

- https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-setkeyframes (8 October2026 draft): successful setKeyframes replaces the effect keyframes.
- https://drafts.csswg.org/web-animations-1/#computing-property-values: keyframe properties compute using the target element context before producing the effect.
- https://drafts.csswg.org/css-cascade-5/#explicit-defaulting: initial selects the property's initial value; inherit selects the parent's computed value.
- https://drafts.csswg.org/css-values-5/#attr-security: attribute-derived provenance survives arbitrary substitution, including registered-property token serialization; using tainted data as a URL invalidates the declaration.

These requirements support the two constant-endpoint oracles. They do not require changing global mathematical value equality or establish a broad animation-taint propagation proof.
