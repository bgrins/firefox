# Relative overflow positioning: formatting and lint

Actual-path clang-format and explicit WPT lint passed; the WPT is unchanged.
The only source modification splits the containerSize argument onto a new line.
FORMAT-BRIDGE.json records and verifies that single exact replacement; no code
tokens change. The final standalone native/WPT patch is formatted-proposal.patch.
The preceding browser tests exercised the same expressions before formatting.

Reviewer tooling selected #layout-reviewers. Original source and temporary WPT
absence were restored, with HEAD/index unchanged. The built source is therefore
still the prior baseline. The final candidate is retained as an artifact pending
root acceptance/install, with no unsigned commit or push.
