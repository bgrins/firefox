# Equal-font, different-count cache alias

`equal_font_key_stale_count` reuses the immutable dependency model and holds both own and parent fonts equal, for arbitrary font values. The first context has index 1/count 2 and the second index 3/count 3. A mask containing both font fields still aliases them; reusing the first evaluated count yields 2 when fresh evaluation yields 3. `FalseReuse.lean` rejects that reuse as equal to fresh evaluation.

This addresses a narrower correspondence than the prior model's fixed-parent/different-own-font example. It matches the required cache-key alias shape for the source hypothesis in `css-sibling-count-rule-cache-review-v1`: count is omitted even if font-dependent conditions are present. Native rule-node identity, line height, writing mode, color scheme, zoom and appearance-subtree state must additionally remain equal; those fields are external premises, not modeled or inferred from the theorem. The model does not prove a native cache hit or the proposed fix. It also does not model CSS floating-point values, unit conversion or rendering.

The theorem audits standard `propext` and `Quot.sound` only. Actual isolated replay d4e999/0 checked one witness and rejected one false control; scratch objects were removed. `Dependency.lean` is hash-authenticated and copied only into the temporary import directory, not duplicated in this package or changed. No canonical coverage, new bug count or native acceptance is claimed.

```sh
python3 -I -S -B artifacts/css-sibling-count-rule-cache-model-v1/replay.py artifacts/css-sibling-count-rule-cache-model-v1/run-2
```
