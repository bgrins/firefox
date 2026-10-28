# Release Firefox: contextual tree-counting line-height

The installed /Applications/Firefox.app version158.0 reproduces the contextual number line-height failure without preference changes. Its random preference is false and random syntax is unsupported; all eight tested non-random expressions are supported.

Unitless sibling-index() and sibling-count() each yield computed line-height0px and actual line-box height0 across before/insertion/removal. Expected values are20/30/20px at font10px. The equivalent length forms calc(sibling-index() * 1em) and calc(sibling-count() * 1em) both give20/30/20px. Literal2, calc(2), percentage ratio and inherited-lh ratio controls match their expected positive computed values and geometry in all three phases.

This independently confirms a release-browser effect of the same missing-context leaf mapping as the Nightly random cases. It does not add another bug count or establish that the proposed repair works in a release build. The one-file source repair and all-seven-parser repair were only typechecked together in the local configured Gecko graph.

The release executable/XUL/application metadata hashes and identities match before/after. The complete local native/binary/research snapshot and exact pending165 staged selection also match. One owned iframe was removed, and the owned tab and headless browser session were closed. No feature preference, source, binary, index content or runtime epoch was changed.
