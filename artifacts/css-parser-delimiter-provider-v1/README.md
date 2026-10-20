# Tokenizer delimiter-provider bridge

`lean/DelimiterProvider.lean` derives the until-after delimiter law for ByteLex
from a one-byte width contract on semicolon, exclamation and comma. Curly opening
is handled directly by the tokenizer model, independently of fallback providers.
Five general results compose this law with the accepted until-after refinement.

The independent review proves the exact finite driver's delimiter law for
arbitrary byte lists and supplies positive and negative provider witnesses.
It also refutes that driver's global every-family progress premise; the complete
refinement corollary cannot be instantiated with this partial driver as-is.
This limitation is preserved, rather than treating the finite corpus as proof
of universal progress. No new native or browser defect is claimed.

Review: `../css-parser-delimiter-provider-review-v1/REPORT.md`.
Root replay and scoped decision: `../css-parser-delimiter-provider-root-v1/`.
The review capsule retains the source closure and compiler entry point. Authenticate
its externally pinned manifests, then compile `ReviewAudit` to a new external
output directory with `python3 -I -S compile.py --output PATH ReviewAudit`.
