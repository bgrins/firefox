# Accepted113: refresh hidden SVG viewport geometry before matrix queries

Accepted for a separate local Gecko/WPT commit, pending signing. The exact patch contains SVGGraphicsElement.cpp and one eight-case WPT; research stays in a preceding commit. No native patch is installed by this acceptance record.

After an ordinary-size hidden host grows from100px to200px, getCTM/getScreenCTM previously retained a stale viewBox scale of1 instead of2. Both entrypoints now use the existing hidden-content-aware GetPrimaryFrame(Layout) query before unchanged matrix calculation and singular fallback. The returned frame is not retained across reflow.

NormalizedHEAD90 gives32PASS/2FAIL; HEAD90 plus only the candidate gives34PASS. All eight new cases pass, all26 existing controls are preserved, and eight separate availability observations are identical. Lint, both builds and restoration pass. Root and independent review verify all27 restored source bodies,50 source guards,355 final roles,925 staged paths,26 existing native modifications and both installed112 test identities. No pending107 is needed for these tested histories. Separate patch applicability/source audits support independence from the recorded upstream base, but no pristine-upstream browser run is claimed.

The source audit found the missing query preparation; browser comparisons establish this repair. Existing conditional provider-observation results provide context, not an end-to-end native proof. Full SVG availability, dirty-state/lifetime completeness, broad performance and release novelty are outside this acceptance. No security impact is established.

The authoritative reviewer lookup selects #firefox-svg-reviewers. The planned native subject is recorded in ACCEPTANCE.json. Installation and signed-commit receipts will be separate; this immutable record retains their current pending status.
