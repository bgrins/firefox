# Central baseline origin proposal

Unaccepted, unbuilt source proposal against HEAD 90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e. Browser comparison and rounding review are pending.

The current central branch computes an offset from the line-over edge regardless of the requested first/last group. Encode that offset using the already line-inversion-adjusted group before returning it. This preserves the selected edge and existing half-box rounding, while converting the opposite-origin query using the border-box size.

This changes only central/mathematical/middle synthesis. It does not repair large-coordinate overflow in existing margin sums or prove all synthesis consumers. The small empty-inline-block fixture and a stronger symmetric-reference oracle must be observed before acceptance.
