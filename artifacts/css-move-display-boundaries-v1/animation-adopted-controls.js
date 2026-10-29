() => {
  const rows = [];
  for (const shape of ["root", "light-child", "shadow-child"]) {
    for (const operation of ["none", "self", "original-gap", "cross", "appendChild"]) {
      const fixture = document.createElement("section");
      document.body.append(fixture);
      const scope = fixture.attachShadow({mode: "open"});
      const style = document.createElement("style");
      style.textContent = `@keyframes travel { from { margin-left: 0px; } to { margin-left: 100px; } }
        .animated { animation: travel 10s linear paused; }`;
      scope.append(style);
      const oldParent = document.createElement("div");
      const newParent = document.createElement("div");
      scope.append(oldParent, newParent);
      const moving = document.createElement("div");
      let animated = moving;
      if (shape !== "root") {
        animated = document.createElement("div");
        if (shape === "shadow-child") {
          const shadow = moving.attachShadow({mode: "open"});
          const sheet = new CSSStyleSheet();
          sheet.replaceSync(style.textContent);
          shadow.adoptedStyleSheets = [sheet];
          shadow.append(animated);
        } else {
          moving.append(animated);
        }
      }
      animated.className = "animated";
      animated.textContent = "x";
      oldParent.append(moving);
      const next = document.createElement("div");
      oldParent.append(next);
      getComputedStyle(newParent).display;
      const animation = animated.getAnimations()[0];
      animation.currentTime = 375;
      const sample = phase => {
        const actual = getComputedStyle(animated).marginLeft;
        const animations = animated.getAnimations();
        return {phase, actual, same: animations[0] === animation,
          originalTime: animation.currentTime, originalState: animation.playState,
          currentTime: animations[0]?.currentTime, count: animations.length,
          pending: animation.pending};
      };
      const before = sample("before");
      if (operation === "self") oldParent.moveBefore(moving, moving);
      if (operation === "original-gap") oldParent.moveBefore(moving, next);
      if (operation === "cross") newParent.moveBefore(moving, null);
      if (operation === "appendChild") newParent.appendChild(moving);
      const after = sample("after");
      rows.push({shape, operation, before, after});
      fixture.remove();
    }
  }
  return {userAgent: navigator.userAgent, rows, remainingFixtures: document.body.children.length};
}
