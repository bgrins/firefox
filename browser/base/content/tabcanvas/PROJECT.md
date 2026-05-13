# Tab Canvas - Project Plan

## Vision

A Figma-style infinite canvas where browser tabs are represented as visual cards
that users can spatially organize, group, scale, and manage. The canvas replaces
the traditional linear tab strip with a 2D workspace for visual tab management.

The feature is built as a standalone canvas engine (`canvas-engine.js`) with zero
Firefox dependencies, plus a thin browser-chrome adapter (`browser-tabcanvas.js`).
Development focuses primarily on the standalone editor, tested via Playwright,
before integrating into the browser.

## Current State (as of May 2026)

### What Works

- **Core canvas interactions**: Pan (scroll, space+drag, middle-click), zoom
  (ctrl+scroll, ctrl+/-, ctrl+0 reset, ctrl+1 fit-all), all with Figma-style
  behavior (bare scroll = pan, ctrl+scroll = zoom toward cursor).
- **Node management**: Add, remove, select, multi-select (shift+click), marquee
  selection, move (drag from anywhere on node), resize (8 handles), arrow key
  nudge, delete key.
- **Snap-to-grid**: 8px grid. Positions and sizes snap during drag, resize, and
  nudge. Snap alignment guides (red lines) appear when edges align with other
  objects during drag.
- **Tab Groups (Frames)**: Create via F key or toolbar. Groups are dashed-border
  containers. Nodes belong to groups via center-point containment. Groups
  auto-expand to fit children. Groups auto-shrink when children leave. Moving a
  group moves all its children. Deleting a group keeps its children.
- **Visual feedback**: Drop-target highlight (green glow) when dragging a node
  over a group. Selection border + resize handles. Grabbing cursor during
  drag/pan.
- **Double-click**: Detected via click timing (400ms window) since pointer
  capture suppresses native dblclick. In browser integration, double-click
  activates the tab and closes the canvas.
- **Test suite**: 44 Playwright tests covering initialization, selection, move,
  resize, pan/zoom, tab groups, delete, double-click, drag threshold, zoom
  clamping, multi-drag, node-leaving-frame, and API methods. Self-contained
  via `webServer` config.
- **Browser integration**: Ctrl/Cmd+I toggles canvas overlay. Tabs rendered as
  cards with favicon + title headers and PageThumbs thumbnails. Tab events
  (open/close/modify/select) sync to canvas. Thumbnail refresh on re-show.
  Position preservation across show/hide cycles.

### Architecture

```
tabcanvas/
  canvas-engine.js     Core InfiniteCanvas class (zero Firefox deps)
  canvas-engine.css    Core styles (class-based, no IDs)
  test.html            Standalone test/dev page
  test.js              Test page setup (mock data, toolbar, event log)
  test-canvas-engine.js  Playwright test suite (44 tests)
  playwright.config.js   Playwright config with webServer

browser-tabcanvas.js   Browser chrome adapter (TabCanvas object)
browser-tabcanvas.css  Overlay shell (show/hide only)
```

The engine/adapter separation is clean. `InfiniteCanvas` knows nothing about
Firefox. `TabCanvas` maps gBrowser tabs to canvas nodes and handles thumbnails.

## Known Bugs

### P0 - Breaks Things

1. **`_screenToCanvas` missing container offset** - The coordinate transform
   does not subtract the container's bounding rect position. Marquee selection
   and F-to-create-frame produce incorrect coordinates when the container is not
   at page origin (always true in browser chrome due to toolbar offset; also
   true in test page due to 40px toolbar).
   - File: `canvas-engine.js`, `_screenToCanvas()` / `_canvasToScreen()`
   - Fix: Subtract `container.getBoundingClientRect().left/top`

### P1 - Important

2. **Dot grid does not track pan/zoom** - The `::before` pseudo-element has
   fixed `background-size: 30px` and no `background-position`. Dots stay fixed
   to screen instead of moving with the canvas.
   - File: `canvas-engine.css`, `.infinite-canvas::before`
   - Fix: Set CSS custom properties from `_updateTransform()`, use in CSS

3. **`view-change` not emitted from all zoom/pan paths** - Only emitted after
   pan gesture ends. Wheel zoom, keyboard zoom, `zoomTo()`, and `fitAll()` do
   not emit. The test.js toolbar uses a MutationObserver hack to work around
   this.
   - File: `canvas-engine.js`, `_onWheel`, keyboard zoom handlers, `zoomTo`,
     `fitAll`

4. **No `destroy()` or `off()` methods** - Event listeners and callbacks cannot
   be cleaned up. Memory leak if canvas is rebuilt.

5. **Node-add in test.js uses screen coordinates** - The "+" button calculates
   position in screen space but passes to `addNode` which expects canvas space.
   New nodes appear at wrong positions when panned/zoomed.
   - File: `test.js`, `btnAddNode` click handler

