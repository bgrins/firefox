# Initial independence policy remains split

The nine JavaScript registration failures have a direct current-spec oracle: registration must reject a parsed typed initial value that is not computationally independent. The conditional @property color observations have a different status.

The [August 6 specification edit](https://github.com/w3c/css-houdini-drafts/commit/e1f11c5e6fffef319bcdc0f0fe25034d1a6a4b3f) made descriptors optional. Its actual diff removed the explicit independence requirement from the CSS rule's initial-value descriptor while retaining it in JavaScript registration. The [editor's explanation](https://github.com/w3c/csswg-drafts/issues/13211#issuecomment-5207189739) describes optional descriptors and invalid descriptor fallback; it does not explain an intentional relaxation of independence.

An [existing follow-up comment](https://github.com/w3c/csswg-drafts/issues/13211#issuecomment-5390397584) explicitly asks whether this discrepancy was intentional. The fetched comment list contains no answer. The current @property introduction also describes equivalence to JavaScript registration, so absence of the descriptor sentence alone cannot establish unconditional contextual-initial validity.

The [March 11 discussion](https://github.com/w3c/csswg-drafts/issues/12735#issuecomment-4040186968) treats scheme-dependent colors as outside computational independence and considers removing the restriction separately. Its literal resolution line instead says “computationally independent”; this conflicts with the surrounding discussion and must not be silently corrected when quoted. That discussion predates the August edit and does not resolve the current textual inconsistency.

Disposition: keep the JavaScript rejection probes normative and the CSS-rule color observations conditional. Do not accept an element-color behavior change merely because the test still has FAIL status or because cached initials are internally consistent. The candidate experiment may measure the change, but acceptance requires resolving the policy or preserving the required contextual behavior. No narrow type whitelist is proposed.

Captures were fetched from the public GitHub API on 2026-10-27. The initial restricted-network attempt failed before fetching; the authorized read-only retry succeeded. No issue comment, external edit or submission was made.
