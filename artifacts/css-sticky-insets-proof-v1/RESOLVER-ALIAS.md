# Explicit offset / auto-code alias

The retained Searchfox `ServoStyleConstsInlines.h` explicitly returns `nscoord_MAX` from `DefaultLengthToAppUnits` once the float appunit length reaches its float threshold. Pure `LengthPercentage::Resolve` follows this conversion through `ToLength` and `ToAppUnits`. Percentage and calc branches instead use `DefaultPercentLengthToAppUnits` / `NSToCoordTruncClamped(float)`, which also explicitly saturates to the same maximum. Finite inputs do not yield a coordinate above that maximum through these branches. `NS_AUTOOFFSET` is that same maximum, 1073741823.

This means an explicit finite inset can lose its active identity. The model's excluded encoded value is a genuine native provider restriction, not a guarantee of the native coordinate type. Root independently reproduced the boundary on the development and installed release binaries: `css-sticky-offset-alias-probe-v1/{candidate,release}/RESULT.json`, 32 rows each, eight discrepancies and 24 controls, including the neighboring 17895697px control. These are external corroborating receipts, not this capsule's browser executions.

A local reservation at `ComputeStickySideOffset`, after its genuine auto branch, is the narrow producer repair boundary: an explicit resolution of max becomes max−1. This leaves every smaller finite resolved value intact. No general max−1 convention was found in a bounded Searchfox search of layout; this recommendation follows the actual sentinel encoding. It does not prove subsequent offset addition/subtraction safe, and does not address NaN conversion. Those remain separate numeric/provider premises. The full H1/H2 sources and theorem domain are unchanged.

Exact retained source identities are in `RESOLVER-ALIAS.json`.
