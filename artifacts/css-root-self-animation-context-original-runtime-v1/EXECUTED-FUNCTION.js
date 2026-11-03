async () => JSON.stringify(await (
(async () => {
  const result = {schema: "root-self-animation-context-v1", userAgent: navigator.userAgent, cases: [], errors: [], cleanup: false};
  const frames = [], animations = [];
  const variationNumber = raw => {
    const match = /^"wdth"\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)$/i.exec(raw);
    return match ? Number(match[1]) : null;
  };
  const settle = async win => {
    await win.document.fonts.ready;
    await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
  };
  const makeFrame = async (unit, size, line) => {
    const frame = document.createElement("iframe");
    frame.title = "Root animation context diagnostic";
    const loaded = new Promise(resolve => {frame.onload = resolve;});
    frame.srcdoc = `<!doctype html><meta charset="utf-8"><title>Root animation context</title><style>
      html { writing-mode: horizontal-tb; text-orientation: mixed; }
      html.configured { font-family: monospace; font-size: ${size}px; line-height: ${line}px; }
      html.ordinary-variation { font-variation-settings: "wdth" calc(2${unit} / 1px); }
      html.ordinary-size { font-size: 2${unit}; }
      #rem { width: 100rem; height: 0; } #rlh { width: 100rlh; height: 0; }
    </style><div id="rem"></div><div id="rlh"></div>`;
    frames.push(frame); document.body.append(frame); await loaded;
    const win = frame.contentWindow, doc = frame.contentDocument, root = doc.documentElement;
    await settle(win);
    const initial = {fontSize: win.getComputedStyle(root).fontSize, lineHeight: win.getComputedStyle(root).lineHeight,
      rem: doc.getElementById("rem").getBoundingClientRect().width / 100,
      rlh: doc.getElementById("rlh").getBoundingClientRect().width / 100};
    root.className = "configured";
    return {frame, win, doc, root, initial};
  };
  const makeAnimation = (root, property, values) => {
    const animation = root.animate(values.map(value => ({[property]: value})), {duration: 1000, fill: "both"});
    animations.push(animation); animation.pause(); animation.currentTime = 500; return animation;
  };
  const info = animation => ({targetIsRoot: animation.effect.target === animation.effect.target.ownerDocument.documentElement,
    progress: animation.effect.getComputedTiming().progress, playState: animation.playState,
    currentTime: animation.currentTime, keyframes: animation.effect.getKeyframes()});
  try {
    for (const unit of ["rem", "rlh"]) {
      for (const property of ["fontVariationSettings", "fontSize"]) {
        for (const [size, line] of [[23, 37], [31, 47]]) {
          const reference = await makeFrame(unit, size, line);
          reference.root.className = "configured ordinary-variation";
          const ordinaryVariationRaw = reference.win.getComputedStyle(reference.root).fontVariationSettings;
          reference.root.className = "configured ordinary-size";
          const ordinarySizeRaw = reference.win.getComputedStyle(reference.root).fontSize;
          const target = await makeFrame(unit, size, line);
          const read = () => target.win.getComputedStyle(target.root)[property];
          const literalValues = property === "fontSize" ? ["20px", "40px"] : ['"wdth" 20', '"wdth" 40'];
          const literal = makeAnimation(target.root, property, literalValues);
          const literalRaw = read(), literalInfo = info(literal);
          literal.cancel();
          const inheritedControl = makeAnimation(target.root, "fontSize", ["1em", "3em"]);
          const inheritedControlRaw = target.win.getComputedStyle(target.root).fontSize;
          const inheritedControlInfo = info(inheritedControl);
          inheritedControl.cancel();
          const restored = target.win.getComputedStyle(target.root);
          const underlying = {fontSize: restored.fontSize, lineHeight: restored.lineHeight,
            writingMode: restored.writingMode, textOrientation: restored.textOrientation};
          const values = [1, 3].map(n => property === "fontSize" ? `${n}${unit}` : `"wdth" calc(${n}${unit} / 1px)`);
          const entry = {unit, property, size, line, compatMode: target.doc.compatMode,
            referenceCompatMode: reference.doc.compatMode, initial: target.initial, referenceInitial: reference.initial,
            supports: values.map(value => target.win.CSS.supports(property === "fontSize" ? "font-size" : "font-variation-settings", value)),
            literalRaw, literalInfo, inheritedControlRaw, inheritedControlInfo, underlying, ordinaryVariationRaw, ordinaryVariationValue: variationNumber(ordinaryVariationRaw),
            ordinarySizeRaw, ordinarySizeValue: parseFloat(ordinarySizeRaw), samples: []};
          result.cases.push(entry);
          const animation = makeAnimation(target.root, property, values);
          const take = timing => {
            const raw = read();
            entry.samples.push({timing, raw, value: property === "fontSize" ? parseFloat(raw) : variationNumber(raw), animation: info(animation)});
          };
          take("first"); await settle(target.win); take("settled");
          animation.cancel(); target.frame.remove(); reference.frame.remove();
        }
      }
    }
  } catch (error) {result.errors.push({name: error.name, message: error.message, stack: error.stack});}
  finally {
    for (const animation of animations) animation.cancel();
    for (const frame of frames) frame.remove();
    result.cleanup = frames.every(frame => !frame.isConnected);
  }
  return result;
})()

))