# Relative baseline spec and provider scope

Consulted 2026-10-20: [CSS Position 3](https://drafts.csswg.org/css-position-3/#valdef-position-relative) and [Flexbox container baselines](https://drafts.csswg.org/css-flexbox-1/#flex-baselines).

Relative positioning first lays out the item normally and then applies a visual offset. That offset must not reposition non-descendant boxes, apart from the stated scrollable-overflow effect. The baseline-aligned container and peer are non-descendants. Combining this restriction with the flex baseline export rules supports using the donor's normal position. The tested scenarios do not exercise scrolling, fragmentation or orthogonal donor synthesis.

The normal-position API reads a saved physical normal position when available, otherwise the current physical position. Its logical conversion accounts for the child size when origins are reversed. Correct freshness and lifetime of the saved property are separate provider obligations.