## Performance Concerns (for 50+ nodes)

| Issue | Impact | Fix |
|-------|--------|-----|
| `_applyRect` sets 4 individual style props | Layout thrashing on drag with many selected | Use `transform: translate()` + width/height |
| `_collectNonDragEdges` rebuilds every pointermove | O(n) per frame during drag | Cache at drag start |
| `_showSnapGuides` calls `_getAllBounds()` every move | O(n) per frame during drag | Cache bounds at drag start |
| Guide DOM elements created/destroyed per frame | DOM thrashing | Reuse element pool |
| No rAF throttling on drag/resize/pan | Can process 120+ events/sec | Gate behind requestAnimationFrame |
| `_updateSelectionVisuals` iterates all items | O(n) per selection change | Only toggle changed items |
| CSS transitions during interaction | GPU compositing on every node | Suppress transitions during drag/marquee |
| No viewport culling | All 100+ nodes in DOM | Only render visible nodes |

## Roadmap

### Phase 1: Engine Foundation Fixes

Focus: Fix bugs and missing APIs that block all subsequent work.

- [x] Fix `_screenToCanvas` / `_canvasToScreen` to subtract container offset
- [x] Make dot grid track pan/zoom via CSS custom properties
- [x] Emit `view-change` from all zoom/pan code paths
- [x] Add `destroy()` method (removes all event listeners and DOM)
- [x] Add `off(eventName, callback)` for listener removal
- [x] Fix test.js node-add to use `_screenToCanvas`
- [x] Add tests for coordinate transforms, frame resize, auto-expand/shrink

### Phase 2: Performance

Focus: Make the engine handle 50-100+ nodes smoothly.

- [x] rAF throttle `_onPointerMove` (gates all interaction handlers)
- [x] Use CSS transforms for node positioning instead of left/top
- [x] Cache snap guide edges at drag start, not per frame
- [x] Pool/reuse snap guide DOM elements
- [x] Suppress CSS transitions during active interaction (`is-interacting`)
- [x] Only toggle selection class on changed items (targeted select/deselect)
- [x] Add stress test: create 100 nodes, measure drag FPS

### Phase 3: Feature Completeness

Focus: Bring the standalone editor to feature parity with Figma basics.

- [x] **Serialization**: `toJSON()` / `fromJSON()` for full canvas state
- [x] **Undo/Redo**: Command stack with Ctrl+Z / Ctrl+Shift+Z
- [x] **Zoom-to-selection**: `fitSelection()` zooms to selected items
- [x] **Programmatic positioning API**: `setNodePosition()`, `getFrameChildren()`
- [x] **Frame label editing**: Double-click frame label to rename inline
- [x] **Z-index management**: `bringToFront()` / `sendToBack()`
- [x] **Auto-layout**: `autoLayout(frameId)` arranges nodes in grid within frames
- [x] **Node color/theming**: `setNodeColor(id, bg, header)`, group colors auto-assigned
- [x] **Visual group membership**: `data-frame-id` attr + `--group-color` CSS property on nodes

### Phase 4: Browser Integration

Focus: Connect the standalone engine to Firefox's tab system.

- [ ] **Persistence**: Save/restore canvas layout via SessionStore or prefs
- [ ] **Tab group mapping**: Sync canvas frames with Firefox tab groups
- [ ] **Stable node IDs**: Use `tab.permanentKey` instead of `linkedPanel`
- [ ] **Throttled thumbnail capture**: Queue-based, refresh visible tabs periodically
- [ ] **Narrow keyboard interception**: Only intercept keys the canvas handles
- [ ] **Show/hide animation**: Fade + scale transition for overlay
- [ ] **Remove duplicate zoom indicator** from browser-box.inc.xhtml

### Phase 5: Polish

- [x] Right-click context menu (node: delete/z-order, frame: rename/auto-layout/delete, canvas: add node/group/fit)
- [x] Minimap overview widget (bottom-right, shows node dots + viewport rect, click to pan)
- [x] Visual group membership (colored left border strip on nodes via `--group-color`)
- [x] Auto-assigned group colors from palette
- [ ] Firefox design system tokens for theming
- [ ] Accessibility (ARIA roles, keyboard navigation, screen reader)
- [ ] RTL support
- [ ] Touch/trackpad gesture refinement

## Running Tests

```bash
cd browser/base/content/tabcanvas
npx playwright test
```

The `playwright.config.js` auto-starts an HTTP server on port 9876 and runs
44 tests in Chromium headless. Tests take ~5 seconds.

## Dev Workflow

1. Edit `canvas-engine.js` / `canvas-engine.css`
2. Open `test.html` in a browser for manual testing
3. Run `npx playwright test` to verify
4. For browser integration: `MOZCONFIG=mozconfig-artifact ./mach build faster`
   then `MOZCONFIG=mozconfig-artifact ./mach run`, press Ctrl/Cmd+I
