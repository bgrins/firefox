# Tab Canvas - State Management Design

## Principle: Keep It Simple

The canvas engine already owns its state and works well. The browser adapter
bridges events bidirectionally. We do NOT need a separate model layer at this
stage. The adapter becomes slightly smarter about persistence and tab group
mapping, but the fundamental architecture stays the same.

## Architecture

```
  InfiniteCanvas (owns positions, groups, z-order, undo/redo)
       |  emits events: node-move, node-delete, frame-create, etc.
       |  provides: toJSON(), fromJSON()
       v
  BrowserAdapter (bridges canvas <-> tabbrowser)
       |  listens to canvas events -> updates tabbrowser
       |  listens to tab events -> updates canvas
       |  persists layout via SessionStore
       v
  tabbrowser (owns tab existence, titles, loading state)
```

**The canvas engine stays as-is.** It is NOT a "pure renderer." It owns all
interaction logic (drag, resize, snap) and reports final results via events.
The adapter does not intercept 60fps drag updates -- only the final `node-move`
event after drag ends.

## Persistence

The adapter debounce-saves on significant events:

```js
_scheduleSave() {
  clearTimeout(this._saveTimer);
  this._saveTimer = setTimeout(() => {
    let data = this._canvas.toJSON();
    SessionStore.setCustomWindowValue(window, "tabCanvasLayout", JSON.stringify(data));
  }, 500);
}
```

Events that trigger save: `node-move`, `node-resize`, `node-delete`,
`frame-create`, `frame-label-change`, `selection-change` (for group membership).

On startup, the adapter checks for saved layout:
```js
let saved = SessionStore.getCustomWindowValue(window, "tabCanvasLayout");
if (saved) {
  this._canvas.fromJSON(JSON.parse(saved));
} else {
  this._buildNodes(); // fresh grid layout
}
```

## Tab Group Mapping

The adapter maintains a simple map:

```js
this._canvasToTabGroup = new Map();  // canvasFrameId -> browserTabGroupId
this._tabGroupToCanvas = new Map();  // browserTabGroupId -> canvasFrameId
```

**Canvas -> Browser sync:**
- `frame-create` event: call `gBrowser.addTabGroup(tabs, { label, color })`
- `frame-label-change` event: update browser tab group label
- Node dropped into frame: call `tabGroup.addTab(tab)`
- Node removed from frame: call `tabGroup.removeTab(tab)`

**Browser -> Canvas sync:**
- Tab group created externally: `_onTabGroupCreated` -> `canvas.addFrame()`
- Tab group removed externally: `_onTabGroupRemoved` -> `canvas.removeFrame()`
- Tab moved between groups: update canvas node's frameId

## Stable IDs

Use `tab.permanentKey` (survives session restore) instead of `linkedPanel`:

```js
_addTabNode(tab, index) {
  let id = "tab_" + tab.permanentKey;
  // ...
}
```

## Undo/Redo Boundary

The canvas engine's undo/redo handles **canvas operations only**:
- Move, resize, delete nodes/frames, create frames

For browser-side operations (close tab), the adapter can use Firefox's
built-in `SessionStore.undoCloseTab()`. These are separate undo stacks.
The canvas undo stack does NOT try to undo browser operations.

If a user deletes a tab on the canvas:
1. Canvas records a delete command (for undo of the canvas node)
2. Adapter calls `gBrowser.removeTab(tab)`
3. If user presses Ctrl+Z on canvas, the canvas re-adds the node
4. The adapter's undo handler re-opens the tab via `SessionStore.undoCloseTab()`
   (searching by permanentKey, not index)

This is a pragmatic split: the canvas handles spatial undo, the adapter
handles browser undo, and they coordinate via events.

## What Changes While Canvas Is Hidden

The adapter uses "lazy reconcile on show":
- Tab opens/closes while hidden: NOT applied to canvas immediately
- On next `show()`: `_syncNodes()` runs, adds new tabs, removes closed ones
- Existing node positions are preserved
- New nodes are placed in available empty space (not overlapping)

## Special Tab Types

- **Pinned tabs**: Visually distinct (smaller card, pin indicator).
  Cannot be dragged into groups. Adapter checks `tab.pinned`.
- **Container tabs**: Show container color via `tab.userContextId`.
  Purely visual, no special handling needed.
- **Lazy/unloaded tabs**: `tab.getAttribute("pending")` = true.
  Skip live thumbnail capture, show cached thumbnail or placeholder.

## Tab Ordering

The canvas is a 2D spatial organizer, NOT a tab reorderer. Tab order in the
browser tab strip remains authoritative. The canvas does not attempt to
derive or change linear tab order from spatial positions.

## Migration Path (Incremental)

1. Switch to `permanentKey` IDs (one-line change in adapter)
2. Add debounced persistence via SessionStore
3. Add tab group bidirectional mapping
4. Handle pinned/container/lazy tabs in adapter
5. Improve `_syncNodes` for smarter new-tab placement
