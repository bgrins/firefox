# Contained quote append invalidation

Expanded baseline: 12 FAIL, 52 PASS, one OK across all four quote operations,
initial depth zero/one, nested/direct child scopes, optional trailing quote and
before/after insertion. Fresh equivalents and insertion removal are controls.
Root raw/input review is in ../css-quote-scope-append-probe-v1/ROOT-BASELINE-v2.json.

The candidate retains immediate appended-node calculation, but requests existing
batched quote recalculation when the owning scope has children. Parent-first
scope traversal then updates dependent entry depths. The check is conservative
for children that precede the appended node; no per-insertion subtree scan is
introduced. Leaf-list append keeps its existing fast path.

The candidate build and all 64 new cases pass. The final regression run includes
15 existing passes and three existing failures matching unchanged metadata
(first-letter 003/004 and language mutation). Format changes no candidate bytes;
eight unrelated formatter changes were restored. Lint has zero errors and one
ignored-WPT warning. The three-file patch applies exactly at branch base and
HEAD; no isolated-base build was run. ROOT-NATIVE-WPT-v1.json pins these gates.

Pending: independent native review and full formal scope/production. The draft
formal target retains scope/provider/order/dirty-delivery and arbitrary edit
sequence obligations. No formal acceptance or new commit is claimed. Work stays
local; configured signing remains unavailable.
