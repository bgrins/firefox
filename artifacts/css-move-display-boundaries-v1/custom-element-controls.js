() => {
  const name = `move-audit-${Math.random().toString(36).slice(2)}`;
  customElements.define(name, class extends HTMLElement {
    constructor() { super(); this.events = []; }
    connectedCallback() { this.events.push("connected"); }
    disconnectedCallback() { this.events.push("disconnected"); }
    connectedMoveCallback() { this.events.push("moved"); }
  });
  const rows = [];
  for (const shape of ["root", "light-child", "shadow-child", "nested-shadow-child"]) {
    for (const operation of ["none", "self", "cross", "appendChild"]) {
      const fixture = document.createElement("div");
      const oldParent = document.createElement("div");
      const newParent = document.createElement("div");
      fixture.append(oldParent, newParent);
      document.body.append(fixture);
      const target = document.createElement(name);
      const moving = shape === "root" ? target : document.createElement("div");
      if (shape === "light-child") moving.append(target);
      if (shape === "shadow-child") moving.attachShadow({mode: "open"}).append(target);
      if (shape === "nested-shadow-child") {
        const host = document.createElement("div");
        moving.attachShadow({mode: "open"}).append(host);
        host.attachShadow({mode: "open"}).append(target);
      }
      oldParent.append(moving);
      const initial = [...target.events];
      target.events.length = 0;
      if (operation === "self") oldParent.moveBefore(moving, moving);
      if (operation === "cross") newParent.moveBefore(moving, null);
      if (operation === "appendChild") newParent.appendChild(moving);
      rows.push({shape, operation, initial, after: [...target.events]});
      fixture.remove();
    }
  }
  return {userAgent: navigator.userAgent, rows, remainingFixtures: document.body.children.length};
}
