# Standalone whitespace fix commits

The integration branch has one native/WPT commit for each fix. These local
standalone refs put each accepted upstream adaptation directly after its evidence
companion on retained upstream 976279105b2e78b8666a959eb3f25c9176cefaf8.
They let each fix be reviewed or extracted independently of the other repairs.

create-standalone.py takes 83, 84 or 85, reads the committed package and evidence,
uses a temporary Git index, verifies exact application/reversal and native/WPT
blobs, signs two commits, and creates a new local ref. It refuses an existing ref
and preserves the current branch, index and relevant working files. Receipts are
STANDALONE-83.json, STANDALONE-84.json and STANDALONE-85.json after creation.

The shared browser evidence and static independence review are retained. No
isolated upstream Firefox build or browser run is claimed. These are alternative
commits for the same three defects and do not increase the count of 85 fixes.

## Created refs

- Fix 83: `stylo-css-attr-leading-whitespace-fix`, native `4be5b070191054a263197654d1f30096a9306b43`.
- Fix 84: `stylo-css-variable-trailing-token-fix`, native `5b4fe54b37bc5a3bb848ceb8300f5d92ea4c2e3a`.
- Fix 85: `stylo-css-variable-escaped-whitespace-fix`, native `8a528dbb92bbaca6db31123f8b0da45983fa798a`.
