# Top-level curly declaration fallback reproduction

The unchanged local Firefox build from parser recovery repair 66 fails 24 of 48 checks. Six noncustom font-family inputs combining a top-level curly block and other tokens are retained through setProperty, cssText, stylesheet parsing, and CSS.supports. The remaining 24 checks pass, including color rejection and custom-property, whole-curly-block and square-block controls.

The probe is copied unchanged from css-declaration-reparse-static-v1/declaration-curly-fallback.html. Full raw and console records, source/config/binary hashes before and after, and keyed outcomes are retained. This is a browser reproduction on the current stack, not an isolated upstream build or a repaired-source result. The diagnostic WPT remains uncommitted until the standalone native repair is ready. No new committed-fix count is claimed.
