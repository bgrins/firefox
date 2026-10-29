() => {
  const rows = [];
  const selectors = [
    ".parent:has(> .marked)",
    ".parent:has(.marked .leaf)",
    ".child:first-child",
    ".child:last-child",
    ".child:nth-child(2)",
    ".child:nth-last-child(2)",
    ".marked + .child",
    ".marked ~ .child",
  ];
  const displays = ["block", "none", "contents"];
  for (const mode of ["ordinary", "shadow", "slotted"]) {
    for (const oldDisplay of displays) {
      for (const newDisplay of displays) {
        for (const movedDisplay of displays) {
          for (const operation of ["appendChild", "moveBefore"]) {
            for (const selector of selectors) {
              const fixture = document.createElement("div");
              document.body.append(fixture);
              const root = mode === "shadow"
                ? fixture.attachShadow({mode: "open"}) : fixture;
              const style = document.createElement("style");
              style.textContent = `
                .parent, .child { color: rgb(10, 20, 30); }
                ${selector} { color: rgb(40, 50, 60); }
                .block { display: block; }
                .none { display: none; }
                .contents { display: contents; }
              `;
              root.append(style);
              const oldParent = document.createElement("div");
              const newParent = document.createElement("div");
              oldParent.className = `parent ${oldDisplay}`;
              newParent.className = `parent ${newDisplay}`;
              root.append(oldParent, newParent);
              if (mode === "slotted") {
                for (const parent of [oldParent, newParent]) {
                  parent.attachShadow({mode: "open"}).append(document.createElement("slot"));
                }
              }
              const moved = document.createElement("div");
              moved.className = `child marked ${movedDisplay}`;
              const leaf = document.createElement("span");
              leaf.className = "leaf";
              moved.append(leaf);
              const oldA = document.createElement("div");
              const oldB = document.createElement("div");
              const newA = document.createElement("div");
              oldA.className = oldB.className = newA.className = "child";
              oldParent.append(moved, oldA, oldB);
              newParent.append(newA);
              const targets = [oldParent, oldA, oldB, newParent, newA, moved];
              const snapshot = phase => {
                const actual = targets.map(node => getComputedStyle(node).color);
                return targets.map((node, index) => ({
                  phase,
                  target: index,
                  actual: actual[index],
                  expected: node.matches(selector) ? "rgb(40, 50, 60)" : "rgb(10, 20, 30)",
                }));
              };
              const before = snapshot("before");
              let error = null;
              let after = [];
              let restored = [];
              try {
                if (operation === "moveBefore") {
                  newParent.moveBefore(moved, null);
                } else {
                  newParent.appendChild(moved);
                }
                after = snapshot("after");
                if (operation === "moveBefore") {
                  oldParent.moveBefore(moved, oldA);
                } else {
                  oldParent.insertBefore(moved, oldA);
                }
                restored = snapshot("restored");
              } catch (caught) {
                error = `${caught.name}: ${caught.message}`;
              }
              rows.push({mode, oldDisplay, newDisplay, movedDisplay, operation,
                selector, error, snapshots: [...before, ...after, ...restored]});
              fixture.remove();
            }
          }
        }
      }
    }
  }
  return {userAgent: navigator.userAgent, moveBeforeSupported: typeof Element.prototype.moveBefore === "function",
    rows, remainingFixtures: document.body.children.length};
}
