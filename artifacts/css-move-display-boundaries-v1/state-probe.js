() => {
  const rows = [];
  for (const mode of ["elements", "to-shadow-root", "from-shadow-root", "shadow-roots", "self-reference", "original-gap"]) {
    const fixture = document.createElement("div");
    document.body.append(fixture);
    const a = document.createElement("div");
    const b = document.createElement("div");
    fixture.append(a, b);
    const oldParent = ["from-shadow-root", "shadow-roots"].includes(mode)
      ? a.attachShadow({mode: "open"}) : a;
    const newParent = ["to-shadow-root", "shadow-roots"].includes(mode)
      ? b.attachShadow({mode: "open"}) : b;
    const moving = document.createElement("div");
    const inner = moving.attachShadow({mode: "open"});
    inner.innerHTML = `<style>
      @keyframes travel { from { margin-left: 0px; } to { margin-left: 100px; } }
      .animated { animation: travel 10s linear paused; }
    </style><div class="animated">x</div><div class="imperative">y</div>`;
    oldParent.append(moving);
    const next = document.createElement("div");
    oldParent.append(next);
    const animated = inner.querySelector(".animated");
    const imperative = inner.querySelector(".imperative");
    const cssAnimation = animated.getAnimations()[0];
    const scriptAnimation = imperative.animate([{opacity: 0}, {opacity: 1}], {duration: 10000});
    scriptAnimation.pause();
    cssAnimation.currentTime = 375;
    scriptAnimation.currentTime = 625;
    const sample = phase => ({
      phase,
      marginLeft: getComputedStyle(animated).marginLeft,
      cssIdentity: animated.getAnimations()[0] === cssAnimation,
      cssCount: animated.getAnimations().length,
      cssTime: cssAnimation.currentTime,
      cssState: cssAnimation.playState,
      scriptIdentity: imperative.getAnimations()[0] === scriptAnimation,
      scriptTime: scriptAnimation.currentTime,
      scriptState: scriptAnimation.playState,
    });
    const snapshots = [sample("before")];
    let error = null;
    try {
      if (mode === "self-reference" || mode === "original-gap") {
        oldParent.moveBefore(moving, mode === "self-reference" ? moving : next);
      } else {
        newParent.moveBefore(moving, null);
      }
      snapshots.push(sample("after"));
      oldParent.moveBefore(moving, next);
      snapshots.push(sample("restored"));
    } catch (caught) {
      error = `${caught.name}: ${caught.message}`;
    }
    rows.push({mode, error, snapshots});
    scriptAnimation.cancel();
    fixture.remove();
  }
  return {userAgent: navigator.userAgent, rows, remainingFixtures: document.body.children.length};
}
