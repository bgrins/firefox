# Tab Canvas TODO

## Immediate (before next feature work)

- [ ] **Data model design** - Plan two-way sync between canvas state and tabbrowser
  - How does the canvas learn about tab opens/closes/moves from tabbrowser?
  - How does tabbrowser learn about canvas operations (group changes, tab closes)?
  - What is the source of truth? (canvas state, tabbrowser state, or a shared model?)
  - How does undo/redo work across both internal canvas ops and external tab events?
  - See STATE-MANAGEMENT.md for detailed design

- [ ] **Multi-selection improvements** - Select multiple tabs, drag as group, align
  - Box select should highlight what will be selected during drag
  - Shift+click on group label should select group + all children
  - Right-click on multi-selection should offer batch operations

## Engine features

- [ ] Ctrl+D to duplicate selection (same as alt+drag but in-place offset)
- [ ] Ctrl+G to group selected nodes into a new tab group
- [ ] Tab key to cycle selection through nodes
- [ ] Double-click on node body to "enter" the tab (same as browser activate)
- [ ] Minimap drag to pan (currently click-only)
- [ ] Zoom to selection (Shift+1)
- [ ] Copy/paste between canvas instances

## Visual polish

- [ ] Firefox design system tokens for theming (light/dark mode)
- [ ] Smoother animations for auto-layout and auto-expand
- [ ] Better minimap - show group boundaries, not just node dots
- [ ] Grid dots should dim at low zoom, intensify at high zoom
- [ ] Selection count badge in toolbar

## Browser integration (Phase 4)

- [ ] ESM loading in browser chrome via ChromeUtils.importESModule
- [ ] Persistence via SessionStore
- [ ] Map canvas groups to Firefox tab groups
- [ ] Stable node IDs via tab.permanentKey
- [ ] Throttled thumbnail capture queue
- [ ] Show/hide animation on Ctrl+I toggle
- [ ] Narrow keyboard interception (only canvas keys, not all)

## Testing

- [ ] Stress test: 200+ nodes, measure FPS during drag
- [ ] Test mid-drag scroll compensation
- [ ] Test group clone with children (ghost + final state)
- [ ] Test alignment commands via toolbar buttons
- [ ] Cross-browser test (Firefox via playwright-firefox)
