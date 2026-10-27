# Primary specification mapping

Read 23 October 2026 through the official SVGWG draft using the web tool. The overview identifies this as the SVG 2 Editor’s Draft dated 14 September 2025. The installed webspec-index tool was unavailable in the prior session; no toolchain installation was attempted in this bounded source audit. These are dated reading notes, not a retained complete HTML or commit snapshot.

- [SVG 2 overview](https://svgwg.org/svg2-draft/): version/status.
- [Basic Data Types, §4.5.2 SVGLength](https://svgwg.org/svg2-draft/types.html#InterfaceSVGLength): `value` resolves the stored length using its associated element and directionality; the horizontal percentage basis is that element's SVG viewport width. Conversion step 3 says: “Let absolute be the value that would be returned from the value member.” Target-percentage conversion also uses the current directional viewport basis. `valueInSpecifiedUnits` returns the stored numeric factor, so retaining 50 after a resize is legitimate until conversion changes the representation.
- [Coordinate Systems, §8.1 and §8.9](https://svgwg.org/svg2-draft/coords.html): SVG viewport/user-coordinate semantics differ from the page viewport. A viewBox can preserve the percentage basis while CSS size changes. The proposed fixture deliberately omits viewBox, transforms, zoom, hidden/skipped content and animation.

The proposed expected 50% of 400 = 200 user units and 100 user units / 400 = 25% are deductions for that fixture, not a requirement that every SVG length track CSS pixels. No claim that conversion must literally call a particular native flushing API is made.
