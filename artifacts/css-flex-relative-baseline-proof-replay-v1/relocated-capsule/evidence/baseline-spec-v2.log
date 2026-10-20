# CSS-ALIGN-3#baseline-export

**Determining the Baselines of a Box** (heading)

**SHA**: hash:4603756cb870122b864974842e35f26311afcc105618d50415aa48eef781ab1b

## Content

Each box, for a given axis, has potentially a **first baseline set** (and **last baseline set**) that nominally corresponds to the [baseline set](CSS-ALIGN-3#baseline-set) of the first/last line of text within the box. The **alignment baseline**, which is the baseline used to align the box in its [alignment context](CSS-ALIGN-3#shared-alignment-context), is one of the baselines in its baseline set, usually the dominant baseline associated with the shared alignment context. (See the [dominant-baseline](CSS-INLINE-3#propdef-dominant-baseline) and [alignment-baseline](CSS-INLINE-3#propdef-alignment-baseline) properties in \[CSS-INLINE-3\].)

The first and last [baseline sets](CSS-ALIGN-3#baseline-set) of a box are determined differently based on the layout model, as follows:

line box 

The first/last [baseline set](CSS-ALIGN-3#baseline-set) of a line box is [generated](CSS-ALIGN-3#generate-baselines) from the dominant baseline and the font settings of its [root inline box](CSS-INLINE-3#root-inline-box).

block containers 

The first/last [baseline set](CSS-ALIGN-3#baseline-set) of a [block container](CSS-DISPLAY-4#block-container) is taken from the first/last [in-flow](CSS-DISPLAY-4#in-flow) line box in the block container or the first/last in-flow block-level child in the block container that contributes a set of first/last baselines, whichever comes first/last. If there is no such line box or child, then the block container has no baseline set.However, for legacy reasons if its [baseline-source](CSS-INLINE-3#propdef-baseline-source) is [auto](CSS-INLINE-3#valdef-baseline-source-auto) (the [initial value](CSS-CASCADE-5#initial-value)) a [block-level](CSS-DISPLAY-4#block-level) or [inline-level](CSS-DISPLAY-4#inline-level) [block container](CSS-DISPLAY-4#block-container) that is a [block-axis scroll container](CSS-OVERFLOW-3#block-axis-scroll-container) always has a [last baseline set](CSS-ALIGN-3#last-baseline-set), whose baselines all correspond to its [block-end](CSS-WRITING-MODES-4#block-end) [margin edge](CSS-BOX-4#margin-edge).

multi-column containers 

The first [baseline set](CSS-ALIGN-3#baseline-set) of a [multi-column container](CSS-MULTICOL-1#multi-column-container) is the first baseline set of the [column](ECMA426#sec-terms-and-definitions-colun) or [multi-column spanner](CSS-MULTICOL-2#multi-column-spanner) with the highest ([block-start](CSS-WRITING-MODES-4#block-start)–most) baseline corresponding to the multi-column container’s [alignment baseline](CSS-ALIGN-3#alignment-baseline). If there is no such line box or child, then the multi-column container has no first baseline set.The last [baseline set](CSS-ALIGN-3#baseline-set) is analogous, but uses the *last* baseline set and *lowest* ([block-end](CSS-WRITING-MODES-4#block-end)–most) baseline.

tables 

The first/last [baseline set](CSS-ALIGN-3#baseline-set) of a table box is the first/last baseline set of its first/last row (after any reordering of table row group box).When finding the first/last baseline set of an inline-block, any baselines contributed by table boxes must be skipped. (This quirk is a legacy behavior from \[CSS2\].)

table rows 

The first [baseline set](CSS-ALIGN-3#baseline-set) of a table row box is taken from the first available of:

1.  If any cells in the row participate in first [baseline alignment](CSS-ALIGN-3#baseline-alignment) along the table’s [inline axis](CSS-WRITING-MODES-4#inline-axis), [generate](CSS-ALIGN-3#generate-baselines) a [baseline set](CSS-ALIGN-3#baseline-set) from their shared [alignment baseline](CSS-ALIGN-3#alignment-baseline) and the row’s [first available font](CSS-FONTS-4#first-available-font), after alignment has been performed.

2.  Otherwise, if any cells in the row participate in last [baseline alignment](CSS-ALIGN-3#baseline-alignment) along the table’s [inline axis](CSS-WRITING-MODES-4#inline-axis), [generate](CSS-ALIGN-3#generate-baselines) from *that* [alignment baseline](CSS-ALIGN-3#alignment-baseline).

3.  Otherwise, if the row is not empty, [synthesize](CSS-ALIGN-3#synthesize-baseline) from the lowest and highest [content edges](CSS-BOX-4#content-edge) of all the cells in the row. See [CSS 2 § 17.5.3 Table height algorithms](CSS2#height-layout).

4.  Otherwise, use the [block-start](CSS-WRITING-MODES-4#block-start) [content edge](CSS-BOX-4#content-edge) of the table row box itself as the [alignment baseline](CSS-ALIGN-3#alignment-baseline).

For this purpose, any table cell that spans multiple rows is ignored if it’s span does not start in this row; except that for step 2, it’s ignored if its span does not *end* in this row.

*Last baselines are analogous (with “first”/“last” and “start”/“end” inverted).*

Spanning cells participate only in the first/last row that they span for the purpose of [first baseline](CSS-ALIGN-3#valdef-justify-self-first-baseline)/[last baseline](CSS-ALIGN-3#valdef-justify-self-last-baseline).

flex containers 

See [Flex Baselines](CSS3-FLEXBOX#flex-baselines) in \[CSS-FLEXBOX-1\].

grid containers 

See [Grid Baselines](CSS3-GRID-LAYOUT#grid-baselines) in \[CSS-GRID-1\].To **generate baselines** for a box from a single baseline, use the baseline table from the font settings and [first available font](CSS-FONTS-4#first-available-font) of that box, and align that baseline set to the given single baseline.

If a box that participates in [baseline alignment](CSS-ALIGN-3#baseline-alignment) has no [baseline set](CSS-ALIGN-3#baseline-set), then its [alignment baseline](CSS-ALIGN-3#alignment-baseline) is [synthesized](CSS-ALIGN-3#synthesize-baseline) according to the rules of the [formatting context](CSS-DISPLAY-4#formatting-context) in which it participates. To **synthesize baselines** from a rectangle (or two parallel lines), synthesize the alphabetic baseline from the [line-under](CSS-WRITING-MODES-4#line-under) line, and the central baseline by averaging the positions of the two edges or lines. See [CSS Inline Layout 3 § A Synthesizing Alignment Metrics](CSS-INLINE-3#baseline-synthesis) for rules on synthesizing additional baselines.

> **Note:** Note: The edges used to [synthesize](CSS-ALIGN-3#synthesize-baseline) baselines from a box depend on their [formatting context](CSS-DISPLAY-4#formatting-context): inline-level boxes synthesize from their margin edges \[CSS-INLINE-3\], table cells synthesize from their content edges \[CSS2\], and grid and flex items synthesize from their border edges \[CSS-GRID-1\] \[CSS-FLEXBOX-1\].

In general, the [writing mode](CSS-WRITING-MODES-4#writing-mode) of the box, shape, or other object being aligned is used to determine the [line-under](CSS-WRITING-MODES-4#line-under) and [line-over](CSS-WRITING-MODES-4#line-over) edges for synthesis. However, when that writing mode’s [block flow direction](CSS-WRITING-MODES-4#block-flow-direction) is parallel to the axis of the [alignment context](CSS-ALIGN-3#shared-alignment-context), an axis-compatible writing mode must be assumed:

*   If the box establishing the [alignment context](CSS-ALIGN-3#shared-alignment-context) has a [block flow direction](CSS-WRITING-MODES-4#block-flow-direction) that is orthogonal to the axis of the alignment context, use its [writing mode](CSS-WRITING-MODES-4#writing-mode).

*   Otherwise:

    *   If the box’s own [writing mode](CSS-WRITING-MODES-4#writing-mode) is vertical, assume [horizontal-tb](CSS-WRITING-MODES-4#valdef-writing-mode-horizontal-tb).

    *   If the box’s own [writing mode](CSS-WRITING-MODES-4#writing-mode) is horizontal, assume [vertical-lr](CSS-WRITING-MODES-4#valdef-writing-mode-vertical-lr) if [direction](CSS-WRITING-MODES-3#propdef-direction) is [ltr](CSS-WRITING-MODES-4#valdef-direction-ltr) and [vertical-rl](CSS-WRITING-MODES-4#valdef-writing-mode-vertical-rl) if direction is [rtl](CSS-WRITING-MODES-4#valdef-direction-rtl).

For the purposes of finding the baselines of a box, it and all its [in-flow](CSS-DISPLAY-4#in-flow) descendants that are [block-axis scroll containers](CSS-OVERFLOW-3#block-axis-scroll-container) must be considered as if scrolled to their initial scroll position. Additionally, if the position of a [scroll container](CSS-OVERFLOW-3#scroll-container)’s first/last baseline is outside its border edge, that baseline’s position is clamped to the border edge.

## Navigation

- Parent: `baseline-rules` — Baseline Alignment Details
- Next: `baseline-terms` — Baseline Alignment Grouping
- Children: 5
  - `first-baseline-set` — first baseline set
  - `last-baseline-set` — last baseline set
  - `alignment-baseline` — alignment baseline
  - `generate-baselines` — generate baselines
  - `synthesize-baseline` — synthesize baselines

## Outgoing refs (44)

`webspec-index refs CSS-ALIGN-3#baseline-export -d outgoing -l 44`

## Incoming refs (1)

- CSS-ALIGN-3#contents

### Possible effects

CSS-ALIGN-3#baseline-export

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-ALIGN-3#baseline-export" --format markdown`
