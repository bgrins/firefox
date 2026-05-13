# Tab Canvas - State Management Design

## The Problem

The canvas has two worlds that need to stay in sync:

1. **Canvas state**: Node positions, sizes, group membership, z-order, view state
2. **Browser state**: Open tabs, tab groups, tab titles, favicons, loading state

Changes can originate from either side:
- User drags a tab card on the canvas -> canvas state changes
- User closes a tab via the browser tab bar -> browser state changes
- User creates a group on canvas -> needs to create a browser tab group
- User moves a tab between groups on canvas -> needs to update browser tab group
- External: a web page changes its title -> canvas card needs to update

Undo/redo crosses both worlds: undoing a "close tab" on the canvas means
re-opening the tab in the browser.

## Design Options

### Option A: Canvas is Source of Truth

Canvas owns all state. Browser adapter reads from canvas and pushes changes
to tabbrowser.

```
User action -> Canvas state change -> Emit event -> Adapter updates tabbrowser
Tab event   -> Adapter updates canvas state
```

**Pros**: Simple, canvas engine stays self-contained.
**Cons**: Canvas doesn't know about browser-specific state (loading, audio, etc.).
Undo/redo for browser operations (close tab) is complex because the canvas
needs to re-create browser objects.

### Option B: Browser is Source of Truth

Tabbrowser owns all state. Canvas is a pure view layer that reads from
tabbrowser and renders.

```
User action -> Canvas dispatches intent -> Adapter modifies tabbrowser ->
              tabbrowser fires event -> Canvas re-renders
```

**Pros**: Single source of truth. Browser state is always correct.
**Cons**: Every canvas interaction has a round-trip through the adapter.
Canvas engine can't work standalone (breaks our architecture).

### Option C: Shared Model with Sync (Recommended)

A shared data model (`TabCanvasModel`) sits between the canvas engine and
the browser adapter. Both sides read/write to it. Changes are reconciled.

```
                    TabCanvasModel
                   /              \
     InfiniteCanvas                BrowserAdapter
     (positions, groups,           (tabs, groups,
      z-order, view state)          titles, thumbnails)
```

The model holds:
- `tabs[]` - each tab has: id, canvasPosition, groupId, browserTab reference
- `groups[]` - each group has: id, label, color, canvasPosition
- `viewState` - pan, zoom

**Change flow:**
1. Canvas operation (move, resize, group) -> model update -> emit change event
2. Browser event (tab open/close/modify) -> model update -> emit change event
3. Canvas listens to model changes and updates its nodes
4. Adapter listens to model changes and updates tabbrowser

**Undo/redo:**
The model maintains a command stack. Each command knows how to undo itself
in both the canvas and browser worlds.

## Recommended: Option C with Lazy Sync

### The Model

```js
class TabCanvasModel {
  constructor() {
    this.tabs = new Map();      // tabId -> TabEntry
    this.groups = new Map();    // groupId -> GroupEntry
    this.viewState = { panX: 0, panY: 0, zoom: 1 };
    this.undoStack = [];
    this.redoStack = [];
  }
}

class TabEntry {
  constructor(id) {
    this.id = id;               // stable ID (permanentKey)
    this.x = 0;                 // canvas position
    this.y = 0;
    this.width = 280;
    this.height = 212;
    this.groupId = null;        // which group it belongs to
    this.title = "";            // from browser
    this.iconUrl = "";          // from browser
    this.thumbnailData = null;  // captured thumbnail
    this.browserTab = null;     // weak ref to actual tab (not serialized)
  }
}

class GroupEntry {
  constructor(id) {
    this.id = id;
    this.x = 0;
    this.y = 0;
    this.width = 600;
    this.height = 400;
    this.label = "Tab Group";
    this.color = "#0a84ff";
    this.browserTabGroup = null; // weak ref (not serialized)
  }
}
```

### Sync Rules

1. **Canvas -> Model -> Browser**
   - User moves tab card: model.tabs[id].x/y updates, no browser change needed
   - User deletes tab card: model removes tab, adapter calls gBrowser.removeTab()
   - User creates group: model adds group, adapter creates tabGroup in browser
   - User moves tab between groups: model updates groupId, adapter moves tab

2. **Browser -> Model -> Canvas**
   - Tab opened: adapter creates TabEntry in model, canvas adds node
   - Tab closed: adapter removes TabEntry from model, canvas removes node
   - Tab title changed: adapter updates TabEntry.title, canvas updates node header
   - Tab group changed externally: adapter updates groupId, canvas reparents

3. **Conflict resolution**
   - Browser wins for tab existence (if a tab is closed externally, it's gone)
   - Canvas wins for positions (browser doesn't know about spatial layout)
   - Groups sync bidirectionally (canvas groups map to browser tab groups)

### Undo/Redo Strategy

Commands are model-level operations:

```js
class MoveCommand {
  constructor(model, tabId, fromX, fromY, toX, toY) { ... }
  execute() { model.tabs[tabId].x = toX; model.tabs[tabId].y = toY; }
  undo() { model.tabs[tabId].x = fromX; model.tabs[tabId].y = fromY; }
}

class DeleteTabCommand {
  constructor(model, adapter, tabId) { ... }
  execute() {
    this.snapshot = model.tabs[tabId].serialize();
    model.removeTab(tabId);
    adapter.closeTab(tabId);
  }
  undo() {
    adapter.reopenTab(this.snapshot);  // SessionStore.undoCloseTab or similar
    model.addTab(this.snapshot);
  }
}

class ChangeGroupCommand {
  constructor(model, adapter, tabId, fromGroup, toGroup) { ... }
  execute() { model.setGroup(tabId, toGroup); adapter.moveTabToGroup(tabId, toGroup); }
  undo() { model.setGroup(tabId, fromGroup); adapter.moveTabToGroup(tabId, fromGroup); }
}
```

### Serialization

The model serializes to JSON for SessionStore persistence:

```js
model.toJSON() -> {
  tabs: [{id, x, y, width, height, groupId}, ...],
  groups: [{id, x, y, width, height, label, color}, ...],
  viewState: {panX, panY, zoom}
}
```

Browser-specific references (browserTab, browserTabGroup) are NOT serialized.
On restore, the adapter matches tabs by permanentKey.

### Migration Path

1. **Now**: InfiniteCanvas has its own internal state. No model layer.
2. **Step 1**: Extract position/group data into a TabCanvasModel class.
   Canvas engine becomes a pure renderer that reads from the model.
3. **Step 2**: Adapter writes browser events to the model instead of
   directly calling canvas methods.
4. **Step 3**: Undo/redo moves from canvas engine to the model layer.
5. **Step 4**: Persistence via model.toJSON() / fromJSON().

### Impact on Current Code

- `canvas-engine.js` keeps its current API but becomes "dumb" about data.
  The model calls `canvas.addNode()`, `canvas.removeNode()`, etc.
- `browser-tabcanvas.js` becomes thinner: it creates the model, listens
  to tab events, and connects model to canvas.
- `snap-manager.js` unchanged (pure geometry, no state).
- Undo/redo commands move from canvas engine to the model.
- `toJSON`/`fromJSON` on the canvas engine can stay as a convenience
  but the model is the authoritative serialization point.
