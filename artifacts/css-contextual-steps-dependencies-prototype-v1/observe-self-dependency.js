async function observeContextualEasingSelfDependency() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:320px;height:180px;border:0";
  const loaded = new Promise(resolve => frame.onload = resolve);
  frame.srcdoc = "<!doctype html><html><head></head><body></body></html>";
  document.body.append(frame);
  try {
    await loaded;
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const easing = "steps(calc(1 + max(0, sign(15px - 1em))), end)";
    const supported = win.CSS.supports("animation-timing-function", easing);
    if (!supported) return {observationOnly: true, supported, snapshots: []};
    const sheet = doc.createElement("style");
    sheet.textContent = `
      @keyframes contextual {
        from { font-size: 10px; animation-timing-function: ${easing} }
        to { font-size: 20px }
      }
      @keyframes literal { from { font-size: 10px } to { font-size: 20px } }
      #target { animation: contextual 1000ms linear both paused }
      #one { animation: literal 1000ms steps(1, end) both paused }
      #two { animation: literal 1000ms steps(2, end) both paused }
    `;
    doc.head.append(sheet);
    const elements = ["target", "one", "two"].map(id => {
      const element = doc.createElement("div");
      element.id = id;
      element.textContent = id;
      doc.body.append(element);
      return element;
    });
    const animations = elements.map(element => element.getAnimations()[0]);
    for (const animation of animations) animation.currentTime = 750;
    const snapshots = [];
    for (let i = 0; i < 6; ++i) {
      snapshots.push(elements.map((element, index) => ({
        id: element.id,
        font: win.getComputedStyle(element).fontSize,
        sameAnimation: element.getAnimations()[0] === animations[index],
        currentTime: animations[index].currentTime,
        keyframes: animations[index].effect.getKeyframes(),
      })));
      await new Promise(resolve => win.requestAnimationFrame(resolve));
    }
    return {observationOnly: true, supported, easing, snapshots};
  } finally {
    frame.remove();
  }
}
