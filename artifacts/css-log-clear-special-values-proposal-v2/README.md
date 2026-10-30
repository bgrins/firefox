# Log fixture resource-path correction

This is the sole execution candidate for the proposed log fixture. V1 is historical static-only preparation: its numeric helper URL incorrectly resolved inside css/css-values/support, so its two ordinary callbacks could not register in a browser. Static lint and manifest registration did not validate resource loading. No browser result was claimed for v1.

The only fixture change is `support/numeric-testcommon.js` to `../support/numeric-testcommon.js`. Native patch and SOURCE.json are byte-identical to v1; the 24 callback definitions, expectations and helper code are unchanged. The proposal rationale and scope in v1 still apply. The separate dispatch Lean model remains applicable without replay because the native helper is unchanged.

The comparison plan resolves and hashes every script URL at its intended WPT location. These static checks do not establish browser results. The native patch must be rebased onto MinMax if it is accepted first; this correction installs nothing.
