# Tab Canvas TODO

## Interaction fixes (high priority)

- [ ] **Click-into-group selection**: When a group is selected and you click a
  node inside it, the selection should focus into that inner node (deselect the
  group, select just the node). This matches Figma's nested selection model.
- [ ] **Edge-of-viewport auto-pan during drag**: When dragging a node near the
  edge, automatically pan the canvas. Needs careful implementation to not
  interfere with click detection.
- [ ] **Shift+drag to lock aspect ratio during resize**

## Engine features

- [ ] Tab key to cycle selection through nodes
- [ ] Double-click on node body to "enter" the tab (emit event for adapter)
- [ ] Copy/paste (Ctrl+C/Ctrl+V)
- [ ] Distance labels on gap snap indicators (show "40px" between the lines)
- [ ] Grid dots should dim at low zoom, intensify at high zoom

## Visual polish

- [ ] Firefox design system tokens for theming (light/dark mode)
- [ ] Animated auto-layout and auto-expand (currently snaps instantly)
- [ ] Better placeholder content in node body for standalone test page
- [ ] Hover cursor feedback on node header before clicking

## Browser integration (Phase 4)

- [ ] Persistence via SessionStore (debounced toJSON on state changes)
- [ ] Map canvas groups to Firefox tab groups bidirectionally
- [ ] Stable node IDs via tab.permanentKey
- [ ] Handle pinned tabs (visual distinction, prevent group assignment)
- [ ] Handle container tabs (show container color)
- [ ] Handle lazy/unloaded tabs (placeholder instead of live content)
- [ ] Smarter new-tab placement in _syncNodes when canvas was hidden
- [ ] Show/hide animation on Ctrl+I toggle
- [ ] Narrow keyboard interception (only canvas keys, not all)

## Testing

- [ ] Stress test: 200+ nodes, measure FPS during drag
- [ ] Test group clone with children (ghost + final state)
- [ ] Cross-browser test (Firefox via playwright-firefox)
