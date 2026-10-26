# Column provider boundary WPT drafts

Status: **20 unrun diagnostic WPT drafts, source and static checks only**. No native, installed WPT, browser, build or Git changes. This adds12 span controls and8 fragmented-table controls to the root-owned experiment:66existing+18skipped-line+20provider=104subtests.

## Test and observation contract

`hidden-column-span-fragment-queries.html` registers the exact ordered names in `EXPECTED-ROSTER.json`. It has no support files beyond the standard testharness scripts. Proposed location: `css/css-contain/content-visibility/hidden-column-span-fragment-queries.html`.

The span cases cover `col span=1`, `col span=2`, and an empty `colgroup span=2` followed by a one-column group. The span-bearing colgroup has no col children, respecting HTML's content model. Each shape separately changes the outer width or table width, with independently constructed bounding-box-first and client-rect-list-first cases. No test asks one API to rescue the other on the hidden target.

Each case records warm, hide, change, restore and show. At each stage the only preparatory hidden-tree geometry query is the outer wrapper; the selected target is then queried twice. Visible-peer target/cell/table queries follow. All observations are gathered before calibration and candidate assertions, preserving restoration/repeat records even on an expected hidden-query failure. The visible peer is a separate tree at the same coordinates, without hidden content. Equal positions avoid normalization concealing offsets.

The three fixed table tracks calibrate to40px at120px and20px at60px. Fragment fixtures have four20px rows inside two40px-high columns with20px gap: outer width260→140 gives table/fragment width120→60. Every visible cell must occupy its exact expected row, track and fragment position; the visible table must expose two40px-high rectangles. The calibration is intentionally strict. If a UA does not produce this layout, stop the experiment and investigate the fixture; do not call its resulting failure a query-provider regression.

No column/group rectangle count, union width, continuation count or fragmented column height is invented from the span attribute. The hidden result must equal the complete same-state visible target result, retaining order and zero rectangles. Visible bounding geometry is additionally checked against the CSSOM union algorithm. This is a freshness/hidden-versus-visible comparison under calibrated table layout, not a proof of the visible implementation's complete span geometry semantics. Visible provider rectangles must be finite, nonempty and include positive area so empty results cannot vacuously pass.

Every support/outer/visible/provider/fragment calibration message contains `calibration`. The runtime controller must treat any such failure as a fixture gate failure and restore, distinct from first/repeated-query mismatches. Fragmentation is not optional and no failed support check becomes a skip.

## Source and primary-spec linkage

HTML defines columns/groups as representing one or more tracks, and restricts a span-bearing colgroup to empty content. [HTML col](https://html.spec.whatwg.org/multipage/tables.html#the-col-element), [HTML colgroup](https://html.spec.whatwg.org/multipage/tables.html#the-colgroup-element).

CSSOM returns all associated fragments, including zero extents, in content order. Its separate bounding algorithm determines how the list is combined. This is why a guessed `span × width` or filtered nonzero list is not used as the target oracle. [Client rects](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects), [bounding box](https://drafts.csswg.org/cssom-view/#element-get-the-bounding-box).

CSS fragmentation permits breaks between table rows; the test checks the actual two-fragment result independently. Fixed-layout sizing supplies equal unused track space. [Break opportunities](https://drafts.csswg.org/css-break-3/#possible-breaks), [fixed table layout](https://www.w3.org/TR/CSS22/tables.html#fixed-table-layout).

Fresh Searchfox `nsTableColGroupFrame::SetInitialChildList` confirms empty groups obtain anonymous columns via `GetSpan()`. The retained complete `ConstructTableCol` shows span-generated col frames share content/parent and are linked as nonfluid continuations. The checked parent route from column→group→first-in-flow table is retained from the prior source audit. This supports exercising the current lookup; it does not prove every table fragment is published through the first table, or derive complete CSSOM continuation collection. No current live-source identity is inferred from Searchfox.

`SOURCE-TRANSFER.json` binds reused discovery evidence. Fresh spec query outputs retain their source hashes and failed index lookups; direct primary web fallback verified fixed-layout text. No spec→native or source→test-fidelity automation is claimed.

## Shared auto-scroll caller: remains untested

The retained `ScrollContentIntoView` excerpt obtains the target primary frame, makes content-visibility:auto ancestors temporarily visible, calls the shared readiness helper, updates relevancy, then either performs forced layout or the existing interruptible-layout fallback. The proposal retains this sequence and the original query-frame ancestor walk. It only broadens the helper gate for clean col/group targets with dirty table providers; no pointer is stored across the flush.

That is a real caller effect, not covered by these hidden geometry tests. Native source alone does not establish that a new forced layout is harmless to scroll alignment or containment. The current specification distinguishes scrolling an auto element while size containment remains active from focusing it, which removes skipping first; a hidden ancestor instead prevents scrolling. A test expecting the final visible box to be exactly aligned could therefore be a false oracle. [Containment restrictions, points5–6](https://drafts.csswg.org/css-contain-2/#cv-notes).

Existing `content-visibility-058.html` is a useful separate regression: it uses contain-intrinsic-size, an offscreen auto ancestor, an absolute descendant and a reference screenshot. It neither targets col/group nor establishes that this new provider branch executed. Its source is retained, but no new runtime result is claimed.

Before a dedicated scroll-provider case, establish `contentvisibilityautostatechange` with skipped=true without querying target geometry, mutate the relevant table while still skipped, invoke scrollIntoView once, and retain the subsequent state/scroll observations against a separately justified size-contained reference. A fixed distance plus a few animation frames is not a reliable branch-coverage gate. An event timeout must be calibration failure, not a passing no-op. This task deliberately adds no such asynchronous test; auto-scroll semantics, relevance timing and continuation lifetime remain open acceptance boundaries.

## Static validation and limits

`STATIC-CHECK.json` records Node syntax exit0, exact20-name registration and descriptor equality, and four pure CSSOM-union controls including zero rectangles. No DOM, layout, browser or process launch occurred. The fixture is ready for root review and calibration; no claim that either baseline or candidate passes these new cases.
