# Independent cherry-pick assessment for image and color-union repairs

The prior A-then-B plan does not meet independent cherry-pickability against the committed base. It describes two reviewable behavior changes in a dependent stack. This successor does not relabel that stack as independent. Root reports combined candidate42 session85310 running; no candidate result is used here, and no native patch or fixture is changed.

## Smallest defensible image-only boundary to investigate

Define C as the registration's existing `DependentDataTypes::COLOR` eligibility and I as an explicit `<image>` syntax component. A union/default repair can be activated for C. A distinct image-admission repair can be activated for I and not C. This division is by registration admission, not by whether a particular serialized token looks like a color. It includes pure images and image/identifier or image/length unions; mixed image/color registrations remain in the already-admitted color family.

An image-only candidate against the committed base would need all of the following changes together:

1. Preserve the original COLOR branch of `find_non_custom_references`; add deferred admission for I-and-not-C even when the image has no var/attr reference. Admission must still happen for an absolute-color gradient with em/lh stops. Merely setting a COLOR_SCHEME edge for every image is not an acceptable final fix.
2. After selected custom/attr references have been visited, refine the added image marker only for I-and-not-C. Do not execute the current unconditional removal of COLOR_SCHEME for unrelated or C registrations. Preserve the original singleton preparation guard and original behavior for C nodes.
3. Select the actual parsed image/alternative using the full ordered registration syntax, including repetition and var/attr substitution. Keep existing unit flags; the selected image may require no scheme edge while still requiring font/line-height ordering. Retain the parsed AST through computation to avoid introducing an unproved second-substitution/second-parse equivalence requirement.
4. Include actual initial/default selection and the post-edge cycle/default hook, restricted to I-and-not-C. Pure-image var/attr nodes already enter the old graph, so admission-only edits omit a reachable new default path. Preserve computed-parent copying, root/non-inheriting initial recomputation, existing invalid handling and taint behavior.
5. Leave all old COLOR registrations on the old application path. If an image-only node and a COLOR node participate in one graph, their outcomes can still interact through real dependencies; predicate separation does not prove global behavioral isolation.

The current V3 selector and recursive image/color classifier can supply this machinery without the animation or contextual-attr prototypes. This is a self-contained image-only source design, not an implemented minimal patch or a correctness proof. The analogous A-only candidate needs the same machinery gated by C, with no new Image-only admission/default treatment. Simply subtracting one Image condition from the combined patch is insufficient for either isolation.

## Shared code versus a cherry-pickable commit stack

The retained-AST preparation/application extraction, invalid-initial selector and recursive classifier are shared native machinery. It is feasible to package each standalone alternative patch against the committed base with the helpers it actually uses and its own WPT. Such alternatives have no semantic dependency on the other bugfix, but their overlapping helper additions and traversal edits will conflict if both are cherry-picked. A manually reconciled combined tree must be reviewed and tested; this is not a finished independently applicable two-commit stack.

A common behavior-preserving refactor prerequisite would make the eventual stack cleaner, but then neither dependent bug commit is independently cherry-pickable to the original base unless the prerequisite is included. That fails the literal requirement and must not be hidden in an administrative commit. No source theorem establishes that such a prerequisite is unavoidable: it is an implementation/review tradeoff. Conversely, duplicating large selector/classifier implementations under separate bug-specific names solely to avoid patch conflicts is not a minimal maintainable fix.

The practical next step is to validate standalone A-only and image-only alternatives first, then choose a final packaging after reviewing their actual overlap. If clean independent cherry-picks and a single nonduplicating stack cannot both be achieved, report that concrete overlap to the user rather than claim the dependent stack satisfies the requirement. The combined candidate currently running remains evidence for combined behavior only.

## Native and WPT evidence required

- Original committed-provider baseline: freeze and authenticate all42 outcomes/restoration. Run the separate three absolute-color image-unit cases on that same original provenance; current42 CanvasText cases do not isolate unit ordering.
- A-only against the committed base: full42 plus the supplemental image-unit page. It must establish union/default improvements and retain existing image behavior unless a real shared dependency explains an interaction. Do not classify outcomes by callback title alone.
- Image-only against the committed base: the same resources, including the original five union tests. It must establish image improvements without silently repairing or regressing the unrelated COLOR path. Mixed image/identifier versus image/color parser cases still need focused coverage before landing; no new fixture is created while the combined outcome is unknown.
- Reconciled A+image tree: repeat the same comparison and inspect exact source composition. Semantic equivalence to combined V3 is an obligation, not guaranteed by disjoint eligibility labels. Compile each standalone tree; isolated classifier tests do not type-check or exercise traversal/application.

Each eventual bug commit should carry its own narrowly grounded WPT. Conditional accepted-contextual-initial preservation cases remain research validation, pending the separate independence/spec work. The original42 and the supplemental3 are immutable. This note creates no new runtime, fixture, native source or signing operation.
