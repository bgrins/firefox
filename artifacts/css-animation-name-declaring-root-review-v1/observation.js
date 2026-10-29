async function observeAnimationNameDeclaringRoot() {
  const frame = document.createElement("iframe");
  document.body.append(frame);
  try {
    const doc = frame.contentDocument;
    doc.open();
    doc.write(`<!doctype html><style>
      @keyframes root-collision { from, to { background-color: green; } }
      .outer::part(target) { animation: root-collision 1000ms linear both paused; }
      #literal-green { background-color: green; }
      #literal-blue { background-color: blue; }
    </style><div id="literal-green"></div><div id="literal-blue"></div>`);
    doc.close();
    const win = frame.contentWindow;
    const cases = [];
    for (const name of ["outer-collision", "inner-control", "outer-only-control"]) {
      const host = doc.createElement("div");
      host.className = name === "inner-control" ? "" : "outer";
      doc.body.append(host);
      const root = host.attachShadow({mode: "open"});
      const keyframes = doc.createElement("style");
      const rules = "@keyframes root-collision { from, to { background-color: blue; } }";
      if (name !== "outer-only-control") keyframes.textContent = rules;
      root.append(keyframes);
      const style = doc.createElement("style");
      style.textContent = "[part] { display: block; width: 10px; height: 10px; background-color: red; }";
      if (name === "inner-control") style.textContent += "[part] { animation: root-collision 1000ms linear both paused; }";
      root.append(style);
      const target = doc.createElement("div");
      target.setAttribute("part", "target");
      root.append(target);
      cases.push({name, target, keyframes, rules});
    }
    const literals = Object.fromEntries(["green", "blue"].map(color => [color,
      win.getComputedStyle(doc.getElementById(`literal-${color}`)).backgroundColor]));
    const snapshots = [];
    for (const phase of ["initial", "remove-inner-keyframes", "restore-inner-keyframes"]) {
      for (const item of cases) {
        if (item.name !== "outer-only-control") {
          if (phase === "remove-inner-keyframes") item.keyframes.textContent = "";
          if (phase === "restore-inner-keyframes") item.keyframes.textContent = item.rules;
        }
      }
      for (const item of cases) {
        const animations = item.target.getAnimations();
        for (const animation of animations) {
          await animation.ready;
          animation.currentTime = 500;
        }
        const read = () => win.getComputedStyle(item.target).backgroundColor;
        const expectedColor = item.name === "inner-control" && phase !== "remove-inner-keyframes" ? "blue" : "green";
        snapshots.push({name: item.name, phase, expectedColor,
          expected: literals[expectedColor], first: read(), second: read(),
          animationCount: animations.length,
          animationName: win.getComputedStyle(item.target).animationName,
          keyframeColors: animations.map(a => a.effect.getKeyframes().map(k => k.backgroundColor))});
      }
    }
    return JSON.parse(JSON.stringify({support: win.CSS.supports("animation-name", "root-collision"), literals, snapshots}));
  } finally {
    frame.remove();
  }
}
